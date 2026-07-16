# particleML Cloud-Only Development and Experiment Plan

## Material Passport

| Field | Value |
|---|---|
| Status | ANALYZED |
| Document version | 1.1.0 |
| Date | 2026-07-17 |
| Research baseline | Research Plan v0.4.0 |
| Execution model | Local editing; cloud-only debugging, testing, extraction, and training |
| Language | English |

## 1. Summary

- The local computer is a source-editing environment only. It may be used for
  editing, reviewing, Git operations, and reading cloud-generated reports.
- No Python, Node.js, Docker, CMSSW, ROOT, OmniLearned, fixture, unit-test,
  integration-test, or training result produced locally is accepted as
  verification evidence.
- GitHub Actions is the default CPU CI environment. RunPod with persistent
  storage is the default interactive Python and GPU environment.
- Real CMS extraction runs on a separately qualified POSIX host with measured
  EOS/XRootD performance.
- Development follows this order: cloud foundation, deterministic core,
  synthetic cloud fixtures, CMSSW E0, OmniLearned E0.5, and E1-E3.

## 2. Cloud Execution Topology

### 2.1 Local Workstation

Allowed activities:

- Edit English source code, configuration, documentation, and tests.
- Inspect Git diffs and commit or push changes.
- Review CI logs and cloud artifacts.
- Connect to cloud environments using SSH or a remote editor.

Prohibited as verification evidence:

- Local test results, notebook execution, dataset inspection, model loading,
  training, profiling, or container checks.
- Local environment versions or hardware properties in formal run records.

### 2.2 GitHub Actions

Use Ubuntu runners as the authoritative environment for:

- Python 3.10 and 3.12 unit tests.
- JSON Schema and contract tests.
- Synthetic compact ROOT/HDF5 fixture tests.
- Static typing and linting.
- Documentation consistency checks.
- VitePress builds.

Required checks are:

```text
ruff check
mypy src/particleml
pytest
python scripts/validate_software_docs.py
pnpm test
pnpm docs:build
```

A pull request cannot merge unless all applicable checks pass. CI logs and the
tested commit SHA form the implementation-verification evidence.

### 2.3 RunPod Development Environment

Default setup:

- Secure RunPod pod with a persistent volume.
- Ubuntu 22.04 and Python 3.10.
- RTX 4090 for interactive debugging and E0.5/E1 smoke work.
- A40, RTX A6000, or L40S 48 GB only after E1 measures memory and runtime need.
- A100 80 GB as a short-lived rescue option, not the default.
- Repository mounted under `/workspace/particleML`.
- `PARTICLEML_ARTIFACT_ROOT=/workspace/artifacts`.
- Long tasks run under `tmux`; GPU state is captured with `nvidia-smi`.

The RunPod environment is built from a versioned image definition and fully
pinned dependency lock. Image digest, dependency-lock SHA-256, CUDA, driver,
PyTorch, GPU model, and VRAM enter run records.

### 2.4 CMS Extraction Environment

- Use a POSIX host capable of running the pinned CMSSW 7.6.7 container.
- Qualify candidate CERN-adjacent, institutional, or European cloud hosts with
  direct EOS/XRootD access.
- First process one TT and one QCD file and measure product availability,
  throughput, CPU/event, wall time, failure rate, and compact-output size.
- Promote a host only when the projected E0 pilot and storage cost fit the
  active budget with a 25% reserve.
- Do not download or scan the multi-terabyte corpus from the local workstation.
- Use RunPod for extraction only if its measured XRootD route passes the same
  qualification.

## 3. Implementation Phases

### Phase 0 - Contract Correction and Cloud Bootstrap

- Correct the OmniLearned view contract to use its native integer PID interface:
  - A: four kinematic fields.
  - B: kinematics plus charge with `--use-add --num-add 1`.
  - C: kinematics plus integer PID plus charge with
    `--use-pid --pid_idx 4 --use-add --num-add 1`.
  - D: kinematics plus integer PID plus charge plus four D fields with
    `--use-pid --pid_idx 4 --use-add --num-add 5`.
- Do not materialize one-hot PID columns in OmniLearned HDF5 views.
- Update architecture, specification, and traceability documents before
  implementing views.
- Create the PEP 621/Hatchling Python package, CLI entry point, dependency
  locks, lint/type/test configuration, and GitHub Actions workflow.
- Separate current documentation changes from unrelated literature-dossier
  changes before starting the implementation branch.

Exit criterion: the first cloud CI run passes for package import, schemas,
documentation, and minimal test discovery.

### Phase 1 - Deterministic Core and Contracts

- Implement the public enums, dataclasses, artifact records, stable exceptions,
  and CLI exit-code mapping.
- Implement source-manifest validation, exact-byte hashing, exact-PFN split
  assignment, and stable jet identities.
- Implement the three JSON Schema validators and representative success/failure
  fixtures.
- Implement temporary output, validation, hashing, publication,
  `COMPLETED.json`, and resume/hash-mismatch behavior.
- Provide `manifest validate`, `contracts validate`, and `split build` commands.

Exit criterion: FR-DATA-001, FR-DATA-006, FR-REP-001/002 and their mapped CI
tests pass.

### Phase 2 - Synthetic Cloud Data Pipeline

- Generate small deterministic compact ROOT fixtures in CI; do not depend on
  local files.
- Implement ROOT-to-canonical-HDF5 conversion, masks, sorting, truncation, PID
  sign removal, track-state codes, missingness, and full-D layout.
- Implement training-only fitted state, nested class-balanced subsets, QCD
  record round-robin, and A-D views.
- Implement `convert`, `audit data`, and `view build`.
- Move reusable notebook logic into package modules; notebooks become API
  consumers only.
- Retain JetClass notebooks and configuration as legacy learning material.

Exit criterion: A-D ordered jet IDs, labels, masks, split hashes, and subset
hashes are identical in cloud fixture tests.

### Phase 3 - CMSSW Extractor and E0

- Implement the CMSSW analyzer, build file, extraction configuration, product
  checks, truth traversal, cutflow, and raw constituent output.
- Run CMSSW integration tests only on the qualified extraction host.
- Process at least 5-10 TT files and multiple files from every candidate QCD
  record.
- Produce source/split manifests, compact ROOT, canonical HDF5, A-D views, and
  E0 audit artifacts.
- Freeze QCD mixture, particle cuts, pT/eta control, pileup policy,
  track-missingness policy, yield projection, cost projection, and `n_max`.
- If `10^5` jets per class is infeasible, publish Research Plan v0.4.x before
  E0.5.

Exit criterion: every AC-E0-001 gate passes with retained cloud artifacts and
hashes.

### Phase 4 - OmniLearned E0.5

- Build an isolated PyTorch environment from OmniLearned commit
  `5091595d226b6021e967ab2ecfff832f40c026f6`.
- Record the checkpoint asset, immutable revision, filename, license, SHA-256,
  pretraining corpus, and normalization convention.
- Run the official `omnilearned dataloader` for every A-D view and hash each
  validated index.
- Enforce the command allowlist and reject conditional/global inputs and
  undocumented flags.
- Run finite A-D forward/backward checks and tiny fine-tunes showing loss
  reduction.
- If native adapter compatibility fails, use only the recorded neutralization
  policy or supervised fallback; update claim eligibility accordingly.

Exit criterion: AC-E05-001 passes on RunPod with retained layer-loading and
smoke-run evidence.

### Phase 5 - E1 Pilot

- Execute A and D at `10^3` and `10^4` jets per class with one seed.
- Save schema-valid run records, ordered predictions, metrics, logs, timing,
  GPU memory, checkpoint size, and storage size.
- Use E1 measurements to select the GPU class and approve or reject the E2
  budget.

Exit criterion: AC-E1-001 passes and the projected E2 cost fits the budget with
a 25% reserve.

### Phase 6 - E2 Core Matrix

- Execute A-D across the three frozen training scales and three first-pass
  seeds.
- Preserve failed runs rather than silently retrying or deleting them.
- Verify exact test identity alignment before paired statistics.
- Compute AUC, background rejection, accuracy, paired deltas, seed variation,
  and at least 1,000 paired bootstrap replicates.

Exit criterion: AC-E2-001 passes with every planned condition accounted for.

### Phase 7 - E3 and Reporting

- Implement the masked Deep Sets/PFN baseline.
- Run A versus D at frozen `n_max` with three seeds.
- Keep random-initialized OmniLearned optional and broader model benchmarking
  deferred.
- Generate figures, tables, matrix status, and claim-eligibility ledger
  exclusively from validated artifacts.

Exit criterion: AC-E3-001 passes or is formally deferred with the manuscript
claim boundary narrowed.

## 4. Public Interfaces

- Preserve the specification's manifest, split, conversion, view, index,
  checkpoint, experiment, metric, and reporting APIs.
- Final CLI groups are `manifest`, `split`, `convert`, `audit`, `view`,
  `checkpoint`, `index`, `run`, `evaluate`, `report`, and `contracts`.
- JSON Schema major version remains 1.0.0 until a deliberately incompatible
  artifact migration is approved.
- Scientific settings come only from versioned configuration or explicit CLI
  arguments.
- Provider credentials are stored in cloud secret stores and never enter
  manifests, logs, artifacts, or Git.

## 5. Cloud Artifact and Synchronization Policy

- Git contains code, tests, schemas, configurations, compact synthetic fixtures,
  and documentation only.
- Raw CMS files, canonical datasets, views, indices, checkpoints, predictions,
  and reports live on persistent cloud storage.
- Every formal artifact receives SHA-256 metadata and a completion record.
- Temporary GPU disks are not authoritative storage.
- Cloud-to-cloud transfers use direct filesystem, Git, or HTTP/HTTPS mechanisms;
  no intermediate application web service is introduced.
- The local workstation may download small reports for reading but is not an
  artifact source of truth.

## 6. Test and Acceptance Policy

- Local execution never changes a requirement status.
- `implemented` requires code plus passing GitHub Actions evidence.
- `verified` requires the mapped cloud test or experiment gate and retained
  artifact identity.
- CMSSW and GPU tests are manual-dispatch cloud workflows because ordinary CI
  lacks the required data, legacy container, and accelerator.
- No formal run is automatically retried.
- Near-null results do not trigger post-hoc feature additions or seed removal.
- Documentation and traceability are updated in the same pull request as any
  interface, schema, dataset, endpoint, or claim-boundary change.

## 7. Budget Defaults

- Maximum working budget: USD 500 unless superseded by an approved research-plan
  amendment.
- Debugging and CI-related cloud work: USD 50-100.
- Main GPU runs: USD 300-375.
- Failure, rerun, storage, and price-variation reserve: USD 50-100.
- Prefer RTX 4090 for debugging, 48 GB GPUs for measured main-training need,
  and A100 80 GB only for short rescue runs.
- E2 cannot begin until E0 and E1 replace projected cost fields with measured
  values.

## 8. Assumptions

- GitHub Actions and RunPod are the default cloud execution environments unless
  an institutional platform is later declared.
- The CMS extraction host is selected by measured qualification, not provider
  reputation.
- The local computer remains editing-only for the entire project.
- Formal data remains CMS 2015; JetClass is not promoted back into the
  production pipeline.
- Multi-agent development remains disabled unless separately approved by the
  user.
