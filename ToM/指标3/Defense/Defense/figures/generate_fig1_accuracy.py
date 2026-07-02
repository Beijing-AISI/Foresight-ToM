#!/usr/bin/env python3
"""
生成图1：直接展示准确率（而非提升幅度）- 使用120样本新数据
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import json
import numpy as np
import os

# 设置中文字体
font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False
else:
    font_prop = fm.FontProperties()
    print("Warning: Chinese font not found, using default font")

plt.rcParams['figure.dpi'] = 300

# 加载数据 - 使用新的120样本数据
models_data = {
    'GLM4': json.load(open('results/13scenarios_summary_glm4_9b_falsearg_20260624_120samples.json')),
    'Qwen2.5': json.load(open('results/13scenarios_summary_qwen2.5_7b_falsearg_20260624_120samples.json')),
    'LLaMA3.1': json.load(open('results/13scenarios_summary_llama3.1_8b_falsearg_20260624_120samples.json'))
}

# 定义场景映射
baseline_scenarios = {
    '无警告': 'S01_labeled_no_warning',
    '弱警告': 'S05_labeled_weak_warning',
    '强警告': 'S09_labeled_strong_warning'
}

defense_strategies = {
    '基线': {
        '无警告': 'S01_labeled_no_warning',
        '弱警告': 'S05_labeled_weak_warning',
        '强警告': 'S09_labeled_strong_warning'
    },
    'OneShot': {
        '无警告': 'S02_labeled_no_warning_oneshot',
        '弱警告': 'S06_labeled_weak_warning_oneshot',
        '强警告': 'S10_labeled_strong_warning_oneshot'
    },
    'CoT': {
        '无警告': 'S03_labeled_no_warning_cot',
        '弱警告': 'S07_labeled_weak_warning_cot',
        '强警告': 'S11_labeled_strong_warning_cot'
    },
    'FC': {
        '无警告': 'S04_labeled_no_warning_fc',
        '弱警告': 'S08_labeled_weak_warning_fc',
        '强警告': 'S12_labeled_strong_warning_fc'
    }
}

# ============================================================================
# 图1: 直接展示准确率（不是提升幅度）
# ============================================================================
print("生成图1: 防御策略准确率对比 (120样本)...")

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
warning_levels = ['无警告', '弱警告', '强警告']
models = ['GLM4', 'Qwen2.5', 'LLaMA3.1']
strategies = ['基线', 'OneShot', 'CoT', 'FC']
colors = {'基线': '#D3D3D3', 'OneShot': '#FFA07A', 'CoT': '#87CEEB', 'FC': '#90EE90'}

for idx, warning in enumerate(warning_levels):
    ax = axes[idx]

    # 计算每个模型、每种策略的准确率
    accuracies = {strategy: [] for strategy in strategies}

    for model_name in models:
        for strategy in strategies:
            defense_acc = models_data[model_name]['scenarios'][defense_strategies[strategy][warning]]['accuracy']
            accuracies[strategy].append(defense_acc)

    # 绘制分组柱状图
    x = np.arange(len(models))
    width = 0.2

    for i, strategy in enumerate(strategies):
        offset = (i - 1.5) * width
        bars = ax.bar(x + offset, accuracies[strategy], width,
                      label=strategy, color=colors[strategy],
                      edgecolor='black', linewidth=0.8)

        # 添加数值标签
        for bar, val in zip(bars, accuracies[strategy]):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{val:.1f}%', ha='center', va='bottom',
                    fontsize=7, fontproperties=font_prop)

    ax.set_xlabel('模型', fontsize=11, fontweight='bold', fontproperties=font_prop)
    ax.set_ylabel('准确率 (%)', fontsize=11, fontweight='bold', fontproperties=font_prop)
    ax.set_title(f'{warning}场景', fontsize=12, fontweight='bold', fontproperties=font_prop)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontproperties=font_prop)
    ax.legend(prop=font_prop, loc='upper left', fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 100)

plt.tight_layout()
plt.savefig('figures/fig1_defense_accuracy_by_warning.png', dpi=300, bbox_inches='tight')
plt.savefig('figures/fig1_defense_accuracy_by_warning.pdf', bbox_inches='tight')
print("✓ figures/fig1_defense_accuracy_by_warning.png")
plt.close()

# ============================================================================
# 计算并输出提升数据（用于文本解释）
# ============================================================================
print("\n" + "="*80)
print("提升数据（用于文本解释）- 120样本")
print("="*80)

for warning in warning_levels:
    print(f"\n### {warning}场景")
    print("-" * 80)

    for strategy in ['OneShot', 'CoT', 'FC']:
        print(f"\n{strategy}策略:")
        improvements = []

        for model_name in models:
            baseline_acc = models_data[model_name]['scenarios'][baseline_scenarios[warning]]['accuracy']
            defense_acc = models_data[model_name]['scenarios'][defense_strategies[strategy][warning]]['accuracy']
            improvement = defense_acc - baseline_acc
            improvements.append(improvement)

            达标 = "✓" if improvement >= 15 else "✗"
            print(f"  {model_name}: {baseline_acc:.1f}% → {defense_acc:.1f}% (提升 {improvement:+.1f}pp) {达标}")

        avg_improvement = np.mean(improvements)
        all_pass = all(imp >= 15 for imp in improvements)
        print(f"  平均提升: {avg_improvement:+.1f}pp {'✓ 全部达标' if all_pass else '✗ 未全部达标'}")

print("\n" + "="*80)
print("✓ 图表生成完成！")
print("="*80)
