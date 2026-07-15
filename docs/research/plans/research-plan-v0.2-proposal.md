
# Research Plan Proposal

## Research Title

Controlled Feature-Representation Ablations for PET-Style Jet Tagging on JetClass

## 0. Executive Summary

This project should be framed as a controlled empirical study of particle-level input representation for jet tagging, not as a broad comparison of every possible jet foundation-model transfer strategy.

The core study asks:

> How does particle-level feature richness affect the performance and data efficiency of a PET-style jet-tagging backbone when the dataset, task, split, preprocessing pipeline, and evaluation metrics are held fixed?

The first publishable version should use JetClass binary top tagging as the primary task. All feature configurations should be generated from the same raw JetClass files and the same train/validation/test manifest. This makes the comparison scientifically cleaner and operationally feasible.

External transfer to a separate top-tagging or quark-gluon benchmark remains a valuable extension, but it should not be the first core experiment. External datasets introduce generator, detector, label, and feature-schema shifts that make attribution difficult. The project should first establish a controlled JetClass result, then use external transfer as a follow-up robustness test.

## 1. Research Questions

### Primary Research Question

**RQ1.** On JetClass binary top tagging, how much does adding particle-level feature information beyond kinematics improve PET-style model performance?

The central comparison is between feature configurations produced from the same events:

| Config | Particle-level input | Purpose |
|---|---|---|
| A | Kinematics only | Measures the baseline value of pure four-momentum information |
| B | Kinematics + charge | Tests the incremental value of electric charge |
| C | Kinematics + charge + PID | Tests the incremental value of particle identity after charge is included |
| D | Kinematics + charge + PID + frozen non-truth particle observables from E0 | Tests the strongest allowed detector-level particle representation |

This table is a nested feature ladder: each configuration must contain all fields from the previous configuration plus one additional allowed feature group. The exact columns for each group must be frozen after the JetClass exploratory data analysis step. If a listed field is unavailable or ambiguously encoded, it must be removed from the configuration rather than hand-filled inconsistently.

Config D must be defined by an E0 feature dictionary before formal training. It may include only particle-level observables that are present for every selected event, have a documented JetClass source column, and can be computed without using class labels, generator truth ancestry, or target-dependent information. Truth-level variables, label-derived variables, post-hoc top/QCD indicators, and variables computed using the target label are explicitly excluded.

### Secondary Research Questions

**RQ2.** Is the benefit of richer particle features larger in the small-labeled data regime?

This is tested by repeating the main feature configurations at fixed labeled data fractions while keeping the validation and test sets unchanged.

**RQ3.** Are the feature-ablation conclusions robust to matched initialization controls?

This is a control question, not a primary contribution. The minimum control is matched random-initialized training under the same feature configurations and data fractions. If a reliable PET-style pretrained checkpoint is available, it can be added as an optional initialization condition. The key test is whether the A-D feature ranking and data-efficiency conclusions remain stable, not whether pretraining is globally superior.

### Future Work Question

**FW1.** Do the JetClass conclusions survive transfer to an external jet-tagging benchmark?

This is future work. It should be attempted only after the JetClass core study has a stable preprocessing pipeline, metric pipeline, pilot run report, and minimum viable paper draft. It is not required for the first publishable version.

## 2. Scientific Motivation

Jet tagging models process jets as sets of particles. Each particle can be represented with minimal kinematic information or with richer particle properties such as charge and particle identity. Richer inputs may improve classification because they expose physically meaningful structure, but they also make models more dependent on dataset-specific feature definitions.

This creates a focused empirical question:

> When all other experimental factors are controlled, which particle-level input features actually improve jet-tagging performance, and under what data-scale conditions?

This framing is stronger than a broad model benchmark because it isolates one research variable: input representation. It also produces useful results even if the strongest feature set does not win. A null result would indicate that kinematics already captures most of the useful signal for this task. A positive result would quantify when and how richer particle information matters.

## 3. Scope and Claim Hierarchy

The project should use a strict hierarchy of claims.

| Claim level | Status | Required evidence |
|---|---|---|
| Core claim | Required | Feature configurations A-D compared on the same JetClass top/QCD split |
| Data-efficiency claim | Required | A-D repeated across fixed labeled-data fractions |
| Initialization-robustness claim | Conditional control | A-D feature ranking remains stable under matched initialization settings |
| External-transfer extension | Future work | Same trained workflow evaluated on one external benchmark with documented schema mapping |

The paper should not claim that one architecture is globally best, that one feature schema generalizes to all jet datasets, or that PID transfer is universally superior. The defensible claim is narrower and stronger:

> Within a fixed JetClass top-tagging protocol, particle-level feature richness has a measurable effect on performance and data efficiency, and this effect can be quantified under controlled preprocessing and evaluation.

Data efficiency must be reported as a computable quantity, not only as a qualitative statement. The primary data-efficiency statistic is the normalized AUC gap closed at labeled-data fraction \(f\):

```text
normalized_gap_closed(f) = (AUC(f) - 0.5) / (AUC(100%) - 0.5)
```

This should be reported for each feature configuration at the fixed labeled-data fractions used in E2. When interpolation is justified by the measured fractions, the paper may also report the smallest labeled fraction needed to reach a predeclared target such as 95% of the 100% data AUC gap.

## 4. Dataset and Task

### Primary Dataset

The primary dataset is JetClass. The formal study should use a binary classification task:

| Item | Choice |
|---|---|
| Task | Hadronic top jet vs. QCD background |
| Input unit | Jet represented as a padded/masked particle set |
| Split | Fixed train/validation/test manifest |
| Leakage control | No event may appear in more than one split |
| Output | Binary classifier score for top vs. QCD |

The first data milestone is not model training. It is a data audit that records:

1. available HDF5 groups and feature columns;
2. particle tensor shape, padding convention, and mask convention;
3. label extraction rule for top vs. QCD;
4. class balance for train, validation, and test;
5. manifest hash and preprocessing version.

### External Dataset

External transfer is a phase-2 extension. A candidate external benchmark may be used only if the following checklist passes:

| Requirement | Reason |
|---|---|
| Same binary task can be defined clearly | Avoids label-definition ambiguity |
| Particle-level kinematics are available | Required for Config A |
| PID or charge information is documented if used | Prevents silent schema mismatch |
| Train/validation/test split can be fixed | Enables reproducibility |
| Feature mapping to JetClass can be written explicitly | Avoids post-hoc interpretation |

If no external dataset passes this checklist, the project should not force an external-transfer claim. The core JetClass ablation remains valid.

## 5. Model and Baselines

### Main Model

The main model should be a PET-style or Particle Transformer-style particle-set backbone compatible with masked variable-length particle inputs.

| Condition | Role |
|---|---|
| PET-style backbone, pretrained when available | Main experimental system |
| Same PET-style backbone, random initialization | Tests whether pretraining matters |
| Deep Sets baseline | Low-complexity sanity baseline for the feature-ablation trend |

ParticleNet or another stronger baseline should be optional. It should be added only after the core PET-style experiments and Deep Sets sanity baseline are complete.

### Training Modes

The first formal study should not run every fine-tuning mode immediately. Training modes should be staged:

| Stage | Mode | Purpose |
|---|---|---|
| Pilot | Full supervised training on a small subset | Verifies pipeline, shapes, metrics, and runtime |
| Core | Full fine-tuning or full supervised training | Primary comparison across feature configs |
| Conditional | Linear probe | Tests representation transfer only if pretrained checkpoint is reliable and the core JetClass ablation is complete |
| Conditional | Partial fine-tuning | Added only if linear probe and full fine-tuning suggest a meaningful gap after the MVP is stable |

This keeps the first paper focused. Linear probing and partial fine-tuning are useful, but they should not multiply the core matrix before the basic feature effect is established. They are optional follow-up analyses, not requirements for the minimum viable paper.

## 6. Experimental Design

### E0: Data and Pipeline Audit

Goal: prove that the dataset and code path are ready for formal experiments.

Required outputs:

| Output | Success criterion |
|---|---|
| JetClass EDA note | Documents shapes, labels, masks, and feature columns |
| Split manifest | Fixed train/validation/test event list or reproducible split rule |
| Feature preprocessing spec | A-D generated from one raw source and one function |
| Preprocessing tests | Shape, dtype, NaN/Inf, mask, padding, and normalization checks pass |
| Metric smoke test | AUC and background rejection can be computed from dummy or pilot predictions |

No formal result should be reported before E0 passes.

### E1: Pilot Run

Goal: estimate feasibility before launching the full matrix.

Recommended pilot:

| Factor | Setting |
|---|---|
| Feature configs | A and C |
| Data fractions | 1% and 10% |
| Seeds | 1 |
| Model | Deep Sets and PET-style backbone if available |
| Metrics | Validation AUC, test AUC, background rejection at fixed signal efficiency |

Passing criteria:

1. every run completes without manual file edits;
2. output JSON contains config, seed, manifest hash, git commit, and metrics;
3. validation curves are not obviously broken;
4. runtime and memory are compatible with the available compute budget;
5. plots can be generated automatically from saved predictions.

If E1 fails, fix the pipeline before expanding the matrix.

### E2: Core Feature-Ablation Study

Goal: answer RQ1 and RQ2.

Minimum formal matrix:

| Dimension | Values |
|---|---|
| Task | JetClass top vs. QCD |
| Feature configs | A, B, C, D |
| Data fractions | 1%, 10%, 100% |
| Seeds | 3 minimum, 5 preferred for final tables |
| Model | PET-style backbone |
| Baseline | Deep Sets on the same feature configs |
| Metrics | ROC AUC, background rejection, accuracy as auxiliary |

This matrix is large enough to support the main claim while remaining tractable. The 10% setting replaces intermediate fractions such as 5% and 25% to keep the first formal study compact. Extra fractions may be added only after the 1%, 10%, and 100% curves are stable.

Primary endpoint:

> Difference in test ROC AUC between Config A and Config C/D at each data fraction, with paired uncertainty over seeds and the same fixed test set.

Secondary endpoints:

1. background rejection at signal efficiency 30% and 50%;
2. convergence speed measured by validation AUC vs. epoch;
3. feature-gain slope from 1% to 100% labeled data;
4. consistency of feature ranking between PET-style and Deep Sets models.

### E3: Initialization Robustness Control

Goal: answer RQ3 as a control on the core feature-ablation conclusion.

Matrix:

| Dimension | Values |
|---|---|
| Feature configs | A and C first; D if compute permits |
| Data fractions | 1%, 10%, 100% |
| Initialization | Matched random initialization; pretrained initialization only if checkpoint loading is reliable |
| Seeds | Same seed list as E2 |
| Training mode | Same fine-tuning schedule and early stopping rule |

Interpretation:

| Result | Meaning |
|---|---|
| Feature ranking stable across matched random-initialized runs | Core feature-ablation conclusion is not an initialization artifact |
| Feature ranking changes materially across seeds or initialization settings | The feature effect is initialization-sensitive and should be reported cautiously |
| Pretrained improves mainly at 1% if available | Pretraining may improve label efficiency, but this remains a secondary control result |
| Pretrained worsens or destabilizes results if available | Checkpoint-feature mismatch or fine-tuning instability must be investigated |

E3 should not be used to claim broad foundation-model superiority. A pretrained checkpoint is an optional initialization condition, not a dependency for completing the paper.

### E4: Future Work External Transfer Extension

Goal: test whether the JetClass feature-ablation conclusion survives a dataset shift.

E4 should use one external benchmark and one primary task. The preferred design is not "Plan A dataset vs. Plan B dataset." The preferred design is:

1. choose one external dataset;
2. define one fixed task and split;
3. derive kinematics-only and kinematics+PID views from the same events;
4. compare feature views under the same model and metric pipeline.

If PID is unavailable or incompatible, E4 should be limited to kinematics-only transfer and reported as a robustness check, not as a PID conclusion. E4 should not be treated as part of the minimum viable paper.

## 7. Metrics and Statistical Reporting

Primary metrics:

| Metric | Purpose |
|---|---|
| ROC AUC | Main ranking metric for binary classification |
| Background rejection at signal efficiency 30% and 50% | Physics-facing performance metric |
| Validation AUC curve | Optimization and data-efficiency diagnostic |
| Accuracy | Auxiliary metric only |

Uncertainty reporting:

1. report mean and standard error across seeds;
2. use bootstrap confidence intervals on the fixed test set when practical;
3. use paired comparisons wherever predictions are produced on the same test events;
4. report all seeds, including failed or excluded runs with reasons.

For background rejection, report:

```text
1 / epsilon_B at epsilon_S = 0.30
1 / epsilon_B at epsilon_S = 0.50
```

The paper should avoid overinterpreting small differences if confidence intervals overlap and the seed count is low.

## 8. Reproducibility Requirements

Every formal run must save a machine-readable record with:

| Field | Reason |
|---|---|
| run_id | Unique lookup key |
| git_commit | Code traceability |
| data_manifest_hash | Split traceability |
| preprocessing_version | Feature traceability |
| feature_config | Main experimental variable |
| model_name | Architecture traceability |
| initialization | Pretrained or random |
| seed | Statistical repeatability |
| hyperparameters | Training reproducibility |
| best_validation_epoch | Early stopping audit |
| test_metrics | Final evaluation |
| prediction_file | Enables paired tests and bootstrap |

Formal figures and tables should be generated from these records, not from manual spreadsheet edits.

## 9. Risk Register and Decision Gates

| Risk | Consequence | Mitigation | Gate |
|---|---|---|---|
| Feature columns are misunderstood | False feature-ablation conclusion | Complete E0 data audit and preprocessing tests | Before E1 |
| Padding or masks leak information | Inflated performance | Add tests showing padded particles do not affect output | Before E1 |
| Initialization budgets differ | Unfair initialization-robustness control | Use matched schedules and log all hyperparameters | Before E3 |
| Reference checkpoint cannot be reproduced | Optional pretrained initialization condition cannot be run | Complete E1/E2 as supervised feature-ablation paper | E3 gate |
| Core matrix is too expensive | Incomplete project | Use 3 seeds first, add 5-seed final reruns only for key configs | E2 gate |
| External dataset schema differs | Uninterpretable transfer result | Treat E4 as optional and require explicit schema mapping | E4 gate |
| Results are near-null | Weak narrative if framed badly | Emphasize controlled negative result and uncertainty | Writing gate |

## 10. Minimum Viable Paper

A minimum viable paper should contain:

1. a clear statement that the study is a controlled feature-representation ablation on JetClass top tagging;
2. a table defining feature configurations A-D as a nested feature ladder with truth-level and label-derived variables excluded;
3. an E0 reproducibility paragraph describing split, masks, preprocessing, and metrics;
4. AUC, normalized AUC gap closed, and background-rejection results across feature configs and data fractions;
5. a Deep Sets baseline showing whether the feature trend is architecture specific;
6. an initialization robustness control if compute permits, with pretrained initialization included only if checkpoint reproduction is reliable;
7. a limitations section stating that external transfer is future work unless E4 is completed.

Suggested paper structure:

| Section | Content |
|---|---|
| Introduction | Why particle-level feature representation matters for jet foundation models |
| Dataset and Task | JetClass top vs. QCD, split manifest, feature columns |
| Methods | PET-style model, Deep Sets baseline, feature configs, training protocol |
| Experiments | E0-E2 core matrix, optional E3 control, metrics, uncertainty reporting |
| Results | Feature-ablation curves, data-efficiency curves, optional pretraining control |
| Discussion | What feature richness buys, where it does not help, limits of JetClass-only evidence |
| Conclusion | Practical recommendation for feature selection in PET-style jet tagging |

## 11. Execution Timeline

| Phase | Duration | Exit criterion |
|---|---:|---|
| E0 data audit and preprocessing | 2-3 weeks | A-D tensors and tests pass |
| E1 pilot | 1-2 weeks | Reduced matrix completes and plots generate |
| E2 core ablation | 3-5 weeks | Main tables for A-D x data fractions x seeds complete |
| E3 initialization robustness control | 1-3 weeks | Feature ranking stability checked under matched initialization settings or formally dropped |
| Writing and figures | 2-3 weeks | Draft manuscript has tables, figures, and reproducibility appendix |
| E4 external transfer | Future work | Added only after minimum viable paper is stable |

## 12. One-Sentence Version

This project should first produce a controlled JetClass top-tagging study that quantifies how a nested particle-level feature ladder affects PET-style model performance and data efficiency under fixed splits, preprocessing, metrics, and seeds; initialization and external-transfer experiments should be treated as controls or future extensions rather than as requirements for the first paper.
