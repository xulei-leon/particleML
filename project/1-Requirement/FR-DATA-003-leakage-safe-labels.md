# FR-DATA-003 Leakage-Safe Labels

- `FR-ID`: `FR-DATA-003`
- `Title`: Leakage-safe labels
- `Phase`: Phase 3 - CMSSW Extractor and E0
- `Development Order`: 11
- `Priority`: P0
- `Prerequisites`: `FR-DATA-001`
- `Affected Packages`: `cmssw/ParticleMLExtractor/`, extraction fixtures, `tests/test_audit.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-DATA-003

## Goal

Ensure the binary target encodes only the preregistered hadronic-top and declared-QCD definitions and cannot leak rejected TT jets into background.

## Requirement Description

Signal jets shall have one unambiguous last-copy, fully hadronic top match with the top and every `bqq'` daughter inside the approved radius. Background jets shall originate only from declared QCD records.

## High-Level Requirements

- Implement truth traversal and containment exactly from Research Plan v0.4.
- Preserve truth details only for audit and cutflow.
- Reject ambiguous, incomplete, non-hadronic, or out-of-radius TT matches from the binary dataset.
- Never relabel a rejected TT jet as QCD.
- Report label cutflow by record, source file, and rejection reason.

## Inputs

- Selected reconstructed AK8 jets and generator truth from TT simulation.
- Declared active QCD record IDs.
- Frozen matching radius and truth-selection policy.

## Outputs

- Binary label for accepted signal or QCD jets.
- Structured cutflow and truth-audit fields excluded from model arrays.

## Implementation Constraints

- Label ambiguity is a scientific-integrity failure, not a recoverable warning.
- Record identity, generator bin, and truth variables must not appear in model views.

## Failure and Degradation

- Fail the affected event/file for invalid truth traversal or an ambiguous accepted match.
- Exclude non-signal TT jets; do not degrade them into a background class.

## Acceptance Criteria

- Hand-inspected truth fixtures reproduce the expected accepted and rejected cases.
- The background sample contains only approved QCD record IDs.
- A model-input audit finds no truth, record, or generator-bin fields.
- E0 retains label/cutflow counts sufficient to reproduce all exclusions.

## Minimum Verification

- Qualified-host `test_truth_matching` fixtures covering last-copy, decay mode, daughter containment, ambiguity, and QCD provenance.
- Shuffled-label and model-input leakage probes in the E0 data audit.

## Out of Scope

- Weak supervision, multi-class labels, or alternative truth definitions.
- Treating TT rejection categories as background.

## Notes

- A label-policy change requires a Research Plan v0.4.x amendment.
