# Results (120-sample run)

**Setup:** 3 models (`glm4:9b`, `qwen2.5:7b`, `llama3.1:8b`) × 12 scenarios (S01-S12, see
[`README.md`](README.md) for the matrix) × 2 argument types (`false_argument` = the attack,
`true_argument` = an honest control) × 120 samples = 72 runs, 8,640 model calls total (FC scenarios
use 2 calls/sample, everything else 1).

**Provenance:** raw stdout for every run is in [`logs/batch_by_model_20260624_012800/`](logs/batch_by_model_20260624_012800/);
per-scenario accuracy is aggregated in [`results/`](results/) (`13scenarios_summary_*.json`, one per
model × argument-type, plus a flat `accuracy_summary.csv`). Regenerate the tables below with
`python3 summarize_results.py`.

## Defense success rate under the attack (`false_argument`), averaged across the 3 models

| Defense strategy | No warning | Weak warning | Strong warning |
|---|---|---|---|
| Baseline | 24.4% | 32.2% | 53.9% |
| OneShot | 29.2% | 37.2% | 56.4% |
| CoT | 42.2% | 46.1% | 63.0% |
| **FC** | **55.0%** | **52.2%** | 57.8% |

**FC is the only strategy that's stable across all three models.** Relative to the no-defense
baseline, FC is the sole strategy that reaches ≥15 percentage-point improvement on *every* model
under no-warning (27.5–34.2pp) and weak-warning (15.8–24.2pp). OneShot and CoT each clear that bar
on at most one model — e.g. CoT gives GLM4 +32.5pp under no warning but only +8.3pp on Llama3.1.
Under a strong warning, no strategy clears 15pp on all three models; the warning itself already
does most of the work (baseline jumps from ~24-32% to ~54%), so additional defenses have little
headroom left. See `figures/fig3_defense_stability.png` for the per-model breakdown.

## True vs. false argument (is the model actually reading the argument?)

Swapping `false_argument` for `true_argument` (same length, argues for the correct answer instead)
isolates whether a defense is genuinely evaluating the argument's content or just learning to
distrust/ignore it outright. Averaged across all 4 strategies and 3 models:

| Warning level | FALSE arg | TRUE arg | Δ |
|---|---|---|---|
| No warning | 37.7% | 88.6% | 50.9pp |
| Weak warning | 42.0% | 85.0% | 43.1pp |
| Strong warning | 57.8% | 70.6% | 12.8pp |

Only the **strong-warning** condition brings FALSE/TRUE within 15pp of each other on every
strategy (11.1–15.0pp, see `figures/fig2_defense_balance_true_false.png`) — i.e. it's the only
condition where the model treats the argument's content, not just its presence, as the deciding
factor. Under no/weak warning the gap ranges from 13.3pp (Qwen2.5, FC, no warning — FC's one
near-balanced case) up to 73.4pp (Qwen2.5, Baseline, no warning): models are picking up on argument
*validity* very inconsistently, and mostly succeed on `true_argument` by coincidence (it agrees with
what the story already supports) rather than by verifying it.

One anomaly: **Llama3.1 under strong warning** is the only case where TRUE argument scores *lower*
than FALSE (Baseline: 53.3% vs 66.7%, -13.4pp) — the strong-warning instruction appears to make it
distrust the argument so hard it sometimes talks itself out of a correct one.

## Per-model, per-scenario detail

### GLM4:9b

| Scenario | False Arg | True Arg | Δ |
|------|-----------|----------|------|
| No warning – Baseline | 25.8% | 94.2% | +68.4pp |
| No warning – OneShot | 24.2% | 91.7% | +67.5pp |
| No warning – CoT | 58.3% | 90.0% | +31.7pp |
| No warning – FC | 53.3% | 89.2% | +35.9pp |
| Weak warning – Baseline | 32.5% | 92.5% | +60.0pp |
| Weak warning – OneShot | 35.0% | 90.0% | +55.0pp |
| Weak warning – CoT | 59.2% | 88.3% | +29.1pp |
| Weak warning – FC | 52.5% | 89.2% | +36.7pp |
| Strong warning – Baseline | 53.3% | 82.5% | +29.2pp |
| Strong warning – OneShot | 49.2% | 75.8% | +26.6pp |
| Strong warning – CoT | 62.5% | 81.7% | +19.2pp |
| Strong warning – FC | 57.5% | 85.8% | +28.3pp |

### Qwen2.5:7b

| Scenario | False Arg | True Arg | Δ |
|------|-----------|----------|------|
| No warning – Baseline | 20.8% | 94.2% | +73.4pp |
| No warning – OneShot | 21.7% | 85.8% | +64.1pp |
| No warning – CoT | 33.3% | 89.2% | +55.9pp |
| No warning – FC | 55.0% | 68.3% | +13.3pp |
| Weak warning – Baseline | 25.0% | 90.8% | +65.8pp |
| Weak warning – OneShot | 22.5% | 80.8% | +58.3pp |
| Weak warning – CoT | 34.2% | 86.7% | +52.5pp |
| Weak warning – FC | 49.2% | 66.7% | +17.5pp |
| Strong warning – Baseline | 41.7% | 59.2% | +17.5pp |
| Strong warning – OneShot | 50.0% | 69.2% | +19.2pp |
| Strong warning – CoT | 55.8% | 57.5% | +1.7pp |
| Strong warning – FC | 49.2% | 60.0% | +10.8pp |

### Llama3.1:8b

| Scenario | False Arg | True Arg | Δ |
|------|-----------|----------|------|
| No warning – Baseline | 26.7% | 95.0% | +68.3pp |
| No warning – OneShot | 41.7% | 89.2% | +47.5pp |
| No warning – CoT | 35.0% | 94.2% | +59.2pp |
| No warning – FC | 56.7% | 81.7% | +25.0pp |
| Weak warning – Baseline | 39.2% | 84.2% | +45.0pp |
| Weak warning – OneShot | 54.2% | 84.2% | +30.0pp |
| Weak warning – CoT | 45.0% | 91.7% | +46.7pp |
| Weak warning – FC | 55.0% | 75.0% | +20.0pp |
| Strong warning – Baseline | 66.7% | 53.3% | **-13.4pp** |
| Strong warning – OneShot | 70.0% | 65.8% | -4.2pp |
| Strong warning – CoT | 70.8% | 84.2% | +13.4pp |
| Strong warning – FC | 66.7% | 72.5% | +5.8pp |

## Cross-model comparison

### False argument (the attack)

| Scenario | GLM4 | Qwen2.5 | Llama3.1 |
|------|------|---------|----------|
| No warning – Baseline | 25.8% | 20.8% | 26.7% |
| No warning – OneShot | 24.2% | 21.7% | 41.7% |
| No warning – CoT | 58.3% | 33.3% | 35.0% |
| No warning – FC | 53.3% | 55.0% | 56.7% |
| Weak warning – Baseline | 32.5% | 25.0% | 39.2% |
| Weak warning – OneShot | 35.0% | 22.5% | 54.2% |
| Weak warning – CoT | 59.2% | 34.2% | 45.0% |
| Weak warning – FC | 52.5% | 49.2% | 55.0% |
| Strong warning – Baseline | 53.3% | 41.7% | 66.7% |
| Strong warning – OneShot | 49.2% | 50.0% | 70.0% |
| Strong warning – CoT | 62.5% | 55.8% | 70.8% |
| Strong warning – FC | 57.5% | 49.2% | 66.7% |

### True argument (control)

| Scenario | GLM4 | Qwen2.5 | Llama3.1 |
|------|------|---------|----------|
| No warning – Baseline | 94.2% | 94.2% | 95.0% |
| No warning – OneShot | 91.7% | 85.8% | 89.2% |
| No warning – CoT | 90.0% | 89.2% | 94.2% |
| No warning – FC | 89.2% | 68.3% | 81.7% |
| Weak warning – Baseline | 92.5% | 90.8% | 84.2% |
| Weak warning – OneShot | 90.0% | 80.8% | 84.2% |
| Weak warning – CoT | 88.3% | 86.7% | 91.7% |
| Weak warning – FC | 89.2% | 66.7% | 75.0% |
| Strong warning – Baseline | 82.5% | 59.2% | 53.3% |
| Strong warning – OneShot | 75.8% | 69.2% | 65.8% |
| Strong warning – CoT | 81.7% | 57.5% | 84.2% |
| Strong warning – FC | 85.8% | 60.0% | 72.5% |

## Figures

Generated by `figures/generate_*.py` from `results/*.json`; see each script for the exact
computation.

- **`fig1_defense_accuracy_by_warning.png`** — absolute accuracy of all 4 strategies × 3 models,
  one panel per warning level.
- **`fig2_defense_balance_true_false.png`** — FALSE vs. TRUE argument accuracy per strategy
  (averaged over models), with the Δ annotated per bar pair. This is the source for the
  true/false-balance table above.
- **`fig3_defense_stability.png`** — per-model improvement (pp) of OneShot/CoT/FC over baseline,
  with a 15pp reference line, one panel per warning level. This is the source for the
  stability claims above.

## Caveat

Per-sample detail JSONs (individual model responses, not just aggregate accuracy) were lost for
this run — `main_defense.py` didn't create `results/` before writing to it (fixed now, see the
`os.makedirs` call in `main()`). The raw terminal logs in `logs/` are the only surviving record of
the actual model outputs; the numbers above were reconstructed from the `"Completed: N/120 correct"`
lines in those logs and cross-checked against `results/*.json`.
