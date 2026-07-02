# Parallel ToM Attack Setup

## Overview

Run ToM attack experiments across multiple GPUs in parallel. Expected speedup: **5×** (2 hours → ~24 minutes).

## Step-by-Step

### 1. Kill existing Ollama

```bash
sudo pkill ollama
```

### 2. Start parallel Ollama instances

```bash
bash Defense/start_parallel_ollama.sh
```

This will:
- Pull models (once, shared across all instances)
- Start 4 parallel Ollama instances on ports 11435–11438
- Verify each instance is running on its GPU

### 3. Run parallel attacks

```bash
bash Defense/run_parallel_attack.sh
```

This will:
- Run 6 attack configs across 4 GPUs (2 configs share one GPU)
- Each config: 20 samples × 5 orders = 100 samples
- Total: 600 samples in ~24 minutes instead of ~2 hours

## Files

| File | Purpose |
|--|------|
| `start_parallel_ollama.sh` | Start 4 parallel Ollama instances |
| `run_parallel_attack.sh` | Run 6 attack configs in parallel |
| `tom_attack.py` | Main attack script (now supports `--port`) |

## GPU Requirements

- 4+ GPUs with at least ~6GB VRAM each
- Models shared across all instances (no duplicates)

## Manual Per-Config Command

For a single config on a specific GPU:

```bash
CUDA_VISIBLE_DEVICES=0 ollama serve &  # port 11435
python3 Defense/tom_attack.py \
    --attacker qwen3.5:latest \
    --victim llama3.1:8b \
    --tell No_Tell --prompt CoT --length 1 \
    --num_samples 20 --orders 0 1 2 3 4 \
    --short_attack --port 11435 \
    --output Defense/tom_attack_No_Tell_CoT_len1.json
```
