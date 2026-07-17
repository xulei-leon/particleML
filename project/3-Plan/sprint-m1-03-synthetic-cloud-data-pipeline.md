# Sprint M1-03 Synthetic Cloud Data Pipeline

**Milestone:** M1 - Software Foundation and Synthetic Data Pipeline

**Goal:** Implement canonical conversion, training-only preprocessing, deterministic subsets, native-PID A-D views, and data-audit primitives against compact synthetic cloud fixtures.

**Architecture:** Scientific transformation logic lives in `src/particleml`; notebooks remain consumers. The Sprint consumes compact ROOT contracts but does not require real CMS extraction or model training.

**Tech Stack:** Python, uproot/ROOT reader boundary, h5py, NumPy, JSON, pytest, GitHub Actions.

## Workflow Configuration and Evidence Boundary

- `FR_DIR`: `project/1-Requirement`
- `FR_BACKLOG_DIR`: `project/1-Requirement/backlog`
- `FR_DONE_DIR`: `project/1-Requirement/Done`
- `DESIGN_DIR`: `project/2-Design`
- `SPRINT_DIR`: `project/3-Plan`
- `SPRINT_DONE_DIR`: `project/3-Plan/Done`
- `REVIEW_DIR`: `project/4-Reviews`
- `REVIEW_DONE_DIR`: `project/4-Reviews/Done`
- `WORKFLOW_STATE_PATH`: this Sprint document; no separate state file was requested.
- `VERIFICATION_COMMANDS`: Section 7, sourced from the approved development plan and mapped FR minimum checks.

Local execution is diagnostic-only. The user prohibited GitHub pushes on 2026-07-17, so cloud CI and tested-commit-SHA verification remain explicitly deferred. No local fixture or result may advance E0 or a requirement to `verified`.

## 1. Sprint Goal

Demonstrate diagnostically, without claiming formal evidence, that one canonical full-D dataset produces identity-equivalent A-D views and reusable training-only state from deterministic generated fixtures.

Core objectives:

- Convert compact ROOT to canonical HDF5 with masks, stable identities, PID/track-state rules, sorting, and truncation.
- Build nested class-balanced subsets and freeze QCD/control preprocessing.
- Materialize native integer-PID A-D views with identical membership/order.

## 2. Prerequisites

- [Sprint M1-02](./sprint-m1-02-deterministic-core-and-contracts.md), completed through review, local diagnostics, and local commit `87a7c1a`; cloud CI remains deferred under the no-push instruction.
- Reuse the M1-02 public boundaries: `manifest.py` for split assignment, source manifests, and stable jet IDs; `contracts.py` for typed errors/value/schema contracts; `artifacts.py` for temporary publication and `COMPLETED.json`; and `cli.py` for thin command wiring.
- [FR-DATA-004](../1-Requirement/FR-DATA-004-canonical-full-d-dataset.md), [FR-DATA-005](../1-Requirement/FR-DATA-005-nested-a-d-views.md), [FR-DATA-007](../1-Requirement/FR-DATA-007-training-only-fitted-state.md), [FR-DATA-008](../1-Requirement/FR-DATA-008-fixed-training-subsets.md), [FR-DATA-009](../1-Requirement/FR-DATA-009-qcd-mixture-and-confound-controls.md).
- Corrected Phase 0 integer-PID contract.

## 3. Scope

Included:

- Deterministic compact ROOT fixture generation in the test suite. Local runs are diagnostic; the same fixtures are intended for cloud CI when pushes are separately authorized.
- Conversion, canonical layout, preprocessing state, subset selection, QCD round-robin, A-D views, and audit primitives.
- `convert`, `audit data`, and `view build` commands.
- Migration of reusable notebook logic into tested package modules.

Not included:

- Real CMS product decoding or qualified-host extraction.
- OmniLearned index/model execution.
- JetClass as a production corpus.

## 4. File Structure and Responsibilities

| File / Directory | Operation | Responsibility |
|---|---|---|
| `src/particleml/dataset.py` | Create | ROOT conversion, canonical transforms, fitted preprocessing state, semantic HDF5 validation |
| `src/particleml/views.py` | Create | Subsets and A-D materialization |
| `src/particleml/metrics.py` | Create minimal | Deterministic AUC and shuffled-label numerical probes only |
| `src/particleml/audit.py` | Create | Versioned audit policy, forbidden-field/confound/missingness checks, and retained structured pass/fail report |
| `src/particleml/cli.py` | Modify | `convert`, `audit data`, `view build` wiring |
| `tests/fixtures/generate_compact_root.py` | Create | On-demand uproot fixture factory and expected records; no binary ROOT files are committed |
| `tests/test_dataset.py` | Create | Canonical and preprocessing contracts |
| `tests/test_views.py` | Create | Subsets and A-D equality |
| `tests/test_audit.py` | Create | Audit thresholds and leakage probes |

## 5. Work Scope

### 5.1 Work Package: Canonical Conversion

The fixture factory writes one `jets` tree with jet-level branches `record_id`, `canonical_pfn`, `run`, `lumi`, `event`, `jet_index`, `split`, `target`, `jet_pt`, `jet_eta`, `jet_phi`, `pv_z`, and `n_vertices`; jagged constituent branches are `particle_pt`, `particle_eta`, `particle_phi`, `particle_energy`, `particle_charge`, `particle_pdg_id`, `particle_dxy`, `particle_dxy_error`, `particle_dz`, `particle_dz_error`, and `particle_has_track_details`. Tests create fixtures in temporary directories from committed Python records.

The binding canonical layout is specification §3.3:

| Path | Shape / dtype | Contract |
|---|---|---|
| `/particles/continuous` | `[N,150,9]`, `float32` | `delta_eta`, `delta_phi`, `log_pt`, `log_energy`, `charge`, `dxy_raw`, `dxy_error_raw`, `dz_raw`, `dz_error_raw` |
| `/particles/pid_type` | `[N,150]`, `uint8` | Frozen absolute-PDG-ID category |
| `/particles/mask` | `[N,150]`, `bool` | Sole validity indicator; padding is zero/false |
| `/particles/track_state` | `[N,150]`, `uint8` | Padding `0`, usable `1`, neutral `2`, charged-missing `3` |
| `/labels/pid` | `[N]`, `int8` | QCD `0`, top `1` |
| `/identity/*`, `/split/name`, `/audit/*` | `[N]` | Specification §3.3 identity, split, and audit datasets; never primary inputs |

All datasets use gzip level 4 and jet-major chunks. The ordered semantic HDF5 hash algorithm covers sorted dataset paths, dtype/shape metadata, C-order dataset bytes, and allowlisted root attributes; it excludes non-semantic HDF5 file metadata and is stored as a versioned root attribute.

- [x] Write failing layout, transform, PID sign, track-state, mask, sorting, truncation, and provenance tests.
- [x] Generate compact fixtures deterministically without relying on local source data; retain the GitHub Actions path for future cloud verification.
- [x] Require explicit positive `min_particle_pt_gev` and `min_particle_energy_gev`; missing or non-positive values block conversion with `DATA_*`.
- [x] Implement canonical HDF5 writer and semantic validation.
- [x] Publish only after validation/hash/completion.

### 5.2 Work Package: Fitted State and Fixed Subsets

- [x] Write failing training-only and canonical-JSON hash tests.
- [x] Ingest strict versioned JSON policy fields for feature/schema version, canonical hash, training fit identities, continuous location/scale, positive particle cuts, PID vocabulary, pT/eta control, pileup policy, track policy, D-field units/transform, and content hash; reject missing, unknown, or unresolved values and use no scientific defaults.
- [x] Fit continuous state and pT/eta controls exactly once from the complete training partition; validation/test identities cannot influence state.
- [x] Rank each signal and each active-record QCD queue by the unsigned big-endian integer value of `SHA256(str(subset_seed) + "\0" + jet_id)`, then `jet_id`; select QCD round-robin across ascending record IDs.
- [x] Support the formal `10^3`, `10^4`, and provisional `10^5` jets-per-class grid (or an E0-amended grid), with the subset seed distinct from model-seed semantics. Synthetic tests use smaller proportional grids to prove the same prefix behavior.
- [x] Store ordered identity lists and hashes; fail with stable code `SPLIT_INSUFFICIENT_CLASS_YIELD` (the project error-taxonomy form of the FR's `INSUFFICIENT_CLASS_YIELD`) instead of shrinking or sampling with replacement.

### 5.3 Work Package: Native-PID A-D Views and Audit

- [x] Write failing A-D equality and exact field-order tests.
- [x] Materialize A/B/C/D without one-hot PID columns.
- [x] Store and snapshot exact argv fragments: A none; B `--use-add --num-add 1`; C `--use-pid --pid_idx 4 --use-add --num-add 1`; D `--use-pid --pid_idx 4 --use-add --num-add 5`. External execution remains deferred.
- [x] Reject model tensors containing identity/audit/truth fields, including `record_id`, `canonical_pfn`/PFN hash, `run`, `lumi`, `event`, `jet_index`, `jet_pt`, `jet_eta`, `pv_z`, `n_vertices`, generator-bin/process/truth fields, or audit weights.
- [x] Implement training-only pT/eta control, pileup diagnostics, track missingness, QCD mixture counts, and deterministic class-balanced shuffled-label probes. A strict versioned audit policy supplies the permutation seed and `shuffled_label_auc_max`; code has no default threshold.
- [x] Retain a structured audit report with observed values, configured thresholds, fit identities, and pass/fail decisions.
- [x] Reject canonical, split-manifest, subset, or preprocessing dependency hash mismatches with `VIEW_STALE_HASH`, after validating dependency completion markers through `artifacts.py`.

## 6. TDD and Test Plan

- [x] Cover valid and invalid ROOT fixtures, empty jets, exactly padded and over-150 truncated jets, non-finite values, duplicate identities, unknown PID species, neutral charge, charged missing-track state, missing policies, unit/mask errors, PID sign, padding, pT-tie original-index ordering, and truncation.
- [x] Cover training-only fit/control identities, subset nesting, QCD record balance, insufficient yield, A-D identity/field/argv equality, forbidden-input enumeration, versioned audit thresholds, missingness, mixture counts, and shuffled-label reproducibility/pass-fail.
- [x] Test commands through package APIs and thin CLI integration.

## 7. Verification Commands

```text
pytest -q tests/test_dataset.py tests/test_views.py tests/test_audit.py
ruff check
mypy src/particleml
pytest
python scripts/validate_software_docs.py
pnpm test
pnpm docs:build
```

Run locally as diagnostics in this no-push workflow. Formal evidence still requires GitHub Actions after separate push authorization.

The pytest commands provide M1-03 functional coverage. Ruff and mypy are static checks. The software-document, pnpm, and VitePress commands are repository-wide consistency checks and are not substitutes for data-pipeline tests.

### Local Diagnostic Results (2026-07-17)

- Targeted M1-03 suite: `24 passed`.
- Full Python suite: `101 passed`.
- Ruff and strict mypy: passed.
- Software documentation validator: passed for 4 documents, 3 schemas, 39 traced requirements, and 8 link-bearing files.
- Python sdist and wheel builds: passed.
- Node tests: `3 passed`.
- VitePress documentation build: passed.
- `git diff --check`: passed.
- GitHub Actions / qualified-host evidence: deferred because the user prohibited pushing; no requirement or experiment stage is advanced to `verified` by these local diagnostics.

## 8. Risks and Recovery

- Risk: HDF5 byte hashes vary due to library metadata. Control: use the versioned semantic dataset/attribute hash defined in WP 5.1 and pin h5py.
- Risk: native PID field order drifts from OmniLearned flags. Control: M1-03 field-index and argv snapshots are validated before view publication.
- Risk: synthetic fixtures conceal real CMSSW edge cases. Control: exercise the minimum valid/fail-closed matrix in §6 and defer E0 status until M3 qualified-host artifacts pass.
- Recovery: canonical fixtures and views are content-addressed derived artifacts and can be rebuilt.

## 9. Deliverables

- [x] Canonical conversion and HDF5 contract.
- [x] Immutable preprocessing state and subset manifests.
- [x] A-D views with byte-identical identity/order contracts.
- [x] Data-audit primitives and local generated-fixture diagnostics; cloud evidence remains deferred.

## 10. Completion Criteria

- [x] All A-D identities, labels, masks, split hashes, and subset hashes match in the listed local diagnostics; cloud CI evidence is explicitly deferred.
- [x] No one-hot PID columns exist in OmniLearned view fixtures.
- [x] Real-data E0 remains pending M3-01.

## 11. Delivery Conclusion

Document review confirmation, implementation, code review confirmation, and all listed local diagnostics are complete, so this Sprint is eligible for its local workflow commit. Cloud verification is explicitly deferred under the user's no-push instruction, and real-data E0 remains pending M3-01.
