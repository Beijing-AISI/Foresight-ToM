#!/usr/bin/env python3
"""
从results文件夹中汇总所有实验结果
生成详细的统计报告
"""

import json
import glob
import os
from datetime import datetime
import numpy as np

def load_latest_results():
    """加载最新时间戳的所有结果文件"""

    # 找到所有summary文件
    summary_files = glob.glob('results/*_summary_*.json')

    if not summary_files:
        print("错误: 未找到任何结果文件")
        return None

    # 按时间戳分组
    timestamp_groups = {}
    for f in summary_files:
        parts = os.path.basename(f).split('_')
        # 提取时间戳（倒数第一个部分去掉.json）
        timestamp = parts[-1].replace('.json', '')

        if timestamp not in timestamp_groups:
            timestamp_groups[timestamp] = []
        timestamp_groups[timestamp].append(f)

    # 选择最新的时间戳
    latest_timestamp = max(timestamp_groups.keys())
    latest_files = timestamp_groups[latest_timestamp]

    print(f"找到 {len(latest_files)} 个结果文件（时间戳: {latest_timestamp}）")

    # 加载所有数据
    results_data = {}
    for file_path in latest_files:
        with open(file_path, 'r') as f:
            data = json.load(f)
            model = data['model']
            arg_type = data['argument_type']
            key = f"{model}_{arg_type}"
            results_data[key] = data

    return results_data, latest_timestamp


def generate_report(results_data, timestamp):
    """生成详细报告"""

    print("\n" + "="*90)
    print("完整测试结果报告 - S01-S12重新编号版本")
    print("="*90)
    print(f"时间戳: {timestamp}")
    print(f"测试配置: 12场景 × 3模型 × 2论证类型 × 120样本")

    # 提取模型列表
    models = sorted(set(k.split('_')[0] for k in results_data.keys()))

    # 定义场景映射（新编号）
    scenario_groups = {
        '无警告': ['S01_labeled_no_warning', 'S02_labeled_no_warning_oneshot',
                  'S03_labeled_no_warning_cot', 'S04_labeled_no_warning_fc'],
        '弱警告': ['S05_labeled_weak_warning', 'S06_labeled_weak_warning_oneshot',
                  'S07_labeled_weak_warning_cot', 'S08_labeled_weak_warning_fc'],
        '强警告': ['S09_labeled_strong_warning', 'S10_labeled_strong_warning_oneshot',
                  'S11_labeled_strong_warning_cot', 'S12_labeled_strong_warning_fc']
    }

    strategy_names = {
        'no_warning': '基线',
        'no_warning_oneshot': 'OneShot',
        'no_warning_cot': 'CoT',
        'no_warning_fc': 'FC',
        'weak_warning': '基线',
        'weak_warning_oneshot': 'OneShot',
        'weak_warning_cot': 'CoT',
        'weak_warning_fc': 'FC',
        'strong_warning': '基线',
        'strong_warning_oneshot': 'OneShot',
        'strong_warning_cot': 'CoT',
        'strong_warning_fc': 'FC'
    }

    # ========================================================================
    # 1. 按模型和论证类型汇总
    # ========================================================================
    print("\n" + "="*90)
    print("1. 整体结果按模型和论证类型")
    print("="*90)
    print(f"\n{'模型':<15s} | {'FALSE_ARG':>12s} | {'TRUE_ARG':>12s} | {'综合':>12s}")
    print("-" * 60)

    for model in models:
        false_key = f"{model}_false"
        true_key = f"{model}_true"

        if false_key in results_data and true_key in results_data:
            false_data = results_data[false_key]
            true_data = results_data[true_key]

            # 计算平均准确率
            false_accs = [v['accuracy'] for v in false_data['scenarios'].values()]
            true_accs = [v['accuracy'] for v in true_data['scenarios'].values()]

            false_avg = np.mean(false_accs)
            true_avg = np.mean(true_accs)
            overall_avg = (false_avg + true_avg) / 2

            print(f"{model:<15s} | {false_avg:11.1f}% | {true_avg:11.1f}% | {overall_avg:11.1f}%")

    # ========================================================================
    # 2. 详细场景结果（按模型）
    # ========================================================================
    print("\n" + "="*90)
    print("2. 详细场景结果")
    print("="*90)

    for model in models:
        false_key = f"{model}_false"
        true_key = f"{model}_true"

        if false_key not in results_data or true_key not in results_data:
            continue

        print(f"\n### {model}")
        print(f"\n{'场景':<40s} | {'FALSE_ARG':>12s} | {'TRUE_ARG':>12s}")
        print("-" * 70)

        false_data = results_data[false_key]
        true_data = results_data[true_key]

        for scenario_id, scenario_info in false_data['scenarios'].items():
            false_acc = scenario_info['accuracy']
            true_acc = true_data['scenarios'][scenario_id]['accuracy']

            name = scenario_info['name']
            print(f"{name:<40s} | {false_acc:11.1f}% | {true_acc:11.1f}%")

    # ========================================================================
    # 3. 防御策略效果分析（跨模型平均）
    # ========================================================================
    print("\n" + "="*90)
    print("3. 防御策略效果（跨模型平均，FALSE_ARGUMENT场景）")
    print("="*90)

    print(f"\n{'警告级别':<12s} | {'基线':>10s} | {'OneShot':>10s} | {'CoT':>10s} | {'FC':>10s}")
    print("-" * 60)

    for warning_level, scenario_ids in scenario_groups.items():
        accs = [[], [], [], []]  # 基线, OneShot, CoT, FC

        for model in models:
            false_key = f"{model}_false"
            if false_key not in results_data:
                continue

            for idx, sid in enumerate(scenario_ids):
                if sid in results_data[false_key]['scenarios']:
                    accs[idx].append(results_data[false_key]['scenarios'][sid]['accuracy'])

        avgs = [np.mean(a) if a else 0 for a in accs]
        print(f"{warning_level:<12s} | {avgs[0]:9.1f}% | {avgs[1]:9.1f}% | {avgs[2]:9.1f}% | {avgs[3]:9.1f}%")

    # ========================================================================
    # 4. FC防御提升分析
    # ========================================================================
    print("\n" + "="*90)
    print("4. FC防御相对基线的提升（FALSE_ARGUMENT场景）")
    print("="*90)

    print(f"\n{'警告级别':<12s} | {'GLM4':>15s} | {'Qwen2.5':>15s} | {'LLaMA3.1':>15s}")
    print("-" * 65)

    baseline_scenarios = {
        '无警告': 'S01_labeled_no_warning',
        '弱警告': 'S05_labeled_weak_warning',
        '强警告': 'S09_labeled_strong_warning'
    }

    fc_scenarios = {
        '无警告': 'S04_labeled_no_warning_fc',
        '弱警告': 'S08_labeled_weak_warning_fc',
        '强警告': 'S12_labeled_strong_warning_fc'
    }

    for warning_level in ['无警告', '弱警告', '强警告']:
        baseline_sid = baseline_scenarios[warning_level]
        fc_sid = fc_scenarios[warning_level]

        improvements = []
        for model in models:
            false_key = f"{model}_false"
            if false_key not in results_data:
                improvements.append("N/A")
                continue

            baseline_acc = results_data[false_key]['scenarios'][baseline_sid]['accuracy']
            fc_acc = results_data[false_key]['scenarios'][fc_sid]['accuracy']
            improvement = fc_acc - baseline_acc

            improvements.append(f"{improvement:+6.1f}pp")

        print(f"{warning_level:<12s} | {improvements[0]:>15s} | {improvements[1]:>15s} | {improvements[2]:>15s}")

    # ========================================================================
    # 5. 生成汇总JSON
    # ========================================================================
    summary_output = {
        'timestamp': timestamp,
        'test_config': {
            'scenarios': 12,
            'models': len(models),
            'argument_types': 2,
            'samples_per_scenario': 120,
            'total_tests': 12 * len(models) * 2 * 120
        },
        'models': {}
    }

    for model in models:
        false_key = f"{model}_false"
        true_key = f"{model}_true"

        if false_key in results_data and true_key in results_data:
            summary_output['models'][model] = {
                'false_argument': {
                    sid: {
                        'name': info['name'],
                        'accuracy': info['accuracy'],
                        'correct': info['correct'],
                        'total': info['total']
                    }
                    for sid, info in results_data[false_key]['scenarios'].items()
                },
                'true_argument': {
                    sid: {
                        'name': info['name'],
                        'accuracy': info['accuracy'],
                        'correct': info['correct'],
                        'total': info['total']
                    }
                    for sid, info in results_data[true_key]['scenarios'].items()
                }
            }

    output_file = f'COMPLETE_RESULTS_RENUMBERED_{timestamp}.json'
    with open(output_file, 'w') as f:
        json.dump(summary_output, f, indent=2, ensure_ascii=False)

    print("\n" + "="*90)
    print(f"✓ 完整汇总已保存到: {output_file}")
    print("="*90)

    return summary_output


def main():
    print("正在加载结果文件...")

    results_data, timestamp = load_latest_results()

    if results_data is None:
        return

    print(f"✓ 成功加载 {len(results_data)} 个结果")

    # 生成报告
    generate_report(results_data, timestamp)


if __name__ == '__main__':
    main()
