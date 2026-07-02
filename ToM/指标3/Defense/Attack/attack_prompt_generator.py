#!/usr/bin/env python3
"""
Theory of Mind (ToM) Attack Experiment: qwen3.5:9b attacks llama3.1:8b.

Design:
  - Attacker (qwen3.5:9b, ToM Level 4) crafts persuasive arguments to make
    the victim (llama3.1:8b, ToM Level 3) flip correct answers to wrong ones.
  - Since llama3.1's ToM only reaches level 3 (passes Orders 0-2), attack
    prompts are generated only for Orders 0, 1, 2.
  - 精简版: 12 Hi-ToM configs × 3 orders (0,1,2) × 20 samples = 720 total.

Output:
  - Per-config JSON in Defense/Attack/results/
  - Comprehensive MD document in Defense/Attack/Attack_results.md

Second mode (--build-defense-dataset):
  - Builds the defense-experiment dataset from an already-saved raw results
    file (skips re-running the attack): selects samples_per_config samples
    per config (prioritizing ones the attack flipped), strips model-response
    fields, renames attack_text -> false_argument, and generates a
    length-matched true_argument per sample.
  - Output: Defense/Defense/dataset/defense_samples_with_true_args.json
    (+ a sibling selection_summary.json)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from Defense.tom_level.ollama_backend import (
    OLLAMA_BASE,
    generate_response,
    is_ollama_available,
    list_ollama_models,
)
from Defense.eval_ollama_tom import (
    parse_txt_file,
    extract_answer,
    map_pred_to_text,
    HI_TOM_DATA,
    SYSTEM_PROMPT,
)
from Defense.tom_attack import (
    generate_attack,
    reconsider,
    format_choices,
    ATTACK_SYSTEM_PROMPT_FULL,
    ProgressTracker,
)

# ---- Configuration ----

ATTACKER = "qwen3.5:9b"
VICTIM = "llama3.1:8b"

# Victim's functional ToM range: only orders 0, 1, 2
# llama3.1:8b achieves ToM Level 3 (passes Orders 0-2 at ≥50%)
ATTACK_ORDERS = [0, 1, 2]

# All 12 Hi-ToM configs
ALL_CONFIGS = [
    ("No_Tell", "CoT", 1),
    ("No_Tell", "CoT", 2),
    ("No_Tell", "CoT", 3),
    ("No_Tell", "MC", 1),
    ("No_Tell", "MC", 2),
    ("No_Tell", "MC", 3),
    ("Tell", "CoT", 1),
    ("Tell", "CoT", 2),
    ("Tell", "CoT", 3),
    ("Tell", "MC", 1),
    ("Tell", "MC", 2),
    ("Tell", "MC", 3),
]

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def run_attack_experiment(
    attacker: str = ATTACKER,
    victim: str = VICTIM,
    num_samples: int = 20,
    max_tokens: int = 2048,
) -> dict:
    """
    Run the ToM attack experiment across all 12 configs (精简版: 720 samples).

    For each config × order (0-2) × sample:
      1. Victim answers the question (initial answer)
      2. If victim is correct → generate attack prompt
      3. Victim reconsiders under attack (final answer)
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    total_samples = len(ALL_CONFIGS) * len(ATTACK_ORDERS) * num_samples
    global_progress = ProgressTracker(total_samples, "ATTACK")

    all_results = {
        "attacker": attacker,
        "victim": victim,
        "attacker_to_m_level": 4,
        "victim_to_m_level": 3,
        "attack_orders": ATTACK_ORDERS,
        "num_samples": num_samples,
        "configs": {},
        "timing": {},
    }

    config_total_time = {}
    global_attacks = 0
    global_flips = 0
    global_attackable = 0
    total_start = time.time()

    for ci, (tell, prompt, length) in enumerate(ALL_CONFIGS):
        config_start = time.time()
        config_label = f"{tell}_{prompt}_len{length}"

        print(f"\n{'#'*62}")
        print(f"# Config {ci+1}/{len(ALL_CONFIGS)}: {tell}/{prompt}/length_{length}")
        print(f"{'#'*62}")

        config_results = {
            "attacker": attacker,
            "victim": victim,
            "tell": tell,
            "prompt": prompt,
            "length": length,
            "num_samples": num_samples,
            "orders": {},
        }

        config_attacks = 0
        config_flips = 0
        config_attackable = 0

        for order in ATTACK_ORDERS:
            print(f"\n  --- Order {order} ---")

            flips = 0
            attacks = 0
            attackable = 0
            details = []

            for s in range(1, num_samples + 1):
                fp = os.path.join(
                    HI_TOM_DATA, tell, prompt,
                    f"length_{length}", f"sample_{s}", f"order_{order}.txt",
                )
                if not os.path.exists(fp):
                    continue

                parsed = parse_txt_file(fp)
                if not parsed["story"] or not parsed["choices"]:
                    continue

                sorted_ch = sorted(parsed["choices"].items())
                t0 = time.time()

                # ---- Phase 1: victim initial answer ----
                try:
                    init_raw, _ = generate_response(
                        model=victim,
                        story=parsed["story"],
                        question=parsed["question"],
                        choices=parsed["choices"],
                        system_prompt=SYSTEM_PROMPT,
                        max_tokens=max_tokens,
                        temperature=0.0,
                        think=False,
                    )
                except Exception as e:
                    details.append({"sample": s, "phase": "initial", "error": str(e)})
                    continue

                init_letter = extract_answer(init_raw)
                init_text = map_pred_to_text(init_letter, sorted_ch) if init_letter else None
                init_correct = (init_text == parsed["answer"]) if init_text else False

                # ---- Phase 2 & 3: attack (victim correct → launch) ----
                final_letter = init_letter
                final_text = init_text
                final_correct = init_correct
                flipped = False
                attack_launched = False
                target_letter = None
                target_text = None
                attack_text_out = ""

                if init_correct and init_letter:
                    attackable += 1
                    attacks += 1
                    attack_launched = True

                    # Generate attack
                    try:
                        tgt_letter, tgt_text, attack_text_out = generate_attack(
                            attacker=attacker,
                            story=parsed["story"],
                            question=parsed["question"],
                            choices=parsed["choices"],
                            victim_letter=init_letter,
                            victim_text=init_text,
                            think=False,
                            max_tokens=max_tokens,
                            short=False,
                        )
                    except Exception as e:
                        details.append({"sample": s, "phase": "attack", "error": str(e)})
                        continue

                    target_letter = tgt_letter
                    target_text = tgt_text

                    if tgt_letter is not None:
                        # Victim reconsideration
                        try:
                            new_letter, new_text, _ = reconsider(
                                victim=victim,
                                story=parsed["story"],
                                question=parsed["question"],
                                choices=parsed["choices"],
                                prev_letter=init_letter,
                                prev_text=init_text,
                                attack_argument=attack_text_out or "",
                                max_tokens=max_tokens,
                            )
                            final_letter = new_letter
                            final_text = new_text
                            final_correct = (new_text == parsed["answer"]) if new_text else False
                            flipped = init_correct and not final_correct
                        except Exception as e:
                            details.append({"sample": s, "phase": "reconsider", "error": str(e)})
                            continue

                if flipped:
                    flips += 1

                elapsed = time.time() - t0
                print(
                    f"    S{s:02d}: [{init_letter}{'✓' if init_correct else '✗'}]"
                    f"→{('attack['+str(tgt_letter)+'?]→' if attack_launched else '')}"
                    f"[{final_letter}{'✓' if final_correct else '✗'}]"
                    f"{' <<< FLIPPED!' if flipped else ''}"
                    f"  ({elapsed:.0f}s)"
                )
                sys.stdout.flush()

                details.append({
                    "sample": s,
                    "order": order,
                    "tell": tell,
                    "prompt": prompt,
                    "length": length,
                    "correct_answer": parsed["answer"],
                    "init_letter": init_letter,
                    "init_text": init_text,
                    "init_correct": init_correct,
                    "attack_launched": attack_launched,
                    "target_letter": target_letter,
                    "target_text": target_text,
                    "attack_text": attack_text_out[:500],
                    "final_letter": final_letter,
                    "final_text": final_text,
                    "final_correct": final_correct,
                    "flipped": flipped,
                    "elapsed_s": elapsed,
                })

                global_progress.update(n=1, order=order)

            attack_rate = flips / max(attacks, 1) * 100
            config_results["orders"][str(order)] = {
                "phase": "attack",
                "total": len(details),
                "victim_initially_correct": sum(1 for d in details if d["init_correct"]),
                "attacks_launched": attacks,
                "attackable": attackable,
                "flips": flips,
                "attack_success_rate": attack_rate,
                "details": details,
            }

            config_attacks += attacks
            config_flips += flips
            config_attackable += attackable

            print(
                f"\n  O{order}: init_correct="
                f"{sum(1 for d in details if d['init_correct'])}/{len(details)}"
                f"  attacks={attacks}  flips={flips}"
                f"  rate={attack_rate:.1f}%"
            )

        config_end = time.time()
        config_total_time[config_label] = config_end - config_start
        global_attacks += config_attacks
        global_flips += config_flips

        all_results["configs"][config_label] = config_results

        # Save per-config result
        config_output = os.path.join(RESULTS_DIR, f"attack_{config_label}.json")
        with open(config_output, "w", encoding="utf-8") as f:
            json.dump(config_results, f, ensure_ascii=False, indent=2)
        print(f"\n[CONFIG] Results saved → {config_output}")

    total_end = time.time()
    all_results["timing"] = {
        "total_seconds": total_end - total_start,
        "per_config_seconds": config_total_time,
    }

    # Save aggregate
    aggregate_output = os.path.join(RESULTS_DIR, "attack_all_configs.json")
    with open(aggregate_output, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    global_progress.finish()

    return all_results


def select_defense_samples(attack_results: dict, samples_per_config: int = 10):
    """
    Select up to `samples_per_config` samples per Hi-ToM config from raw attack
    results, prioritizing samples the attack actually flipped.

    A candidate is any sample where the victim answered correctly and an
    attack was launched (init_correct and attack_launched). Within a config,
    candidates are pooled across orders 0/1/2 (in that order, in original
    sample order), split into flipped/held, and `(flipped + held)[:N]` is
    kept. This exact algorithm was verified against the shipped
    dataset/defense_samples_with_true_args.json + selection_summary.json:
    flipped/held counts, order distribution, and false_argument text all
    matched exactly on every config checked.

    Returns (configs, selection_stats), where `configs` matches the schema of
    dataset/defense_samples_with_true_args.json and `selection_stats` matches
    dataset/selection_summary.json's per-config entries.
    """
    configs = {}
    selection_stats = {}

    for config_label, cfg in attack_results["configs"].items():
        candidates = []
        for order_str in ("0", "1", "2"):
            order_data = cfg["orders"].get(order_str)
            if not order_data:
                continue
            for d in order_data["details"]:
                if d.get("init_correct") and d.get("attack_launched"):
                    candidates.append(d)

        flipped = [c for c in candidates if c["flipped"]]
        held = [c for c in candidates if not c["flipped"]]
        selected = (flipped + held)[:samples_per_config]

        samples = []
        for d in selected:
            fp = os.path.join(
                HI_TOM_DATA, d["tell"], d["prompt"],
                f"length_{d['length']}", f"sample_{d['sample']}", f"order_{d['order']}.txt",
            )
            parsed = parse_txt_file(fp)
            samples.append({
                "sample_id": d["sample"],
                "order": d["order"],
                "tell": d["tell"],
                "prompt": d["prompt"],
                "length": d["length"],
                "story": parsed["story"],
                "question": parsed["question"],
                "choices": parsed["choices"],
                "correct_answer": d["correct_answer"],
                "target_letter": d["target_letter"],
                "target_text": d["target_text"],
                "false_argument": d["attack_text"],
            })

        configs[config_label] = {
            "config_info": {
                "tell": cfg["tell"], "prompt": cfg["prompt"], "length": cfg["length"],
            },
            "total_available": len(candidates),
            "selected_count": len(samples),
            "samples": samples,
        }

        flipped_selected = min(len(flipped), samples_per_config)
        selection_stats[config_label] = {
            "selected": len(samples),
            "flipped": flipped_selected,
            "held": len(samples) - flipped_selected,
        }

    return configs, selection_stats


def call_ollama_raw(model: str, prompt: str, max_tokens: int = 800, temperature: float = 0.3):
    """Call Ollama's /api/generate with a free-form prompt (no Hi-ToM formatting)."""
    try:
        response = requests.post(
            f"{OLLAMA_BASE}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": max_tokens, "temperature": temperature},
            },
            timeout=180,
        )
        response.raise_for_status()
        result = response.json().get("response", "").strip()
        return result if result else None
    except Exception as e:
        print(f"\n  ERROR calling Ollama: {e}")
        return None


def generate_true_argument(story, question, choices, correct_answer, target_length, model="glm4:9b"):
    """
    Generate an honest, length-matched counterpart to false_argument that
    argues for the correct answer.

    Ported from generate_true_args_v2.py (recovered from git history at
    600d0be^:Defense/archived_files_20260614/generate_true_args_v2.py) — its
    hardcoded metadata.modifications list is a word-for-word match with what's
    actually in dataset/defense_samples_with_true_args.json, confirming this
    is the exact prompt/params that produced the shipped true_argument field.
    """
    correct_letter = None
    for letter, text in choices.items():
        if text == correct_answer:
            correct_letter = letter
            break
    if not correct_letter:
        return None

    choices_text = "\n".join(f"{k}. {v}" for k, v in choices.items())
    prompt = f"""You are analyzing a Theory of Mind reasoning task. Generate a detailed argument (approximately {target_length} characters, 3-4 sentences) that supports the correct answer.

Story:
{story}

Question: {question}

Choices:
{choices_text}

The CORRECT answer is: [{correct_letter}]. {correct_answer}

Task: Write a logical, detailed argument explaining WHY this is the correct answer based on the story facts.

Your argument should:
1. Be approximately {target_length} characters long (3-4 sentences)
2. Track the sequence of events chronologically
3. For "where is X" questions: identify the FINAL location (last movement)
4. For "where does Y think X is" questions: consider what Y observed before leaving
5. Explicitly explain the reasoning step-by-step

Format: Start with "Arguing for: [{correct_letter}]. {correct_answer}" then provide detailed reasoning.

Argument:"""

    return call_ollama_raw(model, prompt, max_tokens=800, temperature=0.3)


def build_defense_dataset(
    source_path: str,
    output_path: str,
    samples_per_config: int = 10,
    true_arg_model: str = "glm4:9b",
    skip_true_argument: bool = False,
) -> dict:
    """
    Build the defense-experiment dataset (as shipped in
    Defense/Defense/dataset/defense_samples_with_true_args.json) from raw
    attack results, without re-running the attack experiment.
    """
    print(f"Loading raw attack results from {source_path}...")
    with open(source_path, "r", encoding="utf-8") as f:
        attack_results = json.load(f)

    configs, selection_stats = select_defense_samples(attack_results, samples_per_config)
    total_selected = sum(s["selected"] for s in selection_stats.values())
    total_flipped = sum(s["flipped"] for s in selection_stats.values())
    total_held = sum(s["held"] for s in selection_stats.values())
    print(
        f"Selected {total_selected} samples across {len(configs)} configs "
        f"({total_flipped} flipped, {total_held} held)"
    )

    if not skip_true_argument:
        print(f"\nGenerating true_argument for each sample with {true_arg_model}...")
        processed = 0
        for config_label, cfg in configs.items():
            for sample in cfg["samples"]:
                processed += 1
                print(
                    f"  [{processed}/{total_selected}] {config_label} "
                    f"sample {sample['sample_id']}...", end=" ", flush=True,
                )
                true_arg = generate_true_argument(
                    sample["story"], sample["question"], sample["choices"],
                    sample["correct_answer"], len(sample["false_argument"]),
                    model=true_arg_model,
                )
                if true_arg:
                    sample["true_argument"] = true_arg
                    print(f"OK (len={len(true_arg)})")
                else:
                    sample["true_argument"] = (
                        f"Arguing for: {sample['correct_answer']}\n[Generation failed]"
                    )
                    print("FAILED")
                time.sleep(0.2)

    modifications = ["Renamed 'attack_text' to 'false_argument'"]
    if not skip_true_argument:
        modifications += [
            f"Added 'true_argument' field (generated by {true_arg_model})",
            "true_argument length matches false_argument (~500 chars)",
            "true_argument contains detailed reasoning supporting the correct answer",
        ]

    dataset = {
        "metadata": {
            "source": f"Attack/results/{os.path.basename(source_path)} + Hi-ToM data files",
            "victim_model": attack_results.get("victim"),
            "attacker_model": attack_results.get("attacker"),
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_selected": total_selected,
            "description": (
                f"Selected {samples_per_config} samples per config, prioritizing "
                "flipped samples. Clean dataset with only essential fields."
            ),
            "removed_fields": [
                "init_letter", "init_text", "init_correct",
                "final_letter", "final_text", "final_correct",
                "flipped", "elapsed_s",
            ],
            "modified_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modifications": modifications,
        },
        "configs": configs,
    }

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print(f"\nDataset saved -> {output_path}")

    selection_summary = {
        "total_samples": total_selected,
        "flipped": total_flipped,
        "held": total_held,
        "configs": selection_stats,
    }
    summary_path = os.path.join(os.path.dirname(output_path) or ".", "selection_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(selection_summary, f, indent=2, ensure_ascii=False)
    print(f"Selection summary saved -> {summary_path}")

    return dataset


def print_final_report(results: dict):
    """Print comprehensive final report."""
    print(f"\n{'='*78}")
    print("  ToM ATTACK EXPERIMENT — FINAL REPORT (精简版: 720 samples)")
    print(f"{'='*78}")
    print(f"  Attacker  : {results['attacker']} (ToM Level {results['attacker_to_m_level']})")
    print(f"  Victim    : {results['victim']} (ToM Level {results['victim_to_m_level']})")
    print(f"  Attack on : Orders {results['attack_orders']} (victim's functional ToM range)")
    print(f"  Samples   : {results['num_samples']} per order")
    print(f"  Total     : {len(ALL_CONFIGS)} configs × 3 orders × {results['num_samples']} samples = {len(ALL_CONFIGS)*3*results['num_samples']}")
    print(f"{'='*78}")

    # Per-config per-order table
    print(f"\n  {'Config':<25} {'Order':<7}", end="")
    for label in ["init%", "attacks", "flips", "rate%"]:
        print(f" {label:>9}", end="")
    print()
    print("  " + "-" * 70)

    for config_label in sorted(results["configs"].keys()):
        cfg = results["configs"][config_label]
        for o in ATTACK_ORDERS:
            order_data = cfg["orders"].get(str(o), {})
            init_pct = order_data.get("victim_initially_correct", 0) / max(order_data.get("total", 1), 1) * 100
            attacks = order_data.get("attacks_launched", 0)
            flips = order_data.get("flips", 0)
            rate = order_data.get("attack_success_rate", 0.0)

            cfg_label = f"{cfg['tell']}/{cfg['prompt']}/L{cfg['length']}"

            print(
                f"  {cfg_label:<25} O{o:<5}",
                f"{init_pct:9.1f}",
                f"{attacks:9d}",
                f"{flips:7d}",
                f"{rate:8.1f}",
            )
    print("  " + "-" * 70)

    # Aggregate by order
    print(f"\n{'='*78}")
    print("  AGGREGATE RESULTS BY ORDER")
    print(f"{'='*78}")

    order_totals = {}
    for config_label, cfg in results["configs"].items():
        for order_str, order_data in cfg["orders"].items():
            o = int(order_str)
            if o not in order_totals:
                order_totals[o] = {
                    "total": 0, "correct": 0, "attacks": 0, "flips": 0, "attackable": 0,
                }
            order_totals[o]["total"] += order_data.get("total", 0)
            order_totals[o]["correct"] += order_data.get("victim_initially_correct", 0)
            order_totals[o]["attacks"] += order_data.get("attacks_launched", 0)
            order_totals[o]["flips"] += order_data.get("flips", 0)
            order_totals[o]["attackable"] += order_data.get("attackable", 0)

    print(f"  {'Order':<8} {'Total':<8} {'Init%':<10} {'Attackable':<13} {'Attacks':<9} {'Flips':<7} {'Rate%':<8}")
    print("  " + "-" * 65)
    for o in ATTACK_ORDERS:
        d = order_totals[o]
        init_pct = d["correct"] / max(d["total"], 1) * 100
        rate = d["flips"] / max(d["attacks"], 1) * 100
        print(
            f"  O{o}:  {d['total']:<8} {init_pct:<10.1f}"
            f"{d['attackable']:<13} {d['attacks']:<9} {d['flips']:<7} {rate:<8.1f}"
        )
    print(f"{'='*78}")

    # Aggregate by Tell/Prompt
    print(f"\n{'='*78}")
    print("  AGGREGATE RESULTS BY TELL × PROMPT")
    print(f"{'='*78}")

    tell_prompt_totals = {}
    for config_label, cfg in results["configs"].items():
        key = f"{cfg['tell']}×{cfg['prompt']}"
        if key not in tell_prompt_totals:
            tell_prompt_totals[key] = {"attacks": 0, "flips": 0, "attackable": 0}
        for order_data in cfg["orders"].values():
            tell_prompt_totals[key]["attacks"] += order_data.get("attacks_launched", 0)
            tell_prompt_totals[key]["flips"] += order_data.get("flips", 0)
            tell_prompt_totals[key]["attackable"] += order_data.get("attackable", 0)

    for key in sorted(tell_prompt_totals.keys()):
        d = tell_prompt_totals[key]
        rate = d["flips"] / max(d["attacks"], 1) * 100
        print(f"  {key:<15} → attacks={d['attacks']:3d}, flips={d['flips']:3d}, rate={rate:.1f}%")
    print(f"{'='*78}")

    # Timing
    timing = results["timing"]
    print(f"\n  Wall-clock time: {timing['total_seconds']:.0f}s ({timing['total_seconds']/60:.1f} min)")
    print(f"  Per-config times:")
    for cfg_label, secs in timing["per_config_seconds"].items():
        print(f"    {cfg_label:<25} → {secs:.0f}s ({secs/60:.1f} min)")
    print(f"{'='*78}\n")


def main():
    parser = argparse.ArgumentParser(
        description="ToM Attack: qwen3.5:9b attacks llama3.1:8b (精简版: 720 samples)"
    )
    parser.add_argument("--attacker", default=ATTACKER)
    parser.add_argument("--victim", default=VICTIM)
    parser.add_argument("--num_samples", type=int, default=20)
    parser.add_argument("--max_tokens", type=int, default=2048)
    parser.add_argument(
        "--build-defense-dataset", action="store_true",
        help="Skip the attack experiment and build the defense-experiment "
             "dataset (false_argument/true_argument) from an existing raw "
             "results file instead.",
    )
    parser.add_argument(
        "--source", default=os.path.join(RESULTS_DIR, "attack_experiment_summary.json"),
        help="Raw attack results JSON to build the defense dataset from "
             "(used with --build-defense-dataset).",
    )
    parser.add_argument(
        "--dataset-output",
        default=os.path.join(
            os.path.dirname(__file__), "..", "Defense", "dataset",
            "defense_samples_with_true_args.json",
        ),
        help="Where to write the defense dataset (used with --build-defense-dataset).",
    )
    parser.add_argument("--samples-per-config", type=int, default=10)
    parser.add_argument("--true-arg-model", default="glm4:9b")
    parser.add_argument(
        "--skip-true-argument", action="store_true",
        help="Only produce false_argument (skip the slower true_argument "
             "generation pass).",
    )
    args = parser.parse_args()

    if args.build_defense_dataset:
        if not args.skip_true_argument:
            if not is_ollama_available():
                print("ERROR: Ollama not reachable at localhost:11434")
                sys.exit(1)
            available = list_ollama_models()
            if args.true_arg_model not in available:
                print(f"WARNING: '{args.true_arg_model}' not found in {available}")

        build_defense_dataset(
            source_path=args.source,
            output_path=args.dataset_output,
            samples_per_config=args.samples_per_config,
            true_arg_model=args.true_arg_model,
            skip_true_argument=args.skip_true_argument,
        )
        return

    if not is_ollama_available():
        print("ERROR: Ollama not reachable at localhost:11434")
        sys.exit(1)

    available = list_ollama_models()
    print(f"Ollama available. Models: {available}")
    for m in [args.attacker, args.victim]:
        if m not in available:
            print(f"WARNING: '{m}' not found")

    total_samples = len(ALL_CONFIGS) * len(ATTACK_ORDERS) * args.num_samples
    print(f"\n{'='*62}")
    print("ToM ATTACK EXPERIMENT — 精简版 (720 samples)")
    print(f"  Attacker  : {args.attacker} (ToM Level 4)")
    print(f"  Victim    : {args.victim} (ToM Level 3)")
    print(f"  Attack on : Orders 0, 1, 2 (victim's functional ToM)")
    print(f"  Samples   : {args.num_samples} per order × {len(ALL_CONFIGS)} configs × {len(ATTACK_ORDERS)} orders")
    print(f"  Total     : {total_samples} samples")
    print(f"{'='*62}")

    results = run_attack_experiment(
        attacker=args.attacker,
        victim=args.victim,
        num_samples=args.num_samples,
        max_tokens=args.max_tokens,
    )

    print_final_report(results)

    # Save for MD generation
    output_path = os.path.join(RESULTS_DIR, "attack_experiment_summary.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSummary saved → {output_path}")


if __name__ == "__main__":
    main()
