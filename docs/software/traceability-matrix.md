# particleML Requirements and Evidence Traceability Matrix

## Document Control

| Field | Value |
|---|---|
| Status | Approved traceability baseline; implementation and experiment evidence not yet verified |
| Document version | 1.1.0 |
| Software documentation suite | 1.1.0 |
| Research baseline | Research Plan v0.4.0 |
| Date | 2026-07-17 |

This matrix maps the [Software Requirements Specification](./requirements.md)
to the [Software Architecture](./architecture.md),
[Implementation Specification](./specification.md), planned tests, experiment
gates, and paper evidence. `specified` means that a mapping exists; it does not
mean the implementation, test, run, artifact, figure, or claim exists.

## 1. Research Questions to Evidence

| Research question | Software requirements | Required experiment evidence | Planned paper evidence | Status |
|---|---|---|---|---|
| RQ1: feature availability across A-D | FR-DATA-004, FR-DATA-005, FR-MODEL-003, FR-TRAIN-001, FR-EVAL-001, FR-EVAL-002 | E0 identity-equivalent views; E0.5 adapters; E2 paired matrix | Figure F1 AUC versus training scale; Figure F2 paired AUC deltas; Table T2 core matrix | `specified` |
| RQ2: labeled-data efficiency | FR-DATA-008, FR-TRAIN-001, FR-EVAL-002, FR-EVAL-003 | Nested frozen subsets; E2 per-scale predictions and paired bootstrap | Figure F1; Table T3 `auc_gap_fraction` or raw-difference fallback | `specified` |
| RQ3: robustness of feature ranking | FR-MODEL-006, FR-TRAIN-004, FR-EVAL-003, AC-E2-001, AC-E3-001 | Three core seeds and Deep Sets/PFN A-versus-D control | Figure F3 seed/baseline comparison; Table T4 robustness summary | `specified` |

## 2. Requirement Traceability

| Requirement | Architecture component | Specification contract | Planned automated test | Gate/artifact | Status |
|---|---|---|---|---|---|
| FR-DATA-001 | Manifest service | §2.1 Source Manifest | `tests/test_manifest.py::test_canonical_manifest_bytes_and_hash` | E0 `manifests/source-manifest.tsv` | `specified` |
| FR-DATA-002 | CMSSW extractor | §3.1 CMSSW Output | `cmssw/.../test/test_extractor_cfg.py`; CMSSW fixture job | E0 compact ROOT and extraction report | `specified` |
| FR-DATA-003 | CMSSW extractor | §3.1; Research Plan §4.3-4.4 | hand-inspected truth fixtures and `test_truth_matching` | E0 label/cutflow audit | `specified` |
| FR-DATA-004 | Dataset service | §3.3 Canonical HDF5 | `tests/test_dataset.py::test_canonical_layout` | E0 canonical full-D HDF5 | `specified` |
| FR-DATA-005 | View service | §4.3 Materialized Views | `tests/test_views.py::test_ad_identity_equivalence`; PID sign/order test; `tests/test_software_document_contract.py` native integer-PID/obsolete-contract regression | E0 A-D view audit | `specified` |
| FR-DATA-006 | Manifest service | §2.2 Split Algorithm | `tests/test_manifest.py::test_exact_pfn_split`; overlap fixtures | E0 split manifest and overlap report | `specified` |
| FR-DATA-007 | Dataset service | §4.1 Fitted State | `tests/test_dataset.py::test_fit_uses_train_only` | E0/E0.5 preprocessing policy | `specified` |
| FR-DATA-008 | Manifest/view services | §4.2 Training Subsets | `tests/test_views.py::test_balanced_nested_subsets` | split-manifest subset payloads | `specified` |
| FR-DATA-009 | Manifest/dataset services | §4.2 and preprocessing contract | `tests/test_dataset.py::test_qcd_round_robin_and_no_audit_inputs` | E0 mixture/confound report | `specified` |
| FR-DATA-010 | Dataset, metrics, and E0 aggregation services | §3.2-3.3; §6.2; §7-8 | `tests/test_audit.py` and `tests/test_e0.py` including shuffled-label, resource, and external-evidence gates | Schema-valid E0 data/yield/leakage/cost audit | `specified` |
| FR-MODEL-001 | `src/particleml/model_integration.py` external boundary | §5.1 Pinned External Dependency | `tests/test_model_integration.py::test_subprocess_boundary_uses_argument_array_shell_false_and_redacts`; formal environment pending | E0.5 dependency audit | `implemented` |
| FR-MODEL-002 | `src/particleml/model_integration.py` index validator and CLI resolver | §5.2 Custom-Data Index | `tests/test_model_integration.py::test_index_required_and_hashed_and_stale_view_rejected`; official RunPod index pending | E0.5 index completion records | `implemented` |
| FR-MODEL-003 | `adapter_flags`, `build_train_argv`, and tensor audit | §5.3 Adapter and Training Command | exact A-D native PID/additional-feature argv snapshots; conditional-flag rejection; tensor-shape report | E0.5 layer-loading audit | `implemented` |
| FR-MODEL-004 | checkpoint validator, E0.5 contract, and gate aggregator | §5.1-5.3 | `tests/test_checkpoint.py`; A-D RunPod smoke still pending | E0.5 checkpoint audit | `implemented` |
| FR-MODEL-005 | explicit fallback resolver and E0.5 model condition | §5.3 and claim eligibility | `tests/test_reporting.py::test_fallback_requires_explicit_approval_and_narrows_model_condition`; formal approval absent | E0.5 policy decision | `implemented` |
| FR-MODEL-006 | Deep Sets/PFN component | §5.4 Baseline | `tests/test_baseline.py` mask, shape, and train smoke | E3 baseline run records | `specified` |
| FR-TRAIN-001 | `src/particleml/experiment.py` gate and matrix resolver | §6; architecture §6.3 | `tests/test_experiment.py::test_gate_order_and_matrix`; formal gates remain blocked | E0-E3 gate ledger | `implemented` |
| FR-TRAIN-002 | experiment CLI and deterministic dry-run ledger | §6.1-6.4 | dry-run, exact-key, stable-identity, and no-overwrite tests | resolved configs and completion records | `implemented` |
| FR-TRAIN-003 | run-record contract and immutable publisher | §7 and run-record Schema | successful, failed, timed-out, and interrupted schema fixtures | every `runs/*/run-record.json` | `implemented` |
| FR-TRAIN-004 | one-attempt lifecycle and matrix-status service | §9 Error Taxonomy | failure/interruption retention, no-auto-retry, and missing-condition tests | failed run records and logs | `implemented` |
| FR-EVAL-001 | prediction array/payload validator | §7; prediction Schema | identity order, duplicate, target mismatch, finite-score, and payload-hash tests | prediction metadata and payload | `implemented` |
| FR-EVAL-002 | centralized metrics service | §8.1 Per-Run Metrics | golden AUC/rejection/accuracy, zero-background, and unstable-ratio fixtures | E1-E3 run metrics | `implemented` |
| FR-EVAL-003 | `paired_stratified_bootstrap` and seed-summary service | §8.2 Paired Comparisons | deterministic PCG64 stratified/common-index bootstrap, mismatch, contrast-set, percentile, and seed-summary fixtures | E2/E3 comparison artifacts | `implemented` |
| FR-EVAL-004 | Reporting service | §7-8 | aggregation completeness and ineligible-claim tests | generated reports, figures, claim ledger | `specified` |
| FR-REP-001 | Contract validator/artifact lifecycle | architecture §8; spec §6.4-7 | content hash and stale-resume tests | hashes and `COMPLETED.json` | `specified` |
| FR-REP-002 | Contract validator | §7 Serialized Contracts | `scripts/validate_software_docs.py`; schema fixtures | five JSON Schemas and validated artifacts | `implemented` |
| FR-REP-003 | Reporting/traceability | requirements §3; reporting contract | status monotonicity tests | matrix and claim ledger | `specified` |
| NFR-COR-001 | All fail-closed boundaries | §9 Error Taxonomy | negative contract/leakage/unit/identity fixtures | failed gate/run records | `specified` |
| NFR-DET-001 | Manifest, views, orchestration, metrics | §2.2, §4.2, §8.2 | repeated hash/subset/bootstrap regression tests | deterministic hashes and seed records | `specified` |
| NFR-PORT-001 | Execution topology | architecture §3; spec §3.1 | environment-record validation; compact local fixtures | CMSSW and ML environment records | `specified` |
| NFR-OBS-001 | Extractor/orchestrator | requirements §5; run timing contract | timing/memory field contract tests | E0 cost table and E1 budget projection | `specified` |
| NFR-ROB-001 | Artifact lifecycle | architecture §8; spec §6.4 | partial-output and completion-sentinel tests | `COMPLETED.json` and retained failures | `specified` |
| NFR-MNT-001 | Component model | architecture §4 | import-boundary and thin-CLI tests | package/test structure | `specified` |
| NFR-PUB-001 | Reporting and traceability | architecture §7; spec §7-8 | planned/failed/incomplete claim-eligibility tests | claim ledger and generated evidence | `specified` |
| AC-E0-001 | E0 control path | requirements §6; architecture §6.3; specification §6.2 and §7 | `tests/test_e0.py` aggregate status and fixture non-promotion tests; qualified-host acceptance run | completed, schema-valid E0 audit | `specified` |
| AC-E05-001 | E0.5 control path | requirements §6; spec §5 | aggregate checkpoint/adapter acceptance test | completed, schema-valid E0.5 audit | `specified` |
| AC-E1-001 | E1 control path | requirements §6; spec §6-8 | tiny matrix end-to-end fixture | pilot run/prediction records and budget | `specified` |
| AC-E2-001 | E2 control path | requirements §6; spec §8 | matrix completeness and paired-statistics test | core run matrix and comparison artifacts | `specified` |
| AC-E3-001 | E3 control path | requirements §6; spec §5.4 and §8 | baseline matrix completeness test | Deep Sets/PFN run and comparison artifacts | `specified` |

## 3. Experiment Gates to Publication Evidence

| Gate | Required retained artifacts | Planned figure/table dependency | Eligible claim only after pass | Current status |
|---|---|---|---|---|
| E0 | source/split manifests, compact ROOT, canonical HDF5, preprocessing policy, data/yield/leakage/cost audit | T1 dataset and audit summary; Methods data pipeline | The selected CMS 2015 corpus can support the frozen downstream protocol | `specified` |
| E0.5 | checkpoint identity, license and corpus record, index hashes, layer-load report, A-D finite smoke results, tiny-loss trace | Methods model integration; reproducibility appendix | The same pretrained backbone is defensibly adapted across A-D, or the claim is explicitly narrowed | `specified` |
| E1 | A/D pilot run records, aligned predictions, metrics, timing/memory/storage, budget | pilot diagnostics are not primary paper results | The clean-command pipeline and resource projection are adequate for E2 | `specified` |
| E2 | complete A-D/scale/seed ledger, successful and failed records, predictions, paired statistics | F1, F2, T2, T3 | RQ1/RQ2 results under the frozen protocol | `specified` |
| E3 | Deep Sets/PFN A/D records and paired statistics; optional random-initialization records | F3, T4 | Feature ranking robustness beyond the primary measurement system | `specified` |

## 4. Planned Paper Evidence Definitions

| ID | Planned evidence | Inputs | Integrity constraint | Status |
|---|---|---|---|---|
| T1 | Dataset, split, yield, missingness, and cost summary | E0 audits and manifests | Values are generated from retained audits, not copied by hand | `specified` |
| F1 | AUC and background rejection versus training size for A-D | E2 schema-valid runs | Show every seed and uncertainty convention | `specified` |
| F2 | Paired A-B, B-C, C-D, C-A, and D-A deltas | aligned E2 predictions | Exact test identity equality and paired bootstrap required | `specified` |
| T2 | Complete core condition matrix | all E2 run records | Failed/missing conditions remain visible | `specified` |
| T3 | Data-efficiency summary | E2 scale predictions | Use frozen `n_max`; replace unstable ratio with raw differences | `specified` |
| F3 | Seed and baseline robustness comparison | E2 plus required E3 baseline | Do not generalize beyond tested conditions | `specified` |
| T4 | Checkpoint, adapter, environment, and reproducibility appendix | E0.5 audits and all formal run records | Mutable nicknames without hashes are prohibited | `specified` |

The permitted high-level manuscript framing is a dataset-record-disjoint
cross-corpus adaptation study under controlled feature availability. It is not
an unseen-class, cross-detector, universal causal feature-importance, or broad
foundation-model-superiority claim.

## 5. Maintenance Rules

- Every active requirement ID must appear exactly once in Section 2.
- A test or artifact path in this matrix may be planned; its status must remain
  `specified` until repository evidence exists.
- `implemented` requires an identified code/document artifact.
- `verified` requires an identified passing automated check or retained gate
  artifact.
- A failed or deferred upstream item prevents stronger downstream status.
- Changes to research questions, endpoints, `n_max`, dataset, labels, or split
  require the corresponding Research Plan v0.4.x amendment before this matrix
  is updated.
