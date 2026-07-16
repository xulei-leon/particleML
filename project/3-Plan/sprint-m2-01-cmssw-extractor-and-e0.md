# Sprint M2-01 CMSSW Extractor and E0

**Milestone:** M2 - Data and Model Feasibility

**Goal:** Implement and qualify the CMSSW extractor, process the multi-file E0 pilot, and freeze the data/control/resource policies required for E0.5 and E1.

**Architecture:** CMSSW owns CMS decoding, truth matching, raw fields, and cutflow only. Modern Python conversion/audit consumes compact ROOT artifacts through the existing contract on separate cloud infrastructure.

**Tech Stack:** CMSSW 7.6.7, C++/Python configuration, ROOT, XRootD/EOS, qualified POSIX host, modern Python conversion on persistent cloud storage.

## 1. Sprint Goal

Pass AC-E0-001 with retained source/split manifests, compact ROOT, canonical HDF5, A-D views, audits, measured host performance, yield, and cost.

Core objectives:

- Qualify a CMS extraction host using measured TT/QCD access.
- Implement corrected-AK8 selection, packed-daughter decoding, leakage-safe labels, raw features, and structured cutflow.
- Run the E0 pilot and freeze mixture, cuts, controls, missingness, `n_max`, and budget decisions.

## 2. Prerequisites

- [Sprint M1-03](./sprint-m1-03-synthetic-cloud-data-pipeline.md).
- [FR-DATA-002](../1-Requirement/FR-DATA-002-cms-extraction.md), [FR-DATA-003](../1-Requirement/FR-DATA-003-leakage-safe-labels.md), and [FR-DATA-010](../1-Requirement/FR-DATA-010-data-audit.md).
- Frozen manifest/split and working persistent artifact storage.

## 3. Scope

Included:

- CMSSW analyzer, build file, extraction configuration, product checks, truth traversal, cutflow, and raw constituent output.
- One-TT/one-QCD host qualification followed by 5-10 TT files and multiple files from every candidate QCD record.
- Cloud conversion to canonical/A-D artifacts and full AC-E0-001 audit.
- Research Plan v0.4.x amendment if measured yield cannot support provisional `10^5` per class.

Not included:

- OmniLearned checkpoint/index/model execution.
- Full-corpus download or scan from the local workstation.
- Provider selection based only on reputation.

## 4. File Structure and Responsibilities

| File / Directory | Operation | Responsibility |
|---|---|---|
| `cmssw/ParticleMLExtractor/BuildFile.xml` | Create | CMSSW dependencies/build |
| `cmssw/ParticleMLExtractor/plugins/ParticleMLExtractor.cc` | Create | CMS decoding, selection, truth, raw output |
| `cmssw/ParticleMLExtractor/python/extract_cfg.py` | Create | Pinned extraction job configuration |
| `cmssw/ParticleMLExtractor/test/` | Create | Qualified-host fixtures and product checks |
| `configs/e0/` | Create | Host qualification and pilot policies |
| `src/particleml/dataset.py` | Modify | Real-output compatibility/audit fixes only |
| `tests/test_audit.py` | Modify | E0 gate aggregation fixtures |

## 5. Work Scope

### 5.1 Work Package: Extraction Host Qualification

- [ ] Select candidate POSIX hosts with direct EOS/XRootD access.
- [ ] Process one TT and one QCD file and record products, throughput, CPU/event, wall time, failure rate, and compact size.
- [ ] Project E0/storage cost with 25% reserve and promote only a passing host.

### 5.2 Work Package: CMSSW Extractor and Truth Tests

- [ ] Write failing product, daughter, truth-containment, ambiguity, D-unit, PV, and cutflow fixtures.
- [ ] Implement corrected-AK8 selection and packed-daughter decoding.
- [ ] Ensure rejected TT jets never become background and audit-only truth does not enter model arrays.
- [ ] Retain container digest, commit, manifest hash, and structured file failures.

### 5.3 Work Package: E0 Pilot and Freeze Decision

- [ ] Process the required TT/QCD multi-file sample without silent file omission.
- [ ] Produce compact ROOT, canonical HDF5, split/subset manifest, A-D views, and all completion records.
- [ ] Run the full data/yield/leakage/cost audit, including shuffled-label and charged no-track checks.
- [ ] Freeze or formally amend QCD mixture, cuts, pT/eta control, pileup, missing-track, `n_max`, yield, and budget.

## 6. TDD and Test Plan

- [ ] Run CMSSW tests only on the qualified extraction host.
- [ ] Reuse M2 contract tests against real compact output in the modern cloud environment.
- [ ] Cover missing products, invalid truth, ambiguous matches, unit/finiteness failures, overlap, track-state threshold, and cost/yield gates.

## 7. Verification Commands

Qualified extraction host:

```text
cmsRun cmssw/ParticleMLExtractor/python/extract_cfg.py
```

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

## 8. Risks and Recovery

- Risk: slow XRootD route makes E0 infeasible. Control: measured host qualification before multi-file work.
- Risk: missing CMS products or ambiguous truth invalidates labels. Control: fail closed and retain per-file cutflow/failure records.
- Risk: yield is below `10^5` per class. Control: stop and approve Research Plan v0.4.x before E0.5.
- Recovery: quarantine affected files; rebuild derived canonical/views from retained valid compact artifacts after an approved fix.

## 9. Deliverables

- [ ] Qualified-host report and measured cost projection.
- [ ] Pinned CMSSW extractor and integration evidence.
- [ ] E0 manifest, compact ROOT, canonical, A-D views, and hashes.
- [ ] Completed AC-E0-001 audit and frozen policy decisions.

## 10. Completion Criteria

- [ ] Every AC-E0-001 item passes with retained cloud evidence.
- [ ] Charged no-track rate is at or below 1%, or E1 remains blocked pending approved review.
- [ ] Any `n_max` change has an approved versioned research-plan amendment.

## 11. Delivery Conclusion

Pending implementation, review confirmation, qualified-host execution, and E0 gate verification.
