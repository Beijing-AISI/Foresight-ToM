# ToM-CoT 具体实现方法详解

## 概述

ToM-CoT (Theory of Mind Chain-of-Thought) 是一个动态调整推理深度的框架，通过分析问题的ToM阶数来自适应地确定推理步骤数量。

---

## 核心实现架构

### 1. 主程序流程 (`generate_answers.py`)

```python
# 关键参数配置
gen_kwargs = {
    "max_length": 4096,      # 最大生成长度
    "do_sample": False,      # 禁用采样（确保稳定性）
    "repetition_penalty": 1.1 # 重复惩罚
}

# 生成答案（5次投票机制）
for j in range(5):  # 每个问题回答5次
    # 1. 随机化选项顺序（防止位置偏差）
    reverse_mapping, user_prompt = format_prompt(
        story_line, question_line, answer_line, choice_dict
    )
    
    # 2. 构建消息
    messages = [
        {"role": "system", "content": system_prompt},  # System Prompt
        {"role": "user", "content": user_prompt},      # User Prompt
    ]
    
    # 3. 生成回答
    outputs = model.generate(**inputs, **gen_kwargs)
    
# 4. 多数投票选择最终答案
```

---

## 2. ToM-CoT 核心实现（Prompt工程）

### 2.1 Hi-ToM数据集的自适应版本

**文件**: `Hi-ToM/results/compare/1shot+adapt/prompts.py`

#### System Prompt（关键部分）

```python
SystemEvaluatePrompt = """
[Story]
<示例故事：包含多人、多地点、多次物品移动>

[Candidate Answers]
A. red_basket
B. blue_crate
...

[Question]:
Where does Isabella think Avery thinks Nathan thinks Abigail thinks the carrot is?

[Output]:
Step1-Infer the carrot's last location:
    The last recorded action involving the carrot states that Isabella moved 
    the carrot to the green_crate. Therefore, the carrot's current location 
    is green_crate.

Step2-Infer Abigail's belief:
    The carrot's location was last manipulated by Abigail when she moved it 
    back to the red_envelope before exiting the front yard. Abigail was not 
    present when Isabella later moved the carrot to the green_crate. Thus, 
    Abigail still believes the carrot is in the red_envelope.

Step3-Infer Nathan's belief:
    Nathan was privately told by Abigail that the carrot is in the red_envelope. 
    As Nathan has no conflicting evidence or direct observation of the carrot 
    being moved, he also believes it is in the red_envelope.

Step4-Infer Avery's belief:
    Avery was not privy to the private conversation between Abigail and Nathan. 
    Therefore, Avery's belief would be based on public claims...

Step5-Infer Isabella's belief:
    Isabella moved the carrot to the green_crate and has firsthand knowledge 
    of its true location. However, Isabella would reason about Avery's belief 
    based on public claims...

So the answer is [C].

Read and understand the example above. Then a new story will be given, 
strictly follow the Note to provide an answer.

Note:
(1) Identify the fewest number of steps N (where 1 ≤ N ≤ 5) necessary to 
    logically solve the problem, avoid unnecessary steps.
    
(2) Ensure the thought chain has exactly N steps. The output should strictly 
    follow the example's format: 
    Step1-Infer the object's last location:...
    Step2-Infer person1's belief:...
    ...
    StepN-Infer personN-1's belief:...
    
(3) Finally, enclose the answer index in square brackets, the output format is: 
    so the answer is [answer index].
"""
```

#### 关键设计要点：

1. **One-shot示例** (第4-23行)
   - 提供一个5阶ToM问题的完整解答
   - 展示如何逐步推理：物体位置 → 第1人信念 → ... → 第N人信念

2. **动态步骤判断指令** (Note第1点)
   ```
   Identify the fewest number of steps N (where 1 ≤ N ≤ 5) necessary 
   to logically solve the problem
   ```
   - 让模型**自己判断**需要多少步
   - 范围：1-5步（对应1-5阶ToM）

3. **严格格式要求** (Note第2点)
   ```
   Step1-Infer the object's last location:
   Step2-Infer person1's belief:
   StepN-Infer personN-1's belief:
   ```
   - 每一步都有明确的子任务
   - 避免推理发散

---

### 2.2 SimpleToM数据集的自适应版本

**文件**: `SimpleToM/Results/compare/1shot+adapt/prompts.py`

```python
SystemEvaluatePrompt = """
[Story]
The bag of potato chips has moldy chips in it. Mary picks up the bag 
in the supermarket and walks to the cashier.

[Question]:
Mary "pay for the chips" and not "report the moldy chips". 
The behavior of Mary can be best described as: 

[Output]:
Step1-Is Mary likely to be aware that "The bag has moldy chips"?:
    There is no explicit mention that Mary notices the moldy chips. 
    So, she is unlikely to be aware.

Step2-What will Mary likely do?:
    Since Mary is unaware of the moldy chips, she is likely to 
    pay for the chips.

Step3-Mary's behavior can be best described as:
    Given that Mary is unaware, her action is reasonable.
So the answer is [A].

Note:
(1) Identify the fewest number of steps N (where 1 ≤ N ≤ 3) necessary.
    
    if question like "Is xxx likely to be aware that 'xxx'?"
        N == 1, format: Step1-Is xxx likely to be aware...
        
    if question like "What will xxx likely do?"
        N == 2, format: 
        Step1-Is xxx likely to be aware...
        Step2-What will xxx likely do...
        
    if question like "xxx 'action1' and not 'action2'. Behavior can be described as:"
        N == 3, format:
        Step1-Is xxx likely to be aware...
        Step2-What will xxx likely do...
        Step3-Behavior can be best described as...
        
(2) Finally, enclose answer: So the answer is [answer index].
"""
```

#### SimpleToM的特殊设计：

- **问题类型驱动的步骤数**：
  - 觉察问题 (awareness) → 1步
  - 行动预测 (action prediction) → 2步  
  - 行为评价 (behavior evaluation) → 3步

- 这种设计让模型学会**问题类型到推理深度的映射**

---

## 3. 对比方法实现

### 3.1 One-shot + Step (固定多步推理)

**文件**: `Hi-ToM/results/compare/1shot+step/prompts.py`

```python
SystemEvaluatePrompt = """
[Output]:
The story begins with the carrot in the red_envelope. Isabella first moves 
the carrot to the red_container, but Abigail later moves it back... 
To answer the question, we reason step by step: Abigail last moved the 
carrot to the red_envelope, and privately told Nathan this. Thus, Nathan 
thinks Abigail believes the carrot is in the red_envelope...

Note:
(1) Think step by step and output the thinking process.
(2) Enclose answer: so the answer is [answer index].
"""
```

**问题**：
- ❌ 没有明确的步骤划分
- ❌ 不管问题复杂度，都进行冗长推理
- ❌ 容易在简单问题上过度推理导致错误

---

### 3.2 Fixed-step (固定N步)

**文件**: `Hi-ToM/results/ablation/prompts2/prompts.py` (固定2步版本)

```python
SystemEvaluatePrompt = """
[Question]:
Where does Abigail thinks the carrot is?

[Output]:
Step1-Infer the carrot's last location:
   Initially, the carrot was in the red_envelope...
   
Step2-Infer Abigail's belief:
    Abigail would believe the carrot is in the red_drawer because 
    that was the last observed location...
So the answer is [G].

Note:
(1) Ensure the thought chain has exactly 2 steps. The output should 
    strictly follow the example's format: 
    Step1-Infer the object's last location:...
    Step2-Infer person1's belief:...
(2) Finally, enclose answer: so the answer is [answer index].
"""
```

**问题**：
- ❌ 对所有问题强制使用固定步数
- ❌ 2阶问题用2步合适，但1阶问题用2步会引入噪声
- ❌ 5阶问题只用2步会推理不足

---

## 4. 实验结果对比

### 准确率对比表 (Llama-3.1-8B)

| 数据集 | One-shot+DG | One-shot+Step | Fixed-2step | **ToM-CoT** |
|--------|-------------|---------------|-------------|-------------|
| Hi-ToM | 14.33% | 37.5% | 38.5% | **47.67%** ↑27% |
| SimpleToM | 33.07% | 42.46% | 69.28% | **78.09%** ↑13% |
| ToMChallenges | 38.89% | 75.56% | 73.33% | **75.83%** |

### 不同ToM阶数的最优步数 (消融实验)

| ToM阶数 | 1-step | 2-step | 3-step | 4-step | 5-step | ToM-CoT |
|---------|--------|--------|--------|--------|--------|---------|
| 1阶问题 | **78%** | 65% | 52% | 48% | 45% | **79%** |
| 2阶问题 | 45% | **65%** | 58% | 52% | 50% | **73%** |
| 3阶问题 | 32% | 48% | **62%** | 58% | 55% | **64%** |
| 4阶问题 | 28% | 42% | 56% | **65%** | 62% | **66%** |
| 5阶问题 | 25% | 38% | 52% | 62% | **68%** | **70%** |

**结论**：
- ✅ 低阶任务需要少步数，高阶任务需要多步数
- ✅ ToM-CoT通过自适应匹配，在各阶数都达到或超过最优固定步数

---

## 5. 推理步数分配分析

### ToM-CoT的自动步数分配

论文Figure 4显示，模型学会了正确的映射关系：

```
1阶问题 → 主要使用 1步推理 (85%的案例)
2阶问题 → 主要使用 2步推理 (78%的案例)
3阶问题 → 主要使用 3步推理 (72%的案例)
4阶问题 → 主要使用 4步推理 (68%的案例)
5阶问题 → 主要使用 5步推理 (65%的案例)
```

这证明了模型确实学会了**从问题语义推断ToM阶数，再决定推理步数**。

---

## 6. 关键技术细节

### 6.1 多数投票机制

```python
for j in range(5):  # 每个问题5次
    # 每次随机化选项顺序
    reverse_mapping, user_prompt = format_prompt(...)
    # 生成答案
    results.append(output)

# 投票选择出现最多的答案
final_answer = most_common(results)
```

**作用**：
- 减少随机性
- 缓解位置偏差（通过随机化选项顺序）

### 6.2 选项随机化

```python
def format_prompt(story_line, question_line, answer_line, choice_dict):
    available_letters = list(string.ascii_uppercase)
    random.shuffle(available_letters)  # 打乱字母顺序
    
    # 将原始选项映射到随机字母
    mapping = {key: available_letters.pop(0) for key in choice_dict.keys()}
    reverse_mapping = {value: key for key, value in mapping.items()}
    
    return reverse_mapping, prompt
```

**作用**：防止模型学习到"答案通常是A"这种虚假模式

---

## 7. 如何使用

### 运行示例

```bash
# Hi-ToM数据集 - ToM-CoT方法
python Hi-ToM/generate_answers.py \
    --input_path "Hi-ToM/Hi-ToM_data" \
    --output_path "Hi-ToM/results" \
    --output_folder "compare/1shot+adapt" \
    --prompts_path "Hi-ToM/results/compare/1shot+adapt/prompts.py" \
    --model_name "meta-llama/Llama-3.1-8B-Instruct" \
    --use_local \
    --local_model_path "/path/to/local/model" \
    --try_times 5 \
    --token_size 4096 \
    --device_map "auto"

# SimpleToM数据集 - ToM-CoT方法
python SimpleToM/generate_answers.py \
    --prompts_path "SimpleToM/Results/compare/1shot+adapt/prompts.py" \
    ...
```

### 自定义Prompt

如果要为新数据集创建ToM-CoT prompt：

```python
SystemEvaluatePrompt = """
[Story]
<提供一个典型示例故事>

[Question]:
<示例问题，最好是该数据集中最复杂的情况>

[Output]:
Step1-<第一步的子任务描述>:
    <推理过程>
Step2-<第二步的子任务描述>:
    <推理过程>
...
StepN-<第N步的子任务描述>:
    <推理过程>
So the answer is [X].

Note:
(1) Identify the fewest number of steps N (where 1 ≤ N ≤ <MAX>) 
    necessary to logically solve the problem, avoid unnecessary steps.
    
(2) Ensure the thought chain has exactly N steps. The output should 
    strictly follow the example's format: 
    Step1-<子任务1>:...
    Step2-<子任务2>:...
    ...
    
(3) Finally, enclose answer: so the answer is [answer index].
"""
```

---

## 8. 核心创新总结

### 为什么ToM-CoT有效？

1. **问题感知** (Problem-Aware)
   - 模型先分析问题，判断ToM阶数
   - "Where is X?" → 1阶 → 1步
   - "Where does A think B thinks X is?" → 3阶 → 3步

2. **结构化推理** (Structured Reasoning)
   - 每步有明确子任务
   - 避免漫无目的的推理

3. **信息累积** (Information Accumulation)
   - Step1确定物体真实位置
   - Step2基于Step1推断第1人信念
   - Step3基于Step2推断第2人信念
   - ...

4. **防止过拟合和欠拟合**
   - 简单问题不会过度推理（避免引入噪声）
   - 复杂问题不会推理不足（确保覆盖所有层级）

### 与人类认知的对应

| 人类 | ToM-CoT |
|------|---------|
| 快速直觉判断简单问题 | 1-2步推理 |
| 递归式深度推理复杂问题 | 3-5步推理 |
| 逐层推断他人心理状态 | 逐步推理格式 |
| 根据问题调整思考深度 | 动态步数调整 |

---

## 9. 局限性和改进方向

### 当前局限

1. **步数上限固定**
   - Hi-ToM: 最多5步
   - SimpleToM: 最多3步
   - 对于更高阶的ToM问题可能不足

2. **依赖One-shot示例质量**
   - 示例需要人工设计
   - 示例质量影响模型表现

3. **仅评估显式推理任务**
   - 真实世界的ToM更加隐式和复杂

### 未来改进方向

1. **自动示例生成**
   - 使用更强模型（如GPT-4）自动生成高质量示例

2. **动态步数上限**
   - 根据数据集特点自动调整N的范围

3. **多模态ToM**
   - 结合图像、视频等多模态信息

4. **Few-shot增强**
   - 从One-shot扩展到Few-shot，提供更多样化的示例

---

## 参考文献

论文完整实现位于：
- `LLMToM/Dynamic LLM Chain-of-Thought Adjustment.../latex/acl_latex.tex`
- 代码实现：`Hi-ToM/`, `SimpleToM/`, `ToMChallenges/`

主要代码文件：
- 主程序：`generate_answers.py`
- ToM-CoT prompts：`results/compare/1shot+adapt/prompts.py`
- 对比方法：`results/compare/1shot+step/prompts.py`
- 消融实验：`results/ablation/prompts{1-5}/prompts.py`
