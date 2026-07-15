# Research Plan v0.4

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: plan
- Origin Date: 2026-07-14
- Verification Status: UNVERIFIED
- Version Label: research_plan_v0.4.0
- Source Inputs:
  - `docs/research/plans/research-plan-v0.3.md`
  - `docs/research/assessments/cms-2015-miniaodsim-feasibility.md`
- Supersedes: `docs/research/plans/research-plan-v0.3.md`

## Title

**Feature Availability in Fine-Tuning Jet Foundation Models: Cross-Corpus Top Tagging with CMS 2015 MINIAODSIM**

Short title:

**Feature Availability in Cross-Corpus Jet Foundation Model Fine-Tuning**

## 0. Executive Summary

This project studies how particle-level feature availability during downstream fine-tuning affects the performance, data efficiency, and interpretability of a pretrained OmniLearned PET-style jet foundation model. The downstream task is binary boosted-top tagging using public CMS 2015 `RunIIFall15MiniAODv2` full-detector simulation.

The primary question is:

> Under a fixed cross-corpus top-versus-QCD fine-tuning protocol, how much do nested particle-level feature sets improve a pretrained OmniLearned PET-style backbone?

The four feature configurations are trained separately:

| Configuration | Particle-level view | Scientific contrast |
|---|---|---|
| A | Kinematics | Four-momentum baseline |
| B | A + electric charge | Incremental value of charge |
| C | B + particle identity | Incremental value of PID beyond charge |
| D | C + impact-parameter information | Incremental value of track displacement information |

The main intervention remains **fine-tune without X**. Test-time masking is not a substitute for configuration-specific fine-tuning. All A-D views are sliced from one compact full-D tensor so that jets, constituent ordering, masks, and splits are identical across configurations.

The downstream records are not listed in the published OmniLearned pretraining corpus. The model has nevertheless encountered top-like and QCD jets and CMS-related data. The permitted claim is therefore **dataset-record-disjoint cross-corpus adaptation under controlled feature availability**, not unseen-class or cross-detector transfer.

### Execution Status

The dataset decision is a **CONDITIONAL GO**. E0 remains blocked until a CMSSW pilot validates daughter references, decoded impact-parameter values and units, generator labels, charged-candidate missingness, matched-top yield, split integrity, and extraction cost.

The provisional largest training scale is `n_max = 10^5` jets per class. It remains provisional because the feasibility scan found only 5 kinematically selected AK8 jets in the first 1,000 inclusive TT events before hadronic-top truth matching. If the pilot cannot support `10^5`, a documented v0.4.x amendment must change `n_max`, the training-size grid, and every dependent `auc_gap_fraction` definition before E1.

## 1. What Changed from v0.3

| Area | v0.3 | v0.4 |
|---|---|---|
| Primary corpus | JetClass | Frozen public CMS 2015 MINIAODSIM record set |
| Feature source | JetClass HDF5 columns | CMSSW-decoded AK8 packed-candidate fields |
| Transfer framing | Same-corpus downstream adaptation | Dataset-record-disjoint cross-corpus adaptation |
| Signal label | JetClass top label | Generator-matched fully hadronic top with daughter containment |
| Background label | JetClass QCD label | Jets from declared CMS QCD records only |
| PID definition | Dataset-dependent PID | Charge-sign-free six-category reconstructed-particle vocabulary |
| Config D | Provisional JetClass displacement columns | Raw decoded `dxy`, `dxyError`, `dz`, and `dzError` |
| Split | Official or custom JetClass manifest | Exact-PFN SHA-256 file split |
| Data engineering | HDF5 staging | CMSSW extraction, compact ROOT, then HDF5 conversion |
| Budget | Primarily GPU training | Raw-data throughput, CPU, storage, and GPU training |

The following v0.3 decisions are retained:

1. Feature configuration is the primary research axis.
2. Labeled-data scale is the secondary data-efficiency axis.
3. Every A-D condition is fine-tuned separately.
4. Evaluation uses identical jets and paired saved predictions.
5. Architecture and initialization are controls, not the main narrative.

## 2. Research Questions

### RQ1: Feature Availability

How does the performance of a fine-tuned pretrained OmniLearned PET-style backbone change across nested particle-level configurations A-D on generator-matched CMS 2015 top jets versus CMS 2015 QCD jets?

Required evidence:

- One compact full-D dataset and identical A-D slices.
- One deterministic file-level train/validation/test split.
- Separate fine-tuning for every feature configuration.
- Fixed optimizer, epoch budget, early stopping, and seed list.
- Paired evaluation on one fixed test set.

### RQ2: Data Efficiency

Do richer feature sets reach a given AUC or background-rejection level with fewer labeled fine-tuning examples?

Primary data-efficiency statistic:

```text
auc_gap_fraction(config, n) =
    (AUC(config, n) - 0.5) / (AUC(config, n_max) - 0.5)
```

The initial design uses `n in {10^3, 10^4, 10^5}` jets per class and provisional `n_max = 10^5`. `n_max` means the largest measured training scale, not saturated full-data performance. If E0 changes `n_max`, the formula and all reported values must use the frozen replacement value.

### RQ3: Robustness of Feature Ranking

Is the A-D ranking stable across random seeds, labeled-data scales, and one lightweight Deep Sets/PFN-style baseline?

Minimum evidence:

- Three seeds for every core condition.
- Five-seed expansion only for key close comparisons.
- A fixed Deep Sets/PFN-style A-versus-D control at the largest feasible scale for a publication-strength result.

## 3. Claim Boundary

| Claim | Status | Evidence Needed |
|---|---|---|
| Feature availability affects downstream performance | Required | A-D core matrix and paired uncertainty |
| Feature availability affects labeled-data efficiency | Required | A-D at fixed training sizes |
| Feature ranking is not only a checkpoint artifact | Publication-strength control | Fixed Deep Sets/PFN-style baseline |
| Pretraining changes label efficiency | Optional | Matched random-initialized backbone |
| Exact downstream records are disjoint from the documented pretraining corpus | Supported by current documentation; recheck if a checkpoint manifest appears | Record-level comparison |
| The task is unseen-class or cross-detector transfer | Prohibited | Top-like, QCD, and CMS-related pretraining overlap |

Recommended wording:

> The downstream corpus consists of CMS 2015 RunIIFall15 MINIAODSIM records not listed in the OmniLearned pretraining corpus. The model had previously encountered top-like and QCD jet classes, so this experiment tests cross-corpus adaptation under controlled feature availability rather than unseen-class transfer.

The study does not estimate universal causal feature importance or establish architecture superiority.

## 4. Dataset and Task

### 4.1 Frozen Source Records

Use one inclusive TT production for signal and five same-campaign QCD records. Do not mix TT extensions in the first study.

Signal:

| Record | Process | Events | Files | Size | DOI |
|---:|---|---:|---:|---:|---|
| 19980 | `TT_TuneCUETP8M1_13TeV-powheg-pythia8`, ext3 | 97,994,442 | 2,413 | 3.051 TiB | [10.7483/OPENDATA.CMS.JJEM.1DKC](https://doi.org/10.7483/OPENDATA.CMS.JJEM.1DKC) |

Background:

| Record | Generator-level pT bin | Events | Files | Size | DOI |
|---:|---|---:|---:|---:|---|
| 18373 | 470-600 GeV | 3,977,770 | 89 | 0.121 TiB | [10.7483/OPENDATA.CMS.5DBS.XCW8](https://doi.org/10.7483/OPENDATA.CMS.5DBS.XCW8) |
| 18376 | 600-800 GeV | 3,979,884 | 91 | 0.126 TiB | [10.7483/OPENDATA.CMS.3Y72.BWW4](https://doi.org/10.7483/OPENDATA.CMS.3Y72.BWW4) |
| 18377 | 800-1,000 GeV | 3,973,224 | 98 | 0.130 TiB | [10.7483/OPENDATA.CMS.SGRV.4ABD](https://doi.org/10.7483/OPENDATA.CMS.SGRV.4ABD) |
| 18355 | 1,000-1,400 GeV | 2,953,982 | 89 | 0.100 TiB | [10.7483/OPENDATA.CMS.WOP0.TFY9](https://doi.org/10.7483/OPENDATA.CMS.WOP0.TFY9) |
| 18358 | 1,400-1,800 GeV | 395,725 | 9 | 0.014 TiB | [10.7483/OPENDATA.CMS.N49K.1FTR](https://doi.org/10.7483/OPENDATA.CMS.N49K.1FTR) |

The source snapshot contains 2,789 unique online PFNs and 3.542 TiB. The feasibility-analysis snapshot hash is:

```text
29ba19ff67480498d6f16e195bf91362b115da8a9a766862fe0fab7b469237d7
```

The extractor must commit the sorted manifest used to produce this hash before formal production. A hash without the manifest is insufficient provenance.

### 4.2 Jet Selection

Use `slimmedJetsAK8` with:

```text
500 GeV <= corrected jet pT < 1000 GeV
abs(jet eta) < 2.0
anti-kt R = 0.8
```

The pT cut applies to the corrected PAT jet `slimmedJetsAK8::pt()` exposed under CMSSW `7_6_7` and global tag `76X_mcRun2_asymptotic_RunIIFall15DR76_v1`. Record the jet-correction metadata. Any uncorrected-pT study must be explicitly labeled as a sensitivity analysis.

Do not impose a top-mass or Soft-Drop mass window in the primary sample.

### 4.3 Signal Label

A signal jet must satisfy all of the following:

1. Find generator top quarks with `abs(pdgId) == 6` and the CMSSW last-copy status flag.
2. Require `deltaR(reconstructed jet, top) < 0.8`.
3. Verify a fully hadronic `top -> b W -> b q q'` decay through `prunedGenParticles`.
4. Require the `b`, `q`, and `q'` daughters separately to satisfy `deltaR(daughter, reconstructed jet axis) < 0.8`.
5. Reject a jet when more than one eligible last-copy top is inside the matching radius.

Generator traversal and status handling must pass unit checks on hand-inspected events. Reconstructed-to-`slimmedGenJetsAK8` matching is a pilot diagnostic, not a signal-label requirement.

Other jets in TT events are excluded; they are not QCD background.

### 4.4 Background Label and QCD Mixture

Background jets come only from the declared QCD records.

The primary extraction set is records 18373, 18376, and 18377. The pilot must also measure selected reconstructed-jet pT for records 18355 and 18358 before excluding them. Before E1, freeze a machine-readable table containing, by split and record:

- files and events processed;
- selected jets before and after pT/eta control;
- jets sampled at every training scale;
- any event or generator weights.

For the non-physical class-balanced study, sample QCD jets round-robin across active records after deterministic ordering by record ID, PFN hash, event number, and jet index. This keeps active record counts within one jet until a record is exhausted. Freeze the realized mixture; record identity and bin identity must never enter model inputs.

If a physically weighted QCD result is reported, obtain generator cross sections from CMS metadata, store the derived weights in provenance, and label that analysis separately.

### 4.5 Distribution and Pileup Control

Estimate pT/eta matching or reweighting only from the training split, freeze it, and apply it unchanged to validation and test data. Jet mass remains unconstrained in the primary result.

Compare reconstructed-vertex multiplicity and PV-z by class on the training split. Treat either of the following as a material mismatch:

- absolute standardized mean difference in vertex multiplicity greater than `0.10`;
- two-sample KS statistic for PV-z greater than `0.10`.

If either threshold is exceeded, fit a frozen training-split-only pileup reweighting rule and report both uncorrected and corrected results. Pileup variables and weights must not be model inputs.

### 4.6 Deterministic Split

Split by source file before jet extraction:

```text
canonical_pfn = exact PFN field from the sorted manifest, encoded as UTF-8
bucket = integer(SHA256(canonical_pfn)) mod 10
bucket 0 -> test
bucket 1 -> validation
bucket 2-9 -> training
```

Do not lowercase, trim, remove protocol prefixes, or otherwise normalize the PFN before hashing. No PFN or event may cross splits. After selection and truth matching, report files, events, and jets by class, record, and split.

## 5. Feature Configurations

### 5.1 Shared Constituent Definition

Resolve `slimmedJetsAK8` daughters to `packedPFCandidates`, sort them by descending pT, and retain at most 150 constituents per jet. Produce one compact full-D tensor, one mask, and one provenance record. A-D are column slices from that tensor.

### 5.2 CMS-to-A-D Mapping

| Config | Training field | CMS source | Processing | Missing-value rule |
|---|---|---|---|---|
| A | `delta_eta` | Candidate and jet `eta()` | Candidate eta minus jet eta | None for retained candidates |
| A | `delta_phi` | Candidate and jet `phi()` | Wrap to `[-pi, pi)` | None |
| A | `log_pt` | Candidate `pt()` | Natural log after a positive minimum cut | None after cut |
| A | `log_energy` | Candidate `energy()` | Natural log after a positive minimum cut | None after cut |
| B | `charge` | Candidate `charge()` | Small integer or float scalar | Zero is physical neutrality |
| C | `pid_type` | Candidate `pdgId()` | Map absolute PDG ID to the frozen vocabulary below | `unknown` category |
| D | `dxy_raw` | Candidate `dxy()` | Store decoded raw value; validate PV semantics and cm unit | Zero for neutral/no-track candidates |
| D | `dxy_error_raw` | Candidate `dxyError()` | Store decoded uncertainty in the same unit | Zero for neutral/no-track candidates |
| D | `dz_raw` | Candidate `dz(0)` | Use primary-vertex index 0; validate cm unit | Zero for neutral/no-track candidates |
| D | `dz_error_raw` | Candidate `dzError()` | Store decoded uncertainty in the same unit | Zero for neutral/no-track candidates |

PID uses `abs(pdgId)` so charge sign is not duplicated:

| Category | Absolute PDG ID |
|---|---:|
| charged hadron | 211 |
| neutral hadron | 130 |
| photon | 22 |
| electron | 11 |
| muon | 13 |
| unknown | all other values |

Initialize the categorical PID adapter from scratch. Do not use generator ancestry.

### 5.3 Impact-Parameter and Missing-Track Policy

Store raw CMSSW-decoded displacement values during extraction. At E0.5, either reproduce the checkpoint's documented convention exactly or fit normalization using the training split only. Do not introduce an ad hoc `tanh` transform.

For neutral candidates and candidates without usable track details, set D fields to zero and record separate counts. Audit charged candidates without usable track details by class, record, and split. If the rate exceeds 1% of retained charged candidates, stop before E1 and review the missing-value policy.

No generator truth, record identifier, process identifier, source file, class-derived variable, event weight, or pileup weight may enter model tensors.

## 6. Extraction and Preprocessing Pipeline

### 6.1 Pinned Environment

```text
CMSSW: 7_6_7
Container: cmsopendata/cmssw_7_6_7-slc6_amd64_gcc493
Global tag: 76X_mcRun2_asymptotic_RunIIFall15DR76_v1
```

Record the resolved container digest in every production manifest.

### 6.2 Minimum Pipeline

```text
CMS MINIAODSIM
  -> one CMSSW EDAnalyzer with fixed selection and truth matching
  -> compact flat ROOT with raw A-D fields and provenance
  -> one Python/h5py conversion to OmniLearned-compatible HDF5
```

The HDF5 output must contain `data`, jet label `pid`, and masks or lengths required by the training code. Jet-level audit variables may be stored in provenance or `global`, but are excluded from the primary classifier.

Stream source files near CERN or from infrastructure with measured EOS/XRootD throughput. Do not download the complete 3.542 TiB corpus to the current local machine.

### 6.3 Required Data Checks

The compact dataset must pass checks for:

1. resolved jet-daughter references;
2. source product presence in every opened file;
3. finite A-C values and documented PID vocabulary;
4. decoded D values, units, and PV-reference semantics;
5. charged no-track rate;
6. full truth-label efficiency chain;
7. tensor shapes, dtype, masks, padding, truncation, NaN, and Inf;
8. exact file-level split and event disjointness;
9. identical jets and ordering across A-D slices;
10. no truth, process, record, or weight fields in model inputs;
11. shuffled-label AUC whose 95% bootstrap interval contains 0.5;
12. source-manifest and final HDF5 hashes.

## 7. Main Fine-Tuning Protocol

### 7.1 Fine-Tune Without X

For each feature configuration:

```text
same pretrained checkpoint
  -> config-specific input adapter
  -> end-to-end fine-tuning on that feature view
  -> paired evaluation on the same fixed test jets
```

Full-feature training followed by test-time feature masking is not a primary result. It may appear only as an appendix diagnostic.

### 7.2 Preferred Input Adapter

1. Build a configuration-specific input projection.
2. Use normalized continuous inputs plus one-hot categorical PID by default.
3. Randomly initialize the configuration-specific adapter and binary output head.
4. Load every shape-compatible non-input backbone weight from the same checkpoint.
5. Log every loaded, skipped, and mismatched tensor.
6. Fine-tune the full model end to end with fixed optimization rules.

If adapter replacement is impossible, fixed full-dimension neutralization is allowed only after E0.5 records the failure. Standardized unavailable continuous inputs and unavailable charge are set to zero; unavailable PID bits are all zero. The resulting input-layer contamination risk must be stated.

### 7.3 E0.5 Adapter Gate

E1 may not start until all four configurations produce finite forward passes and gradients, a tiny epoch reduces loss, and the checkpoint source, license, hash, input schema, loaded layers, and skipped layers are recorded.

## 8. Models and Controls

### Main Model

| Field | Decision |
|---|---|
| Repository | `https://github.com/ViniciusMikuni/OmniLearned` |
| Checkpoint candidate | `pretrain_s`; use `pretrain_m` only if justified before E1 |
| Backbone | PET-style masked variable-length particle-set model |
| Input adapter | Configuration-specific and randomly initialized |
| Output head | Reinitialized binary top/QCD head |
| Training | End-to-end fine-tuning |
| Failure fallback | Supervised OmniLearned-architecture ablation with pretrained-transfer claims removed |

Recheck any released checkpoint training manifest before E1. Exact downstream record overlap blocks the record-disjoint claim but does not invalidate the controlled feature study.

### Controls

| Model condition | Role | Priority |
|---|---|---|
| Pretrained OmniLearned PET-style backbone | Main measurement system | Required |
| In-repository Deep Sets/PFN-style model | Low-cost feature-ranking sanity check | Publication-strength control |
| Random-initialized OmniLearned backbone | Initialization control | Optional |
| ParticleNet, ParT, or broader benchmark | Architecture comparison | Deferred |

Do not add a large dependency for the baseline if the existing training stack can implement masked pooling directly.

## 9. Experimental Stages

### E0: CMSSW Data, Yield, and Cost Pilot

Process at least 5-10 TT files and multiple files from every candidate QCD record on the intended production host.

Required outputs and exit criteria:

| Gate | Pass criterion |
|---|---|
| Manifest | Persistent sorted manifest reproduces the declared source hash |
| Jet daughters | AK8 daughters resolve to packed candidates for TT and QCD |
| A-C fields | Values are finite and vocabulary is documented |
| D fields | Decoded values, errors, cm units, and PV semantics are validated |
| Missingness | Charged no-track rate is measured and passes the 1% review threshold |
| Labels | Hand-inspected events validate last-copy traversal, hadronic decay, containment, and ambiguity rejection |
| Yield | Full selection efficiency and matched-signal projection support frozen `n_max` |
| Split | No PFN/event overlap and adequate selected-jet counts by class and split |
| QCD mixture | Active records and exact sampling mixture are frozen |
| Confounds | pT/eta control and pileup diagnostic are frozen from training data only |
| Leakage | Shuffled-label AUC 95% bootstrap interval contains 0.5 |
| Output | A-D slices, masks, padding, and HDF5 schema pass checks |
| Cost | CPU, wall time, source bytes, throughput, compact bytes, and projected production cost are measured |

If matched-top yield cannot support `10^5` jets per class, publish a v0.4.x amendment before E0.5. Do not lower the 500 GeV jet-pT threshold silently.

### E0.5: Checkpoint and Adapter Spike

Required outputs:

- checkpoint source, tag, license, SHA-256, and pretraining-corpus record;
- input schema and normalization convention;
- loaded/skipped-layer report;
- finite A-D forward and backward passes;
- one tiny fine-tune showing loss decrease;
- frozen adapter or neutralization policy.

### E1: Training Pilot

| Factor | Setting |
|---|---|
| Feature configurations | A and D |
| Training sizes | `10^3` and `10^4` per class |
| Seeds | 1 |
| Model | Pretrained OmniLearned PET-style backbone |
| Metrics | Validation/test AUC and background rejection |

The pilot must run from clean commands, save predictions and run records, and measure runtime, peak GPU memory, checkpoint size, and output storage. E2 requires a budget projection based on E0 extraction and E1 training measurements.

### E2: Core Fine-Tuning Matrix

| Dimension | Values |
|---|---|
| Task | CMS 2015 generator-matched hadronic top vs declared QCD jets |
| Model | Pretrained OmniLearned PET-style backbone |
| Feature configurations | A, B, C, D |
| Training sizes | `10^3`, `10^4`, provisional `10^5` per class |
| Seeds | 3 first pass |
| Evaluation | Fixed paired test set |

Provisional run count:

```text
4 feature configurations x 3 training sizes x 3 seeds = 36 runs
```

If E0 changes `n_max`, retain three scales where yield permits, document the new grid, and recompute the run count before E2.

Primary endpoints are paired `AUC(C) - AUC(A)` and `AUC(D) - AUC(A)` at every training scale. Add two seeds only for preregistered key comparisons whose effect is close to the uncertainty floor.

### E3: Baseline and Initialization Controls

Minimum publication-strength control: Deep Sets/PFN-style A versus D at frozen `n_max`, three seeds. Expand to A-D at the two largest scales only after E2 is complete and budget remains.

Random-initialized OmniLearned A versus D is optional. E3 must not become a broad architecture benchmark.

## 10. Metrics and Statistical Reporting

| Metric | Role |
|---|---|
| Paired AUC deltas | Primary feature-availability results |
| ROC AUC | Main metric for every condition |
| `1 / epsilon_B` at `epsilon_S = 0.30` and `0.50` | Physics-facing performance |
| `auc_gap_fraction` | Secondary data-efficiency summary |
| Accuracy | Auxiliary only |

Report uncertainty at three levels:

1. seed variation across independent training runs;
2. at least 1,000 fixed-seed paired bootstrap replicates on saved test predictions;
3. direct bootstrap uncertainty for `auc_gap_fraction`, with raw AUC differences substituted if its denominator is unstable.

Every formal evaluation must save one prediction per test jet with stable jet identity. Use paired comparisons for A-B, B-C, C-D, C-A, and D-A.

## 11. Reproducibility Requirements

Every formal run must save:

| Field | Purpose |
|---|---|
| `run_id`, `git_commit` | Code traceability |
| source record IDs and canonical PFNs | Corpus traceability |
| source manifest hash and HDF5 hashes | Artifact traceability |
| CMSSW release, global tag, container digest | Extraction reproducibility |
| split-rule version and exact hash input | Split reproducibility |
| run/lumi/event/jet identity | Pairing and overlap audit |
| feature and normalization versions | Input traceability |
| PID vocabulary and missing-track policy | Config C/D traceability |
| pT/eta and pileup-weight versions | Confound-control traceability |
| checkpoint source and SHA-256 | Initialization traceability |
| loaded and skipped layers | Adapter audit |
| feature config, training size, seed | Experimental condition |
| hyperparameters and early-stopping state | Training reproducibility |
| hardware, runtime, and peak memory | Compute audit |
| test metrics and prediction file | Statistical analysis |
| failure status | Complete run accounting |

Figures and tables must be generated from run records, not manually edited spreadsheets.

## 12. Compute and Storage Budget

### 12.1 Raw-Data Planning Bound

The candidate corpus is 3.542 TiB, but production should stream only required files. The preliminary TT prefix scan observed 5 kinematically selected jets per 1,000 events before truth matching. At that raw rate, 100,000 candidates require approximately 20 million TT events and about 0.68 TB of input; truth matching increases the required volume.

The current local access tests measured only about 28-87 kB/s and are not suitable for production. E0 must run on CERN-adjacent, institutional, or cloud infrastructure with measured high-throughput EOS/XRootD access.

### 12.2 Blocking Measured-Cost Table

Do not approve bulk extraction or E2 until E0/E1 replace every `TBD` below with measured values:

| Measurement | Pilot value | Required projection |
|---|---:|---|
| CMSSW CPU seconds per input event | TBD | Full TT and QCD CPU-hours |
| CMSSW wall time per source file | TBD | Production wall time and parallelism |
| Sustained source throughput | TBD | Files and bytes per hour |
| Source bytes per selected signal jet | TBD | Raw TT bytes for frozen `n_max` |
| Compact ROOT bytes per selected jet | TBD | Intermediate storage |
| HDF5 bytes per selected jet | TBD | Training storage |
| Matched signal jets per TT file | TBD | Required TT file count |
| Selected QCD jets per record and file | TBD | Active mixture and file count |
| GPU runtime per E1 condition | TBD | E2 GPU-hours |
| Peak GPU memory | TBD | Instance class |
| Provider CPU/GPU/storage prices | TBD | Dollar budget with 25% reserve |

These values are intentionally not inferred from the schema feasibility scan.

### 12.3 Scope Reduction Order

If projected cost exceeds the active budget:

1. Drop random-initialized OmniLearned controls.
2. Reduce Deep Sets/PFN to A versus D at `n_max`.
3. Drop optional five-seed expansions except the most important paired contrast.
4. Only then reduce `n_max` through a documented amendment.

Do not reduce A-D coverage first and do not silently change the physics selection.

## 13. Timeline and Decision Gates

| Phase | Duration | Exit criterion |
|---|---:|---|
| E0 CMSSW data/yield/cost pilot | 2-4 weeks | All E0 gates pass and `n_max` is frozen |
| E0.5 checkpoint/adapter spike | 1-3 days | A-D loading and tiny fine-tune pass |
| E1 training pilot | 1-2 weeks | Reproducible pilot and measured GPU budget |
| E2 core matrix | 3-5 weeks | Core runs and saved paired predictions complete |
| E3 controls | 1-3 weeks | Minimum baseline complete or formally deferred |
| Analysis and figures | 1-2 weeks | Tables and intervals generated from run records |
| Writing | 2-3 weeks | Methods, Results, Discussion, Limitations, and Reproducibility Appendix drafted |

Decision gates:

| Gate | Decision |
|---|---|
| After E0 schema checks | Stop if daughter references, decoded D fields, or labels are invalid |
| After E0 yield/cost measurement | Freeze or amend `n_max`; approve or reject production host |
| After E0.5 | Use adapter swap, use documented neutralization, or remove pretrained-transfer claims |
| After E1 | Approve E2 only if measured compute and storage fit the active budget |
| Mid-E2 | Complete planned seeds even for near-null differences; do not add post-hoc features |
| After E2 | Add the minimum baseline before broader controls |

## 14. Risk Register

| Risk | Consequence | Mitigation |
|---|---|---|
| Matched-top yield is too low | `10^5` signal jets are infeasible | E0 yield pilot and explicit `n_max` amendment |
| Remote throughput is too low | Extraction stalls or becomes expensive | Run near EOS; measure before production |
| Daughter references fail | Constituent tensors are invalid | CMSSW pilot on multiple TT/QCD files |
| Generator traversal is wrong | Signal labels are contaminated | Hand-inspected events and unit checks |
| Impact-parameter units or PV semantics are wrong | Config D is uninterpretable | Store raw decoded values and validate in CMSSW |
| Charged no-track rate is high | Zero filling biases Config D | 1% review gate and class/split audit |
| PID duplicates charge sign | B-to-C contrast is confounded | Use absolute PDG ID categories only |
| QCD record mixture leaks process information | Inflated or corpus-specific performance | Freeze mixture; exclude record/bin identity from inputs |
| pT, eta, or pileup differs by class | Model learns confounds | Training-only matching/reweighting and declared diagnostics |
| Split hash is implemented inconsistently | File or event leakage | Hash exact manifest PFN bytes and test disjointness |
| Exact pretraining overlap is later found | Record-disjoint claim fails | Recheck checkpoint manifest and downgrade wording |
| Adapter loading fails | Reduced-feature initialization is confounded | E0.5 fallback decision and explicit limitation |
| Results are near-null | Narrative appears weak | Report controlled negative evidence with paired uncertainty |

## 15. Minimum Viable Paper

The minimum paper must include:

1. CMS record IDs, manifest hash, CMSSW environment, and corrected-AK8 selection.
2. Generator-matched fully hadronic top labels and QCD-only background labels.
3. Exact-PFN file split and no-overlap audit.
4. Frozen QCD record mixture and pT/eta/pileup controls.
5. One full-D source tensor and nested A-D views.
6. Charge-sign-free PID and audited missing-track policy.
7. Configuration-specific fine-tuning across three frozen training scales.
8. At least three seeds per core condition.
9. Paired AUC, background rejection, data-efficiency statistics, and saved-prediction bootstrap.
10. Extraction, storage, and training cost measurements.
11. A limitation stating that the result is conditional cross-corpus adaptation, not unseen-class transfer or universal causal feature importance.

For a publication-strength version, add the fixed Deep Sets/PFN-style A-versus-D control.

## 16. Expected Outputs

| Output | Description |
|---|---|
| Research Plan v0.4 | This document |
| Source manifest | Record IDs, PFNs, checksums, sizes, and stable hash |
| E0 CMSSW pilot report | Schema, labels, yield, missingness, throughput, CPU, and storage |
| Compact full-D dataset | Flat ROOT and HDF5 with immutable provenance |
| Feature/split specification | A-D columns, normalization, PID, masks, and exact split rule |
| Checkpoint loading report | Artifact metadata and layer-level loading audit |
| Run manifest | Machine-readable E1-E3 matrix |
| Predictions and metrics | Paired AUC, rejection, bootstrap, and data-efficiency outputs |
| Figures and manuscript | Generated from run records |
| Reproducibility appendix | Commands, hashes, environments, costs, and failures |

## 17. Traceability to the Feasibility Decision

| Required v0.4 change | Location in this plan |
|---|---|
| Replace JetClass with frozen CMS 2015 records | Section 4.1 |
| Replace JetClass columns with CMS-to-A-D mapping | Section 5.2 |
| Use record-disjoint cross-corpus wording | Sections 0 and 3 |
| Add CMSSW extraction and raw throughput | Sections 6, 9, and 12 |
| Use generator-matched hadronic-top signal | Section 4.3 |
| Add PID-without-sign and missing-track audit | Sections 5.2-5.3 |
| Retain fine-tune-without-X and paired evaluation | Sections 7, 9, and 10 |
| Define QCD mixture, corrected pT, pileup diagnostic, and split bytes | Sections 4.2 and 4.4-4.6 |
| Revise `n_max` if measured yield requires it | Sections 0, 2, 9, and 12 |
| Add measured CMSSW CPU, throughput, and storage cost | Sections 9 and 12.2; values remain blocking until E0 |

## 18. One-Sentence Version

This project quantifies how nested reconstructed-particle feature availability affects the performance and labeled-data efficiency of a pretrained OmniLearned PET-style model during dataset-record-disjoint fine-tuning on generator-matched CMS 2015 boosted-top versus QCD jets.
