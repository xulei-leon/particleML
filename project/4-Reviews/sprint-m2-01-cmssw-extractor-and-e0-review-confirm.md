# Sprint M2-01 CMSSW Extractor and E0 Review Confirm

**Reviewed Inputs**

- `project/3-Plan/sprint-m2-01-cmssw-extractor-and-e0.md`
- `project/4-Reviews/sprint-m2-01-cmssw-extractor-and-e0-review-by-opencode-go-kimi-k2.7-code.md` (DeepSeek fallback)
- FR-DATA-002, FR-DATA-003, and FR-DATA-010
- `docs/software/specification.md`, `docs/software/requirements.md`, `docs/software/architecture.md`
- `docs/research/research-plan.md` and `project/3-Plan/particleml-development-plan.md`
- Repository state after local commit `47927a2`

**Review Date**

- 2026-07-17

## Overall Conclusion

The review is sound on the central issue: local deliverables and qualified-host-only gates must be visibly separated before implementation. Several comments overstate normal pre-implementation absence as a defect, misread strict mypy's recursive scope, or object to path variables required by the active Sprint workflow skill. All 20 comments are answered below.

## Decision Table

| No. | Severity | Type | Review Source | Original Comment Summary | Decision | Evidence | Follow-up Plan / Rejection Reason |
|---:|---|---|---|---|---|---|---|
| 1 | Critical | Consistency | Finding 1 | Included scope contradicts the no-host evidence boundary. | Accept | The current Scope section mixes the full AC-E0 lifecycle with this iteration's code delivery. | Split local deliverables and `[HOST_DEFERRED]` work into explicit subsections and maintain a deferred register. |
| 2 | Critical | Documentation | Finding 2 | The file table does not acknowledge that all new CMSSW/E0 files are absent. | Partial | `Operation: Create` already means the files are absent before implementation; that is not a correctness defect. Explicit baseline status still improves auditability. | Add a Status column and state that the CMSSW/config/E0 tree is absent at Sprint start. |
| 3 | Critical | Requirement | Finding 3 | Host qualification is impossible in this workspace. | Accept | FR-DATA-002 requires a qualified POSIX host and real fixture job; neither is configured. | Move qualification and real file coverage to `[HOST_DEFERRED]`; retain only the strict measurement contract locally. |
| 4 | Critical | Consistency | Finding 4 | Real multi-file processing remains an actionable local checklist item. | Accept | Those items require real CMS access and cannot be satisfied by local fixtures. | Tag every work-package item as `[LOCAL]` or `[HOST_DEFERRED]` and define separate acceptance outcomes. |
| 5 | High | Maintainability | Finding 5 | The boundary between `audit.py` and proposed `e0.py` is undefined. | Accept | M1-03 `audit.py` owns one canonical dataset's deterministic checks; M2-01 must aggregate multiple retained evidence families. | Define `audit.py` as per-artifact probes and `e0.py` as cross-artifact AC-E0 aggregation, cost/yield math, freeze decisions, and external-evidence blocking. |
| 6 | High | Contract | Finding 6 | The proposed E0 audit schema is absent from authoritative documentation. | Accept | Documentation and traceability must change with new serialized interfaces. | Add specification/traceability updates to the Sprint file list and implementation scope alongside the schema. |
| 7 | High | Correctness | Finding 7 | `blocked_external_evidence` has no formal status contract. | Accept | Existing M1-03 audit uses only passed/failed and cannot represent mandatory absent host evidence. | Define an E0 status enumeration `passed`, `failed`, `blocked_external_evidence`; do not change per-artifact M1-03 status semantics. |
| 8 | High | Consistency | Finding 8 | Workflow path variables point to directories that do not exist. | Reject | `sprint-workflow` requires resolving these logical paths from repository layout/fallbacks; it does not require creating or moving completion directories unless artifacts are accepted and moved. | Keep the required workflow configuration and do not create empty directories as cosmetic outputs. |
| 9 | Medium | Requirement | Finding 9 | The local contract omits the complete measured cost table. | Accept | FR-DATA-010 requires source bytes, CPU/event, wall time, throughput, failures, storage sizes, and E0/E1/E2 projection with 25% reserve. | Enumerate all required measurement fields and reserve math in the local E0 evidence contract scope. |
| 10 | Medium | Clarity | Finding 10 | Local CMSSW source fixtures and host runtime fixtures are conflated. | Accept | Source/configuration code can be authored and statically checked on Windows, but CMS product behavior cannot. | Split §5.2 into local source/static contract work and host-deferred compile/cmsRun/hand-inspected truth work. |
| 11 | Medium | Test | Finding 11 | Reusable verification commands do not clearly cover new files and may require CMSSW. | Partial | Strict mypy over `src/particleml` does include `e0.py`, and the planned local test is explicitly static. A matrix is still useful. | Add a command/environment matrix stating that all reusable checks pass locally and `cmsRun` alone remains host-deferred. |
| 12 | Medium | Consistency | Finding 12 | Qualification and E0 pilot sample counts are conflated. | Accept | Research Plan v0.4.0 distinguishes 1 TT + 1 QCD qualification from 5-10 TT + multi-file candidate-QCD E0. | Record them as two separate host-deferred gates. |
| 13 | Medium | Documentation | Finding 13 | Static CMSSW contract checks are not defined. | Accept | A local static test must not imply C++ compilation. | Require file/non-empty checks, BuildFile XML parsing, configuration syntax compilation, frozen literal/input-tag/provenance assertions, and explicit no-runtime-evidence labeling. |
| 14 | Medium | Risk | Finding 14 | No risk covers uncompiled CMSSW source. | Accept | Static checks cannot validate CMSSW types, product availability, truth traversal, or decoded units. | Add an uncompiled-boundary risk and require host compile/runtime evidence before promotion. |
| 15 | Low | Documentation | Finding 15 | Prerequisite FR availability is confirmed. | Reject | This is informational and requests no change; the current prerequisite statement is correct. | No action. |
| 16 | Low | Clarity | Finding 16 | The amendment pathway reads like a local freeze decision. | Accept | Research Plan changes require measured E0 evidence. | Scope only an amendment template/trigger contract locally; prohibit publishing an amendment from fixture results. |
| 17 | Low | Documentation | Finding 17 | `Responsibility` could be renamed `Purpose`. | Reject | This column name is consistent with prior Sprint documents and clearly describes technical ownership. | Keep the project convention. |
| 18 | Low | Documentation | Finding 18 | Workflow macros appear unused. | Reject | They are mandatory workflow state recorded under the selected `sprint-workflow` skill and support review/commit path resolution. | Keep them. |
| 19 | Info | Documentation | Finding 19 | Delivery conclusion lacks measurable local criteria. | Accept | Workflow state should name the exact local artifacts and checks. | Replace the placeholder with a local delivery checklist and separate host-deferred register. |
| 20 | Info | Consistency | Finding 20 | Baseline Research Plan version is imprecise. | Accept | The approved source is v0.4.0; v0.4.x denotes future amendments. | Use v0.4.0 for the baseline and reserve v0.4.x for a measured amendment. |

## Needs Immediate Action

- Separate every local implementation item from every host-deferred evidence gate.
- Define module/schema/status boundaries and the full measured-resource contract.
- Make local static-test meaning and formal host acceptance meaning unambiguous.

## Can Be Deferred

- CMSSW compilation, `cmsRun`, hand-inspected truth/product/unit validation, host measurements, real TT/QCD file processing, formal E0 freeze, and AC-E0-001 remain deferred until an authorized qualified host exists.

## Final Status

Accept after the accepted and partial document changes are applied. Implementation may then begin with failing local contract tests; no local result may satisfy a host-deferred row.
