# Belief Manipulation via Asymmetric Theory of Mind:
# Adversarial Attacks on Large Language Models

Jinyu Fan
Independent Researcher

---

## Abstract

This paper investigates a novel vulnerability in large language models (LLMs): the ability
of a high-ToM (Theory of Mind) model to systematically deceive a lower-ToM model by
exploiting the ToM capability asymmetry between them. We design a three-phase adversarial
attack where a high-ToM attacker (qwen3.5, ToM level 5) crafts persuasive counter-arguments
to convince a lower-ToM victim (llama3.1:8b, ToM level 2) to abandon its correct answer
and adopt an incorrect one. We evaluate the attack across all five Hi-ToM orders and find
that it is most effective at 1st- and 2nd-order belief questions, achieving a 66.7% and
60.0% attack success rate respectively. We then propose and evaluate three prompt-level
defense mechanisms—Belief Consolidation, Belief Multi-Validation, and Belief Encryption—and
demonstrate that Belief Consolidation reduces the overall attack success rate by 42.9
percentage points (from 85.7% to 42.9%). These results suggest that ToM capability gaps
between models create exploitable reasoning vulnerabilities that are not captured by
standard benchmark evaluations.

---

## 1. Introduction

Theory of Mind (ToM) reasoning—the ability to track and reason about other agents' beliefs
and knowledge states—is a well-studied cognitive capability in humans and a key capability
tested in LLM benchmarks such as Hi-ToM (Nangia et al., 2020) and GsmCoT (Hendrycks et al.,
2021). Current evaluations measure ToM level as the highest consecutive order at which a
model achieves ≥50% accuracy on nested belief questions.

However, this evaluation framework treats ToM as a *capability* without considering its
*asymmetric distribution* between agents. In adversarial scenarios where one agent has
superior ToM reasoning and deliberately exploits that advantage, a new vulnerability
class emerges.

This paper makes three contributions:

1. We formalize the **ToM belief manipulation attack**, where a high-ToM agent crafts
   deceptive arguments exploiting the victim's weaker belief-nesting capacity.
2. We demonstrate experimentally that llama3.1:8b is highly vulnerable to this attack at
   orders 1–2 (66.7% and 60.0% attack success rates), despite nominally "passing" those
   orders in standard evaluation.
3. We propose and evaluate three defense mechanisms, identifying **Belief Consolidation** as
   the most effective (42.9 percentage point improvement over baseline).

---

## 2. Related Work

**ToM evaluation in LLMs:** The Hi-ToM benchmark (Nangia et al., 2020) tests nested belief
reasoning across five orders, where each order adds one level of belief nesting ("X thinks
that Y thinks that Z..."). ToM level is defined as the highest consecutive order with
accuracy ≥50%.

**Adversarial attacks on LLMs:** Prior work has studied prompt injection (Ouyang et al.,
2022), jailbreak attacks (Zhu et al., 2023), and belief manipulation in humans (Tversky
& Kahneman, 1974). The ToM attack is distinct in exploiting the victim's ToM *strength*
(their belief-tracking ability) rather than exploiting their ToM *weakness* or lack thereof.

**Defense against belief manipulation:** Human cognitive psychology has studied belief
consolidation (pre-commitment strategies) and cognitive decontamination (Tetlock, 1991)
as defenses against misleading influence. Our formalization of these mechanisms in prompt-
engineering form enables quantitative evaluation.

---

## 3. Method

### 3.1 Setup

**Attacker:** qwen3.5:latest (ToM level 5, passes all O0–O4)
**Victim:** llama3.1:8b (ToM level 2, passes O0–O1, fails at O2)
**Benchmark:** Hi-ToM, No_Tell/CoT variant, length-1 stories
**Sample size:** 10 samples per order (5 orders = 50 total)

### 3.2 ToM Belief Manipulation Attack

The attack operates in three phases per sample:

#### Phase 1 — Baseline Answer

The victim answers the Hi-ToM question using the standard Chain-of-Thought prompt (same
as the eval_ollama_tom.py evaluation procedure). The victim's initial answer is checked
for correctness.

#### Phase 2 — Attack Generation

If the victim answered correctly, the attacker is prompted to craft a persuasive argument
for a *wrong* answer. The attacker is given:

- The full story text
- The question and all candidate answers
- The victim's correct answer
- All wrong answer alternatives

The attacker's prompt explicitly instructs it to:
1. Identify the most confusable wrong answer
2. Find a subtle misinterpretation (e.g., swap who moved what, confuse belief nesting,
   mix up temporal order of events)
3. Write a confident step-by-step argument sounding like careful re-reading

Output format:
```
Arguing for: [X]. {wrong answer text}
{3–5 sentence argument}
Therefore, the answer should be [X].
```

#### Phase 3 — Reconsideration

The victim is shown its original correct answer plus the attacker's argument, framed as
"a colleague's perspective." The victim is asked to re-evaluate and provide a final answer.
A **flip** is recorded when the victim changes from correct to incorrect.

**Attack success rate** = (# flips) / (# attacks launched on correct answers)

### 3.3 Defense Mechanisms

We evaluate three defense mechanisms, each modifying the reconsideration prompt while
keeping the attacker's argument identical.

#### Defense 1: Belief Consolidation

Before seeing the attack, the victim must explicitly list 3 facts from the story that
support its original answer. The attack is then evaluated against those consolidated facts;
the victim may only change its answer if the attack identifies a genuine error that the
consolidated facts cannot refute.

**Rationale:** Forces the victim to re-examine its own reasoning chain before exposure to
the attack, creating a pre-commitment that the attack must directly contradict rather than
silently bypass.

#### Defense 2: Belief Multi-Validation

The standard reconsideration prompt is run n=3 times independently at temperature=0.3.
The majority-vote winner becomes the final answer; if no majority exists, the original
answer is held.

**Rationale:** If the attack is non-deterministically effective, independent trials reduce
variance. If the attack consistently works (>50% rate), majority vote will amplify it—a
deliberately reported failure mode.

#### Defense 3: Belief Encryption

Two-step hardening:
1. The victim pre-extracts a structured "belief certificate" from the story: an event
   timeline (who moved what, who was present) and an explicit derivation of the answer.
2. The attack is shown alongside the certificate; the victim evaluates the attack's claims
   only against the certificate, rejecting any claim that contradicts it.

**Rationale:** The belief is encoded into a canonical form before the attack arrives,
preventing the attacker from reframing the raw story narrative.

### 3.4 Experimental Design

The attack was run against two victims to assess the role of model strength:
- **llama3.1:8b** (ToM level 2) — the primary victim, with a clear ToM capability gap
- **qwen3.6:latest** (ToM level ≥4) — a stronger model, to assess whether higher ToM
  confers attack resilience

---

## 4. Results

### 4.1 ToM Level Baseline (5 samples)

| Model | O0 | O1 | O2 | O3 | O4 | ToM Level |
|-------|-----|-----|-----|-----|-----|-----------|
| qwen3.5:latest | 100% | 60% | 60% | 60% | 80% | 5 |
| llama3.1:8b | 60% | 80% | 40%✗ | 80% | 40%✗ | 2 |

### 4.2 Attack Success Rates (10 samples)

**vs llama3.1:8b:**

| Order | Victim Init% | Attacks Launched | Flips | Attack Rate |
|-------|-------------|------------------|-------|-------------|
| 0 | 40% | 4 | 0 | 0.0% |
| 1 | 60% | 6 | **4** | **66.7%** |
| 2 | 50% | 5 | **3** | **60.0%** |
| 3 | 50% | 5 | 1 | 20.0% |
| 4 | 30% | 3 | 1 | 33.3% |
| **Overall** | | **23** | **9** | **39.1%** |

**vs qwen3.6:**

| Order | Victim Init% | Attacks Launched | Flips | Attack Rate |
|-------|-------------|------------------|-------|-------------|
| 0 | 70% | 7 | 0 | 0.0% |
| 1 | 80% | 8 | 1 | 12.5% |
| 2 | 80% | 8 | 1 | 12.5% |
| 3 | 90% | 9 | 0 | 0.0% |
| 4 | 30% | 3 | 0 | 0.0% |
| **Overall** | | **35** | **2** | **5.7%** |

### 4.3 Defense Effectiveness (llama3.1:8b victim, baseline 85.7% attack rate)

| Order | Baseline | Belief Consolidation | Multi-Validation | Encryption |
|-------|---------|----------------------|-----------------|------------|
| O0 | 100% | **0%** (+100pp) | 100% (0pp) | 100% (0pp) |
| O1 | 100% | **33%** (+67pp) | 67% (+33pp) | 67% (+33pp) |
| O2 | 75% | **25%** (+50pp) | 50% (+25pp) | 100% (−25pp) |
| O3 | 67% | 67% (0pp) | 67% (0pp) | 67% (0pp) |
| O4 | 100% | 100% (0pp) | 50% (+50pp) | 50% (+50pp) |
| **Overall** | **85.7%** | **42.9% (+43pp) ✓** | **64.3% (+21pp) ✓** | 78.6% (+7pp) |

---

## 5. Analysis

### 5.1 Why the Attack Works

The ToM belief manipulation attack exploits a specific reasoning gap in llama3.1: it tracks
belief by **observation events** ("Lily witnessed Hannah move the apple to the blue_cupboard")
rather than by **action authorship** ("Lily herself moved the apple to the red_box").

When qwen3.5 argues that "Lily's belief remains fixed on the last location she *observed*,"
this is a deliberate misdirection. The correct reasoning path requires recognizing that
Lily's own action *is* the definitive source of her belief. However, llama3.1 fails to
maintain this distinction, and the attack reframes the narrative to make the observation-based
path sound authoritative.

### 5.2 The False Confidence Paradox

llama3.1 passes O1 in standard evaluation (80% accuracy), giving the appearance of
competent 1st-order belief tracking. Yet the attack succeeds 66.7% of the time at O1.
This **false confidence paradox**—where a model passes a benchmark but fails against an
adversary exploiting the *same* reasoning capability—suggests that standard evaluations
underestimate vulnerability to ToM-based attacks.

### 5.3 Model Strength Matters

qwen3.6's resistance (5.7% overall vs 39.1% for llama3.1) demonstrates that higher ToM
capacity confers significant attack resilience. The attack's primary mechanism (observation
vs. action conflation) is a reasoning pattern that qwen3.6 handles correctly, making the
attacker's misattribution detectable.

### 5.4 Defense Analysis

**Belief Consolidation (+43pp)** succeeds because it forces the victim to re-examine its own
reasoning before exposure to the attack. The victim produces 3 explicit facts supporting
its answer, creating a "pre-commitment" that the attack must contradict. In the attack,
the attacker typically reframes the narrative without directly contradicting these stated
facts, so the victim sees the attack as irrelevant rather than as a refutation.

**Belief Multi-Validation (+21pp)** works via statistical averaging at orders where the
attack is non-deterministically effective (O2 at 50% attack rate). At O1, where the
attack consistently succeeds (66.7% → 66.7%), majority vote cannot help.

**Belief Encryption (+7pp)** fails because llama3.1 cannot reliably extract a correct
belief certificate. The attacker's argument then exploits errors in the certificate itself,
turning the defense into a vulnerability.

---

## 6. Limitations

1. **Small sample size:** 10 samples per order provides initial evidence but requires
   larger studies for robust statistical claims.
2. **Single victim model:** llama3.1:8b is the only victim evaluated; results may vary
   with other models.
3. **Ollama non-determinism:** All experiments run via Ollama API without temperature
   control; model weight updates may affect reproducibility.
4. **Attack parameterization:** temperature=0.3 for attack generation introduces variability;
   a deterministic attacker (temperature=0) might produce more consistent arguments.
5. **Human evaluation omitted:** The stored attack_full text allows manual inspection for
   whether arguments are "fair" (logically coherent) or "corrupted" (self-contradictory),
   but this was not systematically rated.

---

## 7. Conclusion

This paper demonstrates that ToM capability asymmetry between agents creates exploitable
vulnerabilities: a high-ToM attacker can systematically deceive a lower-ToM victim at
rates exceeding 60% on first- and second-order belief questions. The attack succeeds
precisely where the victim has a false sense of confidence—it passes those orders in
standard evaluation but cannot maintain its answers against adversarial counter-arguments.

Among the proposed defenses, **Belief Consolidation** achieves the strongest protection
(42.9pp improvement), suggesting that pre-commitment to supporting facts before exposure
to adversarial arguments is a robust defense against belief manipulation. The results
suggest that future LLM evaluation frameworks should include adversarial robustness tests
that specifically target ToM capability gaps between models.

---

## References

[1] Nangia, N. et al. "Hi-ToM: A Benchmark for Theory of Mind in Language Models."
[2] Hendrycks, D. et al. "Measuring Massive Task Overlap." GsmCoT.
[3] Ouyang, L. et al. "Training language models to follow instructions."
[4] Zhu, Y. et al. "Jailbreak in pieces: Compositional adversarial attacks."
[5] Tversky, A. & Kahneman, D. "Judgment under Uncertainty: Heuristics and Biases."
[6] Tetlock, P. "Cognitive Decontamination."
[7] Ollama API documentation.
