# Foresight-ToM

面向心智揣测（Theory of Mind, ToM）的超级对齐监督框架。用于评估和增强大模型在心智揣测任务上的能力。

## 项目结构

```
.
├── ToM/
│   ├── 指标1/LLMToM/          # 三类模型在 3 种 ToM 任务上的基线评测
│   ├── 指标2/first_test/      # 三类模型在干扰任务注入下的 ToM 能力退化
│   └── 指标3/Defense/         # 三类模型的高阶 ToM 攻击与防御
└── LICENSE
```

---

## 指标1：适配主流心智揣测模型（≥ 3 类）

分别通过三种 ToM 任务类型（Hi-ToM / SimpleToM / ToMChallenges）进行基线评测，验证框架对主流 ToM 任务的适配能力。

### 1.1 Hi-ToM（分层 ToM）

评估模型在多步信念推理中的表现，覆盖 Order 0-4（0 阶=事实推理 → 4 阶=四重嵌套信念）。

| 文件 | 作用 |
|------|------|
| `generate_answers.py` | 核心生成脚本：加载模型，按 story 长度（1/2/3）、线索类型（No_Tell/Tell）、Order 生成推理结果 |
| `json_results.py` | 结果统计：计算标准准确率、联合准确率和各步骤分布 |
| `plot_results.py` | 可视化：绘制准确率混淆矩阵及 CoT vs MC 差异矩阵 |
| `results/ablation/prompts1/prompts.py` | Prompt 模板：含 3 步 CoT 推理示例 |

**运行测试：**

```bash
cd Hi-ToM

# 第 1 步：生成答案
python generate_answers.py \
    --input_path INPUT_DIR \
    --output_path OUTPUT_DIR \
    --output_folder <model_name> \
    --prompts_path prompts/prompts.py \
    --use_local \
    --local_model_path /path/to/model \
    --token_size 4096 --seed 42

# 第 2 步：统计结果
python json_results.py --input_path OUTPUT_DIR/<model_name>/answers --output_path OUTPUT_DIR/<model_name>/results

# 第 3 步：绘制图表
python plot_results.py --input_path OUTPUT_DIR/<model_name>/results --output_path OUTPUT_DIR/<model_name>/plots
```

### 1.2 SimpleToM（基础 ToM）

评估模型在 `allenai/SimpleToM` 数据集（信念状态 / 行为推理 / 判断推理 3 个子任务）上的表现。

| 文件 | 作用 |
|------|------|
| `generate_answers.py` | 核心生成脚本：从 HuggingFace 加载 SimpleToM 数据集，按子任务生成推理结果 |
| `json_results.py` | 结果统计：按场景类型聚合，计算标准/联合准确率 |
| `plot_results.py` | 可视化：绘制混淆矩阵 |
| `prompts.py` | Prompt 模板：含最多 3 步推理示例 |

**运行测试：**

```bash
cd SimpleToM

# 第 1 步：生成答案
python generate_answers.py \
    --output_path OUTPUT_DIR --output_folder <model_name> \
    --prompts_path prompts.py \
    --use_local --local_model_path /path/to/model \
    --token_size 4096 --seed 42

# 第 2 步：统计结果
python json_results.py --input_path OUTPUT_DIR/<model_name>/answers --output_path OUTPUT_DIR/<model_name>/results

# 第 3 步：绘制图表
python plot_results.py --input_path OUTPUT_DIR/<model_name>/results --output_path OUTPUT_DIR/<model_name>/plots
```

### 1.3 ToMChallenges（经典挑战）

评估模型在 Sally-Anne（物体位置转移）和 Smarties（错误预期）两个经典 false-belief 范式上的表现。

| 文件 | 作用 |
|------|------|
| `generate_answers.py` | 核心生成脚本：从 CSV 读取 Sally-Anne/Smarties 数据，分别用 promptsA/B 生成推理结果 |
| `json_results.py` | 结果统计：按范式类型和问题顺序（Order 1/2/3）计算准确率 |
| `prompts.py` | Prompt 模板（Sally-Anne）：含 3 步推理示例 |
| `first_test/LLMtest.py` | API 连通性测试：验证 OpenAI API 调用能力 |
| `first_test/promptsA.py` | Sally-Anne 场景 prompt（1 步推理） |
| `first_test/promptsB.py` | Smarties 场景 prompt（1 步推理） |

**运行测试：**

```bash
cd ToMChallenges

# 第 1 步：生成答案
python generate_answers.py \
    --output_path OUTPUT_DIR --output_folder <model_name> \
    --promptsA_path prompts/promptsA.py --promptsB_path prompts/promptsB.py \
    --use_local --local_model_path /path/to/model \
    --token_size 4096 --seed 42

# 第 2 步：统计结果
python json_results.py --input_path OUTPUT_DIR/<model_name>/answers --output_path OUTPUT_DIR/<model_name>/results

# 可选：测试 API 连通性
python first_test/LLMtest.py
```

---

## 指标2：削弱算法（成功率降低 ≥ 30%）

通过在 ToM 问题前注入干扰任务（随机无关任务 / 故事相关任务），测试三类模型在认知负荷下的 ToM 能力退化。

| 文件 | 作用 |
|------|------|
| `test_qwen72b_raw.py` | 无干扰基线测试（纯 ToM） |
| `test_qwen72b.py` | 有干扰测试（支持随机 / 故事相关干扰任务注入） |
| `muti_task_test.py` | 本地模型多任务干扰测试（HuggingFace 加载） |
| `gen_prompt_test.py` | 支持 `--story_related` 模式的测试脚本 |
| `gen_question_prompt.py` | 定义"根据故事生成相关问题"的 prompt（故事相关干扰用） |
| `promptsA.py` / `promptsB.py` | Sally-Anne / Smarties 纯 ToM prompt（无干扰） |
| `promptsM.py` / `promptsN.py` | Sally-Anne / Smarties 带干扰 prompt |
| `testpromptA.py` / `testpromptB.py` | 含干扰任务的 Sally-Anne / Smarties 测试 prompt |
| `eval_Llama-3.1-8B-Instruct.sh` | Shell 脚本：计算准确率结果 |
| `plot.py` | 绘制三类模型在三种条件（Raw/RanTask/StoryTask）下的准确率对比图 |

**运行测试：**

```bash
cd first_test

# 基线测试（无干扰）
python3 test_qwen72b_raw.py --output_path ./output --output_folder <model_name>_raw --try_times 5 --seed 42

# 干扰测试（3 个随机任务）
python3 test_qwen72b.py --output_path ./output --output_folder <model_name>_ran --try_times 5 --seed 42 --task_num 3

# 故事相关干扰
python3 test_qwen72b.py --output_path ./output --output_folder <model_name>_story --try_times 5 --seed 42 --task_num 3 --story_related

# 本地模型测试
python3 muti_task_test.py --output_path ./output --output_folder <model_name> --model_name THUDM/chatglm3-6b --token_size 4096 --seed 42

# 结果评估 & 绘图
bash eval_Llama-3.1-8B-Instruct.sh
python3 plot.py
```

**关键参数：**

| 参数 | 说明 |
|------|------|
| `--output_path` / `--output_folder` | 结果输出目录 |
| `--try_times` | 每条数据重复测试次数（默认 5） |
| `--task_num` | 干扰任务数量（默认 3） |
| `--story_related` | 开启故事相关干扰（由模型自动生成问题） |
| `--model_name` | 模型名称 |
| `--use_local` / `--local_model_path` | 使用本地模型 |
| `--token_size` | 最大生成 token 数（默认 4096） |

---

## 指标3：防护算法（防御成功率提升 ≥ 15%）

包含 ToM 层级评测、高阶 ToM 攻击、以及三种防御策略的完整实验管线。

### 3.1 ToM 层级评测

| 文件 | 作用 |
|------|------|
| `eval_ollama_tom.py` | 评测任意 Ollama 模型的 ToM Level（Order 0-4） |
| `tom_level/measure.py` | ToM Level 计算：连续 Order 准确率 ≥ 50% 推导 Level（0-5） |
| `tom_level/ollama_backend.py` | Ollama HTTP API 封装 |

**运行测试：**

```bash
cd Defense

# 评测任意模型的 ToM 层级
python3 eval_ollama_tom.py --model llama3.1:8b --num_samples 20

# 评测特定配置
python3 eval_ollama_tom.py --model llama3.1:8b --tell No_Tell --prompt CoT --length 1 --orders 0 1 2 --num_samples 5
```

### 3.2 攻击实验

| 文件 | 作用 |
|------|------|
| `tom_attack.py` | 攻击实验主程序：victim 初始回答 → 攻击生成 → victim 重新考虑 |
| `Attack/attack_prompt_generator.py` | 攻击提示词生成 & 防御数据集构建 |

**运行测试：**

```bash
cd Defense

# 单配置攻击（默认 No_Tell/CoT/length_1）
python3 tom_attack.py --num_samples 10

# 批量跑 3 个核心配置
python3 tom_attack.py --essential --num_samples 20

# 批量跑全部 12 种 Hi-ToM 配置
python3 tom_attack.py --all_configs --num_samples 20
```

### 3.3 防御评测

| 文件 | 作用 |
|------|------|
| `tom_defense.py` | 防御评测：基于已有攻击结果，运行三种防御策略 |
| `Defense/main_defense.py` | 12 场景防御策略对比实验（3 种警告级别 × 4 种策略） |
| `Defense/run_experiments.sh` | 实验编排脚本：3 模型 × 12 场景 × 2 论证类型 |
| `Defense/summarize_results.py` | 结果汇总脚本 |

**运行测试：**

```bash
cd Defense

# 评测三种防御策略
python3 tom_defense.py --results Defense/tom_attack_results.json

# 仅评测特定防御
python3 tom_defense.py --defenses consolidation encryption --orders 0 1 2

# 完整 12 场景防御对比实验
cd Defense
bash run_experiments.sh
python3 summarize_results.py
```

**三种防御算法：**

| 防御策略 | 核心思路 |
|------|------|
| **信念巩固 (Consolidation)** | 先列出 3 条支持自己答案的事实，再评估攻击论证 |
| **信念多次验证 (Multi-Validation)** | 对同一攻击重新考虑 3 次，多数投票决定最终答案 |
| **信念加密 (Encryption)** | 先提取结构化信念证书，攻击论证仅与证书比对 |

---

## 考核指标

三个指标的实验均针对 **Llama-3.1-8B · Qwen2.5-7B · Qwen2.5-72B** 三类主流大模型开展：

| 指标 | 目标 | 对应模块 |
|------|------|------|
| 适配主流 ToM 模型类别 | ≥ 3 类 | 指标1/LLMToM/ — 三类模型在 Hi-ToM、SimpleToM、ToMChallenges 上的基线能力 |
| 削弱算法 - 降低 ToM 成功率 | ≥ 30% | 指标2/first_test/ — 三类模型在干扰任务注入下的 ToM 能力退化 |
| 增强算法 - 提升 ToM 阶数 | ≥ 1 阶 | 指标1/LLMToM/ — 三类模型经增强后 ToM 阶数提升 |
| 防护算法 - 防御成功率提升 | ≥ 15% | 指标3/Defense/ — 三类模型在高阶 ToM 攻击下的防御效果 |

---

## 前置条件

- **指标1**：PyTorch + transformers + datasets，模型可通过 `--use_local` 本地加载或 HuggingFace 远程下载
- **指标2**：OpenAI 兼容 API（用于 Qwen2.5-72B 远程调用）或本地 PyTorch 环境
- **指标3**：Ollama 服务运行于 `localhost:11434`，需安装 `llama3.1:8b`、`qwen3.5:latest` 等模型
