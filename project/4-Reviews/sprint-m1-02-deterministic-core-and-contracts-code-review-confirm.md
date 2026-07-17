# Sprint M1-02 Deterministic Core and Contracts Code Review Confirm

**Reviewed Inputs**

- Current uncommitted M1-02 implementation and tests
- `project/3-Plan/sprint-m1-02-deterministic-core-and-contracts.md`
- `project/4-Reviews/sprint-m1-02-deterministic-core-and-contracts-code-review-by-opencode-go-kimi-k2.7-code.md` (DeepSeek fallback)
- `docs/software/specification.md`
- `schemas/split-manifest.schema.json`

**Review Date**

- 2026-07-17

## Overall Conclusion

The review correctly identifies one full-suite regression and meaningful missing negative tests. Most proposed changes are accepted. The reported mypy failure is stale because the reviewer ran `uv run mypy` without the locked CI requirements; the declared `uv run --with-requirements requirements-ci.lock mypy src/particleml` command passes after the type-stub lock update.

Only one non-empty code-review report was produced: Kimi and GLM timed out after 20 minutes and Ark returned HTTP 400. The user explicitly authorized continuing with one report.

## Decision Table

| No. | Severity | Type | Review Source | Original Comment Summary | Decision | Evidence | Follow-up Plan / Rejection Reason |
|---:|---|---|---|---|---|---|---|
| 1 | Critical | Correctness | Finding 1 | The CLI description change breaks `test_bootstrap.py`. | Accept | The full suite shows the exact assertion regression. | Restore the established “cloud-verified jet-physics workflows” description while retaining the new subcommands. |
| 2 | High | Test | Finding 2 | `SplitConfig` validation lacks tests. | Accept | The type is a Sprint deliverable with non-trivial invariants. | Add valid and parameterized invalid construction tests. |
| 3 | High | Consistency | Finding 3 | `qcd_candidate` is accepted for source records but not source files/config. | Partial | The research plan retains candidate QCD records until E0 freezes the active mixture, so removing the role would narrow the 1.0.0 provenance contract incorrectly. | Add `qcd_candidate` to source-file/config roles and ensure candidate jets are not selected into formal training subsets until marked active. |
| 4 | High | Test | Finding 4 | `split build` has only a happy-path CLI test. | Accept | Hash mismatch, missing input, collision, invalid identity values, and insufficient class yield are required failure families. | Add focused CLI negative tests for those paths. |
| 5 | High | Maintainability | Finding 5 | Mypy cannot resolve `jsonschema` stubs. | Reject | `types-jsonschema` is in the CI extra and regenerated lock; `uv run --with-requirements requirements-ci.lock mypy src/particleml` passes with no issues. The review used a different environment command. | Keep the locked CI dependency and verify again in the final diagnostic suite. |
| 6 | Medium | Correctness | Finding 6 | `_select_qcd` can return a partial result silently. | Accept | The caller currently detects the shortfall, but the private helper contract is unsafe for reuse. | Raise `SPLIT_INSUFFICIENT_CLASS_YIELD` inside `_select_qcd` and test the CLI mapping. |
| 7 | Medium | Consistency | Finding 7 | Config roles diverge from the source-record schema. | Accept | This is the configuration side of Finding 3. | Apply the same `qcd_candidate` alignment and active-only subset rule. |
| 8 | Medium | Maintainability | Finding 8 | `hashlib` is imported locally. | Accept | A module-level import is clearer and consistent with other modules. | Move the import to the module import block. |
| 9 | Medium | Risk | Finding 9 | Split outputs rely on same-filesystem rename and existence prechecks. | Partial | Temporary files are created beside each final path, so cross-volume rename is impossible. Same-filesystem publication is already explicit in the confirmed Sprint; concurrent publishers remain a possible race on POSIX. | Add an implementation comment and retain no-overwrite/collision tests. Cross-process transaction coordination is deferred because formal concurrent writers are out of scope. |
| 10 | Low | Correctness | Finding 10 | Non-string schema versions rely on downstream schema validation. | Accept | Explicit version-type failure improves stable diagnostics. | Raise `CONTRACT_VERSION_TYPE` before JSON Schema validation and add a test. |
| 11 | Low | Test | Finding 11 | Contract-kind detection edge cases are untested. | Accept | Ambiguous identifiers must fail closed. | Test single, missing, and multiple identifier cases. |
| 12 | Low | Correctness | Finding 12 | Stable jet identity permits zero run/lumi/event. | Accept | CMS event coordinates are positive; only `jet_index` is explicitly zero-based. | Require positive record/run/lumi/event and non-negative jet index, with negative/zero tests. |
| 13 | Info | Test | Finding 13 | CLI success output assertion is lenient. | Accept | Exact output is a stable, low-cost CLI contract. | Assert the complete output line including the path. |
| 14 | Info | Risk | Finding 14 | Cleanup failure can mask the original publication error. | Accept | `rmtree` runs in `finally` while another exception may be active. | Use non-raising best-effort partial cleanup and preserve the original exception. |

## Needs Immediate Action

- Apply rows 1-4, 6-8, and 10-14.
- Re-run the targeted suite, full pytest suite, Ruff, and strict mypy.

## Can Be Deferred

- Cross-process transactional coordination for multiple simultaneous `split build` publishers.
- Cloud CI evidence under the user's no-push instruction.

## Final Status

Accept after the confirmed changes pass the complete local diagnostic suite. Local results remain non-formal evidence.
