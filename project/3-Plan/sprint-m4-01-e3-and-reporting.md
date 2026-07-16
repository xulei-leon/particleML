# Sprint M4-01 E3 Control and Evidence-Derived Reporting

**Milestone:** M4 - Publication Control and Reporting

**Goal:** Implement the required Deep Sets/PFN control and generate publication tables, figures, matrix status, and claim eligibility only from validated E0-E3 evidence.

**Architecture:** The in-repository baseline reuses existing data/run/evaluation contracts. Reporting is a read-only consumer of validated artifacts and cannot modify or invent scientific results.

**Tech Stack:** Python, PyTorch baseline, RunPod, NumPy, plotting/table libraries, JSON/JSON Schema, deterministic report generation.

## 1. Sprint Goal

Pass AC-E3-001 or formally defer it with narrowed claims, then produce reproducible T1-T4/F1-F3 evidence and a claim-eligibility ledger.

Core objectives:

- Implement and execute masked Deep Sets/PFN A-versus-D at frozen `n_max` with three seeds.
- Propagate evidence status monotonically across requirements, gates, artifacts, figures, and claims.
- Generate all eligible reports exclusively from schema-valid, content-addressed artifacts.

## 2. Prerequisites

- [Sprint M3-02](./sprint-m3-02-e2-core-matrix.md) with AC-E2-001 passed.
- [FR-MODEL-006](../1-Requirement/FR-MODEL-006-deep-sets-pfn-control.md), [FR-EVAL-004](../1-Requirement/FR-EVAL-004-evidence-derived-reports.md), and [FR-REP-003](../1-Requirement/FR-REP-003-evidence-status-propagation.md).
- Frozen `n_max`, A/D views, three seeds, baseline architecture/optimizer/stopping policy, and complete prior gate artifacts.

## 3. Scope

Included:

- Masked Deep Sets/PFN baseline, A/D E3 runs, aligned predictions, metrics, and paired comparisons.
- Deterministic reporting for dataset/audit, core matrix, data efficiency, robustness, and reproducibility appendix.
- Claim-eligibility/status ledger and documentation/traceability updates.

Not included:

- Broad model benchmarking or mandatory random-initialized OmniLearned.
- Manual spreadsheet corrections or result transcription.
- Claims of unseen-class, cross-detector, causal feature importance, or universal foundation-model superiority.

## 4. File Structure and Responsibilities

| File / Directory | Operation | Responsibility |
|---|---|---|
| `src/particleml/baseline.py` or first justified module | Create | Masked Deep Sets/PFN model |
| `src/particleml/reporting.py` | Create | Validated aggregation, tables, figures, claim ledger |
| `src/particleml/cli.py` | Modify | `report build` and baseline condition wiring |
| `configs/e3/` | Create | Frozen baseline and E3 matrix |
| `configs/reports/` | Create | Evidence definitions and output policy |
| `tests/test_baseline.py` | Create | Mask/shape/train/prediction tests |
| `tests/test_reporting.py` | Modify | Completeness, status, eligibility, determinism |
| `docs/software/traceability-matrix.md` | Modify | Evidence-backed status updates only |

## 5. Work Scope

### 5.1 Work Package: Deep Sets/PFN Control

- [ ] Write failing mask, padding-invariance, shape, pooling, parameter-record, and train-smoke tests.
- [ ] Freeze the per-particle MLP, pooling, head, optimizer, and stopping configuration before formal E3.
- [ ] Execute A and D at `n_max` for three seeds using the standard run/prediction/metric contracts.
- [ ] Retain explicit failures and paired A-D statistics.

### 5.2 Work Package: Evidence Status and Claim Eligibility

- [ ] Write failing status-monotonicity and fallback/deferred-claim tests.
- [ ] Resolve every requirement/test/gate/artifact/figure/claim status from retained evidence.
- [ ] Ensure `implemented` and `verified` cite concrete code/CI/gate identities.
- [ ] Narrow claims automatically if supervised fallback or E3 deferral applies.

### 5.3 Work Package: Reproducible Reports

- [ ] Write failing schema/hash/matrix-completeness and deterministic-output tests.
- [ ] Generate T1 dataset/audit, F1 scale curves, F2 paired deltas, T2 matrix, T3 data efficiency, F3/T4 robustness/reproducibility outputs.
- [ ] Show every seed, uncertainty convention, failed/missing condition, and eligibility state.
- [ ] Rebuild from retained artifacts and compare output hashes.

## 6. TDD and Test Plan

- [ ] Test masks/padding, baseline output shape, frozen configuration, smoke loss, run/prediction compatibility, matrix completeness, invalid artifacts, status monotonicity, claim narrowing, and deterministic reports.
- [ ] Execute E3 on RunPod; generate reports only from retained validated cloud artifacts.

## 7. Verification Commands

```text
pytest -q tests/test_baseline.py tests/test_reporting.py tests/test_metrics.py
ruff check
mypy src/particleml
pytest
python scripts/validate_software_docs.py
pnpm test
pnpm docs:build
```

Formal E3 runs and `particleml report build` execute in the approved cloud environment with exact resolved configuration and artifact hashes retained.

## 8. Risks and Recovery

- Risk: baseline fails or gives incomplete E3 evidence. Control: retain failure/defer status and narrow claims rather than hiding the control.
- Risk: report generation admits planned or invalid runs. Control: schema/hash/completeness gates and explicit success filtering.
- Risk: manual edits break reproducibility. Control: generated outputs are rebuilt from immutable artifacts and content-hashed.
- Recovery: reports are reproducible derived artifacts; rebuild after code/config fixes while retaining original evidence.

## 9. Deliverables

- [ ] Masked Deep Sets/PFN implementation and E3 A/D run records.
- [ ] AC-E3-001 decision and paired robustness evidence.
- [ ] Generated figures/tables/matrix status.
- [ ] Claim-eligibility ledger and evidence-backed traceability update.

## 10. Completion Criteria

- [ ] AC-E3-001 passes, or deferral and narrowed claims are explicit.
- [ ] Every report input is schema-valid, hash-verified, and status-eligible.
- [ ] Rebuild from identical evidence reproduces outputs.
- [ ] Publication framing stays within the approved CMS 2015 feature-availability claim boundary.

## 11. Delivery Conclusion

Pending implementation, review confirmation, RunPod execution, E3 gate verification, and report regeneration.
