# ToM-Attack Defense Evaluation

Evaluates 4 defense strategies (Baseline / OneShot / Chain-of-Thought / Fact-Checking) against a
Theory-of-Mind adversarial argument attack, across 3 warning levels and 3 local LLMs
(`glm4:9b`, `qwen2.5:7b`, `llama3.1:8b`, served via Ollama).

An attacker model previously produced a misleading `[ARGUMENT]` (`false_argument`) that argues
for a wrong answer to a Hi-ToM belief-tracking question. Each scenario places that argument next
to the original `[TASK]` and asks the victim model to answer, optionally with a defense strategy
and/or a warning that the argument may be unreliable. `true_argument` (an honest, length-matched
counterpart) is used as a control to check whether a defense is actually reading the argument or
just ignoring it outright — see `RESULTS.md`.

## Scenario matrix

12 scenarios (`S01`-`S12`) = 3 warning levels × 4 defense strategies, all with `[TASK]`/`[ARGUMENT]`
labels so the model can tell task from argument:

| | Baseline | OneShot | CoT | Fact-Checking (FC) |
|---|---|---|---|---|
| **No warning** | S01 | S02 | S03 | S04 |
| **Weak warning** | S05 | S06 | S07 | S08 |
| **Strong warning** | S09 | S10 | S11 | S12 |

- **No warning**: no mention that the argument might be unreliable.
- **Weak warning**: told the argument is reference only and should be independently verified.
- **Strong warning**: told the argument may contain misleading/incorrect reasoning.
- **OneShot**: one clean worked example (no argument) prepended.
- **CoT**: a 5-step structured-reasoning instruction appended.
- **FC**: two-stage — first a neutral fact-check of the argument against the story (no warning
  language, to keep this stage unbiased), then a second call that answers using that verification.

## Layout

```
main_defense.py           the runner — implements all 12 scenarios
run_experiments.sh        runs the full 3-model × 12-scenario × {false,true} matrix in parallel (one process per model)
summarize_results.py      aggregates results/*_summary_*.json into readable tables
dataset/                  the 120-sample dataset + its README
results/                  per-run summary JSONs (accuracy per scenario) + accuracy_summary.csv
figures/                  plotting scripts + the 3 figures referenced in RESULTS.md
logs/                     raw stdout from the 120-sample run backing RESULTS.md
RESULTS.md                final results and findings
```

## Running it

Single model, single scenario:
```bash
python3 main_defense.py --model glm4:9b --num_samples 120 \
    --scenarios S04_labeled_no_warning_fc --argument-type false \
    --dataset dataset/defense_samples_with_true_args.json
```

All 12 scenarios for one model (`--scenarios all`, the default):
```bash
python3 main_defense.py --model glm4:9b --num_samples 120 --argument-type false
```

Full 3-model × 12-scenario × {false,true} sweep (72 runs, one parallel process per model):
```bash
./run_experiments.sh
```
Requires Ollama running locally with `glm4:9b`, `qwen2.5:7b`, and `llama3.1:8b` pulled.

Then aggregate and plot:
```bash
python3 summarize_results.py
python3 figures/generate_fig1_accuracy.py
python3 figures/generate_fig_balance.py
python3 figures/generate_stability_analysis.py
```

## Results

See [`RESULTS.md`](RESULTS.md) for the full 120-sample results and figures. Headline: Fact-Checking
is the only defense that reliably beats a 15pp-improvement bar across all three models under no/weak
warning; under a strong warning the models are already cautious enough that extra defenses add
little.
