# Complete Project Explanation: ToM (Theory of Mind) Challenges for LLMs

## 🎯 What is this Project Trying to Achieve?

### Scientific Goal
This project evaluates **large language models' (LLMs) Theory of Mind capabilities** - specifically their ability to:
1. **Track false beliefs**: Understand what someone believes is different from reality
2. **Reason about mental states**: Infer what another person knows, believes, or intends
3. **Perspective-taking**: Understand situations from another person's viewpoint
4. **Distinguish belief from reality**: Recognize that someone can believe something that isn't true

### Why This Matters
Humans naturally understand false beliefs (e.g., "Sarah put her toy in the box, then I moved it - where does Sarah think it is?"). The question is: **Do LLMs truly understand these mental states, or are they just guessing based on patterns?**

---

## 🧪 The Experiment Paradigm (How Experiments Work)

### Step-by-Step Process

```
┌─────────────────────────────────────────────────────────────┐
│                    EXPERIMENT FLOWCHART                       │
└─────────────────────────────────────────────────────────────┘

1. [DATA LOADING]
   ├── Read CSV files containing ToM challenge stories
   ├── Each row = one challenge scenario
   └── Example: "Neila found a bag labeled 'plate' but it had 'vest'"

2. [PROMPT FORMATTING]
   ├── Load system prompt with few-shot examples
   ├── Format user prompt with specific challenge
   └── Add multiple choice options (A, B)

3. [MODEL GENERATION]
   ├── Send formatted prompt to LLM
   ├── Model attempts to answer
   └── Repeat try_times (default 5) for reliability

4. [RESPONSE EVALUATION]
   ├── Extract model's answer
   ├── Compare to ground truth
   ├── Calculate accuracy
   └── Save responses to JSON

5. [RESULTS ANALYSIS]
   ├── Compute joint accuracy across all challenges
   ├── Analyze per-step reasoning
   └── Generate visualizations
```

---

## 📊 Understanding the Two Main Challenge Types

### 1. Smarties Task (False Belief Induction)

#### Story Structure
```
Person A finds a container
- Label says: Item X (what SHOULD be there)
- Opens container, finds: Item Y (what IS actually there)
- Person A closes container, doesn't tell anyone
Person B enters and sees the container
Question: What does Person B think is in the container?
```

#### Example Story
```
Story: "Neila found a bag in the attic. The label on the bag says plate. 
        Neila opened the bag and found a vest. There is no plate in the bag.
        Neila closed the bag and put it back. Juanita entered the attic 
        and saw the bag."

Question: "What was supposed to be in the bag?"
Choices:
    A. vest
    B. plate

Correct Answer: B (plate)
Why? Because the label says "plate", so Juanita would assume it's plate,
           not the actual content (vest)
```

#### What This Tests
- Can the model track that Juanita **believes** there's a plate?
- Does the model understand that Juanita's belief differs from reality?
- Can the model reason about what another person **should believe** based on available information?

---

### 2. Sally-Anne Task (False Belief Understanding)

#### Story Structure
```
Two characters and two locations
- Character 1 puts object in Location 1
- Character 1 leaves
- Character 2 moves object to Location 2
- Question: Where does Character 1 think the object is?
```

#### Example Story
```
Story: "Neila and Juanita were hanging out in the attic. They saw a 
        closet and a cabinet. They found a towel in the closet. 
        Juanita left the attic. Neila moved the towel to the cabinet."

Question: "Where was the towel?" (before being moved)
Choices:
    A. cabinet
    B. closet

Correct Answer: B (closet)
Why? Juanita left BEFORE Neila moved it, so Juanita believes it's in the closet
```

#### What This Tests
- Can the model track object location changes?
- Does the model understand Juanita's memory of the original location?
- Can the model reason about another person's **memory** vs **current reality**?

---

## 📄 Each Code File Explained in Detail

### 1. `prompts.py` - System Prompts for Evaluation

#### What It Does
Contains the **few-shot prompt template** that teaches the model how to reason about ToM scenarios.

#### Key Prompt Structure

```python
SystemEvaluatePrompt = """
[Story]
The story describes the scenario...

[Question]
What will happen / What does person believe?

[Candidate Answers]
A. Option 1
B. Option 2

[Output]
Step1-Is Person A aware of "X"??:
    Analyze whether Person A noticed the critical detail...

Step2-What will Person A likely do next?:
    Predict Person A's action based on their knowledge...

Step3-Is the behavior reasonable?:
    Evaluate if the action matches Person A's belief state...

So the answer is [A].
"""
```

#### Why This Format?
- **Step-by-step reasoning**: Forces the model to think through the problem
- **Few-shot learning**: Shows examples of expected reasoning
- **Explicit format**: Ensures consistent output structure
- **Awareness → Prediction → Evaluation**: Logical flow for ToM reasoning

#### How It Works
```
Model receives:
├── System prompt (with examples)
└── User prompt (specific challenge + question)

Model generates:
├── Step 1 analysis (awareness check)
├── Step 2 prediction (behavior prediction)
├── Step 3 evaluation (reasonabiness check)
└── Final answer [A] or [B]
```

---

### 2. `generate_answers.py` - Main Inference Script

#### What It Does
The **engine** that runs the entire experiment - loads models, generates responses, saves results.

#### Code Breakdown

##### Section 1: Imports
```python
import argparse          # Command-line arguments
from concurrent.futures import ProcessPoolExecutor  # Parallel processing
import importlib         # Dynamic module loading
import json, os, re      # Standard utilities
import torch             # PyTorch for model
from transformers import AutoTokenizer, AutoModelForCausalLM  # Load LLMs
from tqdm import tqdm    # Progress bar
import pandas as pd      # CSV handling
```

**Purpose**: Get all tools needed for model inference and data processing.

##### Section 2: `load_prompt_module(prompts_path)`
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

**What It Does**:
1. Dynamically imports a Python file (e.g., `prompts.py`)
2. Extracts all prompt strings (SystemEvaluatePrompt, UserEvaluatePrompt)
3. Saves them to JSON for faster loading
4. Returns the loaded module

**Why Dynamic Import?**
- Allows changing prompts without restarting Python
- Avoids hard-coding prompt strings
- Makes experiments reproducible

##### Section 3: `format_prompt(mc_prompt, choices_dict)`
```python
def format_prompt(mc_prompt, choices_dict):
    available_letters = list(string.ascii_uppercase)
    random.shuffle(available_letters)

    mapping = {key: available_letters.pop(0) for key in choices_dict.keys()}
    reverse_mapping = {value: key for key, value in mapping.items()}

    # Generate final prompt with few-shot examples
    prompt = load_prompts.UserEvaluatePrompt.format(**format_args)

    return reverse_mapping, prompt
```

**What It Does**:
1. Takes a story and question
2. Randomizes multiple choice letters (A, B, C...)
3. Formats prompt with examples
4. Returns formatted prompt + mapping for answer decoding

**Example**:
```
Input:
    Story: "Person A found X..."
    Question: "What is in the bag?"
    choices: {"A": "vest", "B": "plate"}

Output:
    Formatted prompt with random letters
    Mapping: {"A": "vest", "B": "plate"}
```

##### Section 4: Main Execution Flow
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_path", ...)      # Where to save results
    parser.add_argument("--promptsA_path", ...)   # Prompt file for task A
    parser.add_argument("--promptsB_path", ...)   # Prompt file for task B
    parser.add_argument("--model_name", ...)      # Which model to use
    parser.add_argument("--use_local", ...)       # Use local model or HuggingFace
    parser.add_argument("--local_model_path", ...) # Local model path
    parser.add_argument("--try_times", ...)       # How many attempts
    parser.add_argument("--seed", ...)            # Random seed for reproducibility
    parser.add_argument("--token_size", ...)      # Max tokens in response
    args = parser.parse_args()
```

**Purpose**: Parse command-line arguments for flexibility.

##### Section 5: Model Loading
```python
if args.use_local:
    tokenizer = AutoTokenizer.from_pretrained(args.local_model_path, ...)
    model = AutoModelForCausalLM.from_pretrained(args.local_model_path, ...)
else:
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, ...)
    model = AutoModelForCausalLM.from_pretrained(args.local_model_path, ...)
```

**What It Does**:
1. Loads tokenizer (converts text to numbers)
2. Loads model (the actual LLM)
3. Configures device mapping (GPU/CPU)

**Why Two Paths?**
- `--use_local`: Use downloaded models (faster)
- Otherwise: Download from HuggingFace

##### Section 6: Generation Parameters
```python
gen_kwargs = {
    "max_length": args.token_size,      # Response length limit
    "do_sample": False,                  # Deterministic (no randomness)
    "repetition_penalty": 1.1,          # Slight penalty for repeating
}
```

**Purpose**: Control generation behavior.

##### Section 7: Processing Loop
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
        # Find correct answer choice
        answer = None
        for key, value in choices_dict.items():
            if value == short_answer:
                answer = key
                break
        
        # Create output folder
        output_folder = os.path.join(root_folder, f"{config}", f"{story_index}")
        os.makedirs(output_folder, exist_ok=True)
        
        for j in range(args.try_times):
            reverse_mapping, user_prompt = format_prompt(mc_prompt, choices_dict)
            
            # Create messages for model
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            
            # Generate response
            outputs = model.generate(...)
            
            # Save to JSON
            with open(output_fn, "w") as f:
                json.dump(results, f)
```

**What This Loop Does**:
1. For each challenge type (Smarties, Sally-Anne)
2. Load appropriate prompts
3. Read CSV data (stories + questions)
4. For each story:
   - Find the correct answer
   - Format the prompt
   - Generate response (multiple attempts)
   - Save results to JSON

---

### 3. `test.py` - CSV Preprocessing Utility

#### What It Does
Extracts specific columns from the full dataset and creates simplified CSV files.

#### Why Needed?
The original CSV has many columns:
- story_index
- question
- short_answer
- question_type
- mc_prompt (multiple choice prompt)
- AND many other experimental question types

This script keeps only what's needed for the main experiment.

---

### 4. `plot.py` - Visualization Script

#### What It Does
Generates plots showing:
1. Model performance comparison
2. Accuracy across different tasks
3. Scaling effects (model size vs accuracy)

#### Example Visualization
```python
# Load all model accuracies
accuracy_data = []
for model_name in models:
    # Find accuracy files
    # Load joint_accuracy.json
    accuracy_data.append(...)

# Plot
plt.figure(figsize=(10, 6))
plt.bar(models, accuracies)
plt.title("Model Comparison")
plt.savefig("comparison.png")
```

---

## 📂 Understanding the Results Files

### Folder Structure (One Experiment Run)

```
Llama-3.1-8B-Instruct-RanTask/
├── accuracy_results-20250328-163101/
│   ├── joint_accuracy.json      # Combined accuracy across all challenges
│   ├── standard_accuracy.json   # Standard benchmark scores
│   └── step_results.json        # Per-step accuracy breakdown
└── answers-20250328-163101/
    └── Smarties_prompt.csv/
        ├── 1/
        │   ├── 1stA.json        # First person perspective, option A
        │   ├── 1stB.json        # First person perspective, option B
        │   ├── 2ndA.json        # Second person perspective, option A
        │   ├── 2ndB.json        # Second person perspective, option B
        │   ├── assumption.json  # Model's internal belief state
        │   └── reality.json     # Ground truth
        ├── 2/                   # Story 2
        ├── 3/                   # Story 3
        └── ...                  # Up to 30 stories
```

### JSON File Structure

```json
{
  "story_index": "1",
  "question_type": "Smarties",
  "story": "Neila found a bag in the attic. The label on the bag says plate...",
  "short_answer": "vest",
  "answer": "A",
  "system_input": "System prompt with few-shot examples",
  "user_input": "User question with multiple choice",
  "output": "Model's full response text",
  "token_size": 1236,
  "map": {"A": "Smarties", "B": "Plate"}
}
```

**Each Field Explained**:
- `story_index`: Which story scenario (1, 2, 3...)
- `question_type`: Which challenge type (Smarties, Sally-Anne)
- `story`: The full challenge story
- `short_answer`: Correct answer (used for accuracy calculation)
- `answer`: Model's selected choice (A or B)
- `system_input`: System prompt text
- `user_input`: Formatted user question
- `output`: Full model response
- `token_size`: Number of tokens in response
- `map`: Mapping from letter to answer text

---

## 🎭 The Two Task Types Explained

### Smarties Task Variants

| Variant | What It Tests | Example Question |
|---------|---|---|
| **reality** | What IS in the container | "What was in the bag?" |
| **assumption** | What SHOULD be there (based on label) | "What was supposed to be in the bag?" |
| **memory** | What Person A knows about the container | "What does Neila know about the bag?" |

### Sally-Anne Task Variants

| Variant | What It Tests | Example Question |
|---------|---|---|
| **reality** | Current object location | "Where is the towel now?" |
| **memory** | Past object location | "Where was the towel before?" |

---

## 📊 Accuracy Metrics Explained

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

**Metrics Explained**:
- **Sally-Anne accuracy**: Performance on false belief tasks
- **Smarties accuracy**: Performance on belief induction tasks
- **Overall accuracy**: Combined performance
- **Step 1 accuracy**: Awareness detection (is person aware?)
- **Step 2 accuracy**: Behavior prediction (what will they do?)
- **Step 3 accuracy**: Reasonableness evaluation (is this behavior appropriate?)

### Performance Thresholds

| Category | Sally-Anne | Smarties | Overall |
|----------|---|---|---|
| **Poor** | < 60% | < 50% | < 60% |
| **Average** | 60-80% | 50-75% | 60-75% |
| **Good** | 80-90% | 75-85% | 75-85% |
| **Excellent** | > 90% | > 85% | > 85% |

---

## 🧪 How to Interpret Results

### High Accuracy Indicates
- Model correctly tracks false beliefs
- Model distinguishes belief from reality
- Model understands perspective-taking

### Low Accuracy May Indicate
- Model confuses belief with reality
- Model struggles with multi-step reasoning
- Model over-relies on ground truth
- Model lacks true ToM understanding

---

## 📈 Experimental Variations

### 1. `RanTask` (Reasoning/Awareness Task)
- Standard false belief evaluation
- Focus on basic ToM capabilities
- Measures accuracy in identifying correct beliefs

### 2. `StoryTask` (Story-based Task)
- More narrative complexity
- Tests longer reasoning chains
- Evaluates context retention

### 3. `GenTaskPrompt` (Generalized Task Prompting)
- Dynamic prompt generation
- Adaptive task framing
- Context-aware examples

---

## 🔑 Key Research Questions This Project Answers

1. **Do LLMs truly understand false beliefs?**
   - If accuracy is high: Yes, likely true understanding
   - If accuracy is low: May be pattern matching, not true ToM

2. **Does model size matter?**
   - Compare 7B vs 8B vs 72B models
   - Larger models may have better reasoning

3. **How does architecture affect ToM?**
   - Llama vs Qwen performance
   - Different training data effects

4. **What's the step-wise reasoning pattern?**
   - Step 1 (awareness) is usually easiest
   - Step 3 (evaluation) is usually hardest
   - Errors cascade through reasoning

---

## 💡 Summary

### What This Project Does
- Tests LLMs on classic Theory of Mind tasks
- Evaluates false belief understanding
- Compares different model architectures
- Analyzes reasoning patterns

### Why It Matters
- Helps understand AI cognitive capabilities
- Identifies limitations in current LLMs
- Guides model development for reasoning tasks

### Main Takeaway
This is a **scientific evaluation** of whether LLMs can truly reason about mental states, not just predict text based on patterns. The experiments use carefully constructed false belief scenarios to probe the boundary between genuine understanding and sophisticated pattern matching.

---

*For detailed explanation of each file, see the individual README files created in each subdirectory.*
