"""
Ollama backend for ToM evaluation.

Thin wrapper around the Ollama HTTP API (/api/generate) that handles
qwen3-style thinking models (which may split output into `response` and
`thinking` fields) and provides helper utilities.
"""

import requests

OLLAMA_BASE = "http://localhost:11434"


def is_ollama_available() -> bool:
    """Return True if an Ollama server is reachable at localhost:11434."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def list_ollama_models() -> list:
    """Return a list of model names available in the local Ollama instance."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        r.raise_for_status()
        data = r.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def generate_response(
    model: str,
    story: str,
    question: str,
    choices: dict,
    system_prompt: str,
    max_tokens: int = 2048,
    temperature: float = 0.0,
    think: bool = False,
) -> tuple:
    """
    Format a Hi-ToM question and query Ollama.

    Args:
        model:         Ollama model tag, e.g. "qwen3.5:latest"
        story:         Story text (plain string)
        question:      Question text
        choices:       Dict mapping original choice keys to choice text values.
                       Keys are re-labelled A, B, C… in alphabetical order.
        system_prompt: System-level few-shot / instruction prompt
        max_tokens:    Maximum generation tokens
        temperature:   Sampling temperature (0.0 = greedy)

    Returns:
        (response_text, meta)
        response_text: the model's full text output (thinking + answer combined
                       when both fields are present)
        meta:          dict with timing / token counts from Ollama
    """
    letter_idx = 65  # ord('A')
    formatted_choices = ""
    for i, (key, value) in enumerate(sorted(choices.items())):
        letter = chr(letter_idx + i)
        formatted_choices += f"{letter}. {value}\n"

    user_prompt = (
        f"[Story]\n{story}\n\n"
        f"[Candidate Answers]\n{formatted_choices.strip()}\n\n"
        f"[Question]\n{question}\n"
    )
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "think": think,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature,
        },
    }
    resp = requests.post(
        f"{OLLAMA_BASE}/api/generate",
        json=payload,
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()

    response = data.get("response", "")
    thinking = data.get("thinking", "")

    # For answer extraction we want everything the model produced.
    # qwen3-family thinking models may put the step-by-step trace in `thinking`
    # and the final "[X]." marker in `response`; concatenate both.
    if thinking and response:
        full_text = thinking + "\n" + response
    else:
        full_text = response or thinking

    meta = {
        "model": model,
        "response_len": len(response),
        "thinking_len": len(thinking),
        "prompt_eval_count": data.get("prompt_eval_count", 0),
        "eval_count": data.get("eval_count", 0),
    }

    return full_text, meta
