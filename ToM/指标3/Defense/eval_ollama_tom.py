"""
Evaluate any local Ollama model on the Hi-ToM benchmark and report ToM level.

See Defense/README.md for full usage instructions.

Usage:
    python Defense/eval_ollama_tom.py                               # qwen3.5, all orders, 20 samples
    python Defense/eval_ollama_tom.py --model gpt-oss:latest
    python Defense/eval_ollama_tom.py --orders 0 1 --num_samples 5  # quick test
    python Defense/eval_ollama_tom.py --think --max_tokens 8192     # with extended thinking
"""

import argparse
import json
import os
import re
import string
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Defense.tom_level.measure import ToMOrder, level_from_joint_accuracy
from Defense.tom_level.ollama_backend import (
    generate_response,
    is_ollama_available,
    list_ollama_models,
)

HI_TOM_DATA = os.path.join(
    os.path.dirname(__file__), "..", "LLMToM", "Hi-ToM", "Hi-ToM_data"
)

# --------------------------------------------------------------------------- #
# Prompt
# --------------------------------------------------------------------------- #
SYSTEM_PROMPT = """\
[Story]
The bag of potato chips has moldy chips in it. Mary picks up the bag in the supermarket and walks to the cashier.

[Candidate Answers]
A. Reasonable
B. Not reasonable

[Question]:
Next, Mary "pay for the chips" and not "report the moldy chips". The behavior of Mary can be best described as:

[Output]:
Step1-Is Mary likely to be aware that "The bag of potato chips has moldy chips in it."?:
    There is no explicit mention in the story that Mary notices the moldy chips. Mary simply picks up the bag and walks to the cashier without any hesitation or reaction. So, she is unlikely to be aware.

Step2-What will Mary likely do next?:
    Since Mary is unaware of the moldy chips (as deduced in Step 1), she is likely to proceed with her initial action, which is to pay for the chips. Reporting the moldy chips would require her awareness of the issue, which is not present in this scenario. So, she will Pay for the chips.

Step3-Next, Mary "pay for the chips" and not "report the moldy chips". The behavior of Mary can be best described as:
    Given that Mary is unaware of the mold, her action of paying for the chips is consistent with her knowledge of the situation. Her behavior is reasonable because she has no reason to suspect an issue with the chips. So, her behaviour is Reasonable.
So the answer is [A].

Read and understand the example above. Then a new story will be given, strictly follow the Note to provide an answer.
Note:
(1) Identify the fewest number of steps N (where 1 <= N <= 3) necessary to logically solve the problem, avoid unnecessary steps.
(2) The output's step should follow this format:
    Step1-Is xxx likely to be aware that "xxx"?:
    Step2-What will xxx likely do next:
    Step3-xxx "xxx" and not "xxx". The behavior of xxx can be best described as:
(3) Finally, enclose the answer index in square brackets, the output format is: So the answer is [answer index].\
"""


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

def parse_txt_file(filepath: str) -> dict:
    """Parse a Hi-ToM .txt file into story / question / answer / choices."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    story_lines, question_line, answer_line = [], "", ""
    choices: dict = {}
    tag = None

    for line in content.split("\n"):
        line_stripped = line.strip()
        if not line_stripped:
            tag = None
            continue

        if line_stripped.startswith("Story:"):
            tag = "story"
            rest = line_stripped[len("Story:"):].strip()
            if rest:
                story_lines.append(re.sub(r"^\d+\s+", "", rest))
        elif tag == "story" and re.match(r"^\d+\s+", line_stripped):
            story_lines.append(re.sub(r"^\d+\s+", "", line_stripped))
        elif line_stripped.startswith("Question:"):
            question_line = line_stripped[len("Question:"):].strip()
            tag = "question"
        elif line_stripped.startswith("Answer:"):
            answer_line = line_stripped[len("Answer:"):].strip()
            tag = "answer"
        elif line_stripped.startswith("Choices:"):
            choices_str = line_stripped[len("Choices:"):].strip()
            for m in re.finditer(r"([A-Z])\.\s*([^,]+)", choices_str):
                choices[m.group(1).strip()] = m.group(2).strip()
            tag = "choices"

    return {
        "story": "\n".join(story_lines).strip(),
        "question": question_line,
        "answer": answer_line,
        "choices": choices,
    }


# --------------------------------------------------------------------------- #
# Answer extraction
# --------------------------------------------------------------------------- #

def extract_answer(text: str):
    """
    Extract the predicted answer letter from model output.

    Priority:
      1. "[X]." pattern (canonical "So the answer is [X].")
      2. "[X]" pattern (bracket without period)
      3. Lowercase equivalents
      4. Last bracketed letter in the whole text (fallback)
    """
    for letter in string.ascii_uppercase:
        if f"[{letter}]." in text:
            return letter
    for letter in string.ascii_uppercase:
        if f"[{letter}]" in text:
            return letter
    for letter in string.ascii_lowercase:
        if f"[{letter}]." in text:
            return letter.upper()
    for letter in string.ascii_lowercase:
        if f"[{letter}]" in text:
            return letter.upper()
    # Last resort: any bracket in text
    brackets = re.findall(r"\[([A-Za-z])\]", text)
    if brackets:
        return brackets[-1].upper()
    return None


# --------------------------------------------------------------------------- #
# Prediction → answer text mapping
# --------------------------------------------------------------------------- #

def map_pred_to_text(pred_letter: str, sorted_choices: list) -> str:
    """
    Map the model's predicted letter (A, B, C…) back to the choice text.

    The formatted prompt labels sorted choices as A, B, C… regardless of
    their original keys, so we look up by index.
    """
    idx = ord(pred_letter.upper()) - ord("A")
    if idx < len(sorted_choices):
        return sorted_choices[idx][1]  # (original_key, text) → text
    return pred_letter  # fallback: return the letter itself


# --------------------------------------------------------------------------- #
# Single-order evaluation
# --------------------------------------------------------------------------- #

def evaluate_order(
    model: str,
    tell: str,
    prompt_type: str,
    length: int,
    order: int,
    max_tokens: int = 2048,
    think: bool = False,
    num_samples: int = 20,
    verbose: bool = True,
) -> dict:
    """
    Evaluate 20 samples for a given (tell, prompt_type, length, order).

    Returns dict with accuracy, correct, total, and per-sample details.
    """
    correct = 0
    details = []

    for sample_num in range(1, num_samples + 1):
        filepath = os.path.join(
            HI_TOM_DATA,
            tell,
            prompt_type,
            f"length_{length}",
            f"sample_{sample_num}",
            f"order_{order}.txt",
        )

        if not os.path.exists(filepath):
            details.append({"sample": sample_num, "error": "file_not_found"})
            continue

        parsed = parse_txt_file(filepath)
        if not parsed["story"] or not parsed["choices"]:
            details.append({"sample": sample_num, "error": "parse_error"})
            continue

        try:
            t0 = time.time()
            full_text, meta = generate_response(
                model=model,
                story=parsed["story"],
                question=parsed["question"],
                choices=parsed["choices"],
                system_prompt=SYSTEM_PROMPT,
                max_tokens=max_tokens,
                temperature=0.0,
                think=think,
            )
            elapsed = time.time() - t0

            pred_letter = extract_answer(full_text)
            sorted_choices = sorted(parsed["choices"].items())

            if pred_letter is not None:
                pred_text = map_pred_to_text(pred_letter, sorted_choices)
                is_correct = pred_text == parsed["answer"]
            else:
                pred_text = None
                is_correct = False

            if is_correct:
                correct += 1

            entry = {
                "sample": sample_num,
                "correct_answer": parsed["answer"],
                "pred_letter": pred_letter,
                "pred_text": pred_text,
                "is_correct": is_correct,
                "elapsed_s": round(elapsed, 1),
                "response_len": meta["response_len"],
                "thinking_len": meta["thinking_len"],
                "output_preview": full_text[:200].replace("\n", " "),
            }
            details.append(entry)

            if verbose:
                mark = "✓" if is_correct else "✗"
                print(
                    f"    [{mark}] S{sample_num:02d} ({elapsed:.0f}s): "
                    f"pred={pred_letter}({pred_text})  correct={parsed['answer']}"
                )
                sys.stdout.flush()

        except Exception as exc:
            details.append({"sample": sample_num, "error": str(exc)})
            if verbose:
                print(f"    [!] S{sample_num:02d}: ERROR — {exc}")
                sys.stdout.flush()

    total = len(details)
    accuracy = correct / max(total, 1) * 100

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "details": details,
    }


# --------------------------------------------------------------------------- #
# Full model evaluation
# --------------------------------------------------------------------------- #

def evaluate_model(
    model: str,
    tell: str = "No_Tell",
    prompt_type: str = "CoT",
    length: int = 1,
    orders: list = None,
    max_tokens: int = 2048,
    think: bool = False,
    num_samples: int = 20,
) -> dict:
    """
    Evaluate all requested orders for one model configuration.

    Returns a result dict including joint_accuracy and derived ToMOrder.
    """
    if orders is None:
        orders = list(range(5))

    tell_key = f"Tell: {tell}"
    joint_accuracy = {tell_key: {}}

    print(f"\n{'='*60}")
    print(f"Model  : {model}")
    print(f"Config : tell={tell}, prompt={prompt_type}, length={length}")
    print(f"Orders : {orders}")
    print(f"{'='*60}")

    for order in orders:
        order_key = f"Length {length}, Order {order}"
        print(f"\n  --- Order {order} ---")
        t_start = time.time()

        result = evaluate_order(
            model=model,
            tell=tell,
            prompt_type=prompt_type,
            length=length,
            order=order,
            max_tokens=max_tokens,
            think=think,
            num_samples=num_samples,
            verbose=True,
        )

        elapsed_total = time.time() - t_start
        joint_accuracy[tell_key][order_key] = {
            "accuracy": result["accuracy"],
            "correct": result["correct"],
            "total": result["total"],
        }

        status = "PASS ✓" if result["accuracy"] >= 50 else "fail ✗"
        print(
            f"\n  Order {order}: {result['accuracy']:.1f}% "
            f"({result['correct']}/{result['total']})  [{status}]"
            f"  ({elapsed_total:.0f}s total)"
        )

    level = level_from_joint_accuracy(joint_accuracy, tell=tell, length=length)

    print(f"\n{'='*60}")
    print(f"  ToM Level  : {level}")
    print(f"  Level (int): {level.to_m_level}")
    print(f"{'='*60}")

    return {
        "model": model,
        "tell": tell,
        "prompt": prompt_type,
        "length": length,
        "joint_accuracy": joint_accuracy,
        "to_m_level": str(level),
        "to_m_level_int": level.to_m_level,
    }


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(
        description="Test Ollama qwen3.5 (or any local model) for ToM level"
    )
    parser.add_argument(
        "--model", type=str, default="qwen3.5:latest",
        help="Ollama model tag to evaluate"
    )
    parser.add_argument("--tell", type=str, default="No_Tell",
                        choices=["No_Tell", "Tell"])
    parser.add_argument("--prompt", type=str, default="CoT",
                        choices=["CoT", "MC"])
    parser.add_argument("--length", type=int, default=1, choices=[1, 2, 3])
    parser.add_argument(
        "--orders", type=int, nargs="+", default=list(range(5)),
        help="Which orders to evaluate (default: 0 1 2 3 4)"
    )
    parser.add_argument("--num_samples", type=int, default=20,
                        help="Number of samples per order (1-20, default 20)")
    parser.add_argument("--max_tokens", type=int, default=2048)
    parser.add_argument(
        "--think", action="store_true",
        help="Enable chain-of-thought thinking mode (qwen3 extended thinking). "
             "Requires more tokens (8K+). Default: off for faster evaluation."
    )
    parser.add_argument(
        "--output", type=str,
        default=os.path.join(os.path.dirname(__file__), "qwen3_5_tom_results.json"),
        help="Output JSON path"
    )
    args = parser.parse_args()

    if not is_ollama_available():
        print("ERROR: Ollama not reachable at localhost:11434")
        sys.exit(1)

    available = list_ollama_models()
    print(f"Ollama available. Models: {available}")

    if args.model not in available:
        print(f"WARNING: '{args.model}' not in available models: {available}")

    result = evaluate_model(
        model=args.model,
        tell=args.tell,
        prompt_type=args.prompt,
        length=args.length,
        orders=sorted(args.orders),
        max_tokens=args.max_tokens,
        think=args.think,
        num_samples=args.num_samples,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved → {args.output}")

    # ---------- Summary ----------
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  Model : {result['model']}")
    print(f"  Config: tell={result['tell']}, prompt={result['prompt']}, length={result['length']}")
    print()

    tell_key = f"Tell: {result['tell']}"
    for order in sorted(args.orders):
        order_key = f"Length {result['length']}, Order {order}"
        entry = result["joint_accuracy"][tell_key].get(order_key, {})
        acc = entry.get("accuracy", 0.0)
        correct = entry.get("correct", 0)
        total = entry.get("total", 0)
        status = "PASS ✓" if acc >= 50 else "fail ✗"
        print(f"  Order {order}: {acc:5.1f}%  ({correct:2}/{total:2})  [{status}]")

    print()
    print(f"  ToM Level : {result['to_m_level']}")
    print(f"  Level int : {result['to_m_level_int']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
