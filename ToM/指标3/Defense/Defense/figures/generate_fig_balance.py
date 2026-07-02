#!/usr/bin/env python3
"""
生成防御算法均衡性分析图 - 使用120样本新数据
展示各防御策略在TRUE_ARGUMENT和FALSE_ARGUMENT下的表现均衡性
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

# 加载数据 - FALSE和TRUE两种论证类型
models_data_false = {
    'GLM4': json.load(open('results/13scenarios_summary_glm4_9b_falsearg_20260624_120samples.json')),
    'Qwen2.5': json.load(open('results/13scenarios_summary_qwen2.5_7b_falsearg_20260624_120samples.json')),
    'LLaMA3.1': json.load(open('results/13scenarios_summary_llama3.1_8b_falsearg_20260624_120samples.json'))
}

models_data_true = {
    'GLM4': json.load(open('results/13scenarios_summary_glm4_9b_truearg_20260624_120samples.json')),
    'Qwen2.5': json.load(open('results/13scenarios_summary_qwen2.5_7b_truearg_20260624_120samples.json')),
    'LLaMA3.1': json.load(open('results/13scenarios_summary_llama3.1_8b_truearg_20260624_120samples.json'))
}

# 定义场景映射
strategies = {
    '基线-无警告': 'S01_labeled_no_warning',
    '基线-弱警告': 'S05_labeled_weak_warning',
    '基线-强警告': 'S09_labeled_strong_warning',
    'OneShot-无警告': 'S02_labeled_no_warning_oneshot',
    'OneShot-弱警告': 'S06_labeled_weak_warning_oneshot',
    'OneShot-强警告': 'S10_labeled_strong_warning_oneshot',
    'CoT-无警告': 'S03_labeled_no_warning_cot',
    'CoT-弱警告': 'S07_labeled_weak_warning_cot',
    'CoT-强警告': 'S11_labeled_strong_warning_cot',
    'FC-无警告': 'S04_labeled_no_warning_fc',
    'FC-弱警告': 'S08_labeled_weak_warning_fc',
    'FC-强警告': 'S12_labeled_strong_warning_fc',
}

models = ['GLM4', 'Qwen2.5', 'LLaMA3.1']

# ============================================================================
# 图2: 防御算法在TRUE/FALSE论证下的均衡性分析
# ============================================================================
print("生成图2: 防御算法均衡性分析 (120样本)...")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
warning_levels = ['无警告', '弱警告', '强警告']
defense_strategies = ['基线', 'OneShot', 'CoT', 'FC']

for idx, warning in enumerate(warning_levels):
    ax = axes[idx]

    # 计算每种策略在TRUE和FALSE下的准确率
    x_positions = np.arange(len(defense_strategies))
    width = 0.35

    false_accs = []
    true_accs = []

    for strategy in defense_strategies:
        scenario_key = f"{strategy}-{warning}"
        scenario_id = strategies[scenario_key]

        # 计算三个模型的平均准确率
        false_acc = np.mean([models_data_false[m]['scenarios'][scenario_id]['accuracy'] for m in models])
        true_acc = np.mean([models_data_true[m]['scenarios'][scenario_id]['accuracy'] for m in models])

        false_accs.append(false_acc)
        true_accs.append(true_acc)

    # 绘制分组柱状图
    bars1 = ax.bar(x_positions - width/2, false_accs, width, label='FALSE论证',
                   color='#FF6B6B', edgecolor='black', linewidth=0.8)
    bars2 = ax.bar(x_positions + width/2, true_accs, width, label='TRUE论证',
                   color='#4ECDC4', edgecolor='black', linewidth=0.8)

    # 添加数值标签
    for bar, val in zip(bars1, false_accs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val:.1f}%', ha='center', va='bottom',
                fontsize=8, fontproperties=font_prop)

    for bar, val in zip(bars2, true_accs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val:.1f}%', ha='center', va='bottom',
                fontsize=8, fontproperties=font_prop)

    # 计算并显示差异（均衡性指标）
    for i, (false_acc, true_acc) in enumerate(zip(false_accs, true_accs)):
        diff = abs(true_acc - false_acc)
        # 在两个柱子中间下方标注差异
        ax.text(i, -8, f'Δ={diff:.1f}', ha='center', va='top',
                fontsize=7, fontproperties=font_prop, color='red' if diff > 20 else 'green')

    ax.set_xlabel('防御策略', fontsize=11, fontweight='bold', fontproperties=font_prop)
    ax.set_ylabel('准确率 (%)', fontsize=11, fontweight='bold', fontproperties=font_prop)
    ax.set_title(f'{warning}场景：TRUE/FALSE均衡性', fontsize=12, fontweight='bold', fontproperties=font_prop)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(defense_strategies, fontproperties=font_prop)
    ax.legend(prop=font_prop, loc='upper left', fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(-12, 100)
    ax.axhline(y=0, color='black', linewidth=0.5)

plt.tight_layout()
plt.savefig('figures/fig2_defense_balance_true_false.png', dpi=300, bbox_inches='tight')
plt.savefig('figures/fig2_defense_balance_true_false.pdf', bbox_inches='tight')
print("✓ figures/fig2_defense_balance_true_false.png")
plt.close()

# ============================================================================
# 输出详细的均衡性数据（用于文本解释）
# ============================================================================
print("\n" + "="*80)
print("均衡性数据（用于文本解释）- 120样本")
print("="*80)

for warning in warning_levels:
    print(f"\n### {warning}场景")
    print("-" * 80)

    for strategy in defense_strategies:
        scenario_key = f"{strategy}-{warning}"
        scenario_id = strategies[scenario_key]

        # 计算三个模型的平均准确率
        false_acc = np.mean([models_data_false[m]['scenarios'][scenario_id]['accuracy'] for m in models])
        true_acc = np.mean([models_data_true[m]['scenarios'][scenario_id]['accuracy'] for m in models])
        diff = abs(true_acc - false_acc)

        # 计算各模型的差异
        model_diffs = []
        for m in models:
            f_acc = models_data_false[m]['scenarios'][scenario_id]['accuracy']
            t_acc = models_data_true[m]['scenarios'][scenario_id]['accuracy']
            model_diffs.append(abs(t_acc - f_acc))

        max_diff = max(model_diffs)

        balanced = "✓ 均衡" if diff < 15 else "✗ 不均衡"

        print(f"{strategy}: FALSE={false_acc:.1f}%, TRUE={true_acc:.1f}%, Δ={diff:.1f}pp (最大={max_diff:.1f}pp) {balanced}")

print("\n" + "="*80)
print("✓ 图表生成完成！")
print("="*80)
