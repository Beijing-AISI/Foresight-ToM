# ToM 项目完整说明：大型语言模型的心智理论挑战

## 🎯 本项目要实现的目标

### 科学目标
本项目评估**大型语言模型 (LLM) 的心智理论 (Theory of Mind, ToM) 能力**——具体测试它们是否能够真正理解他人的心理状态（信念、知识、意图），还是仅仅在进行模式匹配。

### 什么是心智理论 (ToM)
- 人类天生就能理解虚假信念：*"Sarah 把玩具放在盒子里，然后我把它移走了 - Sarah 认为玩具在哪里？"*
- 关键问题：**LLM 是否真的理解这些心理状态，还是只是在根据模式猜测？**

---

## 🧪 实验范式 (实验如何运作)

### 逐步流程

```
┌─────────────────────────────────────────────────────────────┐
│                      实验流程图                                │
└─────────────────────────────────────────────────────────────┘

1. [数据加载]
   ├── 读取 CSV 文件中的 ToM 挑战故事
   ├── 每行 = 一个挑战场景
   └── 示例：*"Neila 发现一个标签写着'盘子'的袋子，但里面是'背心'"*

2. [提示格式化]
   ├── 加载带少样本示例的系统提示
   ├── 格式化用户提示
   └── 添加多个选择选项 (A, B)

3. [模型生成]
   ├── 将格式化后的提示发送给 LLM
   ├── 模型尝试回答问题
   └── 重复 try_times 次 (默认 5 次) 以提高可靠性

4. [响应评估]
   ├── 提取模型的回答
   ├── 与标准答案比较
   ├── 计算准确率
   └── 将结果保存到 JSON

5. [结果分析]
   ├── 计算所有挑战的综合准确率
   ├── 分析每步推理
   └── 生成可视化图表
```

---

## 📊 两种主要挑战类型详解

### 1. Smarties 任务 (虚假信念诱导)

#### 故事结构
```
人物 A 发现一个容器
- 标签写着：物品 X (应该是什么)
- 打开容器，发现：物品 Y (实际上是什么)
- 人物 A 关上容器，不告诉任何人
人物 B 进入房间看到容器
问题：人物 B 认为容器里是什么？
```

#### 示例故事
```
故事：*"Neila 在阁楼发现一个袋子。袋子标签上写着'plate'(盘子)。
        Neila 没看到里面是什么。Neila 打开袋子发现是'vest'(背心)。
        袋子里没有 plate。Neila 关上袋子放回原处。
        Juanita 进入阁楼看到袋子。*"

问题：*"袋子里应该有什么？*"
选择：
    A. vest (背心) - 实际内容
    B. plate (盘子) - 标签上的内容

正确答案：B (plate)
原因：因为标签说"plate"，所以 Juanita 会认为里面是盘子，
      而不是实际内容 (背心)
```

#### 测试什么
- 模型能否追踪 Juanita 的**错误信念**？
- 模型是否理解信念 ≠ 现实？
- 模型能否基于可用信息推理另一个人的**应该相信什么**？

---

### 2. Sally-Anne 任务 (虚假信念理解)

#### 故事结构
```
两个角色和两个位置
- 角色 1 把物体放在位置 1
- 角色 1 离开
- 角色 2 把物体移到位置 2
- 问题：角色 1 认为物体在哪里？
```

#### 示例故事
```
故事：*"Neila 和 Juanita 在阁楼玩耍。她们看到一个衣柜和一个橱柜。
        她们在衣柜里发现一条毛巾。Juanita 离开阁楼。
        Neila 把毛巾移到橱柜里。*"

问题：*"毛巾在哪里？*(移动之前)*"
选择：
    A. cabinet (橱柜) - 当前位置
    B. closet (衣柜) - 之前的位置

正确答案：B (closet)
原因：Juanita 离开时毛巾还在衣柜，Neila 移动后 Juanita 仍认为在衣柜
```

#### 测试什么
- 模型能否追踪物体位置变化？
- 模型是否理解 Juanita 对原始位置的**记忆** vs **当前现实**？
- 模型能否从 Juanita 的视角看问题？

---

## 📄 每个代码文件的详细解释

### 1. `prompts.py` - 系统提示模板

#### 它的作用
包含**少样本提示模板**，教导模型如何推理关于心智状态的场景。

#### 关键提示结构

```python
SystemEvaluatePrompt = """
[故事]
故事描述场景...

[问题]
会发生什么 / 人物相信什么？

[候选答案]
A. 选项 1
B. 选项 2

[输出]
Step1-人物 A 是否意识到"X"?:
    分析人物 A 是否注意到关键细节...

Step2-人物 A 接下来可能做什么?:
    基于其知识预测人物 A 的行为...

Step3-这种行为是否合理?:
    评估行为是否与人物 A 的信念状态一致...

所以答案是 [A]。
"""
```

#### 为什么这个格式？
- **逐步推理**：迫使模型思考问题
- **少样本学习**：展示期望的推理格式示例
- **明确格式**：确保输出结构一致
- **意识 → 预测 → 评估**：ToM 推理的逻辑流程

#### 工作原理
```
模型接收：
├── 系统提示 (带示例)
└── 用户提示 (具体挑战 + 问题)

模型生成：
├── 第 1 步分析 (意识检查)
├── 第 2 步预测 (行为预测)
├── 第 3 步评估 (合理性检查)
└── 最终答案 [A] 或 [B]
```

---

### 2. `generate_answers.py` - 主要推理引擎

#### 它的作用
运行整个实验的**引擎**——加载模型、生成响应、保存结果。

#### 代码分解

##### 第 1 部分：导入
```python
import argparse          # 命令行参数
from concurrent.futures import ProcessPoolExecutor  # 并行处理
import importlib         # 动态模块加载
import json, os, re      # 标准工具
import torch             # PyTorch 用于模型
from transformers import AutoTokenizer, AutoModelForCausalLM  # 加载 LLM
from tqdm import tqdm    # 进度条
import pandas as pd      # CSV 处理
```

**目的**：获取模型推理和数据处理所需的所有工具。

##### 第 2 部分：`load_prompt_module(prompts_path)`
```python
def load_prompt_module(prompts_path):
    spec = importlib.util.spec_from_file_location("load_prompts", prompts_path)
    load_prompts = importlib.util.module_from_spec(spec)
    sys.modules["load_prompts"] = load_prompts
    spec.loader.exec_module(load_prompts)

    prompts_data = {key: getattr(load_prompts, key) 
                    for key in dir(load_prompts) 
                    if not key.startswith("__")}

    with open(f"./{prompts_path}.json", "w", encoding="utf-8") as json_file:
        json.dump(prompts_data, json_file, ensure_ascii=False, indent=4)
    return load_prompts
```

**它做什么**：
1. 动态导入 Python 文件 (如 `prompts.py`)
2. 提取所有提示字符串 (SystemEvaluatePrompt, UserEvaluatePrompt)
3. 保存到 JSON 以加快加载速度
4. 返回加载的模块

**为什么动态导入？**
- 允许在不重启 Python 时更改提示
- 避免硬编码提示字符串
- 使实验可复现

##### 第 3 部分：`format_prompt(mc_prompt, choices_dict)`
```python
def format_prompt(mc_prompt, choices_dict):
    available_letters = list(string.ascii_uppercase)
    random.shuffle(available_letters)

    mapping = {key: available_letters.pop(0) for key in choices_dict.keys()}
    reverse_mapping = {value: key for key, value in mapping.items()}

    # 生成带少样本示例的最终提示
    prompt = load_prompts.UserEvaluatePrompt.format(**format_args)

    return reverse_mapping, prompt
```

**它做什么**：
1. 接收故事和问题
2. 随机化多个选择字母 (A, B, C...)
3. 用示例格式化提示
4. 返回格式化提示 + 答案解码映射

**示例**：
```
输入：
    故事：*"Person A 发现了 X..."*
    问题：*"袋子里是什么？"*
    选择：{"A": "vest", "B": "plate"}

输出：
    带随机字母的格式化提示
    映射：{"A": "vest", "B": "plate"}
```

##### 第 4 部分：主执行流程
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_path", ...)      # 保存结果的位置
    parser.add_argument("--promptsA_path", ...)   # 任务 A 的提示文件
    parser.add_argument("--promptsB_path", ...)   # 任务 B 的提示文件
    parser.add_argument("--model_name", ...)      # 使用哪个模型
    parser.add_argument("--use_local", ...)       # 使用本地模型或 HuggingFace
    parser.add_argument("--local_model_path", ...) # 本地模型路径
    parser.add_argument("--try_times", ...)       # 尝试次数
    parser.add_argument("--seed", ...)            # 随机种子以保证可复现性
    parser.add_argument("--token_size", ...)      # 响应长度限制
    args = parser.parse_args()
```

**目的**：解析命令行参数以增加灵活性。

##### 第 5 部分：模型加载
```python
if args.use_local:
    tokenizer = AutoTokenizer.from_pretrained(args.local_model_path, ...)
    model = AutoModelForCausalLM.from_pretrained(args.local_model_path, ...)
else:
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, ...)
    model = AutoModelForCausalLM.from_pretrained(args.local_model_path, ...)
```

**它做什么**：
1. 加载分词器 (将文本转换为数字)
2. 加载模型 (实际的 LLM)
3. 配置设备映射 (GPU/CPU)

**为什么两条路径？**
- `--use_local`：使用下载的模型 (更快)
- 否则：从 HuggingFace 下载

##### 第 6 部分：生成参数
```python
gen_kwargs = {
    "max_length": args.token_size,      # 响应长度限制
    "do_sample": False,                  # 确定性 (无随机性)
    "repetition_penalty": 1.1,          # 轻微重复惩罚
}
```

**目的**：控制生成行为。

##### 第 7 部分：处理循环
```python
for config in configs:  # Smarties, Sally-Anne
    if config == "Sally-Anne":
        prompts_path = args.promptsA_path
    elif config == "Smarties":
        prompts_path = args.promptsB_path
    
    load_prompts = load_prompt_module(prompts_path)
    system_prompt = load_prompts.SystemEvaluatePrompt
    user_prompt = load_prompts.UserEvaluatePrompt
    
    data = pd.read_csv(f"../Data/{config}")
    
    for index, row in tqdm(data.iterrows()):
        story = row["mc_prompt"]
        short_answer = row["short_answer"]
        # 查找正确答案选择
        answer = None
        for key, value in choices_dict.items():
            if value == short_answer:
                answer = key
                break
        
        # 创建输出文件夹
        output_folder = os.path.join(root_folder, f"{config}", f"{story_index}")
        os.makedirs(output_folder, exist_ok=True)
        
        for j in range(args.try_times):
            reverse_mapping, user_prompt = format_prompt(mc_prompt, choices_dict)
            
            # 创建模型消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            
            # 生成响应
            outputs = model.generate(...)
            
            # 保存到 JSON
            with open(output_fn, "w") as f:
                json.dump(results, f)
```

**这个循环做什么**：
1. 对每个挑战类型 (Smarties, Sally-Anne)
2. 加载合适的提示
3. 读取 CSV 数据 (故事 + 问题)
4. 对每个故事：
   - 查找正确答案
   - 格式化提示
   - 生成响应 (多次尝试)
   - 保存结果到 JSON

---

### 3. `test.py` - CSV 预处理工具

#### 它的作用
从完整数据集中提取特定列并创建简化的 CSV 文件。

#### 为什么需要？
原始 CSV 有很多列：
- story_index
- question
- short_answer
- question_type
- mc_prompt (多项选择提示)
- AND 许多其他实验问题类型

这个脚本只保留主实验所需的列。

---

### 4. `plot.py` - 可视化脚本

#### 它的作用
生成显示以下内容的图表：
1. 模型性能比较
2. 不同任务的准确率
3. 缩放效果 (模型大小与准确率)

#### 示例可视化
```python
# 加载所有模型准确率
accuracy_data = []
for model_name in models:
    # 查找准确率文件
    # 加载 joint_accuracy.json
    accuracy_data.append(...)

# 绘图
plt.figure(figsize=(10, 6))
plt.bar(models, accuracies)
plt.title("Model Comparison")
plt.savefig("comparison.png")
```

---

## 📂 结果文件结构详解

### 单个实验运行结构

```
Llama-3.1-8B-Instruct-RanTask/
├── accuracy_results-20250328-163101/
│   ├── joint_accuracy.json      # 所有挑战的综合准确率
│   ├── standard_accuracy.json   # 标准基准分数
│   └── step_results.json        # 每步准确率分解
└── answers-20250328-163101/
    └── Smarties_prompt.csv/
        ├── 1/
        │   ├── 1stA.json        # 第一人称视角，选项 A
        │   ├── 1stB.json        # 第一人称视角，选项 B
        │   ├── 2ndA.json        # 第二人称视角，选项 A
        │   ├── 2ndB.json        # 第二人称视角，选项 B
        │   ├── assumption.json  # 模型的内部信念状态
        │   └── reality.json     # 地面真理
        ├── 2/                   # 故事 2
        ├── 3/                   # 故事 3
        └── ...                  # 共 30 个故事
```

### JSON 文件结构

```json
{
  "story_index": "1",
  "question_type": "Smarties",
  "story": "Neila 在阁楼发现一个袋子。标签上写着 plate...",
  "short_answer": "vest",
  "answer": "A",
  "system_input": "带少样本示例的系统提示",
  "user_input": "带多项选择的用户问题",
  "output": "模型的完整响应文本",
  "token_size": 1236,
  "map": {"A": "Smarties", "B": "Plate"}
}
```

**每个字段解释**：
- `story_index`：哪个故事场景 (1, 2, 3...)
- `question_type`：哪个挑战类型 (Smarties, Sally-Anne)
- `story`：完整挑战故事
- `short_answer`：正确答案 (用于准确率计算)
- `answer`：模型的选择 (A 或 B)
- `system_input`：系统提示文本
- `user_input`：格式化用户问题
- `output`：模型完整响应
- `token_size`：响应中的 token 数
- `map`：字母到答案文本的映射

---

## 🎭 两种挑战类型详解

### Smarties 任务变体

| 变体 | 测试内容 | 示例问题 |
|------|----|----|
| **reality** | 容器里**实际**是什么 | "袋子里有什么？" |
| **assumption** | 容器里**应该**是什么 (基于标签) | "袋子里应该有什么？" |
| **memory** | 人物 A 对容器的**知识** | "Neila 关于袋子知道什么？" |

### Sally-Anne 任务变体

| 变体 | 测试内容 | 示例问题 |
|------|----|----|
| **reality** | 物体的**当前**位置 | "毛巾现在在哪里？" |
| **memory** | 物体的**之前**位置 | "毛巾之前在哪里？" |

---

## 📊 准确率指标详解

### `joint_accuracy.json` 结构

```json
{
  "model": "Llama-3.1-8B-Instruct",
  "sally_anne_accuracy": 0.833,
  "smarties_accuracy": 0.767,
  "overall_accuracy": 0.800,
  "reasoning_steps": {
    "step1_accuracy": 0.950,
    "step2_accuracy": 0.867,
    "step3_accuracy": 0.767
  }
}
```

**指标解释**：
- **Sally-Anne accuracy**：虚假信念任务的性能
- **Smarties accuracy**：信念诱导任务的性能
- **Overall accuracy**：综合性能
- **Step 1 accuracy**：意识检测 (人物是否意识到？)
- **Step 2 accuracy**：行为预测 (他们会做什么？)
- **Step 3 accuracy**：合理性评估 (这种行为是否适当？)

### 性能阈值

| 类别 | Sally-Anne | Smarties | 综合 |
|------|----|----|----|
| **差** | < 60% | < 50% | < 60% |
| **一般** | 60-80% | 50-75% | 60-75% |
| **良好** | 80-90% | 75-85% | 75-85% |
| **优秀** | > 90% | > 85% | > 85% |

---

## 💡 如何解读结果

### 高准确率表明
- 模型正确追踪虚假信念
- 模型区分信念与现实
- 模型理解观点采择

### 低准确率可能表明
- 模型混淆信念与现实
- 模型在多步推理方面挣扎
- 模型过度依赖地面真理
- 模型缺乏真正的 ToM 理解

---

## 🧪 实验变体

### 1. `RanTask` (推理/意识任务)
- 标准虚假信念评估
- 关注基本 ToM 能力
- 测量识别正确信念的准确率

### 2. `StoryTask` (基于故事的任务)
- 更多的叙事复杂性
- 测试更长的推理链
- 评估上下文保留

### 3. `GenTaskPrompt` (通用任务提示)
- 动态提示生成
- 任务自适应框架
- 上下文感知示例

---

## 🔑 本项目回答的关键研究问题

1. **LLM 是否真正理解虚假信念？**
   - 如果准确率高：是的，可能真正理解
   - 如果准确率低：可能是模式匹配，而非真正 ToM

2. **模型规模重要吗？**
   - 比较 7B vs 8B vs 72B 模型
   - 测试缩放效果

3. **架构如何影响 ToM？**
   - Llama vs Qwen 性能
   - 不同训练数据的影响

4. **推理模式是什么？**
   - 第 1 步 (意识) 通常最容易
   - 第 3 步 (评估) 通常最难
   - 错误会通过推理级联

---

## 💡 总结

### 本项目做什么
- 在经典心智理论任务上测试 LLM
- 评估虚假信念理解
- 比较不同的模型架构
- 分析推理模式

### 为什么重要
- 帮助理解 AI 认知能力
- 识别当前 LLM 的局限性
- 为推理任务开发模型提供指导

### 主要结论
这是一个**科学评估**，研究 LLM 是否真的能够推理关于心理状态，而不仅仅是基于模式预测文本。实验使用精心设计的虚假信念场景来探究真正理解和高级模式匹配之间的边界。

---

## 📚 相关文件说明

### 目录说明文件
- `README.md` (主目录) - 项目概述和结构
- `ToMChallenges/README.md` - 实验目录说明
- `ToMChallenges/first_test/README.md` - 主要测试目录
- `ToMChallenges/first_test/results/README.md` - 结果目录
- `ToMChallenges/first_test/result_history/README.md` - 实验历史

### 可视化文件
- `first_test/plot2.png` - 模型比较可视化
- `first_test/plot3.png` - 任务难度分析
- `first_test/plot.py` - 绘图脚本

### 其他文件
- `LLMToM/tom.json` - 模型操纵基准 (服装销售角色扮演实验)

---

*对于每个文件的详细解释，请参阅各子目录中的单独 README 文件*

---

## 🚀 如何运行实验

### 基本运行
```bash
cd /data1/fanjinyu/ToM/LLMToM/ToMChallenges
python generate_answers.py \
    --output_path ./my_results \
    --promptsA_path prompts/prompts.py \
    --promptsB_path prompts/prompts.py \
    --model_name mistralai/Mistral-7B-Instruct-v0.2 \
    --use_local \
    --local_model_path ./models/mistral-7b \
    --try_times 5 \
    --seed 42 \
    --token_size 4096 \
    --device_map auto
```

### 使用本地模型
```bash
python generate_answers.py \
    --output_path ./my_results \
    --use_local \
    --local_model_path ./downloads/llama-3.1-8b \
    --device_map cuda:0
```

### 使用 Qwen 模型
```bash
python generate_answers.py \
    --output_path ./qwen_results \
    --promptsB_path first_test/Qwen2.5-7B-Instruct/promptsN.py \
    --use_local \
    --local_model_path ./downloads/qwen2.5-7b
```

---

*此文档提供了该项目关于 ToM 挑战实验的完整解释，包括实验范式和评估方法论。*
