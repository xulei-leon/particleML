# FR-TRAIN-004 Complete Failure Accounting

- `FR-ID`: `FR-TRAIN-004`
- `Title`: Complete failure accounting
- `Phase`: Phase 5 - E1 Pilot
- `Development Order`: 21
- `Priority`: P0
- `Prerequisites`: `FR-TRAIN-003`, `FR-REP-003`
- `Affected Packages`: `src/particleml/experiment.py`, `src/particleml/reporting.py`, `tests/test_experiment.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-TRAIN-004

## Goal

Prevent survivorship bias by preserving every formal failure and making incomplete conditions visible in analysis and reporting.

## Requirement Description

Failed or interrupted attempts shall retain stable failure information and logs, remain in the experiment ledger, and be excluded from successful aggregates by explicit status rather than deletion.

## High-Level Requirements

- Use stable error families and distinguish pre-start gate blocks from started run failures.
- Retain stdout/stderr, timing, partial artifact references, and environment data when available.
- Never auto-retry a formal run.
- Require a new run ID for an explicitly approved rerun.
- Show failed, missing, completed, and optional conditions in matrices and reports.

## Inputs

- Execution lifecycle events, process result, interruption/timeout signals, logs, and partial artifacts.

## Outputs

- Schema-valid failed/interrupted run record and updated condition ledger.

## Implementation Constraints

- Aggregation selects successful status explicitly; it never infers success from artifact presence.
- Near-null results cannot trigger seed removal or hidden reruns.

## Failure and Degradation

- If structured failure metadata is incomplete, mark the condition invalid/incomplete rather than successful.
- More work may be blocked, but the original evidence remains immutable.

## Acceptance Criteria

- Timeout, subprocess failure, user interruption, and invalid-output fixtures remain visible.
- No failed condition contributes to successful metrics.
- Reruns have distinct identities and preserve predecessor records.
- E2 reports every planned condition even when some fail.

## Minimum Verification

- Failure/interruption retention, no-auto-retry, rerun-ID, aggregation-filter, and matrix-visibility tests.
- Cloud CI evidence plus manual-dispatch RunPod interruption smoke before formal E1.

## Out of Scope

- Automatic retry policies.
- Deleting or rewriting failed attempts to make a matrix appear complete.

## Notes

- Supports AC-E2-001's explicit accounting requirement.
