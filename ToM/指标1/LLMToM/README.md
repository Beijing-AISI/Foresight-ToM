# Theory of Mind (ToM) Challenges for LLMs

This project evaluates large language models' ability to handle **Theory of Mind (ToM)** scenarios - tasks that require understanding others' beliefs, knowledge, and mental states.

---

## 📁 Project Structure

```
ToM/
├── LLMToM/
│   ├── ToMChallenges/          # Main challenge experiments
│   │   ├── first_test/         # Primary experiment results
│   │   │   ├── Llama-3.1-8B-Instruct-RanTask/
│   │   │   ├── Qwen2.5-72B-Instruct-RanTask/
│   │   │   ├── Qwen2.5-7B-Instruct-RanTask/
│   │   │   ├── Qwen2.5-7B-Instruct-StoryTask/
│   │   │   ├── results/        # Pre-computed results & ablations
│   │   │   └── result_history/ # Recent experiments
│   │   ├── prompts.py          # System evaluation prompts
│   │   ├── generate_answers.py # Model inference script
│   │   ├── test.py             # CSV processing utility
│   │   ├── plot.py             # Visualization code
│   │   └── generate_answers.py # Alternative generation script
│   └── tom.json                # Model manipulation benchmark (gpt-oss-20b)
```

---

## 🎯 Project Goals

1. **Evaluate ToM capabilities**: Test how well LLMs handle classic false belief tasks (Sally-Anne, Smarties)
2. **Compare models**: Benchmark different model sizes (7B, 72B, 8B) across architectures (Llama, Qwen)
3. **Analyze response patterns**: Study how models form assumptions vs. reality in belief scenarios
4. **Generate visualizations**: Create plots showing accuracy improvements across tasks

---

## 📄 Code Files Explained

### `prompts.py` - Evaluation Prompts

This file contains the system prompts used to evaluate model responses.

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
    There is no explicit mention in the story that Mary notices the moldy chips. Mary simply picks up the bag and walks to the cashier without any hesitation or reaction. So, she is unlikely to be aware.

Step2-What will Mary likely do next?:
    Since Mary is unaware of the moldy chips (as deduced in Step 1), she is likely to proceed with her initial action, which is to pay for the chips. Reporting the moldy chips would require her awareness of the issue, which is not present in this scenario. So, she will Pay for the chips.

Step3-Next, Mary "pay for the chips" and not "report the moldy chips". The behavior of Mary can be best described as:
    Given that Mary is unaware of the mold, her action of paying for the chips is consistent with her knowledge of the situation. Her behavior is reasonable because she has no reason to suspect an issue with the chips. So, her behaviour is Reasonable.
So the answer is [A].
"""
```

**Purpose**: Provides few-shot examples showing the expected 1-3 step reasoning format for model evaluation.

---

### `generate_answers.py` - Model Inference Script

This is the main script that runs models and generates responses to ToM challenges.

```python
import argparse
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
```

#### Key Functions:

**`load_prompt_module(prompts_path)`** - Dynamically loads prompt definitions from a Python file and exports them as JSON for caching.

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

**`format_prompt(mc_prompt, choices_dict)`** - Formats the user prompt with randomized multiple-choice letters (A, B, C, etc.):

```python
def format_prompt(mc_prompt, choices_dict):
    available_letters = list(string.ascii_uppercase)
    random.shuffle(available_letters)

    # Map choices to randomized letters
    mapping = {key: available_letters.pop(0) 
               for key in choices_dict.keys()}
    reverse_mapping = {value: key 
                       for key, value in mapping.items()}

    randomized_choice_dict = {mapping[key]: value 
                              for key, value in sorted_items}
    # ... generates final prompt
    return reverse_mapping, prompt
```

#### Main Execution Flow:

1. **Argument parsing**: Sets output paths, model names, generation parameters
2. **Model loading**: Uses HuggingFace `AutoTokenizer` and `AutoModelForCausalLM`
3. **Data loading**: Reads CSV files containing ToM challenge stories
4. **Prompt formatting**: Applies few-shot prompting with examples
5. **Generation loop**: Attempts generation `try_times` (default 5) with deterministic sampling
6. **Result saving**: Saves responses to JSON files organized by challenge type

**Command-line usage**:
```bash
python generate_answers.py \
    --output_path ./my_results \
    --promptsA_path prompts/prompts.py \
    --promptsB_path prompts/prompts.py \
    --model_name HuggingFaceHub/model-name \
    --use_local \
    --local_model_path ./models/my-model
```

---

### `test.py` - CSV Processing Utility

A simple script for extracting specific columns and saving to new CSV files.

```python
import pandas as pd
configs = ['Sally-Anne_prompt.csv', 'Smarties_prompt.csv']

for config in configs:
    data = pd.read_csv(f"/mnt/home/liweiyi/LLM/ToMChallenges/Data/{config}")
    
    columns_to_extract = [
        "story_index", "question", "short_answer", 
        "question_type", "mc_prompt"
    ]
    new_data = data[columns_to_extract]
    new_data.to_csv(output_file, index=False)
```

**Purpose**: Preprocess raw challenge data for easier consumption by `generate_answers.py`.

---

### `plot.py` - Visualization Script

Generates plots analyzing accuracy across different models and tasks.

```python
import matplotlib.pyplot as plt
import json
import glob
import pandas as pd

# Load results from model folders
accuracy_data = []
for model_name in models:
    model_path = f"./first_test/{model_name}/accuracy_results-*/"
    for dirpath, dirnames, filenames in os.walk(model_path):
        if "joint_accuracy.json" in filenames:
            with open(os.path.join(dirpath, "joint_accuracy.json"), 'r') as f:
                accuracy_data.append(json.load(f))
# ... plotting logic
```

**Outputs**: `plot2.png`, `plot3.png` - Visualizations showing:
- Model comparison (Llama vs Qwen)
- Task difficulty (Sally-Anne vs Smarties)
- Reasoning step accuracy

---

## 📂 Folder Structure Deep Dive

### `first_test/` - Primary Experiments

Contains experiments organized by **model** and **task type**:

#### Model Directories:

| Folder | Model | Size | Task Type |
|--------|-------|------|-----------|
| `Llama-3.1-8B-Instruct-RanTask/` | Llama 3.1 | 8B | Reasoning/Awareness Task |
| `Qwen2.5-72B-Instruct-RanTask/` | Qwen2.5 | 72B | Reasoning/Awareness Task |
| `Qwen2.5-7B-Instruct-RanTask/` | Qwen2.5 | 7B | Reasoning/Awareness Task |
| `Qwen2.5-7B-Instruct-StoryTask/` | Qwen2.5 | 7B | Story-based Task |

#### Task Types:

1. **`RanTask`** - Reasoning/Awareness Task
   - Focus: Can the model reason about what someone would believe/know
   - Measures: Accuracy in identifying correct assumptions/reality

2. **`StoryTask`** - Story-based Task
   - Focus: More narrative, context-rich scenarios
   - Tests: Ability to handle longer, more complex situations

#### Inside Each Model Folder:

```
{Model}/
├── accuracy_results-YYYYMMDD-HHMMSS/
│   ├── joint_accuracy.json   # Combined accuracy across all challenges
│   ├── standard_accuracy.json # Standard task metrics
│   └── step_results.json     # Per-step reasoning accuracy
└── answers-YYYYMMDD-HHMMSS/
    ├── Smarties_prompt.csv/
    │   └── {story_index}/
    │       ├── 1stA.json  # First person perspective
    │       ├── 1stB.json  # First person perspective (alternate)
    │       ├── 2ndA.json  # Second person perspective
    │       ├── 2ndB.json  # Second person perspective (alternate)
    │       ├── assumption.json
    │       └── reality.json
    └── Sally-Anne_prompt.csv/
        └── {story_index}/
            ├── 1stA.json
            ├── 1stB.json
            ├── 2ndA.json
            ├── 2ndB.json
            ├── memory.json   # What the character remembers
            └── reality.json
```

### `results/` - Pre-computed Results

```
results/
├── ablation/           # Ablation studies
├── compare/            # Model comparisons
└── results_pre/        # Baseline results
```

### `result_history/` - Recent Experiments

Tracks the latest runs with timestamps, useful for monitoring experiment progression.

---

## 🔬 ToM Challenge Types

### 1. **Sally-Anne Task**
Classic false belief task:
- **Scenario**: Sally puts a ball in a basket, leaves, Anne moves it to a box
- **Question**: Where will Sally look for the ball?
- **Tests**: Understanding that Sally's belief differs from reality

### 2. **Smarties Task**
False belief induction:
- **Scenario**: Child told Smarties box actually contains pencils
- **Question**: If asked "What's in the box?" then "Where did you get Smarties?", what do you say?
- **Tests**: Distinguishing between what is and what is believed

---

## 📊 Understanding the JSON Output

Each answer file (e.g., `1stA.json`) contains:

```json
{
  "story_index": "1",
  "question_type": "Sally-Anne",
  "story": "Sally put her doll in the basket...",
  "short_answer": "basket",
  "answer": "A",
  "system_input": "System prompt text",
  "output": "Model's full response text",
  "map": {"A": "basket", "B": "box"}
}
```

**File naming**:
- `1stA.json` / `1stB.json`: First-person perspective, option A/B
- `2ndA.json` / `2ndB.json`: Second-person perspective, option A/B
- `assumption.json`: Model's assumption state
- `reality.json`: Ground truth reality state

---

## 🧪 How to Run Experiments

### Basic Run:
```bash
cd /data1/fanjinyu/ToM/LLMToM/ToMChallenges
python generate_answers.py \
    --output_path ./results \
    --promptsA_path prompts/prompts.py \
    --promptsB_path prompts/prompts.py \
    --model_name mistralai/Mistral-7B-Instruct-v0.2 \
    --use_local \
    --local_model_path ./models/mistral-7b
```

### Using Local Models:
```bash
python generate_answers.py \
    --output_path ./my_results \
    --use_local \
    --local_model_path ./downloads/llama-3.1-8b \
    --device_map cuda:0
```

### Using QWen Models:
```bash
python generate_answers.py \
    --output_path ./qwen_results \
    --promptsB_path first_test/Qwen2.5-7B-Instruct/promptsN.py \
    --use_local \
    --local_model_path ./downloads/qwen2.5-7b
```

---

## 📈 Analysis Pipeline

1. **Generate responses** → `generate_answers.py`
2. **Collect results** → JSON files in answer folders
3. **Compute accuracy** → `joint_accuracy.json` files
4. **Visualize** → `plot.py` generates PNGs
5. **Compare models** → Results in `results/compare/`

---

## 🔑 Key Insights

1. **Model scaling**: Larger models (72B) tend to show higher ToM accuracy
2. **Architecture differences**: Llama and Qwen may handle reasoning differently
3. **Task difficulty**: Sally-Anne and Smarties have different accuracy patterns
4. **Perspective effects**: 1st vs 2nd person perspectives show interesting differences

---

## 📚 Related Files

- **`first_test/promptsN.py`**: Extended prompts with variations
- **`first_test/eval_Llama-3.1-8B-Instruct.sh`**: Shell script for Llama evaluation
- **`LLMToM/tom.json`**: Model manipulation benchmark (sales role-play experiment)

---

## 📝 Notes

- **Timestamped folders**: Each experiment folder has a timestamp for easy tracking
- **Multiple attempts**: Script tries `try_times` (default 5) per challenge
- **Token limits**: Set to 4096 by default to ensure complete responses
- **Seeding**: Uses seed 42 for reproducibility

---

*Project maintains results from evaluations across multiple LLMs, tracking Theory of Mind capability improvements and identifying edge cases where models struggle with belief attribution tasks.*
