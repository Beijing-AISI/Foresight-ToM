from collections import defaultdict
import itertools
import json
import argparse
import os
from collections import Counter
import string

CORRECT = "correct"
TOTAL = "total"
ACCURACY = "accuracy"
STEP1 = "Step1"
STEP2 = "Step2"
STEP3 = "Step3"
STEP4 = "Step4"
STEP5 = "Step5"


def extract_answer(text):
    # 从文本中提取答案选项 (A-Z)，优先级为 [A]. > [A]
    for letter in string.ascii_uppercase:  # 遍历 A-Z
        if f"[{letter}]." in text:
            return letter
        
    for letter in string.ascii_uppercase:  # 遍历 A-Z
        if f"[{letter}]" in text:
            return letter
    
    return None

def extract_step(text):
    for step in [STEP5, STEP4, STEP3, STEP2, STEP1]:
        if step in text:
            return step
    return None


def update_results(results, key1, key2, correct):
    """
    更新结果字典：更新正确数和总数。
    """
    results[key1][key2][CORRECT] += int(correct)
    results[key1][key2][TOTAL] += 1


def update_steps(key1, key2, step):
    if step != None:
        step_results[key1][key2][step] += 1

def process_results(results):
    """
    遍历并计算准确率，更新结果字典。
    """
    for key1, value1 in results.items():
        for key2, value2 in value1.items():
            correct = value2.get(CORRECT, 0)
            total = value2.get(TOTAL, 0)
            value2[ACCURACY] = correct / total * 100

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, default="")
    parser.add_argument("--output_path", type=str, default="")  # 添加输出文件路径参数

    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path

    lengths = [1, 2, 3]
    orders = range(5)
    tells = ["No_Tell", "Tell"]

    # 初始化统计数据
    standard_results = defaultdict(lambda: defaultdict(lambda: {ACCURACY: 0, CORRECT: 0, TOTAL: 0}))
    joint_results = defaultdict(lambda: defaultdict(lambda: {ACCURACY: 0, CORRECT: 0, TOTAL: 0}))
    step_results = defaultdict(lambda: defaultdict(lambda: {STEP1: 0, STEP2: 0, STEP3: 0, STEP4: 0, STEP5: 0}))

    for tell, length, sample_num in itertools.product(tells, lengths, range(1, 21)):
        is_joint_correct = True  # 用于记录联合正确性

        for order in orders:

            input_fn = os.path.join(args.input_path, tell, "CoT" ,f"length_{length}",f"sample_{sample_num}",f"order_{order}.jsonl",)

            with open(input_fn, "r", encoding="utf-8") as f:
                data = json.load(f)
                # data = [json.loads(line) for line in f.readlines()]

            preds = []
            for d in data:
                extract = extract_answer(d["output"])
                if extract is not None:
                    pred = d['map'].get(extract)
                    preds.append(pred)
                
                    if pred == data[0]['answer']:
                        update_steps(f"Tell: {tell}", f"Length {length}, Order {order}", extract_step(d["output"]))
                        update_steps("Total", f"Order {order}", extract_step(d["output"]))
            
            if preds:
                preds_counts = Counter(preds)
                max_count = max(preds_counts.values())

                if list(preds_counts.values()).count(max_count) == 1:
                    max_num = max(preds_counts, key=preds_counts.get) # type: ignore
                    is_correct = max_num == data[0]["answer"]
                else:
                    is_correct = False
            else:
                is_correct = False

            # 记录联合正确性
            is_joint_correct = is_correct and is_joint_correct

            update_results(standard_results, f"Tell: {tell}", f"Length {length}, Order {order}", is_correct)
            update_results(standard_results, "Total", f"Order {order}", is_correct)

            update_results(joint_results, f"Tell: {tell}", f"Length {length}, Order {order}", is_joint_correct)
            update_results(joint_results, "Total", f"Order {order}", is_joint_correct)

    # 计算"Total""order"的总准确率
    for order in orders:
        for tmp in [CORRECT, TOTAL]:
            standard_results["Total"]["Total"][tmp] += standard_results["Total"][f"Order {order}"][tmp]
            joint_results["Total"]["Total"][tmp] += joint_results["Total"][f"Order {order}"][tmp]
        for step in [STEP5, STEP4, STEP3, STEP2, STEP1]:
            step_results["Total"]["Total"][step] += step_results["Total"][f"Order {order}"][step]
        

    process_results(standard_results)
    process_results(joint_results)

    os.makedirs(output_path, exist_ok=True)

    with open(f"{output_path}/standard_accuracy.json", "w", encoding="utf-8") as f:
        json.dump(standard_results, f, ensure_ascii=False, indent=4)

    with open(f"{output_path}/joint_accuracy.json", "w", encoding="utf-8") as f:
        json.dump(joint_results, f, ensure_ascii=False, indent=4)

    with open(f"{output_path}/steps.json", "w", encoding="utf-8") as f:
        json.dump(step_results, f, ensure_ascii=False, indent=4)
