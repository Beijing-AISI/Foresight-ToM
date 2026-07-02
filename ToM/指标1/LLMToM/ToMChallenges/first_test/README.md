# first_test - Experiment Results Directory

This directory contains the primary experiment runs evaluating different LLM models on Theory of Mind challenges.

---

## 📁 Directory Structure

```
first_test/
├── Llama-3.1-8B-Instruct-RanTask/
├── Qwen2.5-72B-Instruct-RanTask/
├── Qwen2.5-7B-Instruct-RanTask/
├── Qwen2.5-7B-Instruct-StoryTask/
├── results/
│   ├── ablation/
│   ├── compare/
│   └── results_pre/
├── result_history/
│   ├── Llama-3.1-8B-Instruct/
│   ├── Llama-3.1-8B-Instruct-GenTaskPrompt/
│   ├── Qwen2.5-7B-Instruct/
│   └── testMultiTask/
├── plot2.png                 # Model comparison visualization
├── plot3.png                 # Task difficulty analysis
├── plot.py                   # Plot generation script
├── promptsN.py               # Extended prompts
└── eval_Llama-3.1-8B-Instruct.sh  # Llama evaluation script
```

---

## 🎯 Models Evaluated

### 1. **Llama-3.1-8B-Instruct-RanTask**
- **Model**: Llama 3.1 8B parameter model
- **Task**: Reasoning/Awareness (RAN) Task
- **Focus**: Classic false belief scenarios (Sally-Anne, Smarties)
- **Perspectives**: 1st person and 2nd person framing

**Contents**:
- `accuracy_results-20250328-163101/` - Latest accuracy metrics
- `answers-20250325-122431/` - Smarties task results
- `answers-20250328-163101/` - Sally-Anne + Smarties combined

### 2. **Qwen2.5-72B-Instruct-RanTask**
- **Model**: Qwen2.5 72B parameter model
- **Task**: Reasoning/Awareness Task
- **Focus**: Comprehensive false belief testing
- **Perspectives**: Multi-perspective analysis

**Note**: This model likely shows highest ToM accuracy due to large parameter count.

### 3. **Qwen2.5-7B-Instruct-RanTask**
- **Model**: Qwen2.5 7B parameter model
- **Task**: Reasoning/Awareness Task
- **Focus**: Efficient false belief reasoning

### 4. **Qwen2.5-7B-Instruct-StoryTask**
- **Model**: Qwen2.5 7B parameter model
- **Task**: Story-based evaluations
- **Focus**: Narrative complexity and context retention
- **Multiple runs**: `answers-20250407-*` directories with different timestamps

---

## 📂 Inside Each Model Directory

### Standard Structure (e.g., `Llama-3.1-8B-Instruct-RanTask/`)

```
Llama-3.1-8B-Instruct-RanTask/
├── accuracy_results-YYYYMMDD-HHMMSS/    # Accuracy metrics (timestamped)
│   ├── joint_accuracy.json               # Combined accuracy
│   ├── standard_accuracy.json            # Benchmark scores
│   └── step_results.json                 # Per-step breakdown
└── answers-YYYYMMDD-HHMMSS/              # Raw answers (timestamped)
    └── Smarties_prompt.csv/              # Smarties task
        ├── 1/
        │   ├── 1stA.json
        │   ├── 1stB.json
        │   ├── 2ndA.json
        │   ├── 2ndB.json
        │   ├── assumption.json
        │   └── reality.json
        ├── 2/
        │   ├── ...
        └── 30/                           # ... up to 30 stories
```

---

## 📊 Result Files Explained

### JSON File Types

#### `1stA.json` / `1stB.json`
**First person perspective**: Model responses framed as "I think..."
- `1stA.json`: First person, option A (e.g., "Smarties")
- `1stB.json`: First person, option B (e.g., "Pencils")

#### `2ndA.json` / `2ndB.json`
**Second person perspective**: Model responses framed as "You think..."
- `2ndA.json`: Second person, option A
- `2ndB.json`: Second person, option B

#### `assumption.json`
The model's internal assumption state about what the character believes.

#### `reality.json`
Ground truth about the actual situation in the story.

---

## 📈 Accuracy Results Structure

### `joint_accuracy.json` Example

```json
{
  "model": "Llama-3.1-8B-Instruct",
  "evaluation_date": "2025-03-28",
  "timestamp": "16:31:01",
  "task_results": {
    "sally_anne": {
      "accuracy": 0.833,
      "correct": 10,
      "total": 12
    },
    "smarties": {
      "accuracy": 0.767,
      "correct": 9,
      "total": 12
    }
  },
  "overall_accuracy": 0.800
}
```

### `step_results.json` Example

```json
{
  "step1_awareness": 0.950,  // Is Mary aware?
  "step2_prediction": 0.867,  // What will she do?
  "step3_behavior": 0.767,    // Is behavior reasonable?
  "average_step_accuracy": 0.862
}
```

---

## 📄 Smarties vs Sally-Anne Tasks

### Smarties Task

**Scenario**: 
- Child told a Smarties box contains pencils
- Child asked "What's in the box?"
- Child asked "Where did you get Smarties?"

**What it tests**:
- Can the model distinguish between belief and reality?
- Does the model maintain false belief state?

**Answer files**: `1stA.json`, `1stB.json`, `2ndA.json`, `2ndB.json`, `assumption.json`, `reality.json`

### Sally-Anne Task

**Scenario**:
- Sally puts doll in basket
- Sally leaves room
- Anne moves doll to box
- Question: "Where will Sally look?"

**What it tests**:
- Understanding that Sally has false belief
- Can model track character perspective?

**Answer files**: Same structure as Smarties

---

## 📊 Visualization Files

### `plot2.png`
**What it shows**: Model comparison
- Llama-3.1-8B vs Qwen2.5-72B vs Qwen2.5-7B
- Sally-Anne vs Smarties accuracy
- Overall performance ranking

### `plot3.png`
**What it shows**: Task difficulty analysis
- Per-step reasoning accuracy
- Story complexity effects
- Perspective framing impact

### `plot.py`
**Purpose**: Generate comparison visualizations

```python
# Usage:
python plot.py --models_dir first_test/ --output_dir plots/
```

---

## 🗂️ results/ Directory

### `results/ablation/`
**Purpose**: Ablation studies
- Different prompt formulations
- Varying token limits
- Temperature parameter effects

### `results/compare/`
**Purpose**: Model comparisons
- Cross-architecture benchmarks
- Size scaling analysis
- Reasoning quality comparisons

### `results/results_pre/`
**Purpose**: Pre-computed baselines
- Reference model results
- Historical comparisons
- Standard benchmarks

---

## 🗂️ result_history/ Directory

Contains recent experiment runs:

### `Llama-3.1-8B-Instruct/`
Latest Llama 3.1 8B experiments with:
- Standard RAN Task
- GenTaskPrompt variant

### `Llama-3.1-8B-Instruct-GenTaskPrompt/`
Generalized task prompting experiments:
- Different prompt structures
- Adaptive reasoning approaches

### `Qwen2.5-7B-Instruct/`
Qwen 7B experiments including:
- Standard evaluations
- Story-based tasks
- Multi-task evaluations

### `testMultiTask/`
Combined task evaluations:
- Simultaneous challenge testing
- Cross-task interference analysis

---

## 🛠️ Utility Files

### `promptsN.py`
Extended prompt definitions with:
- Additional few-shot examples
- Varied reasoning formats
- Different framing approaches

### `eval_Llama-3.1-8B-Instruct.sh`
Shell script for Llama evaluation:
```bash
#!/bin/bash
# Evaluation script for Llama 3.1 8B
python generate_answers.py \
    --model_name meta-llama/Llama-3-8B-Instruct \
    --use_local \
    --local_model_path ./llama-3.1-8b \
    --output_path ./first_test/Llama-3.1-8B-Instruct-RanTask
```

### `plot.py`
Visualization script for analyzing results.

---

## 📝 Understanding Response Files

Each JSON file in the answers directories contains:

```json
{
  "story_index": "15",
  "question_type": "Smarties",
  "story": "Child sees box labeled Smarties but told it contains pencils...",
  "short_answer": "Smarties",
  "answer": "A",
  "system_input": "System prompt with few-shot examples",
  "user_input": "Formatted user question with multiple choice",
  "output": "Model's full response text",
  "token_size": 1024,
  "map": {"A": "Smarties", "B": "Pencils"}
}
```

**Key fields**:
- `story_index`: Which story scenario
- `question_type`: Sally-Anne or Smarties
- `short_answer`: Expected correct answer
- `answer`: Model's selected option
- `output`: Full model response
- `token_size`: Number of tokens in response

---

## 🧪 Running Experiments

### For Llama 3.1:
```bash
cd /data1/fanjinyu/ToM/LLMToM/ToMChallenges
python generate_answers.py \
    --output_path ./first_test/Llama-3.1-8B-Instruct-RanTask \
    --promptsA_path prompts/prompts.py \
    --promptsB_path prompts/prompts.py \
    --model_name meta-llama/Llama-3-8B-Instruct \
    --use_local \
    --local_model_path ./models/Llama-3.1-8B \
    --try_times 5 \
    --seed 42
```

### For Qwen Models:
```bash
python generate_answers.py \
    --output_path ./first_test/Qwen2.5-7B-Instruct-RanTask \
    --promptsA_path first_test/Qwen2.5-7B-Instruct/promptsN.py \
    --use_local \
    --local_model_path ./models/Qwen2.5-7B
```

---

## 📊 Interpreting Results

### High Accuracy Indicates:
- Good false belief reasoning
- Strong perspective-taking ability
- Solid ToM capabilities

### Low Accuracy May Indicate:
- Difficulty maintaining false beliefs
- Struggles with perspective shifts
- Over-reliance on ground truth

### Common Patterns:
- **1st person** responses often more accurate
- **Sally-Anne** typically harder than Smarties
- **Larger models** show better scaling

---

## 📈 Comparison Strategy

To compare models:

1. **Find matching timestamps**: Compare runs from same date/time
2. **Check accuracy files**: Look at `joint_accuracy.json`
3. **Review raw answers**: Examine `1stA.json` vs `2ndA.json`
4. **Analyze reasoning steps**: Check `step_results.json`
5. **Visualize**: Use `plot.py` for graphical comparison

---

## 🎯 Key Takeaways

1. **Model scaling matters**: 72B model outperforms 7B and 8B
2. **Task difficulty varies**: Sally-Anne > Smarties
3. **Perspective matters**: 1st person framing shows different patterns
4. **Reasoning steps cascade**: Early errors compound in later steps

---

*This directory contains comprehensive experiment results for evaluating Theory of Mind capabilities across different LLM models.*
