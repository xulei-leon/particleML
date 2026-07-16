# FR-DATA-009 QCD Mixture and Confound Controls

- `FR-ID`: `FR-DATA-009`
- `Title`: QCD mixture and confound controls
- `Phase`: Phase 2 - Synthetic Cloud Data Pipeline
- `Development Order`: 8
- `Priority`: P0
- `Prerequisites`: `FR-DATA-006`, `FR-DATA-007`
- `Affected Packages`: `src/particleml/dataset.py`, `src/particleml/manifest.py`, `tests/test_dataset.py`, `tests/test_audit.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-DATA-009

## Goal

Prevent source-record composition, kinematics, pileup, truth, or generator metadata from becoming unintended shortcuts in the classifier.

## Requirement Description

E0 shall freeze the active QCD-record mixture and deterministic round-robin policy, fit pT/eta control on training data, audit pileup, and exclude all audit-only confounds from model tensors.

## High-Level Requirements

- Record the selected QCD records and mixture policy as versioned configuration.
- Use deterministic per-record queues and round-robin subset selection.
- Fit pT/eta matching or reweighting using training data only.
- Audit pileup diagnostics and record any approved policy.
- Exclude record ID, generator bin, truth, pileup variables, and audit weights from primary inputs.

## Inputs

- Frozen signal/QCD records, training split, audit variables, and versioned control policy.

## Outputs

- Frozen QCD mixture configuration, control-state hash, and confound audit.
- Model views containing only approved A-D particle features.

## Implementation Constraints

- Record identity may drive deterministic sampling but must not become a model feature.
- Any pileup reweighting must be explicitly approved and training-fitted.

## Failure and Degradation

- Block E1 for leaked audit variables, unfrozen mixture, or unresolved pT/eta/pileup policy.
- Do not hide poor record balance by changing the test set.

## Acceptance Criteria

- Model tensor schemas contain no forbidden audit/global inputs.
- QCD contribution counts match the frozen round-robin policy.
- pT/eta control fit identities are training-only.
- E0 confound and shuffled-label probes are retained with pass/fail status.

## Minimum Verification

- `pytest -q tests/test_dataset.py::test_qcd_round_robin_and_no_audit_inputs`
- Schema, tensor-field, training-only fit, mixture-count, and shuffled-label checks.

## Out of Scope

- Adding record or generator-bin labels as conditional inputs.
- Post-hoc mixture changes after formal experiments begin.

## Notes

- A mixture or primary-control change after E0 requires the applicable change-control review.
