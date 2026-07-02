#!/bin/bash

# 优化的并行策略：每个模型一个并行进程
# 3个模型 × 12个场景 × 2种argument = 72个测试
# 并行度：3（每个模型一个进程）

MODELS=("glm4:9b" "qwen2.5:7b" "llama3.1:8b")
SCENARIOS=(
    "S01_labeled_no_warning"
    "S02_labeled_no_warning_oneshot"
    "S03_labeled_no_warning_cot"
    "S04_labeled_no_warning_fc"
    "S05_labeled_weak_warning"
    "S06_labeled_weak_warning_oneshot"
    "S07_labeled_weak_warning_cot"
    "S08_labeled_weak_warning_fc"
    "S09_labeled_strong_warning"
    "S10_labeled_strong_warning_oneshot"
    "S11_labeled_strong_warning_cot"
    "S12_labeled_strong_warning_fc"
)
ARG_TYPES=("false" "true")
NUM_SAMPLES=120
DATASET="dataset/defense_samples_with_true_args.json"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs/batch_by_model_${TIMESTAMP}"

# 创建日志目录
mkdir -p "${LOG_DIR}"

echo "=========================================="
echo "开始大规模完整测试 (120样本，按模型并行)"
echo "=========================================="
echo "模型数: ${#MODELS[@]}"
echo "场景数: ${#SCENARIOS[@]}"
echo "Argument类型数: ${#ARG_TYPES[@]}"
echo "总测试数: $((${#MODELS[@]} * ${#SCENARIOS[@]} * ${#ARG_TYPES[@]}))"
echo "样本数: ${NUM_SAMPLES}"
echo "数据集: ${DATASET}"
echo "日志目录: ${LOG_DIR}"
echo "并行策略: 每个模型一个进程（共3个并行）"
echo "预计总API调用数: ~10,800次"
echo "预计总时间: ~6小时（3模型并行）"
echo "=========================================="
echo ""

# 检查数据集
if [ ! -f "${DATASET}" ]; then
    echo "错误: 数据集文件不存在: ${DATASET}"
    exit 1
fi

# 为每个模型创建一个执行函数
run_model_tests() {
    local model=$1
    local model_short=$(echo "$model" | tr ':' '_')
    local model_log="${LOG_DIR}/${model_short}_progress.log"

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始模型 ${model} 的所有测试" | tee -a "${model_log}"

    local task_count=0
    local total_tasks=$((${#SCENARIOS[@]} * ${#ARG_TYPES[@]}))

    for arg_type in "${ARG_TYPES[@]}"; do
        for scenario in "${SCENARIOS[@]}"; do
            task_count=$((task_count + 1))

            task_id="${model_short}_${scenario}_${arg_type}"
            log_file="${LOG_DIR}/${task_id}.log"

            echo "[$(date '+%H:%M:%S')] [${model_short}] 任务 ${task_count}/${total_tasks}: ${scenario} (${arg_type})" | tee -a "${model_log}"

            # 运行测试
            {
                echo "=== 开始时间: $(date) ==="
                echo "=== 任务: ${task_id} ==="
                echo "=== 模型: ${model} ==="
                echo "=== 场景: ${scenario} ==="
                echo "=== Argument类型: ${arg_type} ==="
                echo "=== 样本数: ${NUM_SAMPLES} ==="
                echo ""

                python3 main_defense.py \
                    --model "${model}" \
                    --num_samples ${NUM_SAMPLES} \
                    --scenarios "${scenario}" \
                    --argument-type "${arg_type}" \
                    --dataset "${DATASET}" 2>&1

                exit_code=$?

                echo ""
                echo "=== 结束时间: $(date) ==="
                echo "=== 退出码: ${exit_code} ==="

                if [ ${exit_code} -eq 0 ]; then
                    # 提取准确率
                    accuracy=$(grep "correct (" "${log_file}" | tail -1 | grep -oP '\(\K[0-9.]+(?=%)')
                    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ ${task_id} (准确率: ${accuracy}%)" | tee -a "${LOG_DIR}/completed.txt"
                    if [ -n "${accuracy}" ]; then
                        echo "${task_id},${accuracy}" >> "${LOG_DIR}/accuracies.csv"
                    fi
                else
                    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ ${task_id} (exit code: ${exit_code})" | tee -a "${LOG_DIR}/failed.txt"
                fi
            } > "${log_file}" 2>&1

        done
    done

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成模型 ${model} 的所有测试 (${total_tasks}个任务)" | tee -a "${model_log}"
}

# 为每个模型启动一个后台进程
MODEL_PIDS=()
for model in "${MODELS[@]}"; do
    echo "启动模型 ${model} 的测试进程..."
    run_model_tests "${model}" &
    MODEL_PIDS+=($!)
done

echo ""
echo "所有模型的测试进程已启动"
echo "进程ID: ${MODEL_PIDS[@]}"
echo ""

# 创建进度监控函数
monitor_progress() {
    while true; do
        sleep 60  # 每分钟更新一次

        # 检查是否所有进程都还在运行
        all_done=true
        for pid in "${MODEL_PIDS[@]}"; do
            if kill -0 $pid 2>/dev/null; then
                all_done=false
                break
            fi
        done

        if [ "$all_done" = true ]; then
            break
        fi

        # 显示进度
        if [ -f "${LOG_DIR}/completed.txt" ]; then
            completed=$(wc -l < "${LOG_DIR}/completed.txt")
            echo "[$(date '+%H:%M:%S')] 进度: ${completed}/72 任务完成"
        fi
    done
}

# 启动进度监控（后台）
monitor_progress &
MONITOR_PID=$!

# 等待所有模型测试完成
echo "等待所有模型测试完成..."
for pid in "${MODEL_PIDS[@]}"; do
    wait $pid
done

# 停止进度监控
kill $MONITOR_PID 2>/dev/null

echo ""
echo "=========================================="
echo "所有测试完成！"
echo "=========================================="

# 统计结果
if [ -f "${LOG_DIR}/completed.txt" ]; then
    completed=$(wc -l < "${LOG_DIR}/completed.txt")
else
    completed=0
fi

if [ -f "${LOG_DIR}/failed.txt" ]; then
    failed=$(wc -l < "${LOG_DIR}/failed.txt")
else
    failed=0
fi

echo "成功: ${completed}"
echo "失败: ${failed}"
echo "总计: 72"
echo ""
echo "日志目录: ${LOG_DIR}"
echo "准确率数据: ${LOG_DIR}/accuracies.csv"

if [ -f "${LOG_DIR}/failed.txt" ]; then
    echo "失败任务:"
    cat "${LOG_DIR}/failed.txt"
fi

echo "=========================================="

# 生成汇总报告
if [ -f "${LOG_DIR}/accuracies.csv" ]; then
    echo ""
    echo "生成汇总报告..."
    python3 - <<'EOF'
import csv
import os
import sys

log_dir = sys.argv[1]
csv_file = os.path.join(log_dir, "accuracies.csv")
summary_file = os.path.join(log_dir, "SUMMARY.txt")

if not os.path.exists(csv_file):
    print("未找到准确率数据文件")
    sys.exit(0)

# 读取数据
data = {}
with open(csv_file, 'r') as f:
    for line in f:
        parts = line.strip().split(',')
        if len(parts) == 2:
            task, acc = parts
            # 解析任务名: model_scenario_argtype
            parts_split = task.rsplit('_', 1)
            if len(parts_split) == 2:
                model_scenario, arg_type = parts_split
                # 进一步拆分 model_scenario
                # 格式: glm4_9b_S01_labeled_no_warning
                parts2 = model_scenario.split('_', 2)
                if len(parts2) >= 3:
                    model = '_'.join(parts2[:2])  # glm4_9b
                    scenario = parts2[2]  # S01_labeled_no_warning

                    key = (model, scenario)
                    if key not in data:
                        data[key] = {}
                    data[key][arg_type] = float(acc)

# 生成报告
with open(summary_file, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("完整测试汇总报告 (120样本)\n")
    f.write("=" * 80 + "\n\n")

    for model in ["glm4_9b", "qwen2.5_7b", "llama3.1_8b"]:
        f.write(f"\n模型: {model}\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'场景':<45} {'False Arg':<12} {'True Arg':<12} {'差异':<10}\n")
        f.write("-" * 80 + "\n")

        scenarios = [
            "S01_labeled_no_warning",
            "S02_labeled_no_warning_oneshot",
            "S03_labeled_no_warning_cot",
            "S04_labeled_no_warning_fc",
            "S05_labeled_weak_warning",
            "S06_labeled_weak_warning_oneshot",
            "S07_labeled_weak_warning_cot",
            "S08_labeled_weak_warning_fc",
            "S09_labeled_strong_warning",
            "S10_labeled_strong_warning_oneshot",
            "S11_labeled_strong_warning_cot",
            "S12_labeled_strong_warning_fc"
        ]

        for scenario in scenarios:
            key = (model, scenario)
            if key in data:
                false_acc = data[key].get('false', 0)
                true_acc = data[key].get('true', 0)
                diff = true_acc - false_acc
                f.write(f"{scenario:<45} {false_acc:>10.1f}% {true_acc:>10.1f}% {diff:>+9.1f}pp\n")
        f.write("\n")

print(f"汇总报告已生成: {summary_file}")
EOF
python3 - "${LOG_DIR}"
fi

echo ""
echo "测试完成！查看汇总报告: ${LOG_DIR}/SUMMARY.txt"
