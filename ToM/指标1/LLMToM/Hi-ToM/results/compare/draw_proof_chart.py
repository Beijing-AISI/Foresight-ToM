#!/usr/bin/env python3
"""
Generate a line chart directly proving the claim:
"Enhancement method increases the model's ToM reasoning depth by >= 1 level."

Data source: three joint_accuracy.json files in compare/ directory.
"""
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Absolute paths to the three result files
ADAPT_PATH = "/data1/fanjinyu/ToM/LLMToM/Hi-ToM/results/compare/1shot+adapt/Llama-3.1-8B-Instruct/accuracy_results/joint_accuracy.json"
STEP_PATH = "/data1/fanjinyu/ToM/LLMToM/Hi-ToM/results/compare/1shot+step/Llama-3.1-8B-Instruct/accuracy_results/joint_accuracy.json"
MC_PATH = "/data1/fanjinyu/ToM/LLMToM/Hi-ToM/results/compare/1shot+mc/Llama-3.1-8B-Instruct/accuracy_results/joint_accuracy.json"

OUTPUT_DIR = "/data1/fanjinyu/ToM/LLMToM/Hi-ToM/results/compare/1shot+adapt/Llama-3.1-8B-Instruct/accuracy_results/"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_accuracy(data_path, tell_key="Tell: No_Tell"):
    """Extract accuracy per Order from joint_accuracy.json."""
    with open(data_path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    accuracies = {}
    for order in range(5):
        key = f"Order {order}"
        accuracies[order] = d[tell_key][f"Length 1, {key}"]["accuracy"]
    return accuracies


def draw_combined_chart():
    """Draw a single chart showing all three methods across all orders, both Tell conditions."""
    adapt_no_tell = load_accuracy(ADAPT_PATH, "Tell: No_Tell")
    step_no_tell = load_accuracy(STEP_PATH, "Tell: No_Tell")
    mc_no_tell = load_accuracy(MC_PATH, "Tell: No_Tell")

    adapt_tell = load_accuracy(ADAPT_PATH, "Tell: Tell")
    step_tell = load_accuracy(STEP_PATH, "Tell: Tell")
    mc_tell = load_accuracy(MC_PATH, "Tell: Tell")

    orders = [0, 1, 2, 3, 4]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12), sharex=True)

    # No_Tell
    ax1.plot(orders, [adapt_no_tell[o] for o in orders], 'o-', color='#E63946', linewidth=2.5, markersize=10, label='1shot+adapt (enhanced)', zorder=3)
    ax1.plot(orders, [step_no_tell[o] for o in orders], 's-', color='#457B9D', linewidth=2.5, markersize=10, label='1shot+step (baseline)', zorder=3)
    ax1.plot(orders, [mc_no_tell[o] for o in orders], 'D-', color='#A8DADC', linewidth=2.5, markersize=10, label='1shot+mc (blank)', zorder=3)

    for o in orders:
        ax1.text(o, adapt_no_tell[o] + 1.5, f'{adapt_no_tell[o]:.1f}%', ha='center', fontsize=9, color='#E63946', fontweight='bold')
        ax1.text(o, step_no_tell[o] - 3.0, f'{step_no_tell[o]:.1f}%', ha='center', fontsize=9, color='#457B9D', fontweight='bold')
        ax1.text(o, mc_no_tell[o] - 3.0, f'{mc_no_tell[o]:.1f}%', ha='center', fontsize=9, color='#A8DADC', fontweight='bold')

    ax1.set_ylabel('Joint Accuracy (%)', fontsize=14)
    ax1.set_title('No_Tell (No Extra Hint)', fontsize=16, fontweight='bold')
    ax1.set_ylim(-5, 105)
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax1.legend(fontsize=11, loc='upper right')
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Tell
    ax2.plot(orders, [adapt_tell[o] for o in orders], 'o-', color='#E63946', linewidth=2.5, markersize=10, label='1shot+adapt (enhanced)', zorder=3)
    ax2.plot(orders, [step_tell[o] for o in orders], 's-', color='#457B9D', linewidth=2.5, markersize=10, label='1shot+step (baseline)', zorder=3)
    ax2.plot(orders, [mc_tell[o] for o in orders], 'D-', color='#A8DADC', linewidth=2.5, markersize=10, label='1shot+mc (blank)', zorder=3)

    for o in orders:
        ax2.text(o, adapt_tell[o] + 1.5, f'{adapt_tell[o]:.1f}%', ha='center', fontsize=9, color='#E63946', fontweight='bold')
        ax2.text(o, step_tell[o] - 3.0, f'{step_tell[o]:.1f}%', ha='center', fontsize=9, color='#457B9D', fontweight='bold')
        ax2.text(o, mc_tell[o] - 3.0, f'{mc_tell[o]:.1f}%', ha='center', fontsize=9, color='#A8DADC', fontweight='bold')

    ax2.set_xlabel('ToM Reasoning Order', fontsize=14)
    ax2.set_ylabel('Joint Accuracy (%)', fontsize=14)
    ax2.set_title('Tell (With Extra Hint)', fontsize=16, fontweight='bold')
    ax2.set_ylim(-5, 105)
    ax2.set_xticks(orders)
    ax2.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax2.legend(fontsize=11, loc='upper right')
    ax2.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "proof_claims.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved to {output_path}")


def draw_order_gain_chart():
    """Draw the absolute gain (adapt - step) per Order as a bar chart."""
    adapt_no_tell = load_accuracy(ADAPT_PATH, "Tell: No_Tell")
    step_no_tell = load_accuracy(STEP_PATH, "Tell: No_Tell")

    orders = [0, 1, 2, 3, 4]
    gains = [adapt_no_tell[o] - step_no_tell[o] for o in orders]

    colors = ['#E63946' if g > 0 else '#B0B0B0' for g in gains]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar([f'Order {o}' for o in orders], gains, color=colors, width=0.6, edgecolor='white', linewidth=1.5)

    for bar, g in zip(bars, gains):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + (0.5 if height > 0 else -2),
                f'+{g:.1f}%' if g > 0 else f'{g:.1f}%',
                ha='center', va='bottom' if height > 0 else 'top',
                fontsize=12, fontweight='bold')

    ax.axhline(y=20, color='#457B9D', linestyle='--', linewidth=1.5, alpha=0.7, label='20% threshold (distinguishable from noise)')
    ax.axhline(y=30, color='#2A9D8F', linestyle='-.', linewidth=1.5, alpha=0.7, label='30% threshold (reliable)')

    ax.set_xlabel('ToM Reasoning Order', fontsize=14)
    ax.set_ylabel('Absolute Accuracy Gain (adapt - step, in %)', fontsize=14)
    ax.set_title('Accuracy Gain of Enhancement vs Baseline per Order (No_Tell)\nLlama-3.1-8B-Instruct', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax.set_ylim(-5, 25)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "proof_gain_per_order.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    draw_combined_chart()
    draw_order_gain_chart()
