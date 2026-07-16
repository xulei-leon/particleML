# FR-TRAIN-002 Deterministic Clean Commands

- `FR-ID`: `FR-TRAIN-002`
- `Title`: Deterministic clean commands
- `Phase`: Phase 5 - E1 Pilot
- `Development Order`: 19
- `Priority`: P0
- `Prerequisites`: `FR-TRAIN-001`, `FR-REP-001`, `FR-REP-002`
- `Affected Packages`: `src/particleml/cli.py`, `src/particleml/experiment.py`, `configs/`, `tests/test_experiment.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-TRAIN-002

## Goal

Make every formal operation reproducible from a non-interactive, validated command with immutable output semantics.

## Requirement Description

All public operations shall be available through the specified `particleml` CLI groups. Configuration precedence, unknown-key rejection, dry-run, resume, hashing, and publication behavior shall be uniform across stages.

## High-Level Requirements

- Implement the final groups: `manifest`, `split`, `convert`, `audit`, `view`, `checkpoint`, `index`, `run`, `evaluate`, `report`, and `contracts`.
- Resolve scientific settings only from explicit CLI values or versioned YAML; only artifact root may come from environment.
- Serialize and hash every resolved formal configuration.
- Resume only when completion, input, and configuration hashes match.
- Never overwrite a formal artifact; changed requests receive a new run/content identity.

## Inputs

- Explicit CLI arguments, one versioned experiment YAML, and optional `PARTICLEML_ARTIFACT_ROOT`.

## Outputs

- Resolved configuration, deterministic argv, concise diagnostics, and immutable artifacts or dry-run plans.

## Implementation Constraints

- CLI modules remain thin and map typed exceptions to stable exit codes.
- Local commands may edit/inspect only; formal verification and execution evidence come from cloud environments.

## Failure and Degradation

- Unknown keys, missing inputs, stale resume hashes, gate failures, or subprocess failures return the documented stable code.
- `--force` cannot overwrite formal output.

## Acceptance Criteria

- Every formal operation runs non-interactively from a clean environment.
- Equivalent configuration resolves to identical hashes and argv.
- Stale or partial output is never reused.
- Dry-run performs no training/extraction and publishes no artifacts.

## Minimum Verification

- Clean CLI, configuration precedence, unknown-key, dry-run, resume match/mismatch, exit-code, and no-overwrite tests.
- `pytest -q tests/test_experiment.py` plus applicable command tests in GitHub Actions.

## Out of Scope

- Interactive notebook-only production paths.
- A web UI, model-serving API, or database-backed scheduler.

## Notes

- Commands use direct filesystem or HTTP/HTTPS mechanisms and no intermediate web service.
