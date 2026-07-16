# FR-DATA-006 Deterministic Split

- `FR-ID`: `FR-DATA-006`
- `Title`: Deterministic split
- `Phase`: Phase 1 - Deterministic Core and Contracts
- `Development Order`: 2
- `Priority`: P0
- `Prerequisites`: `FR-DATA-001`, `FR-REP-002`
- `Affected Packages`: `src/particleml/manifest.py`, `schemas/split-manifest.schema.json`, `tests/test_manifest.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-DATA-006

## Goal

Guarantee dataset-record-disjoint train, validation, and test partitions from the exact frozen PFN identity.

## Requirement Description

The system shall assign every source PFN by SHA-256 of its exact UTF-8 text, interpret the full digest as an unsigned big-endian integer, and map modulo 10 bucket 0 to test, 1 to validation, and all others to train.

## High-Level Requirements

- Preserve PFN text exactly; protocol prefixes participate in the split identity.
- Make every jet from one PFN inherit the same split.
- Detect duplicate PFNs and cross-partition `(record_id, run, lumi, event)` overlap.
- Report file, event, jet, class, and record counts per partition.
- Serialize and validate the split manifest using schema version 1.0.0 plus semantic checks.

## Inputs

- Validated frozen source manifest.
- Canonical dataset identity and versioned split/subset configuration when producing the final split manifest.

## Outputs

- Deterministic PFN-to-split assignments.
- Schema-valid split manifest and overlap/count report.

## Implementation Constraints

- Implement the exact algorithm from specification §2.2 without shortcut hashes or string normalization.
- Split assignment occurs before extraction; downstream artifacts inherit it.

## Failure and Degradation

- Reject overlap, duplicate assignment, unknown split values, manifest-hash mismatch, and event leakage with `SPLIT_*`.
- Do not move files between partitions to rebalance counts.

## Acceptance Criteria

- Golden PFNs map to the documented buckets exactly.
- Whitespace or protocol changes alter identity rather than being normalized away.
- Cross-partition PFN/event overlap fixtures fail closed.
- The output records class/record counts and the source-manifest hash.

## Minimum Verification

- `pytest -q tests/test_manifest.py::test_exact_pfn_split`
- Golden-vector, Unicode UTF-8, overlap, hash, and repeatability tests in GitHub Actions.

## Out of Scope

- Random event-level splitting.
- Post-hoc rebalancing of validation or test data.

## Notes

- A split-policy change requires a Research Plan v0.4.x amendment.
