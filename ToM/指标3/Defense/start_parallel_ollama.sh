#!/bin/bash
# Start 5 parallel Ollama instances, each bound to one GPU
# Usage: bash start_parallel_ollama.sh

MODELS_DIR="${MODELS_DIR:-/root/.ollama/models}"

echo "=== Killing existing Ollama instances ==="
pkill ollama 2>/dev/null || true
sleep 2

echo "=== Checking models ==="
OLLAMA_HOST="http://localhost:11435" ollama list 2>/dev/null | grep -E "qwen3.5|llama"
if [ $? -ne 0 ]; then
    echo "Pulling models (first time only)..."
    for port in 11435 11436 11437 11438; do
        (
            CUDA_VISIBLE_DEVICES=$((port - 11434)) \
            OLLAMA_HOST="0.0.0.0:$port" \
            OLLAMA_MODELS="$MODELS_DIR" \
            ollama pull qwen3.5:latest 2>&1 | tail -1 &
        )
    done
    wait
fi

echo "=== Starting 5 Ollama instances ==="
for port in 11435 11436 11437 11438; do
    gpu=$((port - 11434))
    (
        CUDA_VISIBLE_DEVICES="$gpu" \
        OLLAMA_HOST="0.0.0.0:$port" \
        OLLAMA_MODELS="$MODELS_DIR" \
        ollama serve 2>&1 &
        echo "[GPU $gpu, port $port] Ollama started"
    ) &
done

sleep 3

echo "=== Verifying instances ==="
for port in 11435 11436 11437 11438; do
    status=$(curl -s http://localhost:$port/api/tags 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "[GPU $((port - 11434)), port $port] OK"
    else
        echo "[GPU $((port - 11434)), port $port] FAILED (retrying...)"
        sleep 5
        status=$(curl -s http://localhost:$port/api/tags 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "[GPU $((port - 11434)), port $port] OK (recovered)"
        else
            echo "[GPU $((port - 11434)), port $port] FAILED"
        fi
    fi
done

echo "=== Verifying GPU memory ==="
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits 2>&1

echo "=== All instances started ==="
echo "Available Ollama URLs:"
for port in 11435 11436 11437 11438; do
    echo "  http://localhost:$port"
done
