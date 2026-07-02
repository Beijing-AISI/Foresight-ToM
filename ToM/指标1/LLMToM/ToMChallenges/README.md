# ToMChallenges - Theory of Mind Challenge Experiments

This folder contains the main experiments evaluating LLMs' Theory of Mind capabilities using classic false belief tasks.

---

## 📁 Folder Structure

```
ToMChallenges/
├── first_test/                  # Primary experiment runs
│   ├── Llama-3.1-8B-Instruct-RanTask/
│   ├── Qwen2.5-72B-Instruct-RanTask/
│   ├── Qwen2.5-7B-Instruct-RanTask/
│   ├── Qwen2.5-7B-Instruct-StoryTask/
│   ├── results/                 # Pre-computed & ablation results
│   └── result_history/          # Recent experiment runs
│
├── prompts.py                   # Evaluation system prompts
├── generate_answers.py          # Main inference script
├── test.py                      # CSV processing utility
├── plot.py                      # Visualization code
└── generate_answers.py          # Alternative generation script
```

---

## 🎯 First Test - Experiment Overview

### Models Evaluated

| Model | Size | Architecture | Task Type |
|-------|------|--------------|-----------|
| Llama-3.1-8B-Instruct | 8B | Meta Llama | RAN Task |
| Qwen2.5-72B-Instruct | 72B | Alibaba Qwen | RAN Task |
| Qwen2.5-7B-Instruct | 7B | Alibaba Qwen | RAN Task & Story Task |

### Task Types Explained

#### 1. **RAN Task** (Reasoning/Awareness Task)
Tests basic false belief reasoning:
- **Sally-Anne prompts**: Classic basket-box transfer scenario
- **Smarties prompts**: Box content belief induction
- **1st/2nd person perspectives**: Evaluates different framing approaches

#### 2. **Story Task**
More narrative-based scenarios with extended context

---

## 📂 Inside Each Model Folder

### Example: `Llama-3.1-8B-Instruct-RanTask/`

```
Llama-3.1-8B-Instruct-RanTask/
├── accuracy_results-20250328-163101/   # Timestamped accuracy metrics
│   ├── joint_accuracy.json             # Combined performance
│   ├── standard_accuracy.json          # Standard benchmarks
│   └── step_results.json               # Per-step accuracy
├── answers-20250325-122431/           # First experiment run
│   └── Smarties_prompt.csv/           # Smarties task results
│       ├── 1/                         # Story 1
│       │   ├── 1stA.json              # First person, option A
│       │   ├── 1stB.json              # First person, option B
│       │   ├── 2ndA.json              # Second person, option A
│       │   ├── 2ndB.json              # Second person, option B
│       │   ├── assumption.json        # Model's assumption
│       │   └── reality.json           # Ground truth
│       ├── 2/                         # Story 2 (30+ stories total)
│       │   └── ...                    # Same structure
│       └── ...                        # All story indices
└── answers-20250328-163101/           # Second experiment run
    ├── Sally-Anne_prompt.csv/         # Sally-Anne task results
    └── Smarties_prompt.csv/           # Smarties task results
```

### Result File Structure

Each story folder (e.g., `1/`, `2/`, etc.) contains JSON files with:

```json
{
  "story_index": "1",
  "question_type": "Smarties",
  "story": "Child sees Smarties in a box...",
  "short_answer": "Smarties",
  "answer": "A",
  "system_input": "System prompt text",
  "user_input": "User question",
  "output": "Model's full response",
  "token_size": 1024,
  "map": {"A": "Smarties", "B": "Pencils"}
}
```

---

## 🔬 Understanding the Experiments

### Smarties Task Flow

1. **Setup**: Child told Smarties box contains pencils
2. **Question**: "What do you think is in the box?"
3. **Follow-up**: "Where did you get Smarties?"
4. **Evaluate**: Does model correctly identify the false belief?

### Sally-Anne Task Flow

1. **Setup**: Sally puts doll in basket, leaves room
2. **Action**: Anne moves doll to box
3. **Question**: "Where will Sally look for her doll?"
4. **Evaluate**: Does model understand Sally's false belief?

---

## 📊 Results Directories Explained

### `accuracy_results-*/*`

Contains computed metrics for each model:

- **`joint_accuracy.json`**: Overall accuracy across all challenges
- **`standard_accuracy.json`**: Standard benchmark scores
- **`step_results.json`**: Per-reasoning-step breakdown

### `answers-*/*`

Contains raw model responses organized by:

- **Challenge type**: Smarties vs Sally-Anne
- **Story index**: Individual scenario results
- **Perspective**: 1st person vs 2nd person framing

---

## 📈 Visualization Outputs

Located in `first_test/`:

- **`plot2.png`**: Model comparison visualization
- **plot3.png**: Task difficulty analysis
- **`plot.py`**: Python script for generating plots

---

## 🗂️ results/ Directory

### `results/ablation/`
Ablation studies showing:
- Effect of different prompt formulations
- Impact of token limits
- Performance with different temperature settings

### `results/compare/`
Comparative analyses between:
- Different model architectures (Llama vs Qwen)
- Different model sizes (7B vs 72B)
- Reasoning step effects

### `results/results_pre/`
Pre-computed baseline results for:
- Standard benchmarks
- Reference models
- Historical comparisons

---

## 🗂️ result_history/ Directory

Contains recent experiment runs:

```
result_history/
├── Llama-3.1-8B-Instruct/
├── Llama-3.1-8B-Instruct-GenTaskPrompt/
├── Qwen2.5-7B-Instruct/
└── testMultiTask/
```

These represent:
- **GenTaskPrompt**: Generalized task prompting experiments
- **MultiTask**: Combined task evaluations
- **StoryTask variants**: Different story complexity levels

---

## 📝 Key Files

### `prompts.py`

```python
SystemEvaluatePrompt = """
[Story]
The bag of potato chips has moldy chips in it. Mary picks up the bag in the supermarket and walks to the cashier.

[Candidate Answers]
A. Reasonable
B. Not reasonable

[Question]
Next, Mary "pay for the chips" and not "report the moldy chips". The behavior of Mary can be best described as:

[Output]
Step1-Is Mary likely to be aware that "The bag of potato chips has moldy chips in it."?:
    There is no explicit mention in the story that Mary notices the moldy chips...
Step2-What will Mary likely do next?:
    Since Mary is unaware of the moldy chips...
Step3-Next, Mary "pay for the chips"... The behavior of Mary can be best described as:
    Given that Mary is unaware of the mold, her action... So, her behaviour is Reasonable.
So the answer is [A].
"""
```

**Purpose**: Few-shot example showing the expected reasoning format.

### `generate_answers.py`

Main inference script that:
1. Loads model from HuggingFace or local path
2. Reads CSV data with ToM challenges
3. Applies system prompts
4. Generates responses (multiple attempts per challenge)
5. Saves results to timestamped folders

### `test.py`

CSV extraction utility for preprocessing challenge data.

### `plot.py`

Visualization script that:
1. Loads JSON results from model folders
2. Computes accuracy metrics
3. Generates comparison plots
4. Saves PNG visualizations

---

## 🧪 Running Experiments

### Basic Command

```bash
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

### Using Qwen Models

```bash
python generate_answers.py \
    --output_path ./qwen_results \
    --promptsA_path first_test/Qwen2.5-7B-Instruct/promptsN.py \
    --use_local \
    --local_model_path ./downloads/qwen2.5-7b
```

---

## 📊 Understanding Accuracy Metrics

### `joint_accuracy.json` Structure

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

### Key Metrics

- **Sally-Anne accuracy**: Classic false belief task performance
- **Smarties accuracy**: False belief induction task
- **Overall accuracy**: Combined performance
- **Step accuracy**: Breakdown by reasoning step

---

## 🎯 Task Comparison

| Task | What It Tests | Typical Accuracy |
|------|---------------|------------------|
| Sally-Anne | False belief understanding | ~75-85% |
| Smarties | Belief induction | ~65-75% |
| Story Task | Complex narratives | Varies by model |

---

## 📝 Notes

- **Timestamped folders**: Each run creates a new folder with timestamp (e.g., `answers-20250328-163101`)
- **Multiple attempts**: Script tries `try_times` (default 5) per challenge
- **Perspective analysis**: 1st vs 2nd person framing can yield different results
- **Model comparison**: Compare `Llama-3.1-8B` vs `Qwen2.5-72B` for size scaling effects

---

*This directory contains comprehensive experiments on Theory of Mind capabilities across multiple LLM architectures and sizes.*
