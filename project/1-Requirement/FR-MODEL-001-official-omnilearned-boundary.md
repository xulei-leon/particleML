# FR-MODEL-001 Official OmniLearned Boundary

- `FR-ID`: `FR-MODEL-001`
- `Title`: Official OmniLearned boundary
- `Phase`: Phase 4 - OmniLearned E0.5
- `Development Order`: 13
- `Priority`: P0
- `Prerequisites`: `FR-DATA-005`, `FR-REP-001`
- `Affected Packages`: `src/particleml/model_integration.py`, `configs/`, `tests/test_model_integration.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-MODEL-001

## Goal

Reuse the audited official OmniLearned implementation while keeping external model internals outside particleML's ownership boundary.

## Requirement Description

The primary model path shall invoke OmniLearned revision `5091595d226b6021e967ab2ecfff832f40c026f6` through a subprocess boundary. particleML owns validation, command construction, adapters, records, and evidence, but not PET, its optimizer, checkpoint format, or training loop.

## High-Level Requirements

- Pin the dependency revision and lock the isolated PyTorch environment.
- Invoke argument arrays with `shell=False`, controlled working directory, captured output, and explicit timeout.
- Record executable path, resolved package version, dependency revision, argv, and environment identity.
- Reject undocumented flags and conditional/global inputs.
- Keep provider credentials and signed URLs out of logs and artifacts.

## Inputs

- Validated view/index artifacts, pinned executable, versioned configuration, and checkpoint policy.

## Outputs

- Auditable external commands and collected official outputs.
- Structured subprocess failures and dependency provenance.

## Implementation Constraints

- Do not fork or reimplement PET for the baseline.
- Build the RunPod environment from a pinned image and dependency lock; record image digest, CUDA, driver, PyTorch, GPU, and VRAM.

## Failure and Degradation

- Missing revision, executable mismatch, unsupported flags, timeout, or non-zero process exit fails with `CHECKPOINT_*`, `INDEX_*`, or `RUN_*`.
- No shell-string fallback is permitted.

## Acceptance Criteria

- Tests prove subprocess invocation uses an argument array and the pinned revision.
- The allowlist rejects conditional/global and undocumented options.
- Run records capture dependency and environment identity without secrets.
- No copied PET or optimizer implementation is introduced into the repository.

## Minimum Verification

- `pytest -q tests/test_model_integration.py::test_subprocess_boundary`
- Command injection, timeout, captured-output, revision mismatch, and secret-redaction tests in cloud CI.

## Out of Scope

- Foundation-model pretraining or PET architecture changes.
- Online model serving.

## Notes

- Direct filesystem and HTTP/HTTPS access are allowed; no intermediate web service is introduced.
