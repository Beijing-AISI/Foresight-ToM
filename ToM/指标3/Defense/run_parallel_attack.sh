#!/bin/bash
# Run parallel ToM attack across multiple Ollama instances
# Usage: bash run_parallel_attack.sh

# Configurations to run (6 configs from --essential)
declare -a CONFIGS=(
    "No_Tell CoT 1"
    "No_Tell CoT 3"
    "No_Tell MC 1"
    "No_Tell CoT 2"
    "No_Tell MC 2"
    "No_Tell MC 3"
)

PORTS=(11435 11436 11437 11438)
NUM_PORTS=${#PORTS[@]}

echo "=== Starting ${#CONFIGS[@]} parallel ToM attacks ===="
echo "Each attack runs on a separate GPU/port"
echo ""

PIDS=()
for i in "${!CONFIGS[@]}"; do
    CONFIG=${CONFIGS[$i]}
    PORT=${PORTS[$i]}

    read tell prompt length <<< "$CONFIG"
    config_label="${tell}_${prompt}_len${length}"
    output_file="Defense/tom_attack_${config_label}.json"

    echo "[$i] Starting: $tell/$prompt/len$length (port $PORT)"

    python3 Defense/tom_attack.py \
        --attacker qwen3.5:latest \
        --victim llama3.1:8b \
        --tell $tell \
        --prompt $prompt \
        --length $length \
        --num_samples 20 \
        --orders 0 1 2 3 4 \
        --short_attack \
        --port $PORT \
        --output "$output_file" &

    PIDS+=($!)
    echo "    PID: $(_"
done

echo "=== Waiting for all attacks to complete ===="
for i in "${!PIDS[@]}"; do
    wait "${PIDS[$i]}"
    echo "[$i] Attack completed (exit code ${PIDS[$i]})"
done

echo "=== Checking results ===="
for i in "${!CONFIGS[@]}"; do
    CONFIG=${CONFIGS[$i]}
    read tell prompt length <<< "$CONFIG"
    config_label="${tell}_${prompt}_len${length}"
    output_file="Defense/tom_attack_${config_label}.json"

    if [ -f "$output_file" ]; then
        attackable=$(python3 -c "
import json
with open('$output_file') as f:
    d = json.load(f)
count = sum(1 for s in od.get('details', [])
            for od in d['orders'].values()
            if s.get('attacked') and s.get('attack_full') and len(s.get('attack_full','')) > 10)
print(count)
" 2>/dev/null)
        echo "  $config_label: $attackable attackable samples ✓"
    else
        echo "  $config_label: MISSING ✗"
    fi
done

echo "=== GPU usage ===="
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits

echo "=== Parallel attack completed ===="
