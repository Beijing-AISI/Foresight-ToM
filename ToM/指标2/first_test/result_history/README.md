# result_history/ - Recent Experiments History

This directory tracks recent and ongoing experiment runs, providing a history of ToM capability evaluations across different models and configurations.

---

## 📁 Directory Structure

```
result_history/
├── Llama-3.1-8B-Instruct/
├── Llama-3.1-8B-Instruct-GenTaskPrompt/
├── Qwen2.5-7B-Instruct/
└── testMultiTask/
```

---

## 🎯 Model-Specific Experiments

### 1. Llama-3.1-8B-Instruct

**Purpose**: Latest Llama 3.1 8B experiments with various configurations

**Contents**:
- Standard Reasoning/Awareness Task evaluations
- Recent runs with updated prompts
- Comparison with previous Llama experiments

**Use Case**: Track performance of Llama 3.1 across different runs.

### 2. Llama-3.1-8B-Instruct-GenTaskPrompt

**Purpose**: Generalized task prompting experiments

**Variations**:
- **Standard RAN Task**: Basic false belief scenarios
- **GenTaskPrompt**: Adaptive task prompting approach
- **Prompt Engineering**: Optimized prompt structures
- **Reasoning Traces**: Step-by-step reasoning analysis

**Key Features**:
- Dynamic prompt generation
- Task-adaptive prompting
- Context-aware reasoning

### 3. Qwen2.5-7B-Instruct

**Purpose**: Qwen 2.5 7B evaluations

**Contents**:
- Standard RAN Task results
- Story-based evaluations
- Multi-task experiments
- Reasoning quality analysis

**Comparison Point**: Compare with Qwen 72B for scaling analysis.

### 4. testMultiTask

**Purpose**: Combined multi-task evaluations

**Features**:
- Simultaneous challenge testing
- Cross-task interference analysis
- Combined task performance
- Transfer learning effects

---

## 📊 Understanding Experiment Variants

### Standard vs GenTaskPrompt

#### Standard RAN Task

```
Llama-3.1-8B-Instruct/
└── answers-YYYYMMDD-HHMMSS/
    └── Smarties_prompt.csv/
        └── {story_index}/
            ├── 1stA.json
            ├── 1stB.json
            ├── 2ndA.json
            └── 2ndB.json
```

**Characteristics**:
- Static prompts
- Standard few-shot examples
- Consistent format across runs

#### GenTaskPrompt

```
Llama-3.1-8B-Instruct-GenTaskPrompt/
└── answers-YYYYMMDD-HHMMSS/
    └── {task_type}/
        └── {story_index}/
            ├── 1stA.json
            ├── 1stB.json
            ├── 2ndA.json
            └── 2ndB.json
            └── reasoning_trace.json  # Additional: step-by-step trace
```

**Characteristics**:
- Dynamic prompt generation
- Task-adaptive framing
- Context-aware examples
- Optional reasoning traces

**Benefits**:
- Potentially higher accuracy
- Better handling of edge cases
- More nuanced reasoning
- Adaptation to task difficulty

---

## 📈 Tracking Experiment Progression

### Timestamp Organization

Each subdirectory contains timestamped experiment folders:

```
Llama-3.1-8B-Instruct/
├── accuracy_results-20250407-101150/
└── answers-20250407-101150/

Qwen2.5-7B-Instruct/
├── accuracy_results-20250407-143345/
├── accuracy_results-20250407-164505/
└── answers-20250407-114144/
    └── answers-20250407-142240/
    └── answers-20250407-143345/
    └── answers-20250407-164505/
```

**Timestamp Format**: `YYYYMMDD-HHMMSS`

**Usage**:
- Track performance over time
- Compare different runs
- Identify improvements/regressions

---

## 🔬 Experiment Types

### 1. **Standard Evaluation Runs**

Basic ToM capability tests:
- Fixed prompts
- Standard few-shot examples
- Consistent configuration
- Reproducible conditions

### 2. **GenTaskPrompt Experiments**

Adaptive prompting approaches:
- Dynamic prompt generation
- Task-specific framing
- Context-aware examples
- Potentially higher complexity

### 3. **Multi-Task Tests**

Combined evaluation scenarios:
- Multiple challenge types simultaneously
- Cross-task performance
- Interference effects
- Transfer learning analysis

---

## 📊 Performance Tracking

### Example: Performance Over Time

```
2025-03-25: accuracy = 0.767
2025-03-28: accuracy = 0.800
2025-04-07: accuracy = 0.833
```

**Analysis**:
- 3-day improvement from 76.7% to 80.0%
- 7-day improvement from 80.0% to 83.3%
- Consistent gains of 2-5%

### Example: Prompt Engineering Gains

```
Standard prompts:    accuracy = 0.800
GenTaskPrompt:       accuracy = 0.850
Improvement:         +5.0%
```

---

## 🧪 Running New Experiments

### Basic Run:
```bash
python generate_answers.py \
    --output_path ./result_history/new_experiment \
    --promptsA_path prompts/prompts.py \
    --promptsB_path prompts/prompts.py \
    --model_name mistralai/Mistral-7B-Instruct-v0.2 \
    --use_local \
    --local_model_path ./models/mistral-7b
```

### GenTaskPrompt Variant:
```bash
python generate_answers.py \
    --output_path ./result_history/Llama-3.1-8B-Instruct-GenTaskPrompt \
    --promptsA_path first_test/Qwen2.5-7B-Instruct/promptsN.py \
    --promptsB_path prompts/prompts.py \
    --model_name meta-llama/Llama-3-8B-Instruct \
    --use_local \
    --local_model_path ./models/Llama-3.1-8B \
    --try_times 5
```

---

## 📊 Comparing Result History

### Step-by-Step Comparison

1. **List directories**:
   ```bash
   ls -la result_history/Llama-3.1-8B-Instruct/
   ```

2. **Check timestamps**:
   ```bash
   ls result_history/Llama-3.1-8B-Instruct/
   # accuracy_results-20250407-101150
   # answers-20250407-101150
   ```

3. **Compare accuracies**:
   ```bash
   cat accuracy_results-20250407-101150/joint_accuracy.json
   ```

4. **Analyze improvements**:
   - Earlier runs: lower accuracy
   - Later runs: higher accuracy
   - Identify what changed

---

## 🔍 Understanding Model Variants

### Qwen2.5-7B vs Qwen2.5-72B

| Model | Size | Expected ToM Accuracy | Use Case |
|-------|------|---------------------|----------|
| Qwen2.5-7B | 7B | ~70-80% | Efficient evaluation |
| Qwen2.5-72B | 72B | ~85-95% | Baseline for comparison |

### Llama Scaling

| Model | Size | Expected ToM Accuracy | Use Case |
|-------|------|---------------------|----------|
| Llama-3.1-8B | 8B | ~75-85% | Standard evaluation |

---

## 📊 Experiment Documentation

Each experiment folder may include metadata:

```json
{
  "experiment_name": "Standard RAN Task",
  "date": "2025-04-07",
  "timestamp": "10:11:50",
  "model": "Llama-3.1-8B-Instruct",
  "configuration": {
    "temperature": 0.7,
    "max_tokens": 4096,
    "try_times": 5,
    "seed": 42
  },
  "notes": "Standard evaluation with few-shot prompting"
}
```

---

## 🎯 Common Experiment Patterns

### Pattern 1: Baseline Establishment

```bash
# First run: establish baseline
python generate_answers.py \
    --output_path ./result_history/baseline \
    --model_name base_model

# Second run: verify reproducibility
python generate_answers.py \
    --output_path ./result_history/baseline_v2 \
    --model_name base_model
```

### Pattern 2: Configuration Tuning

```bash
# Try different temperatures
python generate_answers.py --temperature 0.0
python generate_answers.py --temperature 0.5
python generate_answers.py --temperature 0.7

# Try different token limits
python generate_answers.py --token_size 512
python generate_answers.py --token_size 2048
python generate_answers.py --token_size 4096
```

### Pattern 3: Prompt Engineering

```bash
# Standard prompts
python generate_answers.py \
    --promptsA_path prompts/prompts.py

# Enhanced prompts
python generate_answers.py \
    --promptsA_path first_test/promptsN.py

# Compare results
cat accuracy_results-*/joint_accuracy.json
```

---

## 📈 Identifying Trends

### Improvement Indicators:

1. **Increasing accuracy over time**: Model or prompt improvements
2. **Consistent results**: Good reproducibility
3. **Task-specific gains**: Better at certain challenges

### Regression Indicators:

1. **Decreasing accuracy**: Configuration issues
2. **Inconsistent results**: Model loading issues
3. **High variance**: Stochastic effects dominate

---

## 📊 Multi-Model Comparison

To compare across models:

```bash
# List all model folders
ls result_history/

# Extract accuracies
for dir in result_history/*/; do
    echo "=== $dir ==="
    cat $dir/accuracy_results-*/joint_accuracy.json
done
```

---

## 🔬 Advanced Analysis

### Reasoning Trace Analysis

GenTaskPrompt may include detailed reasoning traces:

```json
"reasoning_trace": {
  "step1": {
    "question": "Is Mary aware of the moldy chips?",
    "model_answer": "Unlikely",
    "reasoning": "No explicit mention of awareness..."
  },
  "step2": {
    "question": "What will Mary do next?",
    "model_answer": "Pay for chips",
    "reasoning": "Proceeds with initial action..."
  },
  "step3": {
    "question": "Is behavior reasonable?",
    "model_answer": "Reasonable",
    "reasoning": "Action consistent with knowledge..."
  }
}
```

---

## 📝 Summary Table

| Directory | Model | Experiment Type | Purpose |
|-----------|-------|---------------|----------|
| **Llama-3.1-8B-Instruct/** | Llama 8B | Standard | Baseline evaluations |
| **Llama-3.1-8B-Instruct-GenTaskPrompt/** | Llama 8B | Adaptive | Prompt engineering |
| **Qwen2.5-7B-Instruct/** | Qwen 7B | Standard | Qwen model evaluation |
| **testMultiTask/** | Various | Multi-task | Combined evaluation |

---

## 🔧 Troubleshooting

### Low Accuracy:
- Check model is loading correctly
- Verify data loading is working
- Review token limits aren't truncating
- Consider lowering temperature

### High Variance:
- Increase `try_times` parameter
- Lower temperature for more consistency
- Check for model instability

### Memory Issues:
- Reduce `token_size`
- Use more aggressive caching
- Consider smaller models for testing

---

## 📚 Best Practices

1. **Document experiments**: Record configuration details
2. **Track timestamps**: Use datetime folders
3. **Compare systematically**: Same date/time for fair comparison
4. **Document improvements**: Note what changed and why
5. **Archive old results**: Move completed experiments to archive

---

*This directory provides a history of experiment runs, tracking ToM capability evaluations and enabling performance trend analysis across different models and configurations.*
