# particleML Implementation Specification

## Document Control

| Field | Value |
|---|---|
| Status | Approved implementation contract; implementation not yet verified |
| Document version | 1.0.0 |
| Software documentation suite | 1.0.0 |
| Research baseline | Research Plan v0.4.0 |
| Date | 2026-07-16 |
| Target Python | 3.10 or newer in the pinned ML environment |

This document makes the behavior in the
[Software Requirements Specification](./requirements.md) and
[Software Architecture](./architecture.md) implementation-ready. Values that
must be discovered in E0 or E0.5 are required inputs, not guessed defaults.
The formal dataset is CMS 2015 `RunIIFall15MiniAODv2` simulation.

## 1. Public Types and Package Interfaces

All public Python functions use type annotations. Paths are `pathlib.Path`.
Serialized timestamps are UTC RFC 3339 strings ending in `Z`. SHA-256 values
are lowercase 64-character hexadecimal strings.

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal, Mapping, Sequence

class Split(str, Enum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"

class FeatureConfig(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class Stage(str, Enum):
    E0 = "E0"
    E05 = "E0.5"
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"

class ModelCondition(str, Enum):
    PRETRAINED_OMNILEARNED = "pretrained_omnilearned"
    RANDOM_OMNILEARNED = "random_initialized_omnilearned"
    DEEP_SETS_PFN = "deep_sets_pfn"

@dataclass(frozen=True)
class Artifact:
    path: Path
    sha256: str
    schema_version: str | None = None

@dataclass(frozen=True)
class ViewSpec:
    feature_config: FeatureConfig
    subset_id: str
    train_size_per_class: int
    subset_seed: int

@dataclass(frozen=True)
class RunSpec:
    stage: Stage
    model_condition: ModelCondition
    feature_config: FeatureConfig
    train_size_per_class: int
    model_seed: int
    view: Artifact
    split_manifest: Artifact
    preprocessing: Artifact
    checkpoint: Artifact | None
```

Required public functions are:

```python
def load_source_manifest(path: Path) -> SourceManifest: ...
def hash_source_manifest(manifest: SourceManifest) -> str: ...
def assign_split(canonical_pfn: str) -> Split: ...
def build_split_manifest(canonical: Artifact, config: SplitConfig) -> Artifact: ...
def convert_flat_root(inputs: Sequence[Path], config: ConversionConfig) -> Artifact: ...
def audit_canonical_dataset(canonical: Artifact, policy: AuditPolicy) -> AuditReport: ...
def materialize_view(canonical: Artifact, split_manifest: Artifact,
                     spec: ViewSpec, output_dir: Path) -> Artifact: ...
def build_omnilearned_index(view: Artifact, executable: Path) -> Artifact: ...
def audit_checkpoint(checkpoint: Path, policy: AdapterPolicy) -> CheckpointAudit: ...
def build_train_argv(spec: RunSpec, executable: Path) -> list[str]: ...
def execute_run(spec: RunSpec, artifact_root: Path, resume: bool) -> Artifact: ...
def evaluate_predictions(prediction: Artifact, config: EvaluationConfig) -> Metrics: ...
def paired_bootstrap(left: Artifact, right: Artifact,
                     config: BootstrapConfig) -> PairedInterval: ...
def generate_reports(run_records: Sequence[Artifact], output_dir: Path) -> Sequence[Artifact]: ...
```

Modules raise typed project exceptions. They do not call `sys.exit`; only the
CLI maps exceptions to exit codes.

## 2. Source Manifest and Identity Contracts

### 2.1 Source Manifest

The committed source manifest is UTF-8 without a byte-order mark, uses LF line
endings, contains no header, and has exactly one line per unique source file:

```text
record_id<TAB>canonical_pfn<TAB>adler32_checksum<TAB>size_bytes<LF>
```

Rows are sorted by numeric `record_id`, then the exact UTF-8 byte sequence of
`canonical_pfn`. PFNs are not trimmed, lowercased, URL-decoded, or protocol
normalized. Duplicate PFNs, empty fields, invalid checksums, non-positive sizes,
CRLF, or non-canonical order are errors. The source-manifest SHA-256 is computed
over the exact file bytes.

The approved baseline contains signal record 19980 and QCD candidate records
18373, 18376, 18377, 18355, and 18358. E0 freezes the active QCD subset without
changing the manifest format.

### 2.2 Split Algorithm

The implementation is exactly equivalent to:

```python
digest = hashlib.sha256(canonical_pfn.encode("utf-8")).digest()
bucket = int.from_bytes(digest, byteorder="big", signed=False) % 10
split = {0: "test", 1: "validation"}.get(bucket, "train")
```

All jets from one PFN inherit its split. Semantic validation rejects a PFN in
multiple partitions and a `(record_id, run, lumi, event)` identity in multiple
partitions.

### 2.3 Stable Jet Identity

The stable textual identity is:

```text
cms:<record_id>:<sha256(exact canonical PFN)>:<run>:<lumi>:<event>:<jet_index>
```

All numeric fields are base-10 without padding. `jet_index` is the zero-based
index within the selected reconstructed-jet collection before truth-label
rejection. The full PFN digest is used; identities are unique within a canonical
dataset. Identity arrays are stored in stable lexical order only where an
algorithm explicitly requires sorting; extraction order is otherwise retained
and recorded.

## 3. Extraction and Canonical HDF5

### 3.1 CMSSW Output

The CMSSW extractor runs under:

```text
CMSSW release: 7_6_7
Container: cmsopendata/cmssw_7_6_7-slc6_amd64_gcc493
Global tag: 76X_mcRun2_asymptotic_RunIIFall15DR76_v1
```

Each ROOT output contains a `jets` tree and a job-level metadata object. The
tree includes source identity, split bucket, event/jet identity, corrected jet
kinematics, class label, vertex diagnostics, raw constituent fields, constituent
count before/after truncation, track state, and truth/cutflow fields used only
for audit. The extractor stores the resolved container digest and Git commit.

The primary jet selection is `500 <= corrected_pt_GeV < 1000`, `abs(eta) < 2`,
AK8. The signal and background algorithms are copied from Research Plan v0.4
without local reinterpretation. Required product absence, daughter-resolution
failure, invalid PV access, or non-finite decoded values produces a structured
file failure and a non-zero job exit.

### 3.2 Constituent Transform Inputs

For each retained constituent:

- `delta_eta = candidate_eta - jet_eta`;
- `delta_phi` is wrapped to `[-pi, pi)`;
- `log_pt = ln(candidate_pt_GeV)` after the approved positive minimum cut;
- `log_energy = ln(candidate_energy_GeV)` after the approved positive minimum
  cut;
- `charge` is the decoded candidate charge;
- raw displacement fields are CMSSW-decoded values in the E0-validated unit.

The E0 preprocessing policy must provide positive
`min_particle_pt_gev` and `min_particle_energy_gev`. Their absence blocks
conversion; there is no built-in physics default. Constituents are sorted by
descending pT with original daughter index as the stable tie-breaker and then
truncated to 150.

PID encoding uses `abs(pdgId)`:

| Code | Category | Absolute PDG ID |
|---:|---|---:|
| 0 | unknown | every value not listed below |
| 1 | charged hadron | 211 |
| 2 | neutral hadron | 130 |
| 3 | photon | 22 |
| 4 | electron | 11 |
| 5 | muon | 13 |

Padding also stores code 0 but is distinguished by `mask=false`. Unit tests
must show that positive and negative PDG IDs map to the same code.

Track-state codes are audit-only:

| Code | Meaning |
|---:|---|
| 0 | padding |
| 1 | usable track details |
| 2 | neutral candidate |
| 3 | charged candidate without usable track details |

D values are zero for states 2 and 3. The missing charged-track fraction is
`count(state == 3) / count(state in {1, 3})`; a zero denominator is an audit
error for a non-empty selected dataset.

### 3.3 Canonical HDF5 Layout

The canonical HDF5 file uses gzip level 4 and jet-major chunks. String arrays
are UTF-8 variable-length strings. Required datasets and attributes are:

| Path | Shape/dtype | Meaning |
|---|---|---|
| `/particles/continuous` | `[N,150,9]`, `float32` | `delta_eta`, `delta_phi`, `log_pt`, `log_energy`, `charge`, `dxy_raw`, `dxy_error_raw`, `dz_raw`, `dz_error_raw` |
| `/particles/pid_type` | `[N,150]`, `uint8` | Frozen PID category code |
| `/particles/mask` | `[N,150]`, `bool` | Valid constituent mask |
| `/particles/track_state` | `[N,150]`, `uint8` | Audit-only track-state code |
| `/labels/pid` | `[N]`, `int8` | QCD `0`, top `1` |
| `/identity/jet_id` | `[N]`, UTF-8 | Stable identity |
| `/identity/record_id` | `[N]`, `uint32` | CMS record |
| `/identity/run` | `[N]`, `uint32` | Run number |
| `/identity/lumi` | `[N]`, `uint32` | Luminosity block |
| `/identity/event` | `[N]`, `uint64` | Event number |
| `/identity/jet_index` | `[N]`, `uint16` | Reconstructed-jet index |
| `/identity/pfn_sha256` | `[N]`, fixed ASCII | Exact-PFN SHA-256 |
| `/split/name` | `[N]`, enum/string | `train`, `validation`, `test` |
| `/audit/jet_pt` | `[N]`, `float32` | Corrected jet pT, never a primary input |
| `/audit/jet_eta` | `[N]`, `float32` | Jet eta, never a primary input |
| `/audit/pv_z` | `[N]`, `float32` | Pileup diagnostic only |
| `/audit/n_vertices` | `[N]`, `uint16` | Pileup diagnostic only |

Root attributes include `format_version`, `feature_version`,
`source_manifest_sha256`, `conversion_git_commit`, `cmssw_release`,
`container_digest`, `global_tag`, `max_particles=150`, feature names/order,
and the preprocessing-policy SHA-256.

Required semantic checks are finite valid entries, zero padding, mask-prefix
shape after pT sorting, unique jet identities, split consistency, allowed label
and PID values, no truth/process fields in model arrays, and content hashes.

## 4. Preprocessing, Subsets, and Views

### 4.1 Fitted State

`preprocessing.json` is immutable and records:

- schema/feature version and canonical dataset hash;
- the training identities used to fit state;
- continuous-feature location/scale values;
- positive particle cuts;
- PID vocabulary;
- pT/eta matching or reweighting policy;
- pileup diagnostic and any approved training-only reweighting;
- D-field unit and transform selected by E0.5;
- missing-track policy; and
- the content hash of the canonical JSON representation.

Canonical JSON uses UTF-8, sorted object keys, no insignificant whitespace, and
LF termination for hashing. Scientific policy fields are required. The loader
must not fill them from environment variables or defaults.

Continuous normalization is fitted on the complete frozen training partition,
not separately per training scale. Validation/test data and every model
condition reuse the same state. If E0.5 requires a checkpoint-native transform,
that exact documented transform replaces fitted scaling only for the fields it
names and is recorded with its source.

### 4.2 Training Subsets

The baseline subset seed is stored in the split manifest and configuration; no
library default is allowed. It is separate from `model_seed`.

For signal, rank training identities by the unsigned big-endian integer value
of `SHA256(str(subset_seed) + "\0" + jet_id)` and then by `jet_id`. For QCD,
build one such ranked queue per active record, iterate record IDs in ascending
order, and take one jet from each non-empty queue per round. The first `n`
identities per class form the subset at size `n`. Therefore smaller subsets are
prefixes of larger subsets.

If a requested class lacks `n` jets, materialization fails with
`INSUFFICIENT_CLASS_YIELD`; it never samples with replacement. The realized
identity lists and SHA-256 are stored in the split manifest. All A-D and model
seeds reuse them.

### 4.3 Materialized Views

Every view HDF5 contains:

| Dataset | Shape/dtype |
|---|---|
| `data` | `[N,150,F]`, `float32` |
| `mask` | `[N,150]`, `bool` |
| `pid` | `[N]`, `int8` |
| `jet_id` | `[N]`, UTF-8 |

View dimensions after one-hot PID expansion are:

| Config | `F` | Ordered fields |
|---|---:|---|
| A | 4 | normalized kinematics |
| B | 5 | A + charge |
| C | 11 | B + six PID one-hot channels |
| D | 15 | C + four approved D channels |

For valid unknown particles, the unknown PID bit is one. For configs A/B, PID
channels are absent rather than zero-filled unless E0.5 explicitly approves the
full-dimensional neutralization fallback. View metadata includes canonical,
split, subset, and preprocessing hashes; configuration; ordered field names;
and view SHA-256.

Identity equality across views is byte-for-byte equality of ordered `jet_id`,
`mask`, `pid`, and split/subset hashes. Any mismatch is `VIEW_IDENTITY_MISMATCH`.

## 5. OmniLearned and Baseline Contracts

### 5.1 Pinned External Dependency

The initial audited OmniLearned source revision is
`5091595d226b6021e967ab2ecfff832f40c026f6`. Formal configuration records the
resolved package version and executable path. Subprocesses use an argument
array, `shell=False`, a controlled working directory, captured stdout/stderr,
and an explicit timeout.

Before E1, E0.5 must freeze the actual checkpoint asset: source URL/path,
immutable release/tag, filename, SHA-256, license, pretraining-corpus record,
and input convention. The nickname `pretrain_s` alone is invalid provenance.

### 5.2 Custom-Data Index

`build_omnilearned_index` invokes the pinned package's documented `dataloader`
command for the materialized custom-data root. The exact argv and package
revision are recorded. The index is accepted only when the process succeeds,
expected index files exist, a smoke loader returns the expected row count, and
the index payload is hashed.

An index completion record includes view hash, command, dependency revision,
file list, row count, and index hash. Training refuses an index whose view hash
does not equal the requested view.

### 5.3 Adapter and Training Command

The project-owned adapter maps the view dimension to the pinned backbone input
dimension. It is randomly initialized using `model_seed`; the binary output
head is also reinitialized. The loader emits sorted arrays of loaded, skipped,
and mismatched tensor names with shapes.

The command builder has an explicit allowlist derived and tested against the
pinned CLI. It rejects conditional/global-input options and does not invent a
`clip_inputs` flag. Model-size and training-size variables are named
`model_size` and `train_size_per_class` respectively.

E0.5 validates A-D finite forward/backward passes and requires final tiny-run
training loss to be lower than its initial loss. The audit records values and
does not infer scientific performance from the smoke run.

### 5.4 Deep Sets/PFN Baseline

The baseline is a masked per-particle multilayer perceptron, sum or mean pooling
as frozen before E3, and a binary head. Its architecture, parameter count,
optimizer, and stopping policy are configuration data. It consumes the same
views and produces the same prediction and run-record contracts. It does not
receive audit/global variables.

## 6. Configuration and Command-Line Interface

### 6.1 Configuration Precedence

Precedence is:

1. explicit CLI arguments;
2. one versioned experiment YAML file;
3. environment variable `PARTICLEML_ARTIFACT_ROOT` for the artifact root only;
4. non-scientific built-ins such as log level and worker count.

Dataset records, cuts, labels, feature definitions, split policy, preprocessing,
seeds, model condition, metrics, and claim policy cannot be supplied by ambient
environment variables. Every resolved formal configuration is serialized and
hashed before execution. Unknown keys are errors.

### 6.2 Commands

The `particleml` entry point provides:

| Command | Required behavior |
|---|---|
| `manifest validate --source PATH` | Validate canonical bytes/order and print the source hash. |
| `split build --canonical PATH --config PATH --output PATH` | Create and semantically validate the split/subset manifest. |
| `convert --inputs ... --manifest PATH --policy PATH --output PATH` | Convert compact ROOT files into canonical HDF5. |
| `audit data --canonical PATH --split-manifest PATH --output PATH` | Run E0 data/leakage/cost checks and write a structured audit. |
| `view build --canonical PATH --split-manifest PATH --config A-D --subset ID --output PATH` | Materialize one immutable view. |
| `checkpoint audit --checkpoint PATH --views ROOT --policy PATH --output PATH` | Run the E0.5 checkpoint/adapter gate. |
| `index build --view PATH --output PATH` | Run and validate the OmniLearned custom-data index step. |
| `run train --config PATH [--resume]` | Validate gates and execute one formal run. |
| `evaluate --run-record PATH --output PATH` | Save aligned predictions and metrics. |
| `report build --run-records ROOT --output PATH` | Generate matrix status, statistics, tables, figures, and claim ledger. |
| `contracts validate --path PATH` | Validate a run, split, or prediction document and semantic hashes where available. |

Commands write machine-readable output to files and concise diagnostics to
stderr. `--dry-run` resolves configuration, dependencies, hashes, and argv but
does not execute extraction/training or publish artifacts.

### 6.3 Exit Codes

| Code | Meaning |
|---:|---|
| 0 | Success |
| 2 | CLI syntax or configuration error |
| 3 | Missing or unreadable input |
| 4 | Schema or serialized-contract violation |
| 5 | Scientific integrity, leakage, identity, or hash violation |
| 6 | External dependency or subprocess failure |
| 7 | Training/evaluation attempt failed after start |
| 8 | Required E0/E0.5/E1 gate not passed |
| 130 | User interruption; a failed/interrupted record is retained when a run started |

### 6.4 Resume and Publication

Each stage writes to `<final>.partial.<uuid>`, validates and hashes it, publishes
inside one filesystem, then writes `COMPLETED.json`. `--resume` reuses output
only when the completion record's input/config hashes equal the resolved request.
Mismatch exits with code 5. `--force` does not overwrite formal output; it
creates a new run ID or content-addressed derived path.

## 7. Artifact Layout and Serialized Contracts

```text
<artifact-root>/<study-id>/
|-- manifests/source-manifest.tsv
|-- manifests/split-manifest.json
|-- manifests/preprocessing.json
|-- canonical/canonical-full-d.h5
|-- views/<subset-id>/<config>/view.h5
|-- views/<subset-id>/<config>/omnilearned-index/
|-- audits/e0/data-audit.json
|-- audits/e0.5/checkpoint-audit.json
|-- runs/<run-id>/resolved-config.yaml
|-- runs/<run-id>/run-record.json
|-- runs/<run-id>/stdout.log
|-- runs/<run-id>/stderr.log
|-- predictions/<run-id>/prediction.json
|-- predictions/<run-id>/payload.<npz|parquet|h5>
`-- reports/<report-id>/
```

Serialized contracts use JSON Schema Draft 2020-12:

- `schemas/run-record.schema.json` validates one final successful or failed
  training attempt;
- `schemas/split-manifest.schema.json` validates source/split/subset provenance;
  disjointness remains a semantic code check; and
- `schemas/prediction.schema.json` validates prediction metadata and the logical
  row contract for an external NPZ, Parquet, or HDF5 payload.

All defined object boundaries reject unknown properties. Schema version 1.0.0
is exact; readers reject unsupported major versions.

## 8. Metrics and Statistical Algorithms

### 8.1 Per-Run Metrics

ROC AUC uses the average-rank/Mann-Whitney definition with targets `0/1` and
finite signal scores. A single-class test set is an error. Accuracy uses a
threshold selected on validation data only and stored in the run record; 0.5 is
not silently assumed.

Background efficiency at target signal efficiency 0.30 or 0.50 is obtained by
linear interpolation on the full, non-dropped ROC points. The report stores the
interpolated `epsilon_B` and `1/epsilon_B`. If `epsilon_B == 0`, rejection is
JSON `null`, zero observed background count and total background count are
reported, and no infinite value is serialized.

The data-efficiency statistic is:

```text
auc_gap_fraction(config, n) =
    (AUC(config, n) - 0.5) / (AUC(config, n_max) - 0.5)
```

`n_max` is the largest frozen measured scale. The ratio is declared unstable
when the central denominator is at most 0.01 or more than 5% of paired bootstrap
replicates have a denominator at most 0.01. In that case the report omits the
ratio and reports raw paired AUC differences.

### 8.2 Paired Comparisons and Bootstrap

Predictions are joined by exact ordered `jet_id`; duplicate, missing, reordered,
or target-disagreeing identities are errors. Required contrasts are A-B, B-C,
C-D, C-A, and D-A at each approved scale.

The default bootstrap uses 1,000 replicates, a configuration-recorded seed,
NumPy `PCG64`, and stratified resampling with replacement within signal and
background identities. The same sampled indices are applied to both conditions
and every metric in a contrast. The interval is the 2.5th and 97.5th percentile
of finite replicate differences. The number of discarded non-finite replicates
is reported; more than 1% discarded is a failed analysis.

Seed-level reporting shows every run plus mean and sample standard deviation;
it is not combined with event-bootstrap uncertainty into one standard error.
Five-seed expansion is allowed only for preregistered close key comparisons.

## 9. Error Taxonomy

Stable failure-code families are:

| Family | Examples |
|---|---|
| `MANIFEST_*` | invalid bytes/order, duplicate PFN, source hash mismatch |
| `EXTRACT_*` | missing product, daughter resolution, invalid truth traversal |
| `DATA_*` | non-finite value, invalid unit, charged-track threshold, shape failure |
| `SPLIT_*` | PFN/event overlap, insufficient partition, identity mismatch |
| `VIEW_*` | field order, subset, mask, or identity mismatch |
| `CHECKPOINT_*` | missing identity/license, hash mismatch, incompatible tensor |
| `INDEX_*` | external command failure, stale view, count mismatch |
| `RUN_*` | gate blocked, training failure, timeout, interruption |
| `PREDICTION_*` | duplicate/misaligned identity, target mismatch, payload hash |
| `METRIC_*` | single class, non-finite score, invalid bootstrap |
| `CONTRACT_*` | JSON Schema, unsupported version, unknown property |

Messages include the failed contract and artifact/run ID but never credentials.
Formal failures are retained in run records and are excluded from successful
aggregates by status, not by deleting them.

## 10. Test Layers and Acceptance Commands

Planned tests are grouped as follows:

| Layer | Required coverage |
|---|---|
| Unit | PFN hashing, split buckets, PID sign removal, phi wrapping, track missingness, subset nesting, view field order, command allowlist, metric edge cases |
| Contract | Valid/invalid examples for all three schemas, unknown fields, success/failure conditionals, content hashes |
| Fixture integration | Tiny TT/QCD compact ROOT to canonical HDF5, A-D identity equality, index smoke load, failed resume mismatch |
| CMSSW integration | Required products, daughter resolution, truth traversal, D units/PV semantics on hand-inspected events |
| E0.5 smoke | A-D finite forward/backward, layer report, decreasing tiny-run loss |
| Statistical regression | Known AUC/rejection examples, paired bootstrap reproducibility, unstable ratio fallback |
| Documentation | Links, version/term consistency, requirement traceability, schema validity, placeholder scan |

Repository-level verification commands are:

```text
pnpm test
pnpm docs:build
python scripts/validate_software_docs.py
pytest -q
```

Only the first three are required for the documentation-suite release. `pytest`
becomes mandatory as the Python implementation and its tests are introduced.
Passing documentation checks verifies document consistency, not E0-E3 software
or scientific results.
