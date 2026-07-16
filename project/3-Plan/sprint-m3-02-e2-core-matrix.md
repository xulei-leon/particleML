# Sprint M3-02 E2 Core Matrix

**Milestone:** M3 - Core Experiment

**Goal:** Implement paired statistical comparison and execute the complete frozen A-D, scale, and three-seed core matrix with no silent omissions.

**Architecture:** This Sprint extends the metrics service and executes the existing orchestrator. It does not change data, model, preprocessing, or endpoint contracts after E1 approval.

**Tech Stack:** Python, NumPy `PCG64`, statistical regression fixtures, RunPod GPU execution, content-addressed predictions/comparisons.

## 1. Sprint Goal

Pass AC-E2-001 and produce complete, aligned, paired evidence for RQ1 and RQ2.

Core objectives:

- Implement deterministic class-stratified paired bootstrap and all required A-D contrasts.
- Execute every frozen A-D × scale × three-seed condition once.
- Preserve failures and generate paired metrics only from exact identity-aligned successes.

## 2. Prerequisites

- [Sprint M3-01](./sprint-m3-01-e1-pilot.md) with AC-E1-001 and approved E2 budget.
- [FR-EVAL-003](../1-Requirement/FR-EVAL-003-paired-uncertainty.md).
- Reuse FR-TRAIN-001/003/004 and FR-EVAL-001/002 contracts without changing them.
- Frozen A-D views, scale grid, three first-pass seeds, preprocessing, model policy, and fixed test set.

## 3. Scope

Included:

- Paired A-B, B-C, C-D, C-A, and D-A comparisons at every approved scale.
- At least 1,000 fixed-seed class-stratified paired bootstrap replicates.
- Full E2 matrix execution, failure accounting, prediction alignment, per-run metrics, paired deltas, and seed variation.

Not included:

- Feature additions, scale-grid changes, seed removal, or adaptive reruns based on observed results.
- Deep Sets/PFN E3 control or final publication report generation.
- Combining seed variation with event bootstrap into one uncertainty.

## 4. File Structure and Responsibilities

| File / Directory | Operation | Responsibility |
|---|---|---|
| `src/particleml/metrics.py` | Modify | Paired identity checks, bootstrap, seed summaries |
| `configs/e2/` | Create | Frozen core matrix and bootstrap policy |
| `tests/test_metrics.py` | Modify | Paired statistical regression |
| `tests/test_experiment.py` | Modify | E2 matrix completeness/failure accounting |
| Cloud `runs/`, `predictions/`, `reports/` | Create artifacts | Formal E2 evidence |

## 5. Work Scope

### 5.1 Work Package: Paired Statistics

- [ ] Write failing deterministic golden bootstrap and identity-mismatch tests.
- [ ] Implement exact ordered-identity/target validation and all five contrasts.
- [ ] Use `PCG64`, class-stratified common indices, 1,000+ replicates, percentile intervals, and discard accounting.
- [ ] Keep per-seed results, mean, and sample standard deviation separate.

### 5.2 Work Package: Matrix Freeze and Dry Run

- [ ] Validate matrix cardinality against frozen A-D, scales, seeds, and model policy.
- [ ] Verify every input/index/checkpoint/config hash and projected cost before launch.
- [ ] Retain a reviewed dry-run ledger for all conditions.

### 5.3 Work Package: Formal E2 Execution

- [ ] Execute each condition once without automatic retry.
- [ ] Retain schema-valid success or failure records and aligned predictions for successes.
- [ ] Compute per-run and eligible paired artifacts; reject any identity mismatch.
- [ ] Produce a complete condition ledger with no silent omission.

## 6. TDD and Test Plan

- [ ] Test bootstrap repeatability, stratification, common indices, percentiles, non-finite discard threshold, all contrast names, reordered/duplicate/missing identities, and target mismatch.
- [ ] Run matrix completeness tests with mixed success/failure fixtures before formal execution.
- [ ] Treat near-null outcomes as valid results, not triggers for protocol changes.

## 7. Verification Commands

```text
pytest -q tests/test_metrics.py tests/test_experiment.py
ruff check
mypy src/particleml
pytest
python scripts/validate_software_docs.py
pnpm test
pnpm docs:build
```

Formal matrix commands are produced by `particleml run train --config <versioned-e2-config>` and `particleml evaluate`; exact dry-run argv and hashes are retained before RunPod execution.

## 8. Risks and Recovery

- Risk: identity misalignment invalidates paired inference. Control: exact ordered equality before any bootstrap.
- Risk: matrix cost exceeds approved budget during execution. Control: per-run resource monitoring and stop before unauthorized spend; retain completed/failed conditions.
- Risk: formal run fails. Control: retain failure; no silent retry or deletion.
- Recovery: code/statistics fixes require new versioned comparison artifacts; original runs and predictions remain immutable.

## 9. Deliverables

- [ ] Deterministic paired-bootstrap implementation and tests.
- [ ] Full E2 run/prediction ledger.
- [ ] Required paired comparison and seed-variation artifacts.
- [ ] AC-E2-001 gate record.

## 10. Completion Criteria

- [ ] Every planned condition has a schema-valid success or explicit retained failure.
- [ ] All eligible pairs use the exact fixed test identity order.
- [ ] Required metrics/uncertainty are complete and no condition is omitted.
- [ ] AC-E2-001 passes before M7-01 begins.

## 11. Delivery Conclusion

Pending implementation, review confirmation, RunPod execution, and E2 gate verification.
