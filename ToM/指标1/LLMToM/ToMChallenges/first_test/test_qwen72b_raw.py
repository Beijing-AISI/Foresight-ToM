import argparse
from concurrent.futures import ProcessPoolExecutor
import importlib
import json
import os
import random
import re
import shutil
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
from datasets import load_dataset
import string
import pandas as pd
from openai import OpenAI


client = OpenAI(
    api_key='token-casia-braincog-233',
    base_url='http://210.75.240.144:3006/v1',
)

# 动态加载 prompts 文件
def load_prompt_module(prompts_path):
    spec = importlib.util.spec_from_file_location("load_prompts", prompts_path)
    load_prompts = importlib.util.module_from_spec(spec)
    sys.modules["load_prompts"] = load_prompts
    spec.loader.exec_module(load_prompts)

    prompts_data = {key: getattr(load_prompts, key) for key in dir(load_prompts) if not key.startswith("__")}

    with open(f"./{prompts_path}.json", "w", encoding="utf-8") as json_file:
        json.dump(prompts_data, json_file, ensure_ascii=False, indent=4)
    return load_prompts


def format_prompt(mc_prompt, choices_dict):
    available_letters = list(string.ascii_uppercase)
    random.shuffle(available_letters)

    # 将 choice_dict 的键映射到随机字母
    mapping = {key: available_letters.pop(0) for key in choices_dict.keys()}
    reverse_mapping = {value: key for key, value in mapping.items()}  # 创建反向映射

    randomized_choice_dict = {mapping[key]: value for key, value in choices_dict.items()}
    sorted_items = sorted(randomized_choice_dict.items())
    keys, values = zip(*sorted_items)  # 提取排序后的键和值

    # 动态生成格式化参数
    format_args = {
        'Story': mc_prompt
    }
    format_args.update({f'{chr(97 + i)}': keys[i] for i in range(len(keys))})
    format_args.update({f'choice_{chr(97 + i)}': values[i] for i in range(len(values))})

    prompt = load_prompts.UserEvaluatePrompt.format(**format_args)

    return reverse_mapping, prompt


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--output_path", type=str, default="./thb_test")
    parser.add_argument("--output_folder", type=str, default="./thb_test", help="Folder to save the output file")
    parser.add_argument("--promptsA_path", type=str, default="prompts/prompts.py", help="Path to the prompts file")
    parser.add_argument("--promptsB_path", type=str, default="prompts/prompts.py", help="Path to the prompts file")
    parser.add_argument("--try_times", type=int, default=5)

    args = parser.parse_args()

    root_folder = os.path.join(args.output_path, args.output_folder, "answers")

    if os.path.exists(root_folder):
        print(f"Warning: You are about to clear the output folder: {root_folder}")
        # confirm = (input("Type 'y' to confirm or anything else to cancel: ").strip().lower())
        # if confirm == "y":
        if True:
            print(f"Clearing output folder: {root_folder}")
            shutil.rmtree(root_folder)  # 删除整个文件夹及其内容
            os.makedirs(root_folder, exist_ok=True)  # 重新创建文件夹
        else:
            print("Operation cancelled. Folder was not cleared.")
            exit(1)  # 退出程序，避免后续操作
    else:
        os.makedirs(root_folder, exist_ok=True)  # 重新创建文件夹

    configs = ['Smarties_prompt.csv', 'Sally-Anne_prompt.csv']

    for config in configs:

        if config == "Sally-Anne_prompt.csv":
            prompts_path = args.promptsA_path
        elif config == "Smarties_prompt.csv":
            prompts_path = args.promptsB_path

        # 加载指定的 prompts 文件
        load_prompts = load_prompt_module(prompts_path)
        system_prompt = load_prompts.SystemEvaluatePrompt
        user_prompt = load_prompts.UserEvaluatePrompt

        data = pd.read_csv(f"../Data/{config}")
        # story_index,story,question,answer,short_answer,belief,question_type,qa_prompt,comp_prompt,mc_prompt,fb_prompt,tf_prompt,tfr_prompt
        for index, row in tqdm(data.iterrows(), total=len(data), desc=f"{config}"):
            story_index = row["story_index"]
            question_type = row["question_type"]
            story = row["mc_prompt"]

            short_answer = row["short_answer"]
            # 处理字符串
            short_answer = short_answer.strip().rstrip(".")

            mc_prompt = story
            choices = re.findall(r'([A-Z])\. (.+)', mc_prompt)
            choices_dict = {key: value for key, value in choices}
            answer = None
            for key, value in choices_dict.items():
                if value == short_answer:
                    answer = key
                    break

            mc_prompt = re.sub(r"^Choose the correct answer from A or B for the following question:\nQuestion:\n", "", mc_prompt)
            mc_prompt = re.sub(r'[A-Z]\. .*(\n|$)|Answer:.*', '', mc_prompt, flags=re.DOTALL)
            mc_prompt = re.sub(r'\n+', '\n', mc_prompt).strip()

            if answer == None:
                print("answer can't be none!")
                exit(0)

            output_folder = os.path.join(root_folder, f"{config}", f"{story_index}")
            os.makedirs(output_folder, exist_ok=True)
            output_fn = os.path.join(output_folder, f"{question_type}.json")

            results = []

            for j in range(args.try_times):
                reverse_mapping, user_prompt = format_prompt(mc_prompt, choices_dict)
                d = {"story_index": story_index, "question_type": question_type, "story": story, "short_answer": short_answer, "answer": answer,
                     "system_input": system_prompt} if j == 0 else {}

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
                chat = client.chat.completions.create(
                    model='Qwen/Qwen2.5-72B-Instruct',
                    messages=messages
                )
                outputs = chat.choices[0].message.content

                d["user_input"] = user_prompt
                d["output"] = outputs
                d["map"] = reverse_mapping
                results.append(d)

            with open(output_fn, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
