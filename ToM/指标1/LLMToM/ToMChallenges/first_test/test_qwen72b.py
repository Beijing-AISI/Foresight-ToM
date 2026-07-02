import argparse
import time

import importlib
import json
import os
import random
import re

import sys
from tqdm import tqdm
import string
import pandas as pd
from openai import OpenAI

import gen_question_prompt

client = OpenAI(
    api_key='token-casia-braincog-233',
    base_url='http://210.75.240.144:3006/v1',
)


def gen_random_tasks(story):
    system_prompt = gen_question_prompt.SystemPrompt
    user_prompt = gen_question_prompt.UserPrompt
    format_args = {"Story": story}
    user_prompt = user_prompt.format(**format_args)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    chat = client.chat.completions.create(
        model='Qwen/Qwen2.5-72B-Instruct',
        messages=messages
    )
    outputs = chat.choices[0].message.content

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
    parser.add_argument("--try_times", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--story_related", action="store_true")
    parser.add_argument("--task_num", type=int, default=3)

    args = parser.parse_args()

    random.seed(args.seed)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    root_folder = os.path.join(args.output_path, args.output_folder, f"answers-{timestamp}")
    os.makedirs(root_folder, exist_ok=True)

    configs = ['Smarties_prompt.csv', 'Sally-Anne_prompt.csv']

    for config in configs:
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
                    random_tasks = gen_random_tasks(story=story)
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

                    chat = client.chat.completions.create(
                        model='Qwen/Qwen2.5-72B-Instruct',
                        messages=messages
                    )
                    outputs = chat.choices[0].message.content

                    # outputs = re.sub(r"assistant\n*", "", outputs)

                    conversation_history.append({"role": "user", "content": user_prompt})
                    conversation_history.append({"role": "assistant", "content": outputs})

                    if task_counter == other_task_num:
                        d["user_input"] = user_prompt
                        d["output"] = outputs
                        d["map"] = reverse_mapping
                        d["conversation_history"] = conversation_history
                        results.append(d)

            with open(output_fn, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
