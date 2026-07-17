# Sprint M1-03 Synthetic Cloud Data Pipeline Review Confirm

**Reviewed Inputs**

- `project/3-Plan/sprint-m1-03-synthetic-cloud-data-pipeline.md`
- `project/4-Reviews/sprint-m1-03-synthetic-cloud-data-pipeline-review-by-opencode-go-kimi-k2.7-code.md` (DeepSeek fallback)
- FR-DATA-004, FR-DATA-005, FR-DATA-007, FR-DATA-008, and FR-DATA-009
- `docs/software/specification.md`
- `docs/software/architecture.md`
- M1-02 implementation at commit `87a7c1a`

**Review Date**

- 2026-07-17

## Overall Conclusion

The review is directionally sound and identifies precision gaps that should be resolved before implementation. Its summary claims 23 findings and severity totals that sum to 26, while the actual findings table contains 21 actionable rows. All 21 table rows are answered below.

Only one review report was produced. The user explicitly authorized the single-report gate after repeated Kimi/GLM timeouts and Ark HTTP 400 responses in the same workflow.

## Decision Table

| No. | Severity | Type | Review Source | Original Comment Summary | Decision | Evidence | Follow-up Plan / Rejection Reason |
|---:|---|---|---|---|---|---|---|
| 1 | High | Correctness | Finding 1 | Audit ownership is broader than the listed `metrics.py` responsibility. | Accept | FR-DATA-009 requires field exclusion, confound controls, missingness, and retained outcomes in addition to metric computation. | Add `audit.py` for structured data-audit policy/results; keep `metrics.py` limited to deterministic numerical probes. |
| 2 | High | Correctness | Finding 2 | Exact signal/QCD subset ranking is absent. | Accept | Specification §4.2 fixes the hash input, integer interpretation, tie-break, record ordering, and round-robin behavior. | Add the exact algorithm and seed-separation rule to WP 5.2. |
| 3 | High | Requirement | Finding 3 | Exact A-D OmniLearned argv metadata is not scoped. | Accept | FR-DATA-005 requires exact flags even though external execution is deferred. | Generate and snapshot view metadata/argv fragments without running OmniLearned. |
| 4 | Medium | Consistency | Finding 4 | Fixture generation mechanism and compact schema are unclear. | Accept | Deterministic on-demand fixtures avoid committed binaries and local data dependencies. | Add `tests/fixtures/generate_compact_root.py`, define its required branches, and generate ROOT files in temporary test directories. |
| 5 | Medium | Consistency | Finding 5 | Repository documentation commands do not measure pipeline behavior. | Partial | They are still required repository-wide diagnostics from the approved development plan and catch schema/traceability drift. | Keep them, but label them repository consistency checks rather than M1-03 functional coverage. |
| 6 | Medium | Completeness | Finding 6 | Canonical HDF5 order/layout is not explicit. | Accept | Specification §3.3 is binding. | Add the required paths, shapes, dtypes, field order, gzip level, and jet-major chunk contract. |
| 7 | Medium | Completeness | Finding 7 | Positive particle pT/energy policy fields are not named. | Accept | Specification §3.2 requires both and blocks conversion when absent/non-positive. | Add exact names and fail-closed behavior. |
| 8 | Medium | Risk | Finding 8 | PID/argv drift would be detected too late. | Accept | The view contract is already fixed in specification §4.3. | Add M1-03 column-index, field-order, and argv snapshot tests plus view-completion validation. |
| 9 | Medium | Completeness | Finding 9 | Forbidden inputs and shuffled-label policy are undefined. | Partial | Forbidden fields are source-of-truth facts; a numerical shuffled-label threshold is a scientific policy and must not be invented in code. | Enumerate forbidden identity/audit/truth fields. Require a versioned `shuffled_label_auc_max` and deterministic permutation seed in audit policy; retain observed AUC and pass/fail. |
| 10 | Medium | Requirement | Finding 10 | Formal subset sizes are absent. | Accept | FR-DATA-008 fixes `10^3`, `10^4`, and provisional `10^5` per class unless E0 amends the grid. | Record the formal grid and use proportionally small synthetic sizes only to test the same algorithm/prefix contract. |
| 11 | Low | Clarity | Finding 11 | Insufficient-yield stable code is unnamed. | Partial | FR prose says `INSUFFICIENT_CLASS_YIELD`, while specification error taxonomy requires `SPLIT_*` and M1-02 already implements `SPLIT_INSUFFICIENT_CLASS_YIELD`. | Use `SPLIT_INSUFFICIENT_CLASS_YIELD` as the stable project code and note its mapping to the FR phrase. |
| 12 | Low | Clarity | Finding 12 | Stale view hashes are ambiguous. | Accept | Views bind canonical, split, subset, and preprocessing identities. | Define `VIEW_STALE_HASH` checks for each recorded dependency and integrate them with completion-marker validation. |
| 13 | Low | Clarity | Finding 13 | “Prove” overstates local evidence. | Accept | Local execution is diagnostic-only under the no-push instruction. | Replace “prove” with “demonstrate diagnostically.” |
| 14 | Low | Requirement | Finding 14 | Audit outcome persistence ownership is unclear. | Accept | FR-DATA-009 requires retained pass/fail state; FR-DATA-010 reporting remains later scope. | Make `audit.py` serialize the M1-03 data-audit result; `metrics.py` only computes probe metrics. |
| 15 | Low | Risk | Finding 15 | Semantic HDF5 hash rules are not defined. | Accept | File-byte hashes can vary with HDF5 metadata. | Define a versioned semantic hash over sorted dataset paths, dtype/shape metadata, C-order dataset bytes, and an allowlisted set of root attributes; store the algorithm identifier. |
| 16 | Low | Documentation | Finding 16 | M1-02 dependency APIs are not listed. | Accept | M1-03 must reuse, not duplicate, manifest/contracts/artifact/CLI behavior. | Add the available modules and responsibilities to prerequisites. |
| 17 | Info | Test | Finding 17 | Audit test coverage is not enumerated. | Accept | The targeted command includes `test_audit.py`. | List forbidden fields, training-only control identities, versioned thresholds, missingness, mixture counts, and shuffled-label reproducibility/pass-fail coverage. |
| 18 | Info | Clarity | Finding 18 | Preprocessing policy ingestion is vague. | Accept | Specification §4.1 enumerates required policy/state fields and canonical JSON rules. | Add explicit versioned JSON fields, unknown/missing-key rejection, train-only fit identity, and no-default behavior. |
| 19 | Info | Risk | Finding 19 | Minimum synthetic edge-case coverage is absent. | Accept | Diagnostic fixtures must exercise both valid transformations and fail-closed paths. | Add empty jet, max/truncated jet, non-finite value, duplicate identity, unknown PID, neutral charge, missing track, padding, and pT-tie cases. |
| 20 | Info | Completeness | Finding 20 | Audit thresholds and pass/fail ownership are undefined. | Accept | Thresholds are scientific configuration, not code constants. | Define a strict audit-policy object with explicit thresholds and serialize observed values, thresholds, and decisions. |
| 21 | Info | Completeness | Finding 21 | Fixture storage format is unclear. | Accept | On-demand uproot fixtures are deterministic and avoid repository binary churn. | State that no binary ROOT fixture is committed; generation code and expected records are committed. |

## Needs Immediate Action

- Apply all accepted and partially accepted Sprint clarifications before implementation.
- Preserve the M1-02 public boundaries and keep external OmniLearned execution out of scope.

## Can Be Deferred

- Real CMSSW integration and E0 scientific verification.
- Final FR-DATA-010 reporting aggregation beyond the structured M1-03 audit artifact.
- Cloud CI evidence until push authorization changes.

## Final Status

Accept after the confirmed document changes are applied. Implementation may then begin with failing tests.
