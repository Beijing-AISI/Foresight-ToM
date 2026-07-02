import pandas as pd
configs = ['Sally-Anne_prompt.csv', 'Smarties_prompt.csv']

for config in configs:
    data = pd.read_csv(f"/mnt/home/liweiyi/LLM/ToMChallenges/Data/{config}")

    columns_to_extract = ["story_index", "question", "short_answer", "question_type", "mc_prompt"]

    new_data = data[columns_to_extract]

    # 保存到新的 CSV 文件
    output_file = f'{config}'
    new_data.to_csv(output_file, index=False)

    print(f"提取的列已保存到 {output_file}")
