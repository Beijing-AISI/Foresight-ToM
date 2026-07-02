import argparse
import time
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


# def format_prompt(mc_prompt, choices_dict):
#     available_letters = list(string.ascii_uppercase)
#     random.shuffle(available_letters)
#
#     # 将 choice_dict 的键映射到随机字母
#     mapping = {key: available_letters.pop(0) for key in choices_dict.keys()}
#     reverse_mapping = {value: key for key, value in mapping.items()}  # 创建反向映射
#
#     randomized_choice_dict = {mapping[key]: value for key, value in choices_dict.items()}
#     sorted_items = sorted(randomized_choice_dict.items())
#     keys, values = zip(*sorted_items)  # 提取排序后的键和值
#
#     # 动态生成格式化参数
#     format_args = {
#         'Story': mc_prompt
#     }
#     format_args.update({f'{chr(97 + i)}': keys[i] for i in range(len(keys))})
#     format_args.update({f'choice_{chr(97 + i)}': values[i] for i in range(len(values))})
#
#     prompt = load_prompts.UserEvaluatePrompt.format(**format_args)
#
#     return reverse_mapping, prompt

def gen_random_tasks(tokenizer, model, story):
    import gen_question_prompt
    system_prompt = gen_question_prompt.SystemPrompt
    user_prompt = gen_question_prompt.UserPrompt
    format_args = {"Story": story}
    user_prompt = user_prompt.format(**format_args)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    inputs = tokenizer.apply_chat_template(messages, return_tensors="pt", tokenize=True, return_dict=True)
    inputs = inputs.to(model.device)

    outputs = model.generate(**inputs, **gen_kwargs)
    outputs = outputs[0, inputs["input_ids"].shape[1]:]
    outputs = tokenizer.decode(outputs, skip_special_tokens=True)
    outputs = re.sub(r"assistant\n*", "", outputs)
    tasks = re.split(r'\n+', outputs)
    return tasks


tasks = [
    "17592+56781=?\n", "28992+99581=?\n",
    "Is 15972 a prime number?\n", "Is 2111159 a prime number?\n",
    "Where is the origin of chocolate?\n", "What could be the possible causes of toothache?\n",
    "Where does the phrase 'to be or not to be' come from?\n", "In which year was the ancient Chinese poet Li Bai born?\n",
]

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--output_path", type=str, default=".")
    parser.add_argument("--output_folder", type=str, default="./thb_test", help="Folder to save the output file")
    # parser.add_argument("--promptsA_path", type=str, default="prompts/prompts.py", help="Path to the prompts file")
    # parser.add_argument("--promptsB_path", type=str, default="prompts/prompts.py", help="Path to the prompts file")
    parser.add_argument("--model_name", type=str, default="THUDM/chatglm3-6b")
    parser.add_argument("--use_local", action="store_true", help="Use locally downloaded model")
    parser.add_argument("--local_model_path", type=str, default="", help="Path to local model files")
    parser.add_argument("--try_times", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--token_size", type=int, default=4096, help="Maximum token size (default: 4096)")
    parser.add_argument("--device_map", type=str, default="auto", help="Device map for model loading, e.g., 'auto', 'cuda:0', etc.")
    parser.add_argument("--story_related", action="store_true")
    parser.add_argument("--task_num", type=int, default=3)

    args = parser.parse_args()

    random.seed(args.seed)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    root_folder = os.path.join(args.output_path, args.output_folder, f"answers-{timestamp}")
    os.makedirs(root_folder, exist_ok=True)

    # Load the model and tokenizer
    if args.use_local:
        if not args.local_model_path:
            raise ValueError("When using --use_local, --local_model_path must be specified")
        print(f"Loading local model from: {args.local_model_path}")
        tokenizer = AutoTokenizer.from_pretrained(args.local_model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(args.local_model_path, trust_remote_code=True, device_map=args.device_map,
                                                     torch_dtype=torch.float16)
    else:
        print(f"Downloading model from Hugging Face Hub: {args.model_name}")
        tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(args.local_model_path, trust_remote_code=True, device_map=args.device_map,
                                                     torch_dtype=torch.float16)

    gen_kwargs = {
        # "max_length": args.token_size,  # 限制生成长度
        "max_new_tokens": args.token_size,
        "do_sample": False,  # 禁用采样
        "repetition_penalty": 1.1,  # 轻微重复惩罚
    }

    configs = ['Sally-Anne_prompt.csv', 'Smarties_prompt.csv', ]
    # configs = ['Sally-Anne_prompt.csv']
    # configs = ['Smarties_prompt.csv']

    for config in configs:

        # if config == "Sally-Anne_prompt.csv":
        #     prompts_path = args.promptsA_path
        # elif config == "Smarties_prompt.csv":
        #     prompts_path = args.promptsB_path
        #
        # # 加载指定的 prompts 文件
        # load_prompts = load_prompt_module(prompts_path)
        # system_prompt = load_prompts.SystemEvaluatePrompt
        # user_prompt = load_prompts.UserEvaluatePrompt

        if config == "Sally-Anne_prompt.csv":
            import testpromptA as testprompt
        elif config == "Smarties_prompt.csv":
            import testpromptB as testprompt

        data = pd.read_csv(f"../Data/{config}")
        # story_index,story,question,answer,short_answer,belief,question_type,qa_prompt,comp_prompt,mc_prompt,fb_prompt,tf_prompt,tfr_prompt
        for index, row in tqdm(data.iterrows(), total=len(data), desc=f"{config}"):
            story_index = row["story_index"]
            question_type = row["question_type"]
            story = row["story"]
            mc_prompt = row["mc_prompt"]

            short_answer = row["short_answer"]
            short_answer = short_answer.strip().rstrip(".")

            choices = re.findall(r'([A-Z])\. (.+)', mc_prompt)
            choices_dict = {key: value for key, value in choices}
            answer = None
            for key, value in choices_dict.items():
                if value == short_answer:
                    answer = key
                    break

            question = re.search(rf"{story} (.+)\n+[A-Z]\. ", mc_prompt).group(1)

            # mc_prompt = re.sub(r"^Choose the correct answer from A or B for the following question:\nQuestion:\n", "", mc_prompt)
            # mc_prompt = re.sub(r'[A-Z]\. .*(\n|$)|Answer:.*', '', mc_prompt, flags=re.DOTALL)
            # mc_prompt = re.sub(r'\n+', '\n', mc_prompt).strip()
            #
            # if answer == None:
            #     print("answer can't be none!")
            #     exit(0)

            output_folder = os.path.join(root_folder, f"{config}", f"{story_index}")
            os.makedirs(output_folder, exist_ok=True)
            output_fn = os.path.join(output_folder, f"{question_type}.json")

            results = []

            for j in range(args.try_times):
                system_prompt = testprompt.SystemPrompt
                first_prompt = testprompt.FirstPrompt
                last_prompt = testprompt.LastPrompt
                conversation_history = []

                if args.story_related:
                    random_tasks = gen_random_tasks(tokenizer=tokenizer, model=model, story=story)
                else:
                    random_tasks = tasks[:]

                random.shuffle(random_tasks)
                format_args = {"Story": story, "Question": random_tasks.pop(0)}
                first_prompt = first_prompt.format(**format_args)

                available_letters = list(string.ascii_uppercase)
                random.shuffle(available_letters)
                mapping = {key: available_letters.pop(0) for key in choices_dict.keys()}
                reverse_mapping = {value: key for key, value in mapping.items()}  # 创建反向映射
                randomized_choice_dict = {mapping[key]: value for key, value in choices_dict.items()}
                sorted_items = sorted(randomized_choice_dict.items())
                keys, values = zip(*sorted_items)

                format_args = {'Question': question}
                format_args.update({f'{chr(97 + i)}': keys[i] for i in range(len(keys))})
                format_args.update({f'choice_{chr(97 + i)}': values[i] for i in range(len(values))})
                last_prompt = last_prompt.format(**format_args)

                d = {"story_index": story_index,
                     "question_type": question_type,
                     "story": story,
                     "short_answer": short_answer,
                     "answer": answer,
                     "system_input": system_prompt}

                other_task_num = args.task_num
                user_prompt = first_prompt
                for task_counter in range(other_task_num + 1):
                    if task_counter != 0:
                        user_prompt = "[Question]\n" + random_tasks.pop(0)
                    if task_counter == other_task_num:
                        user_prompt = last_prompt
                    messages = [{"role": "system", "content": system_prompt}]
                    messages.extend(conversation_history)
                    messages.append({"role": "user", "content": user_prompt})

                    inputs = tokenizer.apply_chat_template(messages, return_tensors="pt", tokenize=True, return_dict=True)
                    inputs = inputs.to(model.device)

                    outputs = model.generate(**inputs, **gen_kwargs)
                    token_size = outputs.shape[1]
                    outputs = outputs[0, inputs["input_ids"].shape[1]:]
                    outputs = tokenizer.decode(outputs, skip_special_tokens=True)
                    outputs = re.sub(r"assistant\n*", "", outputs)

                    if token_size < args.token_size:
                        conversation_history.append({"role": "user", "content": user_prompt})
                        conversation_history.append({"role": "assistant", "content": outputs})
                    else:
                        print("too long")

                    if task_counter == other_task_num:
                        d["token_size"] = token_size
                        d["user_input"] = user_prompt
                        d["output"] = outputs
                        d["map"] = reverse_mapping
                        d["conversation_history"] = conversation_history
                        results.append(d)

            with open(output_fn, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
