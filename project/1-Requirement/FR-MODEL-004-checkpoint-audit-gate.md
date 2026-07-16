# FR-MODEL-004 Checkpoint Audit Gate

- `FR-ID`: `FR-MODEL-004`
- `Title`: Checkpoint audit gate
- `Phase`: Phase 4 - OmniLearned E0.5
- `Development Order`: 16
- `Priority`: P0
- `Prerequisites`: `FR-MODEL-001`, `FR-MODEL-002`, `FR-MODEL-003`, `FR-REP-001`
- `Affected Packages`: `src/particleml/model_integration.py`, `src/particleml/cli.py`, `tests/test_checkpoint.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-MODEL-004

## Goal

Establish that the claimed pretrained asset and A-D integration are identifiable, licensed, numerically valid, and minimally trainable before E1.

## Requirement Description

E0.5 shall retain checkpoint source, immutable revision/tag, filename, license, SHA-256, pretraining corpus statement, input schema, normalization convention, layer-load reports, finite A-D forward/backward results, and tiny fine-tunes with decreasing loss.

## High-Level Requirements

- Reject a mutable nickname such as `pretrain_s` as sufficient provenance.
- Verify checkpoint bytes before loading and bind the hash to every dependent run.
- Audit all A-D views and native PID/additional-feature commands.
- Record initial/final tiny-run loss without treating it as scientific performance.
- Emit one structured E0.5 gate result with artifact links and hashes.

## Inputs

- Candidate checkpoint asset and metadata, validated A-D views/indices, adapter policy, and pinned environment.

## Outputs

- `audits/e0.5/checkpoint-audit.json`, layer reports, smoke logs, and pass/fail decision.

## Implementation Constraints

- Execute in cloud on RunPod; local model loading is not verification evidence.
- Preserve dependency lock, image digest, CUDA/driver/PyTorch, GPU model, and VRAM.

## Failure and Degradation

- Missing identity/license/corpus/normalization, hash mismatch, incompatible tensors, non-finite gradients, or non-decreasing tiny loss fails AC-E05-001.
- Only FR-MODEL-005 may authorize a claim-narrowing fallback.

## Acceptance Criteria

- Checkpoint metadata is immutable and complete.
- All A-D index, load, forward/backward, and tiny-loss checks are retained and pass.
- Audit artifacts are content-addressed and marked complete.
- E1 remains blocked until AC-E05-001 passes or an approved fallback is recorded.

## Minimum Verification

- `pytest -q tests/test_checkpoint.py` plus adapter/load and gate-aggregation tests.
- RunPod A-D smoke execution retaining logs, environment record, checkpoint hash, layer reports, and loss traces.

## Out of Scope

- Selecting a checkpoint by downstream test performance.
- Claiming useful transfer from smoke loss alone.

## Notes

- Evidence target and exit gate: AC-E05-001.
