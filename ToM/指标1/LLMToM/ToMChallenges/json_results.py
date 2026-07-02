import json
import argparse
import os
from collections import Counter, defaultdict
import re
import string

CORRECT = "correct"
TOTAL = "total"
ACCURACY = "accuracy"
STEP1 = "Step1"
STEP2 = "Step2"
STEP3 = "Step3"

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
    for step in [STEP3, STEP2, STEP1]:
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

    # 初始化
    standard_results = defaultdict(lambda: defaultdict(lambda: {ACCURACY: 0, CORRECT: 0, TOTAL: 0}))
    joint_results = defaultdict(lambda: defaultdict(lambda: {ACCURACY: 0, CORRECT: 0, TOTAL: 0}))
    step_results = defaultdict(lambda: defaultdict(lambda: {STEP1: 0, STEP2: 0, STEP3: 0}))

    for dir1_name in os.listdir(input_path):
        dir1_path = os.path.join(input_path, dir1_name) # dir1_path: answers/behind_the_scene_service_industry

        if dir1_name == "Sally-Anne_prompt.csv":
            files_mapping = {0: ["reality", "1stA", "2ndA"], 1: ["memory", "1stB", "2ndB"]}
        elif dir1_name == "Smarties_prompt.csv":
            files_mapping = {0: ["reality", "1stA", "2ndA"], 1: ["assumption", "1stB", "2ndB"]}
        else:
            continue

        for dir2_name in os.listdir(dir1_path):
            dir2_path = os.path.join(dir1_path, dir2_name) # dir2_path: answers/behind_the_scene_service_industry/gen321_sev3

            for t, files in files_mapping.items():
                
                is_joint_correct = True

                for idx, file_name in enumerate(files):
                    input_fn = os.path.join(dir2_path, f"{file_name}.json")
                    if not os.path.exists(input_fn):
                        print(f"File not found: {input_fn}")
                        exit()
                    
                    with open(input_fn, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    preds = []
                    for d in data:
                        extract = extract_answer(d["output"])
                        if extract is not None:
                            pred = d['map'].get(extract)
                            preds.append(pred)

                            if pred == data[0]['answer']:
                                update_steps(dir1_name, f"Order {idx + 1}", extract_step(d["output"]))
                                update_steps("Total", f"Order {idx + 1}", extract_step(d["output"]))
                    
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
                    
                    update_results(standard_results, dir1_name, f"Order {idx + 1}", is_correct)
                    update_results(standard_results, "Total", f"Order {idx + 1}", is_correct)

                    update_results(joint_results, dir1_name, f"Order {idx + 1}", is_joint_correct)
                    update_results(joint_results, "Total", f"Order {idx + 1}", is_joint_correct)
            
        
    # 计算"Total""order"的总准确率
    for order in ["Order 1", "Order 2", "Order 3"]:
        for tmp in [CORRECT, TOTAL]:
            standard_results["Total"]["Total"][tmp] += standard_results["Total"][order][tmp]
            joint_results["Total"]["Total"][tmp] += joint_results["Total"][order][tmp]
        for step in [STEP3, STEP2, STEP1]:
            step_results["Total"]["Total"][step] += step_results["Total"][order][step]
    
    process_results(standard_results)
    process_results(joint_results)
        
    os.makedirs(output_path, exist_ok=True)
    
    with open(f"{output_path}/standard_accuracy.json", "w", encoding="utf-8") as f:
        json.dump(standard_results, f, ensure_ascii=False, indent=4)

    with open(f"{output_path}/joint_accuracy.json", "w", encoding="utf-8") as f:
        json.dump(joint_results, f, ensure_ascii=False, indent=4)

    with open(f"{output_path}/step_results.json", "w", encoding="utf-8") as f:
        json.dump(step_results, f, ensure_ascii=False, indent=4)


