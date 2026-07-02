#!/usr/bin/env python3
"""
生成防御算法稳定性分析图表 - 使用120样本新数据
重点展示：哪些防御算法能在三个模型上稳定达到15%以上的提升
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

# 加载数据
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
# 图3: 三种防御算法在不同警告级别下的提升幅度（三个模型）
# ============================================================================
print("生成图3: 防御算法提升幅度对比 (120样本)...")

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
warning_levels = ['无警告', '弱警告', '强警告']
models = ['GLM4', 'Qwen2.5', 'LLaMA3.1']
strategies = ['OneShot', 'CoT', 'FC']
colors = {'OneShot': '#FFA07A', 'CoT': '#87CEEB', 'FC': '#90EE90'}

for idx, warning in enumerate(warning_levels):
    ax = axes[idx]

    # 计算每个模型、每种策略的提升
    improvements = {strategy: [] for strategy in strategies}

    for model_name in models:
        baseline_acc = models_data[model_name]['scenarios'][baseline_scenarios[warning]]['accuracy']

        for strategy in strategies:
            defense_acc = models_data[model_name]['scenarios'][defense_strategies[strategy][warning]]['accuracy']
            improvement = defense_acc - baseline_acc
            improvements[strategy].append(improvement)

    # 绘制分组柱状图
    x = np.arange(len(models))
    width = 0.25

    for i, strategy in enumerate(strategies):
        offset = (i - 1) * width
        bars = ax.bar(x + offset, improvements[strategy], width,
                      label=strategy, color=colors[strategy],
                      edgecolor='black', linewidth=0.8)

        # 添加数值标签
        for bar, val in zip(bars, improvements[strategy]):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1 if height > 0 else height - 2,
                    f'{val:.1f}', ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=8, fontproperties=font_prop)

    # 添加15%目标线
    ax.axhline(y=15, color='red', linestyle='--', linewidth=2, label='15%目标', alpha=0.7)
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)

    ax.set_xlabel('模型', fontsize=11, fontweight='bold', fontproperties=font_prop)
    ax.set_ylabel('准确率提升 (pp)', fontsize=11, fontweight='bold', fontproperties=font_prop)
    ax.set_title(f'{warning}场景', fontsize=12, fontweight='bold', fontproperties=font_prop)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontproperties=font_prop)
    ax.legend(prop=font_prop, loc='upper left', fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(-10, 40)

plt.tight_layout()
plt.savefig('figures/fig3_defense_stability.png', dpi=300, bbox_inches='tight')
plt.savefig('figures/fig3_defense_stability.pdf', bbox_inches='tight')
print("✓ figures/fig3_defense_stability.png")
plt.close()

# ============================================================================
# 输出稳定性数据（用于文本解释）
# ============================================================================
print("\n" + "="*80)
print("稳定性数据（用于文本解释）- 120样本")
print("="*80)

for warning in warning_levels:
    print(f"\n### {warning}场景")
    print("-" * 80)

    for strategy in strategies:
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
        min_improvement = min(improvements)
        max_improvement = max(improvements)
        all_pass = all(imp >= 15 for imp in improvements)

        print(f"  平均提升: {avg_improvement:+.1f}pp")
        print(f"  范围: {min_improvement:+.1f}pp ~ {max_improvement:+.1f}pp")
        print(f"  {'✓ 稳定达标 (全部≥15pp)' if all_pass else '✗ 不稳定'}")

print("\n" + "="*80)
print("✓ 图表生成完成！")
print("="*80)
