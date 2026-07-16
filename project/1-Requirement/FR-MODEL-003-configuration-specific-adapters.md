# FR-MODEL-003 Configuration-Specific Adapters

- `FR-ID`: `FR-MODEL-003`
- `Title`: Configuration-specific adapters
- `Phase`: Phase 4 - OmniLearned E0.5
- `Development Order`: 15
- `Priority`: P0
- `Prerequisites`: `FR-MODEL-001`, `FR-MODEL-002`, `FR-DATA-005`
- `Affected Packages`: `src/particleml/model_integration.py`, `configs/`, `tests/test_model_integration.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline with Phase 0 contract correction
- `Original SRS Section`: Software Requirements Specification §4, FR-MODEL-003

## Goal

Compare A-D through one audited pretrained backbone while expressing each configuration through OmniLearned's supported native PID/additional-feature interface.

## Requirement Description

Each A-D condition shall initialize its input-facing parameters and binary head from the same model seed, load every shape-compatible non-input backbone tensor from one checkpoint, and fine-tune end to end. Loaded, skipped, and mismatched tensors shall be recorded.

## High-Level Requirements

- A uses four kinematic fields and no PID/additional feature flags.
- B uses charge with `--use-add --num-add 1`.
- C uses integer PID at index 4 plus charge with `--use-pid --pid_idx 4 --use-add --num-add 1`.
- D uses integer PID plus charge and four D fields with `--use-pid --pid_idx 4 --use-add --num-add 5`.
- Reinitialize the binary output head and audit backbone loading tensor by tensor.
- Reject conditional/global inputs and distinguish `model_size` from `train_size_per_class`.

## Inputs

- Validated A-D view/index, common checkpoint, model seed, allowlisted training configuration, and E0.5 policy.

## Outputs

- Configuration-specific load report, exact training argv, initialized adapter/head state, and fine-tuned checkpoint.

## Implementation Constraints

- Do not materialize one-hot PID columns in OmniLearned HDF5 views.
- The same checkpoint and eligible non-input weights must be used across A-D.
- Fixed neutralization is available only through an explicit E0.5 decision.

## Failure and Degradation

- Unexpected tensor omissions, incompatible required tensors, illegal flags, non-finite passes, or input-schema mismatch blocks the condition.
- Do not silently switch architectures or pretrained assets between A-D.

## Acceptance Criteria

- A-D commands contain the exact approved field/flag mapping.
- Load reports provide sorted loaded, skipped, and mismatched tensors with shapes.
- All shape-compatible non-input tensors have the same checkpoint provenance.
- Conditional/global inputs are rejected before process execution.

## Minimum Verification

- Adapter shape/load tests for A-D and command snapshot tests.
- PID-index, additional-field count, tensor-audit, seed, and rejected-flag tests.
- RunPod finite forward/backward smoke for A-D.

## Out of Scope

- Different pretrained backbones per configuration.
- Conditional classifier inputs or undocumented OmniLearned flags.

## Notes

- Phase 0 must update architecture/specification tables that still describe one-hot PID views.
