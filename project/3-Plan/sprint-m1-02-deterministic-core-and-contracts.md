# Sprint M1-02 Deterministic Core and Contracts

**Milestone:** M1 - Software Foundation and Synthetic Data Pipeline

**Goal:** Implement the deterministic identities, serialized contracts, artifact lifecycle, and CLI commands that every data/model/run artifact depends on.

**Architecture:** Changes are limited to manifest, contract, artifact-publication, and thin CLI boundaries. No CMS decoding, HDF5 conversion, or model behavior is introduced.

**Tech Stack:** Python, pathlib, dataclasses/enums, hashlib, JSON Schema Draft 2020-12, pytest, Ruff, mypy, GitHub Actions.

## 1. Sprint Goal

Complete the deterministic Phase 1 exit criterion for FR-DATA-001, FR-DATA-006, FR-REP-001, and FR-REP-002.

Core objectives:

- Validate and hash exact source-manifest bytes and assign exact-PFN splits.
- Validate all three JSON Schemas plus cross-artifact semantics.
- Publish immutable artifacts with hashes, completion records, and safe resume behavior.

## 2. Prerequisites

- [Sprint M1-01](./sprint-m1-01-cloud-bootstrap-and-contract-correction.md) completed in cloud CI.
- [FR-DATA-001](../1-Requirement/FR-DATA-001-frozen-source-manifest.md), [FR-DATA-006](../1-Requirement/FR-DATA-006-deterministic-split.md), [FR-REP-001](../1-Requirement/FR-REP-001-content-addressed-provenance.md), [FR-REP-002](../1-Requirement/FR-REP-002-machine-readable-validation.md).
- Existing schema files remain version 1.0.0 unless an approved migration is added.

## 3. Scope

Included:

- Public enums/dataclasses, typed exceptions, CLI exit-code mapping.
- Source-manifest validation/hashing, PFN split assignment, and stable jet identity helpers.
- JSON Schema and semantic validators.
- Temporary-write, validate, hash, publish, completion-marker, and resume primitives.
- `manifest validate`, `contracts validate`, and `split build` commands.

Not included:

- Reading ROOT/HDF5 datasets or building training subsets.
- Executing CMSSW or OmniLearned.
- Formal E0 data production.

## 4. File Structure and Responsibilities

| File / Directory | Operation | Responsibility |
|---|---|---|
| `src/particleml/manifest.py` | Create | Exact-byte manifest, split, and identity logic |
| `src/particleml/contracts.py` | Create | Schemas, semantic checks, artifact lifecycle |
| `src/particleml/cli.py` | Modify | Thin command wiring and exit codes |
| `schemas/*.schema.json` | Modify if required | Version 1.0.0 serialized contracts |
| `tests/test_manifest.py` | Create | Manifest/split/identity tests |
| `tests/test_contracts.py` | Create | Schema and semantic validation tests |
| `tests/test_artifacts.py` | Create | Publication/resume integrity tests |

## 5. Work Scope

### 5.1 Work Package: Public Types and Stable Errors

- [ ] Write failing enum/dataclass/exception/exit-code tests.
- [ ] Implement `Split`, `FeatureConfig`, `Stage`, `ModelCondition`, `Artifact`, `ViewSpec`, and `RunSpec` contracts.
- [ ] Keep modules from calling `sys.exit`; map only at CLI boundary.

### 5.2 Work Package: Manifest, Split, and Identity

- [ ] Write golden and negative exact-byte manifest tests.
- [ ] Implement canonical ordering and SHA-256 over file bytes.
- [ ] Implement exact UTF-8 PFN modulo-10 assignment and stable jet ID format.
- [ ] Reject PFN/event overlap and report partition counts.

### 5.3 Work Package: Schemas and Artifact Lifecycle

- [ ] Add valid/invalid fixtures for run, split, and prediction schemas.
- [ ] Implement unknown-property and major-version rejection plus semantic hash/identity checks.
- [ ] Implement partial output, validation, hash, publication, and `COMPLETED.json`.
- [ ] Test resume match, stale mismatch, partial output, and no overwrite.

## 6. TDD and Test Plan

- [ ] Each behavior starts with a failing unit or contract test.
- [ ] Cover BOM/CRLF/order/duplicates, PFN golden buckets, overlap, schema branches, unknown fields, hash mutation, interruption, and Windows sentinel semantics.
- [ ] Run targeted tests before the full cloud CI suite.

## 7. Verification Commands

```text
pytest -q tests/test_manifest.py tests/test_contracts.py tests/test_artifacts.py
ruff check
mypy src/particleml
pytest
python scripts/validate_software_docs.py
pnpm test
pnpm docs:build
```

All formal results come from GitHub Actions.

## 8. Risks and Recovery

- Risk: manifest normalization changes the scientific split. Control: byte-level golden vectors and no-normalization tests.
- Risk: schema-valid documents violate cross-artifact semantics. Control: separate semantic validators.
- Risk: partial output is reused. Control: completion marker plus input/config hash comparison.
- Recovery: derived test artifacts are disposable; revert code/config without touching persistent cloud artifacts.

## 9. Deliverables

- [ ] Typed public core contracts and stable error mapping.
- [ ] Manifest/split/identity services and CLI commands.
- [ ] Three schema validators and semantic checks.
- [ ] Reusable artifact lifecycle with integrity tests.

## 10. Completion Criteria

- [ ] All mapped FR acceptance criteria pass in cloud CI.
- [ ] CI evidence identifies the tested commit SHA.
- [ ] No E0/E0.5 scientific gate is marked passed.

## 11. Delivery Conclusion

Pending implementation, review confirmation, and cloud verification.
