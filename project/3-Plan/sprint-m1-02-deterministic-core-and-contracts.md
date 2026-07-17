# Sprint M1-02 Deterministic Core and Contracts

**Milestone:** M1 - Software Foundation and Synthetic Data Pipeline

**Goal:** Implement the deterministic identities, serialized contracts, artifact lifecycle, and CLI commands that every data/model/run artifact depends on.

**Architecture:** Changes are limited to manifest, contract, artifact-publication, and thin CLI boundaries. No CMS decoding, HDF5 conversion, physics-feature tensor reading, or model behavior is introduced. `split build` may consume a minimal JSON identity inventory so deterministic event/subset semantics can be tested before the M1-03 HDF5 adapter exists.

**Tech Stack:** Python, pathlib, dataclasses/enums, hashlib, JSON Schema Draft 2020-12, pytest, Ruff, mypy, GitHub Actions.

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

Local command results are diagnostic-only. Under the user's 2026-07-17 no-push instruction, GitHub Actions and tested-commit-SHA verification remain explicitly deferred and no requirement or experiment status may advance to `verified`.

## 1. Sprint Goal

Complete the deterministic Phase 1 exit criterion for FR-DATA-001, FR-DATA-006, FR-REP-001, and FR-REP-002.

Core objectives:

- Validate and hash exact source-manifest bytes and assign exact-PFN splits.
- Validate all three JSON Schemas plus cross-artifact semantics.
- Publish immutable artifacts with hashes, completion records, and safe resume behavior.

## 2. Prerequisites

- [Sprint M1-01](./sprint-m1-01-cloud-bootstrap-and-contract-correction.md) completed through local review, diagnostics, and commit. Cloud CI verification is deferred because the user explicitly prohibited GitHub pushes on 2026-07-17.
- M1-01 prerequisite evidence: native integer-PID contracts are present in `docs/software/specification.md` §4.3 and `docs/software/architecture.md` §5.2; local commit `df2b60e` contains the correction and bootstrap implementation.
- [FR-DATA-001](../1-Requirement/FR-DATA-001-frozen-source-manifest.md), [FR-DATA-006](../1-Requirement/FR-DATA-006-deterministic-split.md), [FR-REP-001](../1-Requirement/FR-REP-001-content-addressed-provenance.md), [FR-REP-002](../1-Requirement/FR-REP-002-machine-readable-validation.md).
- Existing schema files remain version 1.0.0 unless an approved migration is added.

## 3. Scope

Included:

- Public enums/dataclasses, typed exceptions, CLI exit-code mapping.
- Source-manifest validation/hashing, PFN split assignment, and stable jet identity helpers.
- JSON Schema validators and pure semantic validators over caller-supplied identity/count metadata.
- Temporary-write, validate, hash, publish, completion-marker, and resume primitives.
- `manifest validate`, `contracts validate`, and `split build --canonical PATH --config PATH --output PATH` commands. For M1-02, `--canonical` is a minimal JSON identity inventory; M1-03 adds the canonical-HDF5 adapter without changing the command surface.

Not included:

- Reading ROOT/HDF5 physics-feature datasets or producing formal training subsets from scientific data. Synthetic identity lists may exercise the frozen subset-selection algorithm.
- Executing CMSSW or OmniLearned.
- Formal E0 data production.

## 4. File Structure and Responsibilities

| File / Directory | Operation | Responsibility |
|---|---|---|
| `src/particleml/manifest.py` | Create | Exact-byte manifest, split, and identity logic |
| `src/particleml/contracts.py` | Create | Public value types, JSON Schemas, and semantic checks |
| `src/particleml/artifacts.py` | Create | Temporary write, validation, hashing, immutable publication, completion, and resume |
| `src/particleml/cli.py` | Modify | Thin command wiring and exit codes |
| `schemas/*.schema.json` | Modify if required | Version 1.0.0 serialized contracts |
| `tests/test_manifest.py` | Create | Manifest/split/identity tests |
| `tests/test_contracts.py` | Create | Schema and semantic validation tests |
| `tests/test_artifacts.py` | Create | Publication/resume integrity tests |
| `tests/test_cli.py` | Create | CLI command wiring, diagnostics, and stable exit-code tests |

## 5. Work Scope

### 5.1 Work Package: Public Types and Stable Errors

- [x] Write failing enum/dataclass/exception/exit-code tests.
- [x] Implement the public value types below and `SplitConfig` without adding behavior owned by later stages.
- [x] Extend the existing `main() -> int` / `entrypoint() -> NoReturn` pattern; modules raise typed project exceptions and only the CLI maps them to exit codes.

| Type | Binding source | M1-02 responsibility |
|---|---|---|
| `Split` | Specification §1 and §2.2 | Exact partition vocabulary and PFN assignment |
| `FeatureConfig`, `Stage`, `ModelCondition` | Specification §1 | Stable value-only vocabulary for downstream contracts |
| `Artifact` | Specification §1 and architecture §6.4 | Validated path/hash/schema identity |
| `ViewSpec`, `RunSpec` | Specification §1 | Validated immutable value types; execution remains deferred |
| `SplitConfig` | Specification §§2.2, 4.2, and 6.2 | Dataset identity, source-manifest hash, source roles, subset sizes/seeds, and preprocessing references for `split build` |

### 5.2 Work Package: Manifest, Split, and Identity

Binding implementation references are `docs/software/specification.md` §§2.1, 2.2, 2.3, 6.2, 6.3, and 9 plus `docs/software/architecture.md` §§6.2, 6.3, 6.4, and 8. The FRs define scope and acceptance; these sections define the exact byte, identity, command, lifecycle, and error contracts.

- [x] Write golden and negative exact-byte manifest tests.
- [x] Implement canonical ordering and SHA-256 over file bytes.
- [x] Implement exact UTF-8 PFN modulo-10 assignment, exact-PFN digest helpers, and the full stable jet ID from validated caller-supplied `(record_id, PFN, run, lumi, event, jet_index)` values.
- [x] Reject duplicate or cross-partition PFNs during split assignment.
- [x] Implement event-disjointness as a pure semantic validator over caller-supplied `(record_id, run, lumi, event, split)` records. M2-01 wires extracted event data into this validator.
- [x] Define and validate the M1-02 JSON identity inventory used by `split build`; report file, event, jet, class, and record counts without reading physics-feature arrays.

Golden PFN vectors are fixed independently of implementation serialization:

| Exact UTF-8 PFN | SHA-256 | Bucket | Split |
|---|---|---:|---|
| `root://example.invalid//store/test/file-7.root` | `86a2d2ef501197c748e1c536b523b3b0e491d74dd9e24bddf79577888bbd529a` | 0 | `test` |
| `root://example.invalid//store/test/file-0.root` | `037bba1c0c146b75f5dea5c3abf38bb287aa9b8ea0d9c96b9885b88adcdbc3b3` | 1 | `validation` |
| `root://例子.invalid//cms/μ-jet.root` | `71ac8c0965d5841033850debf7bc8bd8c06b825bdfe4928f74d4c12379ff7d61` | 7 | `train` |

### 5.3 Work Package: Schemas and Artifact Lifecycle

- [x] Add valid/invalid fixtures for run, split, and prediction schemas.
- [x] Implement unknown-property and major-version rejection plus semantic hash/identity checks.
- [x] Implement partial-directory output, validation, hash, same-filesystem publication, and authoritative `COMPLETED.json` in `artifacts.py`.
- [x] Test resume match, stale mismatch, interruption, partial output, and no overwrite on Windows and POSIX semantics; a rename alone never substitutes for the completion marker.

## 6. TDD and Test Plan

- [x] Each behavior starts with a failing unit or contract test.
- [x] Cover BOM/CRLF/order/duplicates, the fixed PFN golden vectors, PFN/event overlap, schema branches, unknown fields, unsupported major versions, hash mutation, interruption, completion-marker authority, partial directories, and no-overwrite behavior.
- [x] Run targeted tests before the full local diagnostic suite.

## 7. Verification Commands

```text
pytest -q tests/test_manifest.py tests/test_contracts.py tests/test_artifacts.py
pytest -q tests/test_manifest.py::test_canonical_manifest_bytes_and_hash
pytest -q tests/test_manifest.py::test_exact_pfn_split_golden_vectors
pytest -q tests/test_manifest.py::test_event_overlap_is_rejected
pytest -q tests/test_contracts.py::test_unknown_property_and_major_version_are_rejected
pytest -q tests/test_artifacts.py::test_completed_marker_controls_resume
pytest -q tests/test_cli.py
ruff check
mypy src/particleml
pytest
python scripts/validate_software_docs.py
pnpm test
pnpm docs:build
```

These commands are local diagnostics for this no-push workflow. They do not count as formal verification evidence. GitHub Actions execution and commit-SHA evidence remain deferred until the user separately authorizes a push.

## 8. Risks and Recovery

- Risk: PFN trimming, lowercasing, URL decoding, protocol normalization, BOM stripping, or CRLF-to-LF conversion changes corpus/split identity. Control: byte-level golden vectors and negative no-normalization tests bound to specification §2.1.
- Risk: schema-valid documents violate cross-artifact semantics. Control: separate semantic validators.
- Risk: partial output is reused. Control: completion marker plus input/config hash comparison.
- Risk: pnpm blocks unapproved dependency build scripts. Control: `pnpm-workspace.yaml` explicitly allows only the VitePress-required `esbuild` installation script.
- Deferred risk: concurrent cross-process `split build` publishers are not coordinated beyond same-filesystem temporary files and no-overwrite checks; formal concurrent writers are not part of M1-02.
- Recovery: derived test artifacts are disposable; revert code/config without touching persistent cloud artifacts.

## 9. Deliverables

- [x] Typed public core contracts and stable error mapping.
- [x] Manifest/split/identity services and CLI commands.
- [x] Three schema validators and semantic checks.
- [x] Reusable artifact lifecycle with integrity tests.

## 10. Completion Criteria

- [x] All mapped FR behaviors pass the listed local diagnostic commands.
- [x] The implementation and diagnostic evidence are recorded in this Sprint document and committed locally.
- [x] Cloud CI and tested-commit-SHA evidence are explicitly recorded as deferred under the user's no-push instruction.
- [x] No E0/E0.5 scientific gate is marked passed.

## 11. Delivery Conclusion

Document review confirmation, implementation, code review confirmation, accepted review fixes, and local diagnostics are complete. The Git commit containing this document is the M1-02 completion commit. Cloud verification remains explicitly deferred under the user's no-push instruction, and no E0/E0.5 or requirement status is advanced to `verified`.

## 12. Delivery Evidence

- Local commit: the Git commit containing this document, with required message `feat: complete sprint-m1-02-deterministic-core-and-contracts code and change base on reviews`; resolve its SHA from `git log -1` after the atomic commit gate.
- Document review: `project/4-Reviews/sprint-m1-02-deterministic-core-and-contracts-review-by-opencode-go-kimi-k2.7-code.md` and `project/4-Reviews/sprint-m1-02-deterministic-core-and-contracts-review-confirm.md`.
- Code review: `project/4-Reviews/sprint-m1-02-deterministic-core-and-contracts-code-review-by-opencode-go-kimi-k2.7-code.md` and `project/4-Reviews/sprint-m1-02-deterministic-core-and-contracts-code-review-confirm.md`.
- Review availability: DeepSeek fallback produced the single document and code reports; Kimi/GLM timed out and Ark returned HTTP 400. The user explicitly allowed the single-report gate.
- 2026-07-17 targeted diagnostics: 50 tests passed across manifest, contracts, artifacts, and CLI.
- 2026-07-17 full diagnostics: 76 tests passed; Ruff passed; strict mypy passed; software-document validation passed for 4 documents, 3 schemas, 39 traced requirements, and 8 link-bearing files.
- Packaging and documentation diagnostics: Python sdist/wheel built successfully; 3 Node tests passed; VitePress 1.6.4 built successfully; `git diff --check` passed.
- Cloud verification and tested-commit-SHA evidence are deferred by the user's no-push instruction. Cross-process split publication coordination is deferred. E0/E0.5 statuses remain unchanged.

## 13. Workflow State

- Current phase: all local gates passed; completion commit is the final action.
- Target FR documents: `FR-DATA-001`, `FR-DATA-006`, `FR-REP-001`, and `FR-REP-002`.
- Target Sprint document: `project/3-Plan/sprint-m1-02-deterministic-core-and-contracts.md`.
- Document review report: `project/4-Reviews/sprint-m1-02-deterministic-core-and-contracts-review-by-opencode-go-kimi-k2.7-code.md` (DeepSeek fallback). Kimi and GLM timed out; Ark returned HTTP 400. The user explicitly allowed the single-report gate.
- Document confirmation: `project/4-Reviews/sprint-m1-02-deterministic-core-and-contracts-review-confirm.md`.
- Code review report: `project/4-Reviews/sprint-m1-02-deterministic-core-and-contracts-code-review-by-opencode-go-kimi-k2.7-code.md` (DeepSeek fallback under the primary path).
- Code review confirmation: `project/4-Reviews/sprint-m1-02-deterministic-core-and-contracts-code-review-confirm.md`.
- Implementation targets: `src/particleml/manifest.py`, `src/particleml/contracts.py`, `src/particleml/artifacts.py`, `src/particleml/cli.py`, `schemas/split-manifest.schema.json`, `pnpm-workspace.yaml`, and mapped tests.
- Verification source: Section 7 local diagnostics; GitHub Actions is deferred by user instruction.
- Commit status: completed by the Git commit containing this document; not pushed.
- Later Sprints remain unstarted and must stay sequential; M1-03 is next.
