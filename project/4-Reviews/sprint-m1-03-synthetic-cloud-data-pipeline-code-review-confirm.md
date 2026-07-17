# Sprint M1-03 Synthetic Cloud Data Pipeline Code Review Confirm

**Reviewed Inputs**

- `project/3-Plan/sprint-m1-03-synthetic-cloud-data-pipeline.md`
- `project/4-Reviews/sprint-m1-03-synthetic-cloud-data-pipeline-code-review-by-opencode-go-kimi-k2.7-code.md` (DeepSeek fallback)
- `src/particleml/{artifacts,audit,dataset,manifest,metrics,views}.py`
- `tests/test_{artifacts,audit,cli,dataset,manifest,views}.py`
- FR-DATA-005, FR-DATA-009, FR-REP-001, `docs/software/specification.md`, and `docs/software/architecture.md`

**Review Date**

- 2026-07-17

## Overall Conclusion

The review correctly identifies stale-dependency validation, audit-decision, scalability, and test-coverage work. It overstates the pT tie issue because stable filtering preserves original relative order, and some proposed fixes either invent a scientific imbalance threshold or collapse diagnostic file APIs into the directory-artifact lifecycle without accounting for their different contracts.

All 15 findings are decided below. Accepted and partial actions must be applied and reverified before the Sprint is accepted.

## Decision Table

| No. | Severity | Type | Review Source | Original Comment Summary | Decision | Evidence | Follow-up Plan / Rejection Reason |
|---:|---|---|---|---|---|---|---|
| 1 | High | Correctness | Finding 1 | Filtering before stable pT sorting loses the original tie order. | Reject | Python list filtering preserves relative order, and the subsequent sort uses the surviving order as a tie key. For two surviving equal-pT particles, this order is identical to their original TTree order. | Add an explicit pT-tie regression assertion, but do not change correct sorting logic. |
| 2 | High | Requirement | Finding 2 | View construction does not validate formal dependency completion markers. | Partial | FR-REP-001 and architecture §8 require formal consumers to reject missing markers. However, `resume_artifact` validates a directory plus request hashes, while the current low-level synthetic APIs intentionally consume direct fixture files. | Add a read-only published-artifact verifier in `artifacts.py`; make formal view consumption require it while retaining an explicit diagnostic-unpublished path for local generated fixtures. Translate dependency failures to `VIEW_STALE_HASH`. |
| 3 | High | Requirement | Finding 3 | The identity payload is hashed only after reading and is not compared with an expected subset hash. | Accept | FR-DATA-005 requires subset-hash equality and the split manifest already stores each identity payload SHA-256. | Add an expected subset SHA-256 input, hash exact identity-payload bytes before use, reject mismatch with `VIEW_STALE_HASH`, and retain the verified hash in view metadata. |
| 4 | Medium | Correctness | Finding 4 | QCD mixture counts are hard-coded as passing. | Partial | FR-DATA-009 requires counts to match the frozen mixture policy, but it does not authorize inventing a Gini or max-fraction scientific threshold. | Add explicit expected per-record QCD counts to the strict audit policy and compare exact observed training counts against that mapping. |
| 5 | Medium | Test | Finding 5 | Audit tests cover only a passing policy. | Accept | Sprint §6 explicitly requires shuffled-label pass/fail coverage. | Add failing-threshold and mixture-mismatch tests that assert the overall and per-check decisions. |
| 6 | Medium | Test | Finding 6 | Several enumerated conversion, subset, and stale-input cases lack dedicated tests. | Partial | Existing tests already cover padding, unknown PID mapping, neutral/charged-missing states, truncation, insufficient yield, forbidden fields, and stale canonical content, but exact-boundary, missing-identity, invalid-hash, and explicit tie cases remain useful. | Add focused assertions for exact PID/track/tie behavior, missing view identities, invalid dependency hashes, and round-robin exhaustion; avoid duplicating already-covered behavior. |
| 7 | Medium | Test | Finding 7 | CLI tests omit `audit data` and A/B/D views. | Accept | Sprint §5.3 names all three CLI groups and exact A-D argv fragments. | Parameterize view command coverage across A-D and exercise `audit data`, including a failed audit result that remains a successful command execution with retained status. |
| 8 | Medium | Consistency | Finding 8 | Subset ranking duplicates the manifest ranking implementation. | Accept | The Sprint prerequisite requires reuse of M1-02 manifest boundaries, and both functions implement the same byte-level rule. | Promote the manifest ranking helper to a public `rank_jet_id` function, use it from both split-manifest and view subset selection, and retain golden prefix tests. |
| 9 | Low | Correctness | Finding 9 | Masked values are zeroed twice. | Reject | The first assignment covers normalized continuous fields only; native PID is concatenated afterward. The final assignment is the single operation that also guarantees zero padded PID cells in the materialized tensor. | Keep the final defense-in-depth zeroing and add a concise comment describing the native-PID reason. |
| 10 | Low | Performance | Finding 10 | Pairwise AUC allocates an O(P×N) matrix. | Accept | Formal subset sizes include up to provisional 10^5 jets per class, where the matrix is not viable even for an audit probe. | Replace it with deterministic average-rank AUC in O(n log n), including tie tests. |
| 11 | Low | Maintainability | Finding 11 | `_jagged_values` is unused. | Accept | Repository search finds no caller. | Remove the helper. |
| 12 | Low | Documentation | Finding 12 | `shuffled_label_auc` does not document its typed error for a negative seed. | Accept | The public function raises `IntegrityError(DATA_AUDIT_POLICY)`. | Add a concise `Raises` section. |
| 13 | Info | Risk | Finding 13 | Casting native PID 0-5 to float32 could lose precision if the contract changed radically. | Reject | The frozen vocabulary in the confirmed Sprint and FR-DATA-005 is exactly 0-5, all exactly representable in float32; model HDF5 combines fields in one float tensor. | No change; a hypothetical incompatible vocabulary change requires a new contract version. |
| 14 | Info | Documentation | Finding 14 | `jet_pt` is an implicit shuffled-label score proxy. | Accept | The serialized audit should identify how each observation was produced. | Retain `score_field: audit/jet_pt` in the report and document the probe in code without making scientific fields ambient or default-configurable. |
| 15 | Info | Documentation | Finding 15 | Sprint implementation checkboxes remain unchecked. | Accept | Workflow state must reflect completed and deferred gates before commit. | Update only substantiated checkboxes and record local verification plus the no-push cloud-evidence deferral after final diagnostics pass. |

## Needs Immediate Action

- Implement formal dependency and subset-hash validation without removing the explicit diagnostic fixture path.
- Replace the unconditional QCD mixture decision with an exact policy comparison.
- Replace quadratic AUC, consolidate ranking, and close the accepted test gaps.

## Can Be Deferred

- Formal cloud verification and real CMS product decoding remain deferred to the already documented qualified-host stages.
- A new statistical QCD-mixture imbalance metric is not authorized; exact frozen-count comparison is sufficient for M1-03.

## Final Status

Accept after all accepted and partial actions above are implemented and the full local verification suite passes. One code review report is sufficient under the user's explicit continuation override.
