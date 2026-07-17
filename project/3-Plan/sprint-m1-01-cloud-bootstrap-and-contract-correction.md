# Sprint M1-01 Cloud Bootstrap and Contract Correction

**Milestone:** M1 - Software Foundation and Synthetic Data Pipeline

**Goal:** Correct the OmniLearned A-D view contract and establish the cloud-only Python package, CI, and reproducibility foundation required by every later Sprint.

**Architecture:** This Sprint creates infrastructure and synchronizes contracts only. It preserves the CMSSW/modern-Python process boundary, introduces no scientific dataset, and does not claim that E0 or E0.5 has passed.

**Tech Stack:** Python 3.10/3.12, PEP 621, Hatchling, pytest, Ruff, mypy, GitHub Actions, VitePress, pinned RunPod image definition.

## Workflow Configuration and Evidence Boundary

- `FR_DIR`: `project/1-Requirement`
- `FR_BACKLOG_DIR`: `project/1-Requirement/backlog`
- `FR_DONE_DIR`: `project/1-Requirement/Done`
- `DESIGN_DIR`: `docs/software` (the authoritative design-contract home for this workflow; `project/2-Design` is intentionally not created)
- `SPRINT_DIR`: `project/3-Plan`
- `SPRINT_DONE_DIR`: `project/3-Plan/Done`
- `REVIEW_DIR`: `project/4-Reviews`
- `REVIEW_DONE_DIR`: `project/4-Reviews/Done`
- `WORKFLOW_STATE_PATH`: unset; workflow state is recorded in Sprint and review artifacts.
- `VERIFICATION_COMMANDS`: sourced from the approved development plan and this Sprint's Section 7.

Local commands may be used only as implementation diagnostics. GitHub Actions logs tied to the tested commit SHA are the authoritative verification evidence for this Sprint; RunPod identity checks require retained cloud-generated records. No local result may advance a requirement or experiment status.

## 1. Sprint Goal

Deliver a first authoritative cloud CI run that passes package import, schema/document checks, and minimal test discovery while the software documents consistently specify native integer PID views.

Core objectives:

- Replace the obsolete one-hot PID view contract with the native integer PID/additional-feature mapping in all authoritative documents.
- Bootstrap the `src/particleml` package, thin CLI entry point, dependency locks, and test/lint/type configuration.
- Add GitHub Actions and a versioned RunPod environment definition with auditable environment identity.

## 2. Prerequisites

- [Development plan](./particleml-development-plan.md), Phase 0.
- [FR-DATA-005](../1-Requirement/FR-DATA-005-nested-a-d-views.md), [FR-MODEL-003](../1-Requirement/FR-MODEL-003-configuration-specific-adapters.md), and [FR-REP-002](../1-Requirement/FR-REP-002-machine-readable-validation.md).
- Existing approved SRS, architecture, specification, traceability matrix, and JSON Schemas as source baselines; the architecture, specification, and traceability matrix are scheduled for conformance correction in this Sprint.

Coordination note:

- This Sprint intentionally performs only contract correction for FR-DATA-005/FR-MODEL-003; their functional implementation occurs in M2-01/M4-01.

## 3. Scope

Included:

- Correct architecture, specification, and traceability descriptions of C/D views and OmniLearned flags.
- Create `pyproject.toml`, package/CLI skeleton, lock files, and configuration for pytest, Ruff, and mypy.
- Create cloud CI for Python 3.10/3.12, schemas, documentation, tests, and VitePress.
- Define the pinned RunPod environment and a CI-validated environment-record template.

Not included:

- Dataset conversion, model loading, training, or formal experiment execution.
- CMSSW extraction-host qualification.
- Booting a RunPod pod or claiming a populated GPU environment record; that evidence is retained during M2-02 E0.5 execution.
- Literature-dossier content, generator scripts, and tests.
- Local test results as verification evidence.

## 4. File Structure and Responsibilities

| File / Directory | Operation | Responsibility |
|---|---|---|
| `docs/software/architecture.md` | Modify | Native integer-PID view and model-boundary contract |
| `docs/software/specification.md` | Modify | HDF5 field order, A-D dimensions, and CLI flags |
| `docs/software/traceability-matrix.md` | Modify | Correct planned tests/contracts |
| `pyproject.toml` | Create | PEP 621 package, Hatchling, test/lint/type settings |
| `requirements-ci.lock` | Create | Exact Python CI and development-tool dependency pins |
| `src/particleml/__init__.py` | Create | Minimal importable package |
| `src/particleml/cli.py` | Create | Thin entry-point skeleton |
| `scripts/validate_software_docs.py` | Modify | Reject obsolete one-hot view language and enforce native integer-PID dimensions, order, and flags |
| `.github/workflows/ci.yml` | Create | Authoritative PR/push verification; the existing `docs.yml` remains the deployment-only workflow |
| `containers/runpod/Dockerfile` | Create | Versioned modern Python/GPU image definition |
| `containers/runpod/requirements.lock` | Create | Exact RunPod runtime dependency pins |
| `containers/runpod/environment-record.template.json` | Create | Secret-free required environment identity fields without fabricated runtime values |
| `tests/` | Modify/Create | Import, schema, and document consistency tests |

## 5. Work Scope

### 5.1 Work Package: Correct the A-D Contract

- [ ] Add failing documentation-consistency tests for one-hot PID view language and incorrect C/D dimensions.
- [ ] Replace the materialized-view contract with this exact OmniLearned input mapping:

| Configuration | `F` | Ordered fields | OmniLearned flags |
|---|---:|---|---|
| A | 4 | `delta_eta`, `delta_phi`, `log_pt`, `log_energy` | none |
| B | 5 | A + `charge` | `--use-add --num-add 1` |
| C | 6 | A + `pid_type` at index 4 + `charge` | `--use-pid --pid_idx 4 --use-add --num-add 1` |
| D | 10 | C + `dxy_raw`, `dxy_error_raw`, `dz_raw`, `dz_error_raw` | `--use-pid --pid_idx 4 --use-add --num-add 5` |

- [ ] Document that canonical HDF5 storage remains `kinematics, charge, pid_type, D fields`, while view construction reorders fields to the OmniLearned input order above.
- [ ] Remove the project-owned adapter-boundary one-hot conversion and unknown-PID-bit requirements; any internal PID encoding is owned by the pinned OmniLearned implementation.
- [ ] Remove requirements to materialize one-hot PID columns in OmniLearned HDF5 views.
- [ ] Update the FR-DATA-005 and FR-MODEL-003 planned-test mappings for integer-PID ordering/flags and the obsolete-one-hot regression without advancing implementation status.

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
- [ ] Add the versioned RunPod image definition, runtime lock, and environment-record template.
- [ ] Confirm secrets are provided only by cloud secret stores and are absent from logs/artifacts.

Acceptance:

- [ ] The first GitHub Actions run passes on the tested commit SHA.
- [ ] GitHub Actions validates that the RunPod template covers image digest, lock hash, CUDA, driver, PyTorch, GPU, and VRAM without claiming runtime values.
- [ ] A negative test rejects credential-shaped fields in the environment record, and CI configuration obtains credentials only from cloud secret stores.

## 6. TDD and Test Plan

- [ ] Write contract and import tests before implementation.
- [ ] Cover Python 3.10/3.12, obsolete A-D document contracts, package build/import, CLI help, and secret-free environment-record templates.
- [ ] Do not add the FR-REP-002 Python contract service or its exhaustive serialized-contract fixtures; those remain in M1-02. Existing documentation-validator schema checks remain active.
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
- Risk: CI verification and Pages deployment duplicate or diverge. Control: `ci.yml` owns checks, while `docs.yml` only builds for and deploys GitHub Pages after main-branch changes.
- Recovery: revert this Sprint's isolated infrastructure/configuration changes; no formal artifacts exist yet.

## 9. Deliverables

- [ ] Synchronized software documentation suite.
- [ ] Buildable Python package and CLI skeleton.
- [ ] GitHub Actions workflow and dependency locks.
- [ ] Versioned RunPod environment definition and CI-validated, secret-free record template.
- [ ] Passing cloud CI evidence linked to a commit SHA.

## 10. Completion Criteria

- [ ] All work-package acceptance items pass in GitHub Actions.
- [ ] No local output is cited as verification.
- [ ] Later scientific stages remain `specified`, not `verified`.

## 11. Delivery Conclusion

Implementation, document review confirmation, code review confirmation, local diagnostics, and the Sprint commit are complete. Local results remain diagnostic-only. The user prohibited GitHub pushes on 2026-07-17, so authoritative GitHub Actions verification remains explicitly deferred and no requirement or experiment status advances to `verified`.

## 12. Workflow State

- Current phase: local workflow complete; cloud verification explicitly deferred by the user's no-push instruction.
- Target FR documents: `FR-DATA-005`, `FR-MODEL-003`, and `FR-REP-002`.
- Target Sprint document: `project/3-Plan/sprint-m1-01-cloud-bootstrap-and-contract-correction.md`.
- Document review reports: `project/4-Reviews/sprint-m1-01-cloud-bootstrap-and-contract-correction-review-by-opencode-go-kimi-k2.7-code.md` and `project/4-Reviews/sprint-m1-01-cloud-bootstrap-and-contract-correction-review-by-ark-code-latest.md`.
- Document confirmation: `project/4-Reviews/sprint-m1-01-cloud-bootstrap-and-contract-correction-review-confirm.md`.
- Code review reports: `project/4-Reviews/sprint-m1-01-cloud-bootstrap-and-contract-correction-code-review-by-opencode-go-kimi-k2.7-code.md` and `project/4-Reviews/sprint-m1-01-cloud-bootstrap-and-contract-correction-code-review-by-ark-code-latest.md`.
- Code review confirmation: `project/4-Reviews/sprint-m1-01-cloud-bootstrap-and-contract-correction-code-review-confirm.md`.
- Implementation target: the M1-01 documentation-contract, package/CLI, CI, dependency-lock, RunPod-definition, and test files listed in Section 4.
- Local diagnostic results on 2026-07-17: `ruff check`, `mypy src/particleml`, `pytest`, package build, `python scripts/validate_software_docs.py`, `pnpm test`, `pnpm docs:build`, and `git diff --check` passed. These results do not advance acceptance status.
- Open blocker: GitHub Actions requires a pushed commit/ref. No remote branch or commit has been created because external push authorization has not been granted.
- Commit status: created locally as `df2b60e` with message `feat: complete sprint-m1-01-cloud-bootstrap-and-contract-correction code and change base on reviews`; not pushed.
- Multi-Sprint state: M1-01 is complete under the explicit no-push/cloud-deferral override. M1-02 is active; M1-03, M2-01, M2-02, M3-01, M3-02, and M4-01 remain unstarted.
