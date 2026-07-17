# Sprint M2-01 CMSSW Extractor and E0

**Milestone:** M2 - Data and Model Feasibility

**Goal:** Implement and qualify the CMSSW extractor, process the multi-file E0 pilot, and freeze the data/control/resource policies required for E0.5 and E1.

**Architecture:** CMSSW owns CMS decoding, truth matching, raw fields, and cutflow only. Modern Python conversion/audit consumes compact ROOT artifacts through the existing contract on separate cloud infrastructure.

**Tech Stack:** CMSSW 7.6.7, C++/Python configuration, ROOT, XRootD/EOS, qualified POSIX host, modern Python conversion on persistent cloud storage.

## Workflow Configuration and Evidence Boundary

- `FR_DIR`: `project/1-Requirement`
- `FR_BACKLOG_DIR`: `project/1-Requirement/backlog`
- `FR_DONE_DIR`: `project/1-Requirement/Done`
- `DESIGN_DIR`: `docs/software` and `docs/research`
- `SPRINT_DIR`: `project/3-Plan`
- `SPRINT_DONE_DIR`: `project/3-Plan/Done`
- `REVIEW_DIR`: `project/4-Reviews`
- `REVIEW_DONE_DIR`: `project/4-Reviews/Done`
- `WORKFLOW_STATE_PATH`: this Sprint document; no separate state file was requested.
- `VERIFICATION_COMMANDS`: Section 7, sourced from the approved development plan and mapped FR minimum checks.

The user prohibited GitHub pushes and instructed the sequential development workflow to continue. This Windows workspace has no configured qualified POSIX extraction host or CMSSW 7.6.7 runtime. Therefore this Sprint iteration delivers reviewed extractor/configuration code, deterministic E0 audit aggregation, schemas, and local contract/static diagnostics. It must not invent host measurements, process purported real CMS files, freeze E0 discovery decisions, pass AC-E0-001, or advance any requirement to `implemented` or `verified`. Qualified-host execution and formal E0 evidence remain mandatory deferred gates.

## 1. Sprint Goal

Implement the complete reviewable software boundary needed to run AC-E0-001, while retaining the qualified-host execution and evidence as an explicit external gate.

Core objectives:

- Define the fail-closed host-qualification and measurement contract without claiming unmeasured results.
- Implement corrected-AK8 selection, packed-daughter decoding, leakage-safe labels, raw features, and structured cutflow.
- Aggregate E0 evidence deterministically and freeze decisions only when every required real measurement is present and passing.

## 2. Prerequisites

- [Sprint M1-03](./sprint-m1-03-synthetic-cloud-data-pipeline.md), completed through local commit `47927a2`; cloud evidence remains deferred.
- [FR-DATA-002](../1-Requirement/FR-DATA-002-cms-extraction.md), [FR-DATA-003](../1-Requirement/FR-DATA-003-leakage-safe-labels.md), and [FR-DATA-010](../1-Requirement/FR-DATA-010-data-audit.md).
- Frozen manifest/split and working persistent artifact storage.

## 3. Scope and Deferred Register

This no-host iteration includes:

- CMSSW analyzer, build file, extraction configuration, product checks, truth traversal, cutflow, and raw constituent output.
- Versioned host-qualification, extraction-job, and E0-audit policies/contracts with stable `EXTRACT_*` and gate failure behavior.
- Local source/static contract tests for the legacy CMSSW boundary and deterministic Python E0 aggregation fixtures.
- The complete resource-measurement contract: source bytes, events, CPU/event, wall time, throughput, failures, compact/canonical/view bytes, projected E0/E1/E2 costs, and the mandatory 25% reserve.
- A Research Plan v0.4.x amendment template and trigger contract; no amendment is published without measured E0 yield evidence.

`[HOST_DEFERRED]` mandatory formal work:

- Qualification using exactly one TT and one QCD file with measured access and extractor performance.
- E0 pilot processing of at least 5-10 TT files and multiple files from every candidate QCD record.
- Qualified-host CMSSW compilation, `cmsRun`, hand-inspected product/daughter/truth/unit/PV validation, compact ROOT production, cloud conversion, artifact completion records, and full AC-E0-001 evaluation.
- Measured mixture, cuts, pT/eta control, pileup, missing-track, `n_max`, yield, budget, host-promotion, or Research Plan amendment decisions.

Other work not included:

- OmniLearned checkpoint/index/model execution.
- Full-corpus download or scan from the local workstation.
- Provider selection based only on reputation.
- Any fabricated host qualification, CMSSW execution result, CMS yield, cost, or policy-freeze decision. These outputs require the deferred qualified-host run.

## 4. File Structure and Responsibilities

At Sprint start, the `cmssw/ParticleMLExtractor/`, `configs/e0/`, `src/particleml/e0.py`, and E0 schema targets do not exist. `audit.py` and its M1-03 tests exist and remain the per-canonical-artifact layer.

| File / Directory | Operation | Status at Start | Responsibility |
|---|---|---|---|
| `cmssw/ParticleMLExtractor/BuildFile.xml` | Create | Not created | CMSSW dependencies/build |
| `cmssw/ParticleMLExtractor/plugins/ParticleMLExtractor.cc` | Create | Not created | CMS decoding, selection, truth, raw output |
| `cmssw/ParticleMLExtractor/python/extract_cfg.py` | Create | Not created | Pinned extraction job configuration |
| `cmssw/ParticleMLExtractor/test/` | Create | Not created | Qualified-host fixture source and product checks |
| `configs/e0/` | Create | Not created | Unresolved host qualification and pilot policies |
| `src/particleml/dataset.py` | Modify | Exists | Real-output compatibility/audit fixes only |
| `src/particleml/audit.py` | Reuse | Exists | Per-canonical-artifact leakage, mixture, missingness, and numerical probes |
| `src/particleml/e0.py` | Create | Not created | Cross-artifact AC-E0 aggregation, resource/yield math, freeze decisions, and external-evidence blocking |
| `schemas/e0-audit.schema.json` | Create | Not created | Serialized cross-artifact E0 audit result contract |
| `docs/software/specification.md` | Modify | Exists | Register the E0 audit command/status/schema contract |
| `docs/software/traceability-matrix.md` | Modify | Exists | Map FR-DATA-010 and AC-E0-001 to the new contract/tests |
| `tests/test_audit.py` | Modify | Exists | E0 gate aggregation fixtures |
| `tests/test_cmssw_contract.py` | Create | Not created | Local static/source contract checks; never a substitute for `cmsRun` |

## 5. Work Scope

### 5.1 Work Package: Extraction Host Qualification

- [x] `[LOCAL]` Define a strict unresolved host policy and evidence schema without selecting a provider.
- [x] `[LOCAL]` Implement deterministic throughput, CPU/event, failure-rate, storage, and E0/E1/E2 cost projections with a 25% reserve.
- [x] `[LOCAL]` Reject missing/non-finite/negative measurements and prohibit host promotion from incomplete evidence.
- [ ] `[HOST_DEFERRED]` Process exactly one TT and one QCD file on each candidate and retain products, throughput, CPU/event, wall time, failure rate, and compact size.
- [ ] `[HOST_DEFERRED]` Promote only a measured passing POSIX host with direct EOS/XRootD access.

In this no-host iteration, implement and test the required measurement schema, 25% reserve calculation, missing-evidence rejection, and promotion decision. Leave all measured fields unresolved in the committed configuration and do not select a host.

### 5.2a Work Package: Local CMSSW Source Boundary

- [x] `[LOCAL]` Write failing source-contract tests for required files, non-empty C++, well-formed BuildFile XML, Python configuration syntax, frozen release/global-tag/input tags, provenance fields, stable `EXTRACT_*` failure codes, and forbidden model-field separation.
- [x] `[LOCAL]` Author corrected-AK8 selection, packed-daughter decoding, last-copy fully hadronic truth traversal, daughter containment, ambiguity rejection, QCD-only background, PV/D-field handling, and structured cutflow/failures.
- [x] `[LOCAL]` Retain container digest, commit, manifest hash, exact PFN/split identity, original daughter index, and job timing placeholders in the source contract.

### 5.2b Work Package: Host-Deferred CMSSW Validation

- [ ] `[HOST_DEFERRED]` Compile the exact committed source in CMSSW 7.6.7.
- [ ] `[HOST_DEFERRED]` Run product, daughter, truth-containment, ambiguity, D-unit, PV, finiteness, and cutflow fixtures on hand-inspected MiniAODSIM events.
- [ ] `[HOST_DEFERRED]` Confirm rejected TT jets never become background and audit-only truth never enters model arrays.

Local source tests do not validate CMSSW types, product availability, decoded units, PV semantics, or physics behavior.

### 5.3 Work Package: E0 Aggregation and Deferred Pilot

- [x] `[LOCAL]` Define the E0 schema/status enumeration: `passed`, `failed`, and `blocked_external_evidence`.
- [x] `[LOCAL]` Aggregate mandatory evidence identities, product/label/field checks, missingness, counts, overlap, mixture, controls, shuffled-label, storage, throughput, yield, cost, and freeze decisions without scientific defaults.
- [x] `[LOCAL]` Report `blocked_external_evidence` when any qualified-host artifact or measurement is absent and retain every missing evidence key.
- [ ] `[HOST_DEFERRED]` Process the 5-10 TT and candidate-QCD multi-file sample without silent omission.
- [ ] `[HOST_DEFERRED]` Produce compact ROOT, canonical HDF5, split/subset manifest, A-D views, audit, and all completion records.
- [ ] `[HOST_DEFERRED]` Freeze or formally amend mixture, cuts, controls, pileup, missing-track, `n_max`, yield, and budget only from retained real measurements.

The aggregator must report `blocked_external_evidence` when any mandatory qualified-host artifact or measurement is absent. The committed policy keeps discovery values unresolved; it cannot silently convert local fixture results into a freeze decision.

## 6. TDD and Test Plan

- [ ] `[HOST_DEFERRED]` Run CMSSW tests only on the qualified extraction host.
- [ ] `[HOST_DEFERRED]` Reuse M2 contract tests against real compact output in the modern cloud environment.
- [x] `[LOCAL]` Cover the static `EXTRACT_*` failure boundary plus deterministic overlap, track-state, cost, yield, invalid-measurement, and external-evidence gates; runtime physics behavior remains host-deferred.
- [x] `[LOCAL]` Prove that missing external evidence remains visible and blocks AC-E0-001 rather than being replaced by defaults.

## 7. Verification Commands

Qualified extraction host:

```text
cmsRun cmssw/ParticleMLExtractor/python/extract_cfg.py
```

This command is deferred in the current environment. Its absence is a retained external gate, not a local verification failure and not permission to emulate CMSSW output as formal evidence.

GitHub Actions for reusable Python/contracts:

```text
ruff check
mypy src/particleml
pytest
python scripts/validate_software_docs.py
pnpm test
pnpm docs:build
```

Formal E0 acceptance additionally requires retained qualified-host and cloud artifact hashes, logs, and `COMPLETED.json` records.

Local code-delivery acceptance requires targeted E0/CMSSW contract tests plus every reusable Python/documentation command above. Passing these checks permits the local Sprint workflow commit only; it does not pass AC-E0-001.

### Local Diagnostic Results (2026-07-17)

- Targeted CMSSW/E0/audit suite: `18 passed`.
- Full Python suite: `113 passed`.
- Ruff and strict mypy: passed for 10 source modules.
- Software documentation validation: passed for 4 documents, 4 schemas, 39 traced requirements, and 8 link-bearing files.
- Python sdist and wheel builds: passed.
- Node tests: `3 passed`.
- VitePress documentation build: passed.
- Qualified-host CMSSW execution and formal AC-E0-001 evidence: not run and still blocked.

| Command | Current Environment | Required Outcome |
|---|---|---|
| `pytest -q tests/test_cmssw_contract.py tests/test_audit.py` | Local Windows | Pass; static/source and deterministic aggregation fixtures only |
| `ruff check` | Local Windows | Pass, including all new Python/tests |
| `mypy src/particleml` | Local Windows | Pass, including `e0.py` through recursive package checking |
| `pytest` | Local Windows | Pass; host tests are not embedded in this suite |
| software-doc validator, `pnpm test`, `pnpm docs:build` | Local Windows | Pass as repository consistency checks |
| `cmsRun .../extract_cfg.py` | Qualified POSIX CMSSW host | `[HOST_DEFERRED]`; compile/runtime/product/truth/unit evidence required before AC-E0-001 |

## 8. Risks and Recovery

- Risk: slow XRootD route makes E0 infeasible. Control: measured host qualification before multi-file work.
- Risk: missing CMS products or ambiguous truth invalidates labels. Control: fail closed and retain per-file cutflow/failure records.
- Risk: yield is below `10^5` per class. Control: stop and approve Research Plan v0.4.x before E0.5.
- Risk: CMSSW source is authored without local compilation or runtime validation. Control: bind static checks to specification §3.1, require code review, and prohibit host promotion until the exact commit passes qualified-host compile and hand-inspected event tests.
- Recovery: quarantine affected files; rebuild derived canonical/views from retained valid compact artifacts after an approved fix.

## 9. Deliverables

- [ ] Qualified-host report and measured cost projection.
- [x] Pinned CMSSW extractor source, configuration, structured job wrapper, and local static-contract evidence; qualified-host integration evidence remains deferred.
- [ ] E0 manifest, compact ROOT, canonical, A-D views, and hashes.
- [ ] Completed AC-E0-001 audit and frozen policy decisions.

## 10. Completion Criteria

- [x] Extractor, configuration, audit schema, and E0 aggregation code pass all local reusable diagnostics.
- [x] Missing qualified-host evidence deterministically produces `blocked_external_evidence`; AC-E0-001 and downstream E0.5/E1 remain blocked.
- [x] No charged no-track result, `n_max` change, host promotion, cost, yield, or policy freeze is claimed without retained real evidence and any required research-plan amendment.
- [x] The deferred qualified-host command, required file coverage, artifact identities, and remaining formal acceptance steps are recorded for later authorized execution.

## 11. Delivery Conclusion

Local extractor/E0 software delivery and diagnostics are complete. Qualified-host compilation, one-TT/one-QCD qualification, the 5-10 TT plus candidate-QCD pilot, artifact hashes, policy freezes, and formal E0 verification remain `[HOST_DEFERRED]` and blocking for AC-E0-001, E0.5, and E1.
