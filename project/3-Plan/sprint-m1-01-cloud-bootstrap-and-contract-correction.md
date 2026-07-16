# Sprint M1-01 Cloud Bootstrap and Contract Correction

**Milestone:** M1 - Software Foundation and Synthetic Data Pipeline

**Goal:** Correct the OmniLearned A-D view contract and establish the cloud-only Python package, CI, and reproducibility foundation required by every later Sprint.

**Architecture:** This Sprint creates infrastructure and synchronizes contracts only. It preserves the CMSSW/modern-Python process boundary, introduces no scientific dataset, and does not claim that E0 or E0.5 has passed.

**Tech Stack:** Python 3.10/3.12, PEP 621, Hatchling, pytest, Ruff, mypy, GitHub Actions, VitePress, pinned RunPod image definition.

## 1. Sprint Goal

Deliver a first authoritative cloud CI run that passes package import, schema/document checks, and minimal test discovery while the software documents consistently specify native integer PID views.

Core objectives:

- Replace the obsolete one-hot PID view contract with the native integer PID/additional-feature mapping in all authoritative documents.
- Bootstrap the `src/particleml` package, thin CLI entry point, dependency locks, and test/lint/type configuration.
- Add GitHub Actions and a versioned RunPod environment definition with auditable environment identity.

## 2. Prerequisites

- [Development plan](./particleml-development-plan.md), Phase 0.
- [FR-DATA-005](../1-Requirement/FR-DATA-005-nested-a-d-views.md), [FR-MODEL-003](../1-Requirement/FR-MODEL-003-configuration-specific-adapters.md), and [FR-REP-002](../1-Requirement/FR-REP-002-machine-readable-validation.md).
- Approved SRS, architecture, specification, traceability matrix, and existing JSON Schemas.

Coordination note:

- This Sprint intentionally performs only contract correction for FR-DATA-005/FR-MODEL-003; their functional implementation occurs in M2-01/M4-01.

## 3. Scope

Included:

- Correct architecture, specification, and traceability descriptions of C/D views and OmniLearned flags.
- Create `pyproject.toml`, package/CLI skeleton, lock files, and configuration for pytest, Ruff, and mypy.
- Create cloud CI for Python 3.10/3.12, schemas, documentation, tests, and VitePress.
- Define the pinned RunPod environment and environment-record fields.

Not included:

- Dataset conversion, model loading, training, or formal experiment execution.
- CMSSW extraction-host qualification.
- Local test results as verification evidence.

## 4. File Structure and Responsibilities

| File / Directory | Operation | Responsibility |
|---|---|---|
| `docs/software/architecture.md` | Modify | Native integer-PID view and model-boundary contract |
| `docs/software/specification.md` | Modify | HDF5 field order, A-D dimensions, and CLI flags |
| `docs/software/traceability-matrix.md` | Modify | Correct planned tests/contracts |
| `pyproject.toml` | Create | PEP 621 package, Hatchling, test/lint/type settings |
| `src/particleml/__init__.py` | Create | Minimal importable package |
| `src/particleml/cli.py` | Create | Thin entry-point skeleton |
| `.github/workflows/ci.yml` | Create | Authoritative CPU CI |
| `containers/runpod/` | Create | Versioned modern Python/GPU environment definition |
| `tests/` | Modify/Create | Import, schema, and document consistency tests |

## 5. Work Scope

### 5.1 Work Package: Correct the A-D Contract

- [ ] Add failing documentation-consistency tests for one-hot PID view language and incorrect C/D dimensions.
- [ ] Specify A=4 kinematics, B=A+charge, C=A+integer PID+charge, and D=C+four D fields.
- [ ] Specify `--use-pid --pid_idx 4` for C/D and `--use-add --num-add 1/5` for B/C/D.
- [ ] Remove requirements to materialize one-hot PID columns in OmniLearned HDF5 views.
- [ ] Update traceability without advancing implementation status.

Acceptance:

- [ ] No authoritative document contradicts the Phase 0 native PID contract.
- [ ] The consistency validator fails if the obsolete one-hot view contract returns.

### 5.2 Work Package: Package and CLI Bootstrap

- [ ] Add failing package-import and CLI-help tests.
- [ ] Create typed package metadata, Hatchling build configuration, and `particleml` entry point.
- [ ] Add stable exception/exit-code placeholders only where required by the minimal CLI.
- [ ] Keep all scientific logic out of the bootstrap CLI.

Acceptance:

- [ ] Python 3.10 and 3.12 CI can build and import the package.
- [ ] Minimal test discovery succeeds with no empty future modules.

### 5.3 Work Package: Cloud CI and RunPod Reproducibility

- [ ] Add CI jobs for Ruff, mypy, pytest, schemas/docs, frontend docs tests, and VitePress build.
- [ ] Pin Python/dependency locks and cache only reproducible dependency artifacts.
- [ ] Add the versioned RunPod image definition and environment record template.
- [ ] Confirm secrets are provided only by cloud secret stores and are absent from logs/artifacts.

Acceptance:

- [ ] The first GitHub Actions run passes on the tested commit SHA.
- [ ] RunPod identity fields cover image digest, lock hash, CUDA, driver, PyTorch, GPU, and VRAM.

## 6. TDD and Test Plan

- [ ] Write contract and import tests before implementation.
- [ ] Cover Python 3.10/3.12, invalid document contracts, package build/import, CLI help, and secret-free environment records.
- [ ] Keep local runs diagnostic-only; record only cloud CI results as acceptance evidence.

## 7. Verification Commands

Run in GitHub Actions:

```text
ruff check
mypy src/particleml
pytest
python scripts/validate_software_docs.py
pnpm test
pnpm docs:build
```

## 8. Risks and Recovery

- Risk: the current architecture/specification still encode one-hot PID and could drive incompatible implementation. Control: land the corrected consistency test first.
- Risk: dependency pins diverge between CI and RunPod. Control: record and compare lock SHA-256 and image digest.
- Recovery: revert this Sprint's isolated infrastructure/configuration changes; no formal artifacts exist yet.

## 9. Deliverables

- [ ] Synchronized software documentation suite.
- [ ] Buildable Python package and CLI skeleton.
- [ ] GitHub Actions workflow and dependency locks.
- [ ] Versioned RunPod environment definition.
- [ ] Passing cloud CI evidence linked to a commit SHA.

## 10. Completion Criteria

- [ ] All work-package acceptance items pass in GitHub Actions.
- [ ] No local output is cited as verification.
- [ ] Later scientific stages remain `specified`, not `verified`.

## 11. Delivery Conclusion

Pending implementation, review confirmation, and cloud verification.
