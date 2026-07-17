# Sprint M3-01 E1 Pilot

**Milestone:** M3 - Core Experiment

**Goal:** Implement deterministic run orchestration, failure-complete run records, aligned predictions, required metrics, and execute the A/D E1 resource pilot.

**Architecture:** The orchestrator enforces gates and immutable run lifecycle; model execution stays behind the integration boundary; metrics own evaluation definitions; cloud artifacts remain authoritative.

**Tech Stack:** Python, JSON Schema, PyTorch/OmniLearned subprocess, RunPod, NumPy/scientific metrics, persistent cloud storage.

## 1. Sprint Goal

Pass AC-E1-001 for A and D at `10^3` and `10^4` jets per class with one seed and use measured runtime/memory/storage to approve or reject the E2 budget.

Core objectives:

- Implement stage-gated matrix generation, clean commands, resume, and immutable run/failure records.
- Save aligned prediction artifacts and compute required per-run metrics.
- Execute the four-condition E1 pilot and replace projected E2 resource assumptions with measurements.

## 2. Prerequisites

- [Sprint M2-02](./sprint-m2-02-omnilearned-e05.md) with an approved E0.5 model policy.
- [FR-TRAIN-001](../1-Requirement/FR-TRAIN-001-stage-gated-experiment-matrix.md), [FR-TRAIN-002](../1-Requirement/FR-TRAIN-002-deterministic-clean-commands.md), [FR-TRAIN-003](../1-Requirement/FR-TRAIN-003-run-records.md), [FR-TRAIN-004](../1-Requirement/FR-TRAIN-004-complete-failure-accounting.md).
- [FR-EVAL-001](../1-Requirement/FR-EVAL-001-aligned-predictions.md) and [FR-EVAL-002](../1-Requirement/FR-EVAL-002-required-metrics.md).

## 3. Scope

Included:

- E0-E3 gate model, deterministic matrix resolution, dry-run, run execution/resume, and failure retention.
- Run and prediction schema integration, AUC/rejection/accuracy/data-efficiency primitives.
- A/D × `10^3`/`10^4` × one-seed RunPod pilot.
- Measured GPU/time/storage record and E2 budget decision with 25% reserve.

Not included:

- Full A-D/scale/three-seed E2 matrix.
- Paired bootstrap and publication reports.
- Automatic retries or hidden condition removal.

## 4. File Structure and Responsibilities

| File / Directory | Operation | Responsibility |
|---|---|---|
| `src/particleml/experiment.py` | Create | Gates, matrix, execution, resume, run/failure records |
| `src/particleml/metrics.py` | Modify | Predictions and per-run metrics |
| `src/particleml/cli.py` | Modify | `run train`, `evaluate`, dry-run/resume |
| `configs/e1/` | Create | Frozen pilot conditions and budget policy |
| `tests/test_experiment.py` | Create | Gates, matrix, lifecycle, failures |
| `tests/test_metrics.py` | Create | Alignment and metric definitions |

## 5. Work Scope

### 5.1 Work Package: Orchestration and Run Lifecycle

- [x] Write gate-order, matrix, dry-run, overwrite, exit-code, timeout, and interruption tests.
- [x] Implement deterministic `RunSpec` resolution and immutable run-record publication.
- [x] Emit schema-valid success/failure/timeout/interruption records and preserve one-attempt outcomes without automatic retry.

### 5.2 Work Package: Predictions and Metrics

- [x] Write identity/order/payload and golden AUC/rejection/accuracy tests.
- [x] Publish one score/target/jet ID per fixed test jet with deterministic NPZ bytes, payload hash, metadata hash, and completion marker.
- [x] Implement specified interpolation, zero-background `null`, validation threshold, and unstable-ratio fallback.

### 5.3 Work Package: E1 Execution and Budget Gate

- [ ] Dry-run and review all four A/D-scale conditions before execution.
- [ ] Execute each formal condition once and retain failures as first-class records.
- [ ] Record wall time, GPU time, peak memory, checkpoint/prediction/log/storage sizes, and GPU identity.
- [ ] Approve or reject E2 only after applying the 25% reserve to measured projection.

## 6. TDD and Test Plan

- [ ] Cloud CI covers gate/matrix/lifecycle/contracts/metrics with tiny fixtures.
- [ ] RunPod covers clean-command training/evaluation and resource collection.
- [x] Verify exact ordered A/D test identities and targets before any comparison.

## 7. Verification Commands

```text
pytest -q tests/test_experiment.py tests/test_metrics.py
ruff check
mypy src/particleml
pytest
python scripts/validate_software_docs.py
pnpm test
pnpm docs:build
```

Formal E1 `particleml run train` and `particleml evaluate` argv are resolved from `configs/e1/`, retained by dry-run, and executed on RunPod.

### Local Diagnostic Results (2026-07-17)

- Targeted experiment/metrics/contracts/CLI suite: `35 passed`.
- Full Python suite: `130 passed`.
- Ruff and strict mypy: passed for 12 source modules.
- Software documentation validation: passed for 4 documents, 5 schemas, 39 traced requirements, and 8 link-bearing files.
- Formal E1 execution, resource measurements, and E2 budget approval were not attempted because E0 and E0.5 remain blocked.

## 8. Risks and Recovery

- Risk: partial runs are reused or omitted. Control: completion/hash checks and full matrix ledger.
- Risk: metrics drift from preregistered definitions. Control: golden statistical fixtures before RunPod execution.
- Risk: E2 exceeds USD 500 working budget. Control: block E2 unless measured projection plus reserve passes.
- Recovery: retain failed runs; approved reruns use new run IDs and never overwrite evidence.

## 9. Deliverables

- [x] Deterministic orchestrator and complete local run lifecycle boundary.
- [x] Aligned prediction validation and per-run metric services.
- [ ] Four E1 run outcomes with resource measurements.
- [ ] AC-E1-001 and E2 budget decision artifacts.

## 10. Completion Criteria

- [ ] All four pilot conditions are successful or explicitly retained failures.
- [ ] Successful runs have schema-valid aligned predictions and valid metrics.
- [ ] AC-E1-001 passes and E2 budget is approved before M6-01 starts.

## 11. Delivery Conclusion

Local M3-01 orchestration, lifecycle, prediction-validation, and metric software is implemented and tested. All four E1 conditions remain unexecuted and visible as blocked because AC-E0-001 and AC-E05-001 have no qualifying evidence. Consequently AC-E1-001 and the measured E2 budget decision remain pending; no runtime, memory, storage, cost, or performance result is claimed.
