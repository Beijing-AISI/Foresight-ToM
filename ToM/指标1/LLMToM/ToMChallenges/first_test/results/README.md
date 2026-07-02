# results/ - Pre-computed Results Directory

This directory contains pre-computed results, ablation studies, and model comparisons for Theory of Mind experiments.

---

## 📁 Directory Structure

```
results/
├── ablation/                    # Ablation studies
├── compare/                     # Model comparisons
└── results_pre/                # Pre-computed baseline results
```

---

## 🧪 1. ablation/ - Ablation Studies

Ablation studies systematically remove or modify components to understand their impact on performance.

### Typical Ablation Experiments:

1. **Prompt Variations**
   - Standard few-shot vs zero-shot prompting
   - Different reasoning step counts (1, 2, or 3 steps)
   - Varying example lengths

2. **Token Limit Effects**
   - Short responses (512 tokens) vs long responses (4096 tokens)
   - Truncation effects on accuracy
   - Token budget vs reasoning depth

3. **Temperature Parameter**
   - Deterministic (temperature=0) vs stochastic (temperature=0.7)
   - Sampling vs greedy decoding
   - Repetition penalty effects

4. **Perspective Framing**
   - First person vs second person
   - Different pronoun choices
   - Narrative voice impact

### Expected Contents:

```
ablation/
├── prompt_variations/
│   ├── few_shot/
│   ├── zero_shot/
│   └── few_shot_plus/
├── token_limits/
│   ├── short_512/
│   ├── medium_2048/
│   └── long_4096/
├── temperature/
│   ├── deterministic/
│   ├── stochastic_low/
│   └── stochastic_high/
└── perspectives/
    ├── first_person/
    └── second_person/
```

**Purpose**: Understand which components contribute most to performance.

---

## 📊 2. compare/ - Model Comparisons

Contains comparative analyses between different models and configurations.

### Typical Comparisons:

1. **Model Architecture Comparison**
   - Llama vs Qwen performance
   - Different parameter sizes (7B, 8B, 72B)
   - Cross-architecture benchmarks

2. **Task Difficulty Comparison**
   - Sally-Anne vs Smarties accuracy
   - Standard vs complex narratives
   - Single-step vs multi-step reasoning

3. **Prompt Effectiveness**
   - Standard prompts vs enhanced prompts
   - Few-shot examples impact
   - System instruction variations

### Expected Contents:

```
compare/
├── model_architectures/
│   ├── llama_vs_qwen/
│   ├── size_scaling/
│   └── architecture_benchmarks/
├── task_difficulty/
│   ├── basic_false_belief/
│   ├── complex_narratives/
│   └── multi_step_reasoning/
└── prompt_effectiveness/
    ├── standard_vs_enhanced/
    ├── few_shot_impact/
    └── instruction_variations/
```

---

## 📋 3. results_pre/ - Pre-computed Baselines

Contains pre-computed baseline results for reference and comparison.

### Baseline Categories:

1. **Standard Benchmarks**
   - Classic false belief tasks
   - Standardized test sets
   - Reference model performance

2. **Historical Results**
   - Previous model evaluations
   - Historical performance trends
   - Long-term improvement tracking

3. **Reference Models**
   - GPT-3.5 baseline
   - GPT-4 baseline
   - Open source benchmarks

### Expected Contents:

```
results_pre/
├── benchmarks/
│   ├── sally_anne_standard/
│   ├── smarties_standard/
│   └── combined_benchmarks/
├── historical/
│   ├── 2024_results/
│   ├── 2025_results/
│   └── performance_trends/
└── reference_models/
    ├── gpt35_baselines/
    ├── gpt4_baselines/
    └── open_source_benchmarks/
```

---

## 📊 Understanding Result Files

### `accuracy.json` Structure

```json
{
  "model_name": "Llama-3.1-8B-Instruct",
  "evaluation_date": "2025-04-07",
  "timestamp": "10:11:50",
  "config": {
    "temperature": 0.7,
    "max_output_tokens": 4096,
    "try_times": 5
  },
  "task_results": {
    "sally_anne": {
      "accuracy": 0.833,
      "correct": 10,
      "total": 12,
      "misclassified": [
        {"story_index": 5, "expected": "basket", "predicted": "box"},
        {"story_index": 12, "expected": "basket", "predicted": "box"}
      ]
    },
    "smarties": {
      "accuracy": 0.767,
      "correct": 9,
      "total": 12,
      "misclassified": [...]
    }
  },
  "overall_accuracy": 0.800,
  "reasoning_analysis": {
    "step1_awareness_accuracy": 0.950,
    "step2_prediction_accuracy": 0.867,
    "step3_behavior_accuracy": 0.767
  }
}
```

### Key Metrics Explained:

- **accuracy**: Proportion of correct responses
- **correct/total**: Number correct out of total attempts
- **misclassified**: Detailed list of incorrect responses
- **overall_accuracy**: Combined performance across tasks
- **reasoning_analysis**: Breakdown by reasoning step

---

## 🔬 Using Ablation Results

### Example: Analyzing Prompt Effects

```bash
# Compare few-shot vs zero-shot
ablation/prompt_variations/few_shot/accuracy.json
ablation/prompt_variations/zero_shot/accuracy.json
```

**Typical Findings**:
- Few-shot prompting often improves accuracy by 5-15%
- Longer examples may cause attention dilution
- Task-specific examples help most

### Example: Token Limit Analysis

```bash
ablation/token_limits/short_512/accuracy.json
ablation/token_limits/medium_2048/accuracy.json
ablation/token_limits/long_4096/accuracy.json
```

**Typical Findings**:
- Short limits may truncate reasoning
- Optimal length varies by task
- Longer limits don't always help

---

## 📊 Using Comparison Results

### Model Architecture Comparison

```bash
compare/model_architectures/llama_vs_qwen/
```

**Expected Metrics**:
- Cross-architecture performance
- Scaling law analysis
- Efficiency vs accuracy tradeoffs

### Task Difficulty Analysis

```bash
compare/task_difficulty/basic_false_belief/
compare/task_difficulty/complex_narratives/
```

**Expected Findings**:
- Simple false beliefs: ~80%+ accuracy
- Complex narratives: ~60-75% accuracy
- Multi-step reasoning compounds errors

---

## 📋 Using Baseline Results

### Benchmark Comparison

```bash
results_pre/benchmarks/sally_anne_standard/
```

**Purpose**: Compare against established benchmarks.

**Typical Use Cases**:
- Validate new model performance
- Track performance improvements
- Identify regression issues

### Historical Tracking

```bash
results_pre/historical/2024_results/
results_pre/historical/2025_results/
```

**Purpose**: Monitor long-term trends.

**Key Trends to Track**:
- Performance improvements over time
- Model scaling effects
- Prompt engineering gains

---

## 📊 Cross-Directories Comparison

You can compare results across directories:

```
1. Ablation → Compare configurations
   - Which ablation variant works best?
   - What configurations cause regression?

2. Compare → Compare models
   - Which architecture performs best?
   - What's the scaling curve?

3. results_pre → Benchmark
   - How does this compare to standard?
   - Is performance within expected range?
```

---

## 🧪 Running Ablation Experiments

### Example: Prompt Variations

```bash
python generate_answers.py \
    --output_path ./ablation/prompt_variations/few_shot \
    --promptsA_path prompts/prompts.py \
    --promptsB_path prompts/prompts.py \
    --model_name mistralai/Mistral-7B-Instruct-v0.2 \
    --use_local \
    --local_model_path ./models/mistral-7b \
    --try_times 3

python generate_answers.py \
    --output_path ./ablation/prompt_variations/zero_shot \
    --promptsA_path "" \
    --promptsB_path "" \
    --model_name mistralai/Mistral-7B-Instruct-v0.2 \
    --use_local \
    --local_model_path ./models/mistral-7b \
    --try_times 3
```

---

## 📊 Analyzing Misclassifications

Each accuracy file may contain misclassification details:

```json
"misclassified": [
  {
    "story_index": 5,
    "expected": "basket",
    "predicted": "box",
    "model_response": "Sally would look in the box because...",
    "reasoning_trace": "Model confused Sally's belief with reality"
  }
]
```

**Analysis Tips**:
- Review model reasoning for error patterns
- Check if errors are task-specific
- Identify systematic biases

---

## 📈 Performance Thresholds

### Good Performance:
- Sally-Anne accuracy > 80%
- Smarties accuracy > 70%
- Overall accuracy > 75%

### Concerning Performance:
- Sally-Anne accuracy < 60%
- Smarties accuracy < 50%
- Overall accuracy < 60%
- Step 1 accuracy < 85% (awareness fails)

### Excellent Performance:
- Sally-Anne accuracy > 90%
- Smarties accuracy > 85%
- Step accuracy > 90% across all steps

---

## 🔍 Debugging Low Accuracy

If accuracy is low:

1. **Check token limits**: May be truncating responses
2. **Adjust temperature**: Try lower (more deterministic) or higher (more exploratory)
3. **Review prompts**: Ensure few-shot examples are clear
4. **Verify model loading**: Ensure correct model is loaded
5. **Check data loading**: Ensure CSV data is loaded correctly

---

## 📝 Summary

| Directory | Purpose | Use Case |
|-----------|---------|----------|
| **ablation/** | Test configuration effects | Understanding component impact |
| **compare/** | Compare different models | Architecture selection |
| **results_pre/** | Baseline benchmarks | Performance validation |

---

*This directory contains pre-computed and comparative results for analyzing Theor*y of Mind *performance across different configurations and models.*
