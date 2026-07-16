# Sprint M1-03 Synthetic Cloud Data Pipeline

**Milestone:** M1 - Software Foundation and Synthetic Data Pipeline

**Goal:** Implement canonical conversion, training-only preprocessing, deterministic subsets, native-PID A-D views, and data-audit primitives against compact synthetic cloud fixtures.

**Architecture:** Scientific transformation logic lives in `src/particleml`; notebooks remain consumers. The Sprint consumes compact ROOT contracts but does not require real CMS extraction or model training.

**Tech Stack:** Python, uproot/ROOT reader boundary, h5py, NumPy, JSON, pytest, GitHub Actions.

## 1. Sprint Goal

Prove on deterministic cloud-generated fixtures that one canonical full-D dataset produces identity-equivalent A-D views and reusable training-only state.

Core objectives:

- Convert compact ROOT to canonical HDF5 with masks, stable identities, PID/track-state rules, sorting, and truncation.
- Build nested class-balanced subsets and freeze QCD/control preprocessing.
- Materialize native integer-PID A-D views with identical membership/order.

## 2. Prerequisites

- [Sprint M1-02](./sprint-m1-02-deterministic-core-and-contracts.md).
- [FR-DATA-004](../1-Requirement/FR-DATA-004-canonical-full-d-dataset.md), [FR-DATA-005](../1-Requirement/FR-DATA-005-nested-a-d-views.md), [FR-DATA-007](../1-Requirement/FR-DATA-007-training-only-fitted-state.md), [FR-DATA-008](../1-Requirement/FR-DATA-008-fixed-training-subsets.md), [FR-DATA-009](../1-Requirement/FR-DATA-009-qcd-mixture-and-confound-controls.md).
- Corrected Phase 0 integer-PID contract.

## 3. Scope

Included:

- Deterministic compact ROOT fixture generation in cloud CI.
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
| `src/particleml/dataset.py` | Create | ROOT conversion, transforms, fitted state, data audit |
| `src/particleml/views.py` | Create | Subsets and A-D materialization |
| `src/particleml/metrics.py` | Create minimal | Leakage/shuffled-label audit support only |
| `src/particleml/cli.py` | Modify | `convert`, `audit data`, `view build` wiring |
| `tests/fixtures/` | Create | Deterministic compact ROOT policies/expected records |
| `tests/test_dataset.py` | Create | Canonical and preprocessing contracts |
| `tests/test_views.py` | Create | Subsets and A-D equality |
| `tests/test_audit.py` | Create | Audit thresholds and leakage probes |

## 5. Work Scope

### 5.1 Work Package: Canonical Conversion

- [ ] Write failing layout, transform, PID sign, track-state, mask, sorting, truncation, and provenance tests.
- [ ] Generate compact fixtures deterministically in GitHub Actions.
- [ ] Implement canonical HDF5 writer and semantic validation.
- [ ] Publish only after validation/hash/completion.

### 5.2 Work Package: Fitted State and Fixed Subsets

- [ ] Write failing training-only and canonical-JSON hash tests.
- [ ] Implement required preprocessing policy with no scientific defaults.
- [ ] Implement nested signal ranking and QCD record round-robin.
- [ ] Store identity lists and hashes; fail on insufficient class yield.

### 5.3 Work Package: Native-PID A-D Views and Audit

- [ ] Write failing A-D equality and exact field-order tests.
- [ ] Materialize A/B/C/D without one-hot PID columns.
- [ ] Implement forbidden-input, pT/eta control, pileup diagnostic, missingness, and shuffled-label audit primitives.
- [ ] Add stale-state/view hash invalidation tests.

## 6. TDD and Test Plan

- [ ] Cover valid and invalid ROOT fixtures, non-finite values, missing policies, unit/mask errors, PID sign, padding, tie ordering, truncation, training leakage, subset nesting, QCD balance, A-D identity, and forbidden fields.
- [ ] Test commands through package APIs and thin CLI integration.

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

Run only in GitHub Actions for formal evidence.

## 8. Risks and Recovery

- Risk: HDF5 byte hashes vary due to library metadata. Control: define semantic/content hashing rules and pin h5py.
- Risk: native PID field order drifts from OmniLearned flags. Control: snapshot view metadata and expected M4 command inputs.
- Risk: synthetic fixtures conceal real CMSSW edge cases. Control: defer E0 status until M3 qualified-host artifacts pass.
- Recovery: canonical fixtures and views are content-addressed derived artifacts and can be rebuilt.

## 9. Deliverables

- [ ] Canonical conversion and HDF5 contract.
- [ ] Immutable preprocessing state and subset manifests.
- [ ] A-D views with byte-identical identity/order contracts.
- [ ] Data-audit primitives and cloud fixture evidence.

## 10. Completion Criteria

- [ ] All A-D identities, labels, masks, split hashes, and subset hashes match in CI.
- [ ] No one-hot PID columns exist in OmniLearned view fixtures.
- [ ] Real-data E0 remains pending M3-01.

## 11. Delivery Conclusion

Pending implementation, review confirmation, and cloud verification.
