from collections import defaultdict
import itertools
import json
import argparse
import os
import numpy as np
from matplotlib import pyplot as plt


# 根据统计信息绘制并保存混淆矩阵
def save_confusion_matrix(stats, output_path, choice="standard"):
    sub_dir = choice
    os.makedirs(output_path, exist_ok=True)

    num_prompts = len(args.prompt_type)
    rows = num_prompts
    cols = 2

    # 初始化主图
    if rows == 1:
        fig, axes = plt.subplots(rows, cols, figsize=(16, 6), constrained_layout=True)
        axes = np.array([axes])
    else:
        fig, axes = plt.subplots(rows, cols, figsize=(16, 12), constrained_layout=True)

    fig.suptitle(f"{choice.capitalize()} Accuracy Matrices", fontsize=20)

    index = 0
    for idx, ((tell, prompt), length_order_stats) in enumerate(stats.items()):
        if prompt not in args.prompt_type:
            continue
        else:
            index += 1

        # 初始化混淆矩阵 (3行, 5列)
        matrix = np.zeros((3, 5))  # 3个长度, 5个order

        for (length, order), counts in length_order_stats.items():
            if choice == "standard":
                correct = counts.get("correct", 0)
            elif choice == "joint":
                correct = counts.get("joint_correct", 0)

            total = counts["total"]
            accuracy = (correct / total) if total > 0 else 0
            matrix[length - 1, order] = accuracy

        # 确定当前子图位置
        ax = axes[(index - 1) // 2, (index - 1) % 2]

        # 绘制混淆矩阵
        cax = ax.imshow(matrix, cmap="Blues", aspect="auto", vmin=0.0, vmax=1.0)
        ax.set_title(f"Tell: {tell}, Prompt: {prompt}", fontsize=20)
        ax.set_xlabel("Order")
        ax.set_ylabel("Length")
        ax.set_xticks(range(5))
        ax.set_xticklabels([0, 1, 2, 3, 4])  # 横轴
        ax.set_yticks(range(3))
        ax.set_yticklabels([1, 2, 3])  # 纵轴

        # 在每个格子中显示准确率
        for i in range(3):
            for j in range(5):
                ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", color="black", fontsize=20)

    # 添加整体颜色条
    fig.colorbar(cax, ax=axes, location="right", shrink=0.8, label="Accuracy")

    # 保存图像
    filename = f"combined_matrix_{sub_dir}.png"
    output_file = os.path.join(output_path, filename)
    # plt.tight_layout(rect=[0, 0, 1, 0.95])  # 调整布局以适应标题
    plt.savefig(output_file)
    plt.close()


# 根据统计信息绘制并保存混淆矩阵
def save_diff_matrix(stats, output_path):
    sub_dir = "diff"
    os.makedirs(output_path, exist_ok=True)

    files = args.files_name
    # 初始化主图
    if len(files) == 1:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6), constrained_layout=True)
        axes = np.array([axes])
    else:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12), constrained_layout=True)  # 假设有 4 个组合 (2x2)

    fig.suptitle(f"COT - MC Accuracy Matrics", fontsize=20)

    for idx, (tell, file) in enumerate(itertools.product(tells, files)):
        # 初始化混淆矩阵 (3行, 5列)
        matrix = np.zeros((3, 5))  # 3个长度, 5个order

        for length, order in itertools.product(lengths, orders):
            if file == "standard":
                correct = stats[(tell, "CoT")][(length, order)].get("correct", 0) - stats[(tell, "MC")][(length, order)].get("correct", 0)
            elif file == "joint":
                correct = stats[(tell, "CoT")][(length, order)].get("joint_correct", 0) - stats[(tell, "MC")][(length, order)].get("joint_correct", 0)

            total = stats[(tell, "CoT")][(length, order)]["total"]
            accuracy = (correct / total) if total > 0 else 0
            matrix[length - 1, order] = accuracy

        # 确定当前子图位置
        ax = axes[idx // 2, idx % 2]

        # 绘制混淆矩阵
        cax = ax.imshow(matrix, cmap="coolwarm", aspect="auto", vmin=-1.0, vmax=1.0)
        ax.set_title(f"File: {file}, Tell: {tell}", fontsize=20)
        ax.set_xlabel("Order", fontsize=20)
        ax.set_ylabel("Length", fontsize=20)
        ax.set_xticks(range(5))
        ax.set_xticklabels([0, 1, 2, 3, 4])  # 横轴
        ax.set_yticks(range(3))
        ax.set_yticklabels([1, 2, 3])  # 纵轴

        # 在每个格子中显示准确率
        for i in range(3):
            for j in range(5):
                ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", color="black", fontsize=20)

    # 添加整体颜色条
    fig.colorbar(cax, ax=axes, location="right", shrink=0.8, label="Accuracy")

    # 保存图像
    if len(files) == 1:
        filename = f"{files[0]}_{sub_dir}.png"
    else:
        filename = f"{files[0]}_{files[1]}_{sub_dir}.png"

    output_file = os.path.join(output_path, filename)
    # plt.tight_layout(rect=[0, 0, 1, 0.95])  # 调整布局以适应标题
    plt.savefig(output_file)
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, default="")
    parser.add_argument("--output_path", type=str, default="")
    parser.add_argument(
        "--prompt_type", type=str, choices=["CoT", "MC"], nargs="+", default=["CoT", "MC"], help="Choose the types of prompts (CoT or MC)"
    )
    parser.add_argument(
        "--files_name", type=str, choices=["standard", "joint"], nargs="+", default=["standard", "joint"], help="Choose the name of files (standard or joint)"
    )
    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

    lengths = [1, 2, 3]
    orders = [0, 1, 2, 3, 4]
    prompts = ["CoT", "MC"]
    tells = ["No_Tell", "Tell"]

    with open(f"{input_path}/standard_accuracy.json", "r", encoding="utf-8") as f:
        standard_results = json.load(f)

    with open(f"{input_path}/joint_accuracy.json", "r", encoding="utf-8") as f:
        joint_results = json.load(f)

    stats = defaultdict(
        lambda: defaultdict(lambda: {"correct": 0, "joint_correct": 0, "total": 0})
    )

    # 读取时都读取进来，然后生成图片时，结合命令行参数选择性的输出
    for tell, prompt, length, order in itertools.product(tells, prompts, lengths, orders):
        stats[(tell, prompt)][(length, order)]["correct"] = standard_results[
            f"Tell: {tell}, Prompt: {prompt}"
        ][f"Length {length}, Order {order}"]["correct"]

        stats[(tell, prompt)][(length, order)]["joint_correct"] = joint_results[
            f"Tell: {tell}, Prompt: {prompt}"
        ][f"Length {length}, Order {order}"]["joint_correct"]

        stats[(tell, prompt)][(length, order)]["total"] = standard_results[
            f"Tell: {tell}, Prompt: {prompt}"
        ][f"Length {length}, Order {order}"]["total"]

    os.makedirs(output_path, exist_ok=True)

    # 保存混淆矩阵
    save_confusion_matrix(stats, output_path, choice="standard")  # 标准准确率
    save_confusion_matrix(stats, output_path, choice="joint")  # 联合准确率

    # 保存差异矩阵
    save_diff_matrix(stats, output_path)
