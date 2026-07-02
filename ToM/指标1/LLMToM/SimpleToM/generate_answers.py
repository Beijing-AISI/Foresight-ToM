import argparse
from concurrent.futures import ProcessPoolExecutor
import importlib
import json
import os
import random
import shutil
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
from datasets import load_dataset
import string

# 动态加载 prompts 文件
def load_prompt_module(prompts_path):
    spec = importlib.util.spec_from_file_location("load_prompts", prompts_path)
    load_prompts = importlib.util.module_from_spec(spec)
    sys.modules["load_prompts"] = load_prompts
    spec.loader.exec_module(load_prompts)

    prompts_data = {key: getattr(load_prompts, key) for key in dir(load_prompts) if not key.startswith("__")}

    with open("./prompts.json", "w", encoding="utf-8") as json_file:
        json.dump(prompts_data, json_file, ensure_ascii=False, indent=4)
    return load_prompts

def format_prompt(story, question, choices):

    choice_dict = {label: text for label, text in zip(choices["label"], choices["text"])}

    available_letters = list(string.ascii_uppercase)
    random.shuffle(available_letters)

    # 将 choice_dict 的键映射到随机字母
    mapping = {key: available_letters.pop(0) for key in choice_dict.keys()}
    reverse_mapping = {value: key for key, value in mapping.items()}  # 创建反向映射

    randomized_choice_dict = {mapping[key]: value for key, value in choice_dict.items()}
    sorted_items = sorted(randomized_choice_dict.items()) 
    keys, values = zip(*sorted_items)  # 提取排序后的键和值

    # 动态生成格式化参数
    format_args = {
        'Story': story,
        'Question': question,
    }
    format_args.update({f'{chr(97 + i)}': keys[i] for i in range(len(keys))})
    format_args.update({f'choice_{chr(97 + i)}': values[i] for i in range(len(values))})

    prompt = load_prompts.UserEvaluatePrompt.format(**format_args)

    return reverse_mapping, prompt

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--output_path", type=str, default="") 
    parser.add_argument("--output_folder", type=str, default="", help="Folder to save the output file") 
    parser.add_argument("--prompts_path", type=str, default="prompts/prompts.py", help="Path to the prompts file") 
    parser.add_argument("--model_name", type=str, default="THUDM/chatglm3-6b") 
    parser.add_argument("--use_local", action="store_true", help="Use locally downloaded model") 
    parser.add_argument("--local_model_path", type=str, default="", help="Path to local model files") 
    parser.add_argument("--try_times", type=int, default=5) 
    parser.add_argument("--seed", type=int, default=42) 
    parser.add_argument("--token_size", type=int, default=4096, help="Maximum token size (default: 4096)") 
    parser.add_argument("--device_map", type=str, default="auto", help="Device map for model loading, e.g., 'auto', 'cuda:0', etc.")
    args = parser.parse_args()

    random.seed(args.seed)

    root_folder = os.path.join(args.output_path, args.output_folder, "answers")

    if os.path.exists(root_folder):
        print(f"Warning: You are about to clear the output folder: {root_folder}")
        confirm = (input("Type 'y' to confirm or anything else to cancel: ").strip().lower())
        if confirm == "y":
            print(f"Clearing output folder: {root_folder}")
            shutil.rmtree(root_folder)  # 删除整个文件夹及其内容
            os.makedirs(root_folder, exist_ok=True)  # 重新创建文件夹
        else:
            print("Operation cancelled. Folder was not cleared.")
            exit(1)  # 退出程序，避免后续操作
    else:
        os.makedirs(root_folder, exist_ok=True)  # 重新创建文件夹

    # Load the model and tokenizer
    if args.use_local:
        if not args.local_model_path:
            raise ValueError("When using --use_local, --local_model_path must be specified")
        print(f"Loading local model from: {args.local_model_path}")
        tokenizer = AutoTokenizer.from_pretrained(args.local_model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(args.local_model_path,trust_remote_code=True,device_map=args.device_map,torch_dtype=torch.float16)
    else:
        print(f"Downloading model from Hugging Face Hub: {args.model_name}")
        tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(args.local_model_path,trust_remote_code=True,device_map=args.device_map,torch_dtype=torch.float16)

    # 加载指定的 prompts 文件
    load_prompts = load_prompt_module(args.prompts_path)
    system_prompt = load_prompts.SystemEvaluatePrompt
    user_prompt = load_prompts.UserEvaluatePrompt

    gen_kwargs = {
        "max_length": args.token_size,  # 限制生成长度
        "do_sample": False,  # 禁用采样
        "repetition_penalty": 1.1,  # 轻微重复惩罚
    }

    configs = ['mental-state-qa', 'behavior-qa', 'judgment-qa']
    
    for config in configs:
        dataset = load_dataset("allenai/SimpleToM", config)
        for data in tqdm(dataset['test'], total=len(dataset['test']), desc=f"Processing {config}"):

            id = data['id']
            story = data['story']
            question = data['question']
            scenario_name = data['scenario_name']
            choices = data['choices']
            answer = data['answerKey']

            output_folder = os.path.join(root_folder, scenario_name, id[:id.rfind('_')])
            os.makedirs(output_folder, exist_ok=True)
            output_fn = os.path.join(output_folder, f"{id[id.rfind('_')+1:]}.jsonl")

            
            results = []

            for j in range(args.try_times):
                
                reverse_mapping, user_prompt = format_prompt(story, question, choices)
                d = {"id": id, "scenario_name": scenario_name, "story": story, "question": question, "choices": choices, "answer": answer, "system_input": system_prompt} if j == 0 else {}
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
                inputs = tokenizer.apply_chat_template(
                    messages, return_tensors="pt", tokenize=True, return_dict=True
                )
                inputs = inputs.to(model.device)
                outputs = model.generate(**inputs, **gen_kwargs)
                d["token_size"] = outputs.shape[1]
                d["user_input"] = user_prompt
                outputs = outputs[:, inputs["input_ids"].shape[1] :]
                outputs = tokenizer.decode(outputs[0], skip_special_tokens=True)
                d["output"] = outputs
                d["map"] = reverse_mapping
                results.append(d)
            
            with open(output_fn, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)

