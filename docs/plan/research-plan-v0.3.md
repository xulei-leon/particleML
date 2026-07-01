# Research Plan v0.3

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-06-30; review-confirm patch applied 2026-07-01; ARS compact audit addendum applied 2026-07-01
- Verification Status: UNVERIFIED
- Version Label: research_plan_v0.3.2
- Source Inputs:
  - `docs/plan/research-plan-v0.1.html`
  - `docs/plan/research-plan-v0.2.html`
  - `docs/plan/research-plan-v0.2-proposal.md`
  - `docs/plan/research-plan-v0.2-eval-memo.md`
  - `var/draft-v0.3.md`
  - `docs/4-Reviews/research-plan-v0.3-review-confirm.md`
  - ARS compact editorial audit, 2026-07-01

## Title

**Feature Availability in Fine-Tuning Jet Foundation Models: Controlled Ablations on JetClass Top Tagging**

Short title:

**Feature Availability in Jet Foundation Model Fine-Tuning**

## 0. Executive Summary

This project studies how the set of particle-level input features available during downstream fine-tuning affects the performance, data efficiency, and interpretability of a pretrained OmniLearned PET-style jet foundation model on JetClass binary top tagging.

Version 0.3 narrows the project from a general feature-importance or architecture-benchmarking study into a controlled **feature-availability study**:

> Under a fixed JetClass top-vs-QCD fine-tuning protocol, how much do different nested particle-level feature sets improve a pretrained OmniLearned PET-style backbone?

The central methodological change is that the main intervention is **fine-tune without X**, not **post-hoc mask X at test time**. For every feature configuration, the model is trained, validated, and tested under the same reduced feature view. This makes the experiment a downstream feature-availability study rather than a test-time robustness diagnostic.

The main claim should be written conservatively:

> We quantify how downstream feature availability affects the performance and data efficiency of a fine-tuned pretrained OmniLearned PET-style jet foundation model on JetClass top tagging.

The paper should not claim universal causal feature importance. The result measures empirical feature-availability effects under one controlled dataset, task, checkpoint, input-adaptation rule, and fine-tuning protocol.

### Execution Status After ARS Audit

The research direction is approved as a thesis/paper plan, but the project is not E1-ready until E0 and E0.5 are completed. The next useful action is execution, not further scope expansion.

Blocking gates before E1:

1. Verify the `pretrain_s` checkpoint artifact, license, hash, input schema, and adapter-swap feasibility.
2. Freeze Config D from real JetClass columns and pass the leakage audit.
3. Use E1 measurements to set GPU-hour, memory, storage, and dollar-budget gates.

If any blocking gate fails, keep the project alive by downgrading claims rather than adding scope.

## 1. What Changed from v0.2

v0.2 already made several good decisions: JetClass binary top tagging was fixed as the core task, the project moved away from broad model benchmarking, and the feature ladder A-D became the main experimental variable.

v0.3 keeps those decisions and clarifies four points:

| Area | v0.2 Direction | v0.3 Revision |
|---|---|---|
| Scientific framing | Input feature representations in jet foundation models | Downstream feature availability during OmniLearned PET-style fine-tuning |
| Main intervention | Feature ablation, not always fully specified | Separate fine-tuning run for each feature configuration |
| Claim boundary | Feature richness affects performance and data efficiency | Effect is conditional on fixed fine-tuning protocol, not universal causal feature importance |
| Run matrix | A-D x several data scales x seeds, with controls | 36-run core matrix first; expand only through decision gates (see Section 12) |

The working hierarchy is:

1. **Feature configuration is the primary research axis.**
2. **Labeled-data scale is the secondary axis for data efficiency.**
3. **Architecture and initialization are controls, not the main narrative.**
4. **External transfer is future work unless the core paper is already stable.**

## 2. Research Questions

### RQ1: Feature Availability

In JetClass binary top tagging, how does the performance of a fine-tuned pretrained OmniLearned PET-style backbone change across nested particle-level feature configurations A-D?

Required evidence:

- Same raw JetClass source files.
- Same train/validation/test manifest.
- Same preprocessing and normalization rules.
- Same optimizer, epoch budget, early stopping rule, and seed list.
- Separate fine-tuning runs for each feature configuration.

### RQ2: Data Efficiency

Do richer particle-level feature sets improve labeled-data efficiency, meaning that they reach a given AUC or background-rejection level with fewer labeled fine-tuning examples?

Required evidence:

- A-D repeated at fixed training sizes.
- Validation and test sets held fixed across training sizes.
- Data-efficiency statistic reported explicitly, not only qualitatively.

Primary statistic:

```text
auc_gap_fraction(config, n) =
    (AUC(config, n) - 0.5) / (AUC(config, n_max) - 0.5)
```

where `n` is the labeled training size per class and `n_max = 10^5` jets per class in the core study. This is a fraction of the largest measured AUC gap, not a claim that 10^5 jets per class is saturated full-data performance. Uncertainty for this ratio should be estimated by paired bootstrap from saved predictions; if the denominator is unstable, report raw AUC differences instead.

### RQ3: Robustness of Feature Ranking

Is the A-D feature ranking stable across random seeds, data scale, and at least one lightweight non-OmniLearned baseline?

Required evidence for the minimum strong version:

- At least 3 seeds for every core condition.
- Key comparisons expanded to 5 seeds if differences are close to the statistical noise floor.
- For a publication-strength version, one lightweight sanity baseline, preferably the fixed Deep Sets/PFN-style baseline specified in Section 7.

Optional evidence:

- Random-initialized OmniLearned control for A vs D, or A/C/D, at the largest data scale.

## 3. Claim Boundary

The main paper should use a strict claim hierarchy.

| Claim | Status | Evidence Needed |
|---|---|---|
| Feature availability affects downstream fine-tuning performance | Required | A-D core matrix on fixed JetClass top/QCD split |
| Feature availability affects data efficiency | Required | A-D repeated across fixed training sizes |
| Feature ranking is not only an OmniLearned checkpoint artifact | Required for publication-strength version; deferrable for thesis-only MVP | Fixed Deep Sets/PFN-style baseline |
| Pretraining changes label efficiency | Optional | Matched random-init OmniLearned control |
| Feature conclusions transfer across datasets | Future work | External dataset with explicit schema mapping |

Recommended wording:

> Our results measure feature-availability effects under a fixed fine-tuning protocol. They should not be interpreted as universal causal estimates of the physical importance of individual particle features.

Avoid these claims:

- "PID universally causes better jet-tagging performance."
- "The feature set is the best representation for all jet foundation models."
- "The experiment identifies the causal physical contribution of each feature."
- "The study is a broad benchmark of jet foundation-model architectures."

## 4. Dataset and Task

### Primary Dataset

The primary dataset is JetClass. The formal study uses binary classification:

| Item | Decision |
|---|---|
| Task | Hadronic top jets vs QCD jets |
| Input unit | Jet represented as a masked particle set |
| Split | Official JetClass train/validation/test split if available in the selected files; otherwise a documented custom manifest with fixed seed |
| Labels | Binary top-vs-QCD rule frozen after E0 |
| Leakage control | No event may appear in more than one split |
| Evaluation | Same fixed test set for all conditions |

### Data Acquisition and Storage

Use the official JetClass Zenodo record as the source of truth for file provenance. The full compressed release is about 189.8 GB, so E0 must decide whether the study downloads only the top/QCD files needed for the binary task or stages the larger 10-class release for future work.

| Item | E0 Decision Required |
|---|---|
| Source | JetClass Zenodo DOI / file list and download date |
| File scope | Top+QCD files only for the core study unless full-release storage is already available |
| Storage location | Local external SSD, cloud attached disk, or object storage; do not commit raw data |
| Dev slice | A small 1-5 GB fixed slice for E0/E1 debugging |
| Formal subset | Fixed train/validation/test manifest for each training size |
| File provenance | SHA-256 or equivalent hash for every staged source file |
| Cost gate | If projected storage plus GPU cost exceeds the budget cap in Section 11, cut E3 controls before cutting E2 A-D coverage |

### Training Sizes

The core matrix uses absolute per-class training sizes rather than vague percentages:

| Label | Training Size |
|---|---:|
| Small | 10^3 jets per class |
| Medium | 10^4 jets per class |
| Large | 10^5 jets per class |

The validation and test sets should remain unchanged across training-size conditions. If hardware constraints require smaller test samples during pilot work, the formal evaluation sample must still be fixed before E2 begins.

### Data Audit Requirement

No formal result should be reported until the E0 data audit records:

1. HDF5 groups and available particle-level columns.
2. Particle tensor shape.
3. Padding convention.
4. Mask convention.
5. Label extraction rule for top vs QCD.
6. Class balance for train, validation, and test.
7. Manifest hash.
8. Dataset file-set hash.
9. Preprocessing version.
10. Normalization statistics source.
11. Feature dictionary for configurations A-D.
12. Config D leakage-audit result.

## 5. Feature Configurations

The feature ladder must be nested. Each configuration contains all fields from the previous configuration plus one additional feature group.

| Config | Particle-Level Input | Purpose |
|---|---|---|
| A | Kinematics only | Baseline value of four-momentum information |
| B | A + charge | Incremental value of electric charge |
| C | B + PID | Incremental value of particle identity |
| D | C + provisional impact-parameter / vertex-quality observables | Strongest allowed detector-level representation |

Config D must be frozen after E0. Before E0, use this provisional target, aligned with the four additional features documented by OmniLearned:

```text
D_candidate = C + {d0-like impact parameter, d0 uncertainty,
                   dz-like longitudinal impact parameter, dz uncertainty}
```

The exact names must come from the selected JetClass HDF5 files. If the staged files expose these columns under transformed names, such as `tanh_d0`, `d0err`, `tanh_dz`, or `dzerr`, E0 must record both the source column and the transformed training column. If these columns are absent or ambiguously defined, Config D falls back to Config C and the paper should report A-C only for the feature ladder.

Final Config D may include only particle-level observables that:

- are present for every selected event or have a documented missing-value rule;
- have a documented JetClass source column;
- can be computed without class labels;
- do not use generator ancestry, target labels, or post-hoc top/QCD indicators.

Truth-level variables, label-derived variables, and target-dependent engineered features are excluded.

E0 leakage audit for each Config D candidate:

1. Record source column, physical interpretation, units or transform, missing-value rule, and whether the feature is truth-level or label-derived.
2. Train a tiny fixed probe on that candidate group alone using the E0 dev slice; the goal is not a publishable result, only to flag suspicious leakage.
3. Repeat the probe after label shuffling. The shuffled-label AUC 95% bootstrap interval must contain 0.5; otherwise the probe or split is invalid.
4. Train the same tiny probe on a trivial kinematics-only view. If a candidate-only probe exceeds the trivial kinematics-only probe by more than 0.02 absolute AUC on the E0 dev slice, exclude it unless a domain review explicitly justifies why the feature is physically legitimate and not target leakage.

## 6. Main Fine-Tuning Protocol

### Definition of Fine-Tune Without X

For every feature configuration, the model must be trained, validated, and tested using that feature configuration only.

This is allowed:

```text
pretrained checkpoint -> config-specific fine-tuning -> config-specific evaluation
```

This is not a main result:

```text
full-feature fine-tuning -> test-time mask feature X -> evaluate delta_AUC
```

Post-hoc test-time masking may be used only as an appendix-level robustness diagnostic. It should not appear as the central evidence for RQ1.

If post-hoc masking produces a feature ranking that conflicts with the fine-tune-without-X ranking, report that discrepancy as a diagnostic result and keep the fine-tuned results as the primary evidence.

### Preferred Implementation: Feature-Specific Input Adapter

Each feature configuration should have its own input projection or input adapter:

1. Build a config-specific input adapter. The default adapter is one linear projection over concatenated normalized continuous features plus one-hot categorical fields; any learned PID embedding is a separate ablation, not the default.
2. Randomly initialize the config-specific input adapter.
3. Load pretrained weights for every non-input layer that is shape-compatible.
4. Log every skipped or mismatched layer name, tensor shape, and reason in the run record.
5. Fine-tune the full model end to end.
6. Use the same split, optimizer, scheduler, batch size policy, early stopping rule, and seeds.

This is the recommended implementation because it avoids carrying full-feature input-layer weights into reduced-feature models.

Suggested methods wording:

> For each feature configuration, the input adapter was initialized from scratch while all compatible non-input backbone weights were initialized from the same pretrained OmniLearned checkpoint. The full network was then fine-tuned end to end under the corresponding feature view.

### E0.5: Adapter-Loading Spike

E1 may not start until E0.5 passes. This spike is a 1-3 day engineering gate, not a formal physics experiment.

Required checks:

| Check | Pass Criterion |
|---|---|
| Checkpoint artifact | Primary checkpoint downloaded or located, with SHA-256, license, and source URL recorded |
| Non-input weight loading | All expected non-input layers load, or every skipped layer is logged with a reason |
| A/B/C/D forward pass | Each feature configuration produces finite logits on the E0 dev slice |
| Gradient flow | A one-batch backward pass produces finite gradients in trainable layers |
| Tiny fine-tune | One tiny epoch decreases training loss relative to the first batch |
| Fallback decision | Adapter-swap is either approved as primary or fixed-dimension neutralization is chosen before E1 |

### Acceptable Fallback: Fixed Full-Dimension Neutralization

If checkpoint loading or code structure requires a fixed full input dimension, keep the full dimension but neutralize unavailable features throughout training, validation, and testing.

Rules:

| Feature Type | Neutralization Rule |
|---|---|
| Standardized continuous variables | Set to 0, the training-set mean after standardization |
| One-hot PID | Set all PID bits to 0 for unavailable PID |
| Charge | Prefer adapter removal; if neutralized, set to 0 and run the fallback sensitivity check below |
| Masks | Keep particle masks independent of feature availability |

This fallback is weaker than feature-specific adapters because the full-feature input layer still enters the reduced-feature run. If used, the paper must state this limitation clearly.

Fallback sensitivity check:

- If adapter-swap works for Config B, compare Config B under adapter-swap and fixed-dimension neutralization on a small E1 setting.
- If the AUC difference exceeds the seed-level spread, treat adapter-swap as primary and report neutralization only as a diagnostic.
- If adapter-swap fails entirely, log the failed layers and state the residual input-layer contamination risk in Limitations.

## 7. Models and Controls

### Main Model

The main experimental system is a pretrained OmniLearned PET-style backbone compatible with masked variable-length particle sets.

Primary checkpoint candidate:

| Field | Value to Freeze Before E1 |
|---|---|
| Repository | `https://github.com/ViniciusMikuni/OmniLearned` |
| Checkpoint tag | `pretrain_s` as the first candidate; `pretrain_m` only if `pretrain_s` is unavailable or too weak |
| Exact artifact | Weight file path or release asset recorded during E0.5 |
| SHA-256 | Computed after download during E0.5 |
| License | Repository and weight license recorded during E0.5 |
| Pretraining corpus | Recorded from the checkpoint documentation; explicitly state whether JetClass overlaps with the fine-tuning task |
| Input schema | Input dimensionality, normalization, PID/charge encoding, and mask convention recorded during E0.5 |
| Output head | Replace or reinitialize for binary top-vs-QCD fine-tuning |
| Backup plan | If no compatible pretrained checkpoint loads, convert the paper to a supervised OmniLearned-architecture feature-ablation study and remove pretrained-transfer claims |

Pretraining-overlap rule:

If the checkpoint was pretrained on JetClass or a corpus containing the same top/QCD task family, the paper must describe the study as **downstream adaptation under controlled feature availability**, not as out-of-domain transfer. This limitation belongs in Methods and Limitations.

| Model Condition | Role |
|---|---|
| Pretrained OmniLearned PET-style backbone, fine-tuned end to end | Main system |
| Fixed Deep Sets/PFN-style baseline | Low-cost sanity check for feature ranking |
| Random-initialized OmniLearned PET-style backbone | Optional initialization control |
| ParticleNet, ParT, or broader architecture benchmark | Deferred unless core paper is complete |

The study should not attempt to prove global architecture superiority. The OmniLearned PET-style model is the main measurement instrument; the baseline checks whether the feature trend is obviously architecture-specific.

Baseline specification:

- Default baseline: in-repo Deep Sets/PFN-style model with masked particle pooling.
- Input adapter: same A-D feature tensors as the main model.
- Size target: small enough to train on E3 without changing the project budget; freeze width, depth, optimizer, and epoch budget before E3.
- Dependency rule: do not add a large new dependency only for this baseline unless it is already required by the main training stack.

### Minimum Baseline Recommendation

For an undergraduate thesis or application portfolio, the core OmniLearned fine-tuning matrix may be sufficient.

For a stronger manuscript, add:

| Baseline Scope | Cost | Value |
|---|---:|---|
| Deep Sets A vs D at 10^5, 3 seeds | Low | Minimal sanity check |
| Deep Sets A-D at 10^4 and 10^5, 3 seeds | Moderate | Recommended publication-strength check |
| ParticleNet or ParT | Higher | Optional only after main results are stable |

## 8. Experimental Design

### E0: Data and Pipeline Audit

Goal:

Prove that the dataset and preprocessing pipeline are correct before any formal training claims are made.

Required outputs:

| Output | Success Criterion |
|---|---|
| JetClass EDA note | Shapes, labels, masks, and feature columns documented |
| Split manifest | Fixed event list or reproducible split rule exists |
| Feature preprocessing spec | A-D generated from one raw source and one code path |
| Preprocessing tests | Shape, dtype, NaN/Inf, mask, padding, and normalization checks pass |
| Metric smoke test | Random-score AUC is near 0.5, metrics contain no NaN/Inf, and output schema is stable |
| Config D leakage audit | Candidate columns pass source review and label-shuffle sanity check |
| Manifest hash | Included in every formal run record |

Exit gate:

E0.5 may start only after A-D tensors, Config D audit, and metric smoke tests pass.

### E0.5: Checkpoint and Adapter-Loading Spike

Goal:

Prove that the selected OmniLearned checkpoint can be used with the planned feature-specific input adapters before running real pilots.

Required outputs:

| Output | Success Criterion |
|---|---|
| Checkpoint metadata record | Repository, tag, artifact path, hash, license, pretraining source, input schema, and backup decision recorded |
| Weight-loading report | All non-input compatible layers loaded or skipped layers explicitly logged |
| Forward-pass report | A/B/C/D feature configs produce finite logits on the dev slice |
| Gradient smoke test | One backward pass produces finite gradients |
| Tiny fine-tune report | One tiny epoch decreases loss |
| Adapter policy decision | Adapter-swap approved as primary, or neutralization chosen before E1 |

Exit gate:

E1 may start only after E0.5 passes.

### E1: Pilot Runs

Goal:

Estimate feasibility and catch pipeline errors before launching the full matrix.

Recommended pilot:

| Factor | Setting |
|---|---|
| Feature configs | A and C, or A and D |
| Training sizes | 10^3 and 10^4 per class |
| Seeds | 1 |
| Model | OmniLearned PET-style backbone; Deep Sets/PFN only if already cheap |
| Metrics | Validation AUC, test AUC, background rejection |

Passing criteria:

1. Every run completes without manual file edits.
2. Output JSON includes config, seed, manifest hash, git commit, and metrics.
3. Training curves are not obviously broken.
4. Runtime and memory are compatible with available cloud GPU resources.
5. Plots can be generated automatically from saved predictions.
6. Runtime, memory, and storage measurements are sufficient to project E2 cost.

Exit gate:

E2 may start only after the pilot can be reproduced from a clean command and the Section 11 budget gate is updated with E1 measurements.

### E2: Core Fine-Tuning Matrix

Goal:

Answer RQ1 and RQ2.

Core matrix:

| Dimension | Values |
|---|---|
| Task | JetClass top vs QCD |
| Model | Pretrained OmniLearned PET-style backbone |
| Training mode | End-to-end fine-tuning |
| Feature configs | A, B, C, D |
| Training sizes | 10^3, 10^4, 10^5 per class |
| Seeds | 3 first pass |
| Metrics | ROC AUC, background rejection, auc_gap_fraction |

Run count:

```text
4 feature configs x 3 training sizes x 3 seeds = 36 fine-tuning runs
```

Key follow-up reruns:

- Key 5-seed expansion: A, C, and D at 10^4 and 10^5, adding two seeds for each of those six conditions if budget permits.
- Additional expansion requires a written note that the observed delta_AUC is close to the uncertainty floor.

Primary endpoint:

> Test ROC AUC differences `AUC(C) - AUC(A)` and `AUC(D) - AUC(A)` at each training size, evaluated on the same fixed test set with paired uncertainty.

Secondary endpoints:

1. Background rejection `1 / epsilon_B` at `epsilon_S = 0.30`.
2. Background rejection `1 / epsilon_B` at `epsilon_S = 0.50`.
3. `auc_gap_fraction`.
4. Validation AUC vs epoch.
5. Feature ranking consistency across seeds.
6. Incremental `AUC(D) - AUC(C)` as a tertiary endpoint.

### E3: Baseline and Initialization Controls

Goal:

Test whether the feature-ranking conclusion is an obvious artifact of the OmniLearned checkpoint or model family.

Recommended minimum:

| Control | Scope | Required? |
|---|---|---|
| Fixed Deep Sets/PFN-style baseline | A-D at 10^4 and 10^5, 3 seeds | Required for publication-strength version |
| Deep Sets minimal version | A vs D at 10^5, 3 seeds | Minimum fallback |
| Random-init OmniLearned PET-style model | A vs D at 10^5, 2-3 seeds | Optional |

Interpretation:

| Result | Meaning |
|---|---|
| OmniLearned and baseline show similar A-D ranking | Feature trend is less likely to be checkpoint-specific |
| OmniLearned shows feature gain but baseline does not | Feature effect may depend on OmniLearned inductive bias or pretraining |
| Random-init OmniLearned differs from pretrained OmniLearned mainly at 10^3 or 10^4 | Pretraining may affect label efficiency |
| Feature ranking changes materially across seeds | Report feature effect cautiously and prioritize uncertainty |

E3 should not become a broad architecture benchmark. Its purpose is interpretation of E2.

### E4: External Transfer Extension

Goal:

Test whether the JetClass conclusion survives one dataset shift.

Status:

Future work. Do not include in the minimum viable paper unless E0-E3 are complete and stable.

Required gate before E4:

| Requirement | Reason |
|---|---|
| External binary task can be defined clearly | Avoids label ambiguity |
| Particle-level kinematics are available | Required for Config A |
| PID and charge are documented if used | Avoids silent schema mismatch |
| Fixed split can be created | Enables reproducibility |
| Feature mapping to JetClass can be written explicitly | Prevents post-hoc interpretation |

If PID or charge cannot be mapped cleanly, E4 should be limited to a kinematics-only robustness check.

## 9. Metrics and Statistical Reporting

### Primary Metrics

Result-priority rule:

Raw paired AUC deltas are the primary results. `auc_gap_fraction` is a secondary data-efficiency summary and must not replace the direct paired contrasts.

| Metric | Purpose |
|---|---|
| `AUC(C) - AUC(A)` and `AUC(D) - AUC(A)` | Primary paired feature-availability contrasts |
| ROC AUC | Main binary classification metric reported for every condition |
| Background rejection at fixed signal efficiency | Physics-facing performance metric |
| `auc_gap_fraction` | Secondary data-efficiency metric relative to the largest measured training size |
| Validation AUC curve | Optimization diagnostic |
| Accuracy | Auxiliary metric only |

Background rejection should be reported as:

```text
1 / epsilon_B at epsilon_S = 0.30
1 / epsilon_B at epsilon_S = 0.50
```

### Uncertainty

Report uncertainty at three levels:

1. **Seed variation**: report mean and standard error, or median and spread, across seeds.
2. **Fixed-test bootstrap**: resample per jet on the fixed test set, with at least 1000 replicates and a fixed bootstrap seed.
3. **Paired comparison**: compare A vs B, B vs C, C vs D, C vs A, and D vs A using paired bootstrap on saved predictions; DeLong testing for correlated ROC curves may be added if convenient.
4. **Ratio uncertainty**: estimate `auc_gap_fraction` intervals by bootstrapping the ratio directly. If the denominator is unstable, report raw AUC differences instead.

Do not interpret small differences as meaningful unless the paired uncertainty supports the comparison.

Optional applicant-fit polish:

The researcher's Bayesian background may be used for a small appendix, such as a beta-binomial sanity check for background rejection at fixed signal efficiency. This is optional and must not delay E0-E2.

### Saved Prediction Requirement

Every formal evaluation must save per-event predictions on the fixed test set. Without saved predictions, paired bootstrap and post-hoc statistical checks cannot be done reliably.

## 10. Reproducibility Requirements

Every formal run must save a machine-readable run record.

| Field | Purpose |
|---|---|
| run_id | Unique lookup key |
| git_commit | Code traceability |
| data_manifest_hash | Split traceability |
| dataset_hash | Source file-set traceability |
| preprocessing_version | Feature traceability |
| pretraining_source | Checkpoint and pretraining-corpus traceability |
| feature_config | Main experimental variable |
| model_name | Architecture traceability |
| initialization | Pretrained or random |
| seed | Statistical repeatability |
| training_size_per_class | Data-efficiency axis |
| hyperparameters | Training reproducibility |
| input_adapter_policy | Documents adapter vs neutralization choice |
| loaded_layers | Checkpoint-loading audit |
| skipped_layers | Checkpoint-loading audit |
| hardware_spec | GPU, VRAM, CUDA, framework version |
| runtime_seconds | Cost and reproducibility audit |
| peak_gpu_memory_mb | Memory and cloud-instance planning |
| best_validation_epoch | Early stopping audit |
| test_metrics | Final evaluation |
| prediction_file | Enables paired tests and bootstrap |
| failure_status | Records failed or excluded runs |

Figures and tables should be generated from these run records, not manually edited spreadsheets.

Minimum run-record constraints:

- `feature_config` must be one of `A`, `B`, `C`, or `D`.
- `initialization` must be one of `pretrained`, `random`, or `baseline`.
- `input_adapter_policy` must be one of `adapter_swap` or `fixed_dim_neutralization`.
- `failure_status` must be `ok` or a short failure reason.

## 11. Compute Scope and Budget Discipline

The project is designed for personal cloud GPU use. Current GPU pricing changes over time, so hourly-rate estimates should be verified immediately before purchasing compute. For pre-E1 planning only, use an RTX 4090-class placeholder rate of **0.70 USD/GPU-hour**, close to the July 1, 2026 [RunPod RTX 4090 listing](https://www.runpod.io/gpu-models/rtx-4090) of 0.69 USD/hour for a 24 GB RTX 4090. The dollar estimates below include a 25% reserve for failed runs, debugging, and short reruns.

E1 must produce the measured numbers used for budget approval:

| Measurement | Required Use |
|---|---|
| Runtime for 10^3 jets/class | Pilot sanity and lower-bound estimate |
| Runtime for 10^4 jets/class | Interpolate or project medium-size runs |
| Peak GPU memory | Select cloud instance class |
| Disk footprint for source files, dev slice, tensors, checkpoints, predictions | Decide local vs cloud storage |
| Provider hourly price at purchase time | Convert projected GPU-hours to dollars |

Pre-E1 planning may use rough estimates, but E2 approval must use measured E1 runtime. If projected E2 plus key reruns exceeds the researcher's active budget cap, reduce in this order:

1. Drop random-init OmniLearned control.
2. Reduce Deep Sets/PFN to the minimum A vs D sanity check.
3. Drop optional 5-seed expansions except the single most important A-vs-C or A-vs-D comparison.
4. Only then reduce core E2 training sizes. Do not reduce A-D feature coverage first.

Recommended scope ladder:

| Scope | Runs | Purpose | Pre-E1 Cloud GPU Cost Estimate | Budget Risk |
|---|---:|---|---:|---|
| Pilot only | 4-8 | Validate pipeline and runtime; corresponds to E1 depending on optional second seed or baseline pilot | 5-20 USD | Low |
| Core matrix | 36 | Main RQ1/RQ2 evidence | 90-220 USD | Moderate |
| Core plus key 5-seed reruns | 48 | Adds two seeds for A/C/D at 10^4 and 10^5 if budget permits | 125-290 USD | Moderate |
| Core plus Deep Sets baseline | 50-70 | Stronger manuscript | 160-395 USD | Moderate to high |
| Original broad benchmark | 90+ | Too much for first paper | 350+ USD | High |

Operational rules:

1. Do not launch the full matrix before E1 passes.
2. Run 3 seeds first, then add 5-seed reruns only for the explicit A/C/D key conditions above.
3. Keep external transfer out of the first compute budget.
4. Track failed runs explicitly rather than deleting them from the record.
5. Reserve budget for debugging, storage, and reruns rather than calculating only ideal GPU-hours.
6. Re-check cloud prices immediately before purchase; do not cite stale rates in the manuscript.

## 12. Timeline and Decision Gates

| Phase | Duration | Exit Criterion |
|---|---:|---|
| E0 data audit and preprocessing | 2-3 weeks | A-D tensors, masks, labels, and metric smoke tests pass |
| E0.5 checkpoint and adapter spike | 1-3 days | Checkpoint metadata, adapter loading, finite forward/backward, and tiny fine-tune pass |
| E1 pilot | 1-2 weeks | Reduced OmniLearned runs complete from clean commands |
| E2 core matrix | 3-5 weeks | 36-run core matrix complete with saved predictions |
| E3 controls | 1-3 weeks | Deep Sets/PFN sanity baseline complete or formally deferred |
| Analysis and figures | 1-2 weeks | Main tables, bootstrap intervals, and plots generated from run records |
| Writing | 2-3 weeks | Draft manuscript includes Methods, Results, Discussion, Limitations, and Reproducibility Appendix |
| E4 external transfer | Future work | Added only after minimum viable paper is stable |

Calendar assumptions:

| Mode | Planning Assumption |
|---|---|
| Summer full-time | Lower end of durations may be realistic if cloud compute is available and E0.5 passes quickly |
| Semester part-time | Use the upper end plus 20-30% contingency for coursework, exams, and failed runs |

Mid-project cut gate:

If E1 is not complete by the planned midpoint, freeze the project at E0-E2 thesis MVP and defer E3 controls except the minimum Deep Sets/PFN A vs D sanity check.

Decision gates:

| Gate | Decision |
|---|---|
| After E0 | If feature columns, masks, or Config D candidates are ambiguous, stop and fix preprocessing before checkpoint work |
| After E0.5 | If adapter-swap fails, choose neutralization or convert to supervised feature-ablation before E1 |
| After E1 | If runtime is too high, reduce baseline scope before reducing core A-D coverage |
| Mid-E2 | If A-D differences are near-null, keep running the planned seeds and emphasize uncertainty |
| After E2 | If main trends are stable, add Deep Sets/PFN before adding another OmniLearned variant |
| After E3 | If controls support the feature trend, proceed to manuscript; if not, write the sensitivity honestly |

## 13. Risk Register

| Risk | Consequence | Mitigation |
|---|---|---|
| Feature columns are misunderstood | False feature-ablation conclusion | E0 feature dictionary and preprocessing tests |
| Padding or masks leak information | Inflated performance | Tests showing padded particles do not affect output |
| Checkpoint is unavailable or license is unsuitable | Cannot make pretrained fine-tuning claim | Use backup checkpoint or convert to supervised OmniLearned-architecture feature-ablation |
| Adapter-swap loading fails | Cannot use preferred fine-tuning design | Decide in E0.5 whether to use fixed full-dimension neutralization or remove pretrained-transfer claims |
| Fallback neutralization inherits full-feature input weights | Confounded interpretation | Run feasible contamination diagnostic and state limitation explicitly |
| Single-seed result is noisy | Unstable claim | Minimum 3 seeds, key 5-seed reruns |
| Baseline scope expands too much | Project does not finish | Deep Sets/PFN only; defer ParticleNet/ParT |
| Planning continues after gates are specified | Execution stalls | Stop adding design detail and run E0/E0.5 once this plan is accepted |
| Cloud GPU prices spike | Budget overrun | Apply Section 11 cut order and keep E4 out of first budget |
| Term-time workload disrupts progress | Timeline overrun | Use semester timeline, add contingency, and cut E3 before E2 core coverage |
| External dataset schema differs | Transfer result becomes uninterpretable | Treat E4 as future work with explicit schema gate |
| Results are near-null | Narrative seems weak | Frame as controlled negative evidence with uncertainty |

## 14. Minimum Viable Paper

The thesis minimum viable paper should include:

1. A clear statement that the study measures feature availability during OmniLearned PET-style fine-tuning.
2. JetClass top-vs-QCD task definition and fixed split manifest.
3. A nested feature ladder A-D with excluded truth-level variables stated explicitly.
4. The fine-tune-without-X protocol, including input adapter or neutralization policy.
5. A-D results across 10^3, 10^4, and 10^5 training jets per class.
6. At least 3 seeds per core condition.
7. ROC AUC, background rejection, and `auc_gap_fraction`.
8. Bootstrap or paired uncertainty using saved predictions.
9. A limitations section stating that the results are conditional on the fixed protocol and are not universal causal feature-importance estimates.

For publication-strength version, add a fixed Deep Sets/PFN-style baseline and explicitly state whether E3 was completed or deferred.

Optional target:

The preferred dissemination path is an arXiv preprint plus a relevant HEP-ML or ML4PS-style workshop if timing and results permit. This is not an execution gate for E0-E2.

Suggested manuscript structure:

| Section | Content |
|---|---|
| Introduction | Why feature availability matters for jet foundation-model fine-tuning |
| Dataset and Task | JetClass top vs QCD, split, masks, feature columns |
| Methods | OmniLearned PET-style backbone, input adapters, feature ladder, training protocol |
| Experiments | E0-E2 core matrix, E3 controls if completed |
| Results | Feature-ablation curves and data-efficiency curves |
| Discussion | What richer features buy, where they do not help, and why the claim is conditional |
| Limitations | Checkpoint dependence, JetClass-only evidence, adapter/neutralization assumptions |
| Reproducibility Appendix | Manifest hashes, run records, seeds, configs, commands |

## 15. Expected Outputs

| Output | Description |
|---|---|
| Research plan v0.3 | This document |
| E0 data audit note | Dataset schema, masks, labels, feature dictionary |
| Preprocessing code and tests | One code path for A-D feature generation |
| Run manifest | Machine-readable matrix of formal runs |
| Metric scripts | AUC, background rejection, bootstrap, paired comparison |
| Figures | AUC vs feature config, AUC vs training size, background rejection, auc_gap_fraction |
| Manuscript draft | First-author paper or thesis-style report |
| Reproducibility appendix | Commands, hashes, environment, and run records |
| Optional public artifact bundle | GitHub release or Zenodo deposit for manifests, run records, figures, and prediction files if licensing permits |

## 16. One-Sentence Version

This project quantifies how nested particle-level feature availability affects the performance and data efficiency of a fine-tuned pretrained OmniLearned PET-style model on JetClass top tagging.

Baselines, random initialization, and external transfer are interpretive controls or future extensions, not the main research claim.
