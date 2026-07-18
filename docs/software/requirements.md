# particleML Software Requirements Specification

## Document Control

| Field | Value |
|---|---|
| Status | Approved requirements baseline; local implementation present; formal experiments deferred |
| Document version | 1.1.0 |
| Software documentation suite | 1.2.0 |
| Research baseline | Research Plan v0.4.0 |
| Date | 2026-07-18 |
| Language | English |

This document defines what the publication-supporting particleML software must
do. It does not assert that the required software, datasets, runs, figures, or
scientific results already exist.

## 1. Purpose, Scope, and Authority

The software supports the CMS 2015 top-versus-QCD feature-availability study
defined by [Research Plan v0.4](../research/research-plan.md). It must make the
following evidence chain auditable:

```text
research question -> software requirement -> component -> test
-> experiment artifact -> figure or table -> manuscript claim
```

The first publication-supporting scope is:

- CMS 2015 `RunIIFall15MiniAODv2` generator-matched hadronic-top versus declared
  QCD binary classification;
- nested particle feature configurations A through D;
- a pretrained OmniLearned PET-style primary model, with a gate-controlled
  supervised fallback if pretrained integration is not defensible;
- a Deep Sets/PFN-style publication-strength control;
- E0 data and cost audit, E0.5 checkpoint/adapter spike, E1 pilot, E2 core
  matrix, and scoped E3 controls; and
- deterministic manifests, run records, predictions, statistics, reports, and
  provenance required to support paper claims.

Generation, anomaly detection, likelihood-ratio estimation, a web interface,
distributed training, a model-serving API, and broad architecture benchmarking
are outside this baseline.

Conflicts are resolved in this order:

1. [Research Plan v0.4](../research/research-plan.md) controls the scientific
   question, claim boundary, data selection, experiment matrix, and evidence.
2. This document controls required software behavior and acceptance criteria.
3. [Software Architecture](./architecture.md) controls component boundaries,
   dependency direction, data flow, and execution topology.
4. [Implementation Specification](./specification.md) controls interfaces,
   algorithms, serialized contracts, commands, and artifact layout.
5. JSON Schemas under `schemas/` control serialized artifact validation.
6. [Traceability Matrix](./traceability-matrix.md) records mappings but does not
   override a source of truth.

Any conflict between prose and a JSON Schema is a release blocker. Both must be
corrected in the same change.

## 2. Stakeholders, Assumptions, and Constraints

Primary users are the researcher implementing and operating the study. Other
stakeholders are supervisors, collaborators, reviewers, and future maintainers
who need to reproduce the evidence without undocumented notebook state.

The baseline assumes:

- E0 will run in pinned CMSSW 7.6.7 near sufficiently fast EOS/XRootD access;
- ML conversion and training will run in a separate modern Python environment;
- the official OmniLearned repository is pinned to an audited revision;
- formal data and run artifacts live outside Git, while schemas, manifests,
  configurations, and compact audit records are versioned when practical; and
- E0 and E0.5 discovery outputs may select among explicitly permitted policies,
  but formal execution must fail when a required policy remains unresolved.

External constraints are the CMS Open Data licenses and record metadata,
available compute/storage budget, the official OmniLearned interface, and the
publication-integrity boundary in the research plan. Direct filesystem and
HTTP/HTTPS access are permitted; no intermediate web service is required.

## 3. Status Vocabulary

Each requirement has one lifecycle status:

| Status | Meaning |
|---|---|
| `specified` | Required behavior is defined, but repository evidence does not establish implementation. |
| `implemented` | Code or documentation exists, but the required verification evidence is incomplete. |
| `verified` | The mapped automated check or experiment gate has passed and retained evidence is identified. |
| `deferred` | Deliberately outside the active baseline, with the boundary recorded. |

Identifiers are stable and must never be reused after deletion.

## 4. Functional Requirements

### Data and Preprocessing

### FR-DATA-001 — Frozen source manifest

**Status:** `implemented`

The system shall consume a persistent, sorted source manifest containing CMS
record ID, exact canonical PFN, checksum, and byte size. It shall reproduce and
record the manifest SHA-256 before formal extraction. A hash without the
manifest is insufficient provenance.

### FR-DATA-002 — CMS extraction

**Status:** `implemented`

The CMSSW extractor shall read the frozen records, apply the research-plan AK8
selection, resolve packed daughters, assign labels, and write compact flat ROOT
artifacts containing raw A-D fields, identities, cutflow, and provenance. It
shall not own HDF5 normalization or model behavior.

### FR-DATA-003 — Leakage-safe labels

**Status:** `implemented`

Signal shall require an unambiguous, last-copy, fully hadronic top match with
the top and each `bqq'` daughter contained within the specified radius.
Background shall come only from declared QCD records. TT jets that fail the
signal definition shall not become background.

### FR-DATA-004 — Canonical full-D dataset

**Status:** `implemented`

The system shall convert compact ROOT data into one immutable, full-D canonical
HDF5 dataset with at most 150 pT-ordered constituents per jet, a boolean mask,
binary label, stable jet identity, and provenance. All scientific transforms
shall be recorded and content hashed.

### FR-DATA-005 — Nested A-D views

**Status:** `implemented`

Configurations A-D shall be column views of the same canonical jets. Jet
membership, particle ordering, masks, split assignment, and training subset
shall be identical across configurations. PID shall use absolute-PDG-ID species
categories so Config C does not duplicate charge sign from Config B.

### FR-DATA-006 — Deterministic split

**Status:** `implemented`

The system shall assign source files to train, validation, and test partitions
using the exact UTF-8 PFN SHA-256 modulo-10 rule in Research Plan v0.4. It shall
detect and reject PFN or event overlap and report class/record counts for every
partition.

### FR-DATA-007 — Training-only fitted state

**Status:** `implemented`

Normalization, pT/eta control, optional pileup reweighting, PID vocabulary, and
any approved impact-parameter transform shall be fitted or frozen using the
training partition only, hashed, and applied unchanged to validation and test.
No unresolved transform may receive an implicit default.

### FR-DATA-008 — Fixed training subsets

**Status:** `implemented`

The system shall materialize class-balanced, nested training subsets for
`10^3`, `10^4`, and provisional `10^5` jets per class, or a documented amended
grid after E0. A dedicated subset seed shall be independent of model-training
seeds. Selected identities shall be reused across A-D and all model conditions.

### FR-DATA-009 — QCD mixture and confound controls

**Status:** `implemented`

The system shall freeze the active QCD-record mixture and deterministic
round-robin sampling. It shall fit pT/eta control on training data, audit pileup
diagnostics, and prevent record identity, generator bin, truth, pileup variables,
or weights from entering model tensors.

### FR-DATA-010 — Data audit

**Status:** `implemented`

The system shall report product presence, daughter resolution, label cutflow,
feature finiteness, units, missing charged-track rate, truncation, masks,
padding, class/split counts, leakage probes, artifact hashes, throughput, and
storage cost. A charged no-track rate above 1% shall block E1 pending review.

### Models and Checkpoints

### FR-MODEL-001 — Official OmniLearned boundary

**Status:** `implemented`

The primary path shall reuse the pinned official OmniLearned package through a
process boundary. The project shall not fork or reimplement PET, its optimizer,
checkpoint storage, or its training loop for the baseline study.

### FR-MODEL-002 — Custom-data index

**Status:** `implemented`

Before custom-data training, the system shall run the pinned OmniLearned
`dataloader`/index-building step, validate the produced index, hash it, and
record that hash in every dependent run. Training shall fail if the index is
missing or stale.

### FR-MODEL-003 — Configuration-specific adapters

**Status:** `implemented`

Each A-D condition shall use a newly initialized input adapter and binary head,
load the same shape-compatible non-input backbone weights, record every loaded,
skipped, and mismatched tensor, and fine-tune end to end. Conditional/global
inputs shall be rejected for the primary classifier.

### FR-MODEL-004 — Checkpoint audit gate

**Status:** `implemented`

Before E1, the system shall record checkpoint source, immutable revision or
tag, license, SHA-256, documented pretraining corpus, input schema, and
normalization convention. All A-D forward/backward passes must be finite and a
tiny fine-tune must reduce loss.

### FR-MODEL-005 — Pretraining fallback

**Status:** `implemented`

If checkpoint or adapter compatibility cannot be established, the system shall
either use the E0.5-approved neutralization policy with its limitation recorded,
or fall back to a supervised OmniLearned-architecture ablation. The latter
shall automatically remove pretrained-transfer claims from eligible reports.

### FR-MODEL-006 — Deep Sets/PFN control

**Status:** `implemented`

The project shall provide a small in-repository masked Deep Sets/PFN-style
classifier for the required E3 A-versus-D control. It shall reuse the same
splits, subsets, preprocessing, evaluation, and artifact contracts as the
primary model.

### Training and Orchestration

### FR-TRAIN-001 — Stage-gated experiment matrix

**Status:** `implemented`

The orchestrator shall represent E0, E0.5, E1, E2, and E3 explicitly and refuse
to start a stage until all mandatory prior gate records pass. The E2 matrix
shall be generated from the frozen A-D configurations, training scales, and
three first-pass seeds rather than from hand-entered commands.

### FR-TRAIN-002 — Deterministic clean commands

**Status:** `implemented`

Every formal operation shall be executable from a non-interactive command with
validated configuration. Resume shall reuse an artifact only when input and
configuration hashes match; otherwise it shall fail or create a new run ID.
Formal artifacts shall never be silently overwritten.

### FR-TRAIN-003 — Run records

**Status:** `implemented`

Every attempted training run shall emit a run record conforming to
`schemas/run-record.schema.json`, including code, data, preprocessing,
checkpoint, condition, hyperparameters, environment, timing, memory, artifacts,
metrics when successful, and failure information when unsuccessful.

### FR-TRAIN-004 — Complete failure accounting

**Status:** `implemented`

Failed or interrupted formal attempts shall remain visible. A failed run shall
contain a stable failure code and message, preserve available logs, and shall
not be included in aggregate results as if it had succeeded.

### Evaluation and Reporting

### FR-EVAL-001 — Aligned predictions

**Status:** `implemented`

Every successful formal evaluation shall save one signal score and target for
each fixed test jet in stable order, with stable jet identity and payload hash.
Prediction metadata shall conform to `schemas/prediction.schema.json`.

### FR-EVAL-002 — Required metrics

**Status:** `implemented`

The evaluator shall compute ROC AUC, background rejection at signal efficiencies
0.30 and 0.50, auxiliary accuracy, and the research-plan data-efficiency
summary. Numerical definitions and undefined cases shall follow the
implementation specification.

### FR-EVAL-003 — Paired uncertainty

**Status:** `implemented`

The system shall compute paired A-B, B-C, C-D, C-A, and D-A comparisons on
identically ordered test identities, use at least 1,000 fixed-seed paired
bootstrap replicates, and report seed variation separately from event-level
bootstrap uncertainty.

### FR-EVAL-004 — Evidence-derived reports

**Status:** `implemented`

Tables and figures shall be generated only from schema-valid run records and
prediction artifacts. A report shall distinguish planned, failed, and completed
runs and shall not emit a paper-claim-ready status unless all mapped gates and
controls pass.

### Reproducibility and Traceability

### FR-REP-001 — Content-addressed provenance

**Status:** `implemented`

The system shall retain hashes for source manifests, split manifests, canonical
datasets, views, fitted preprocessing state, OmniLearned indices, checkpoints,
predictions, run records, and generated tables/figures. Hash algorithms and
canonicalization rules shall be versioned.

### FR-REP-002 — Machine-readable validation

**Status:** `implemented`

Run records, split manifests, and prediction metadata shall validate against
JSON Schema Draft 2020-12 before downstream consumption. Unknown properties at
defined schema boundaries shall be rejected.

### FR-REP-003 — Evidence status propagation

**Status:** `implemented`

Requirement, test, experiment, artifact, figure, and claim statuses shall use
the controlled lifecycle vocabulary. A downstream item may not have a stronger
status than its unmet upstream dependency.

## 5. Non-Functional Requirements

### NFR-COR-001 — Fail-closed scientific correctness

**Status:** `implemented`

Missing provenance, unresolved units, overlap, non-finite values, stale hashes,
unapproved preprocessing, model-input leakage, and schema violations shall
block the affected formal stage rather than degrade to warnings.

### NFR-DET-001 — Determinism

**Status:** `implemented`

Given identical versioned inputs, configuration, and seeds, manifest assignment,
subset identity, A-D views, command construction, and report aggregation shall
be reproducible. Stochastic ML operations shall record deterministic settings
and any known nondeterministic kernels.

### NFR-PORT-001 — Environment separation and portability

**Status:** `implemented`

CMSSW extraction and modern Python ML execution shall have separate, pinned
environment records and exchange only contract-defined artifacts. Local Windows
development may validate documents and compact fixtures; production extraction
shall run on a compatible POSIX host near the data.

### NFR-OBS-001 — Resource observability

**Status:** `implemented`

E0 and E1 shall measure CPU/GPU time, wall time, source bytes, throughput,
intermediate and final storage, peak GPU memory, checkpoint size, and failures.
E2 shall remain blocked until a budget projection with reserve is retained.

### NFR-ROB-001 — Restartability and artifact integrity

**Status:** `implemented`

Stage outputs shall be written to a temporary location and published with a
completion record only after validation. POSIX production may use atomic rename;
Windows development shall rely on an explicit `COMPLETED.json` sentinel. Resume
shall verify hashes before reuse.

### NFR-MNT-001 — Maintainable boundaries

**Status:** `implemented`

Extraction, conversion, views, model integration, orchestration, metrics, and
reporting shall be independently testable. CLI code shall remain thin, and
notebooks shall consume package APIs without owning canonical logic.

### NFR-PUB-001 — Publication integrity

**Status:** `implemented`

The system shall never infer an experimental result from configuration or mark
a planned artifact as completed. Manuscript claim eligibility requires mapped
verified requirements, tests, gates, retained predictions, and the required
baseline/control evidence.

## 6. Acceptance Criteria

### AC-E0-001 — Data, yield, leakage, and cost pilot

**Status:** `deferred`

E0 passes only when the frozen manifest, multi-file TT/QCD extraction,
daughter resolution, A-D fields and units, labels, charged no-track rate, yield
projection, exact split integrity, QCD mixture, confound controls, shuffled-label
probe, HDF5/view checks, artifact hashes, and measured cost table all pass. An
`n_max` change requires a versioned research-plan amendment.

### AC-E05-001 — Checkpoint and adapter spike

**Status:** `deferred`

E0.5 passes only when checkpoint identity and license, pretraining-corpus
record, normalization policy, OmniLearned index, layer-loading audit, finite A-D
forward/backward passes, and a decreasing tiny-fine-tune loss are retained.

### AC-E1-001 — Reproducible training pilot

**Status:** `deferred`

E1 passes only when A and D at `10^3` and `10^4` jets per class run from clean
commands with one seed, schema-valid run records and aligned predictions, valid
metrics, measured runtime/memory/storage, and an approved E2 budget projection.

### AC-E2-001 — Core matrix

**Status:** `deferred`

E2 passes only when every approved A-D, training-scale, and three-seed condition
has either a successful schema-valid record or an explicitly retained failure;
the fixed paired test set is used; required paired metrics and uncertainty are
generated; and no condition is silently omitted.

### AC-E3-001 — Publication-strength control

**Status:** `deferred`

E3's minimum acceptance criterion is the Deep Sets/PFN A-versus-D comparison at
the frozen largest training scale with three seeds, using the same data,
preprocessing, predictions, and statistical contracts. Random-initialized
OmniLearned remains optional and broader model benchmarking remains deferred.

## 7. Release and Change Control

A requirement change that alters the dataset, label, split, feature meaning,
training matrix, primary endpoint, or claim boundary requires a Research Plan
v0.4.x amendment before dependent formal runs. Other contract changes require a
documentation-suite version increment, synchronized schema changes where
applicable, a traceability update, and a successful consistency check.
