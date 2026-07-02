from datasets import load_dataset
import json

# 配置列表
configs = ['mental-state-qa', 'behavior-qa', 'judgment-qa']

unique_scenario_names = set()
unique_id_names = set()
# 遍历每个配置并保存数据集内容到本地文件
for config in configs:
    # 加载每个配置的数据集
    dataset = load_dataset("allenai/SimpleToM", config)

    # 打开一个新的 JSON 文件，使用配置名作为文件名
    with open(f"Data/{config}.json", "w", encoding="utf-8") as file:
        # 创建一个列表，用来存储所有条目的字典
        data_list = []

        # 遍历数据集中的每条数据
        for example in dataset['test']:
            # 获取每条数据的相关字段
            id = example['id']
            story = example['story']
            question = example['question']
            scenario_name = example['scenario_name']
            choices = example['choices']  # 包含 'text' 和 'label'
            answer = example['answerKey']

            unique_scenario_names.add(scenario_name)
            unique_id_names.add(id[:id.rfind('_')])
            
            # 创建字典并添加到列表
            data_dict = {
                "id": id,
                "story": story,
                "question": question,
                "scenario_name": scenario_name,
                "choices": {
                    "text": choices["text"],
                    "label": choices["label"]
                },
                "answerKey": answer
            }
            data_list.append(data_dict)

        # 将整个列表写入文件作为 JSON 格式
        json.dump(data_list, file, ensure_ascii=False, indent=2)

    print(f"{config} 数据集已保存到 Data/{config}.json")

print(f"唯一的 scenario_name : {unique_scenario_names}")
print(f"唯一的 id_name : {unique_id_names}")