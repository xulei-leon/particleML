# Sprint M1-03 Synthetic Cloud Data Pipeline — Document Review

**Review type:** Document review
**Reviewer:** OpenCode agent (Kimi K2.7 code path)
**Date:** 2026-07-17
**Target document:** `project/3-Plan/sprint-m1-03-synthetic-cloud-data-pipeline.md`
**Reviewed against:**
- FR-DATA-004, FR-DATA-005, FR-DATA-007, FR-DATA-008, FR-DATA-009
- `docs/software/specification.md` (v1.1.0)
- `docs/software/architecture.md` (v1.1.0)
- Current M1-02 implementation boundary (commit `87a7c1a`)

---

## 1. Summary

The sprint document defines a coherent scope for the synthetic cloud data pipeline — conversion, fitted state, subsets, A-D views, and audit primitives. It correctly identifies the five mapped FRs as prerequisites, respects the M1-02 boundary by not re-implementing manifest/split/artifact services, and correctly excludes real CMS extraction, OmniLearned execution, and JetClass production.

However, the document lacks concrete detail in several critical areas. Key precision gaps include missing explicit feature-order and layout references, omission of the ranking formula and scale-grid sizes, absent cross-module dependency wiring to M1-02 modules, and under-specification of audit primitive scope and coverage boundaries. These findings are detailed below.

---

## 2. Findings Table

| Severity | Type | Location | Issue | Evidence | Recommendation |
|---|---|---|---|---|---|
| **High** | Correctness | §4, File Structure table | `metrics.py` scope is defined as "Leakage/shuffled-label audit support only," but FR-DATA-009 requires forbidden-input checks, pT/eta control, pileup diagnostics, missingness, and shuffled-label primitives (WP 5.3). The `metrics.py` description does not account for confound probes, tensor-field schema checks, or mixture-count verification. | FR-DATA-009 high-level requirements list: "Audit pileup diagnostics," "Exclude record ID, generator bin, truth, pileup variables, and audit weights from primary inputs"; Sprint §4 and §5.3. | Expand the `metrics.py` responsibility in §4 to explicitly list confound-audit and tensor-field exclusion checks, or add a separate `audit.py` module responsibility. |
| **High** | Correctness | §5.2, WP: Fitted State and Fixed Subsets | The QCD round-robin ranking algorithm from FR-DATA-008 and spec §4.2 is not described in the sprint. The exact formula `SHA256(str(seed) + "\0" + jet_id)` for signal ranking and the round-robin iteration order across sorted record IDs are absent. | FR-DATA-008: "Rank signal identities by SHA256(str(seed) + '\\0' + jet_id) and then jet_id. Rank QCD per active record and select round-robin across sorted record IDs." | Add the deterministic ranking formulas to §5.2 so implementers and reviewers can verify correctness without cross-referencing the FR mid-implementation. |
| **High** | Missing Evidence | §5.3, WP: Native-PID A-D Views and Audit | OmniLearned CLI argv generation for each view configuration is not scoped or tested. Spec §4.3 and FR-DATA-005 require exact flags (`--use-pid --pid_idx 4`, `--use-add --num-add N`) per configuration. No work package or test plan item addresses flag correctness. | FR-DATA-005 acceptance criteria: "The generated OmniLearned argv uses the exact PID/additional-feature flags for each configuration." Sprint §5.3 omits any argv-construction task. | Add an explicit task to WP 5.3: "Generate and snapshot the exact OmniLearned argv per configuration" and include an argv-flag test in the test plan (§6). |
| **Medium** | Consistency | §5.1 vs. §4 | WP 5.1 says "Generate compact fixtures deterministically without relying on local source data," but §4's file structure does not list a fixture-generation module or script. Only `tests/fixtures/` is listed as "Create" with the vague description "Deterministic compact ROOT policies/expected records." | Sprint §4 and §5.1. The fixture creation mechanism is under-specified — will it be inline in test files, a pytest fixture, or a generation script? | Add a fixture-generation responsibility to §4 (e.g., `tests/fixtures/generate_compact_root.py` or a conftest-level factory) and specify the compact ROOT schema. |
| **Medium** | Consistency | §7, Verification Commands | The verification commands include `python scripts/validate_software_docs.py`, `pnpm test`, and `pnpm docs:build` — these are documentation-suite commands irrelevant to the data-pipeline tests. They inflate the verification surface without adding pipeline coverage. | Sprint §7, lines 104-108. These appear to be cargo-culted from M1-02's verification block. | Either remove documentation-pipeline commands from §7 and retain only `pytest`, `ruff check`, and `mypy`, or annotate them as "documentation-suite only" with a note that they are not data-pipeline coverage. |
| **Medium** | Completeness | §5.1, WP: Canonical Conversion | The sprint references "PID sign, track-state, mask, sorting, truncation" tests but never states the canonical feature order or references the specific layout from spec §3.3. The implementer must discover the 9-field continuous tensor, the pid_type/mask/track_state datasets, and the audit trees from external documents. | Spec §3.3 defines `/particles/continuous` as `[N,150,9] float32` with ordered field list. Sprint §5.1 mentions "layout" but never enumerates it. | Add a brief layout table or explicit reference to spec §3.3 in §5.1 so the test plan and implementation share a single design source. |
| **Medium** | Completeness | §5.1, §5.2 | Positive particle pT/energy thresholds are mentioned indirectly ("no scientific defaults") but the sprint never states that `min_particle_pt_gev` and `min_particle_energy_gev` are required policy fields whose absence blocks conversion. | Spec §3.2: "The E0 preprocessing policy must provide positive min_particle_pt_gev and min_particle_energy_gev. Their absence blocks conversion." Sprint §5.1-§5.2 mention "policy" but not these required fields. | Add to §5.1: "Require positive `min_particle_pt_gev` and `min_particle_energy_gev` from the preprocessing policy; block conversion if absent." |
| **Medium** | Risk | §8, Risk: native PID field order drifts from OmniLearned flags | The risk correctly identifies field-order drift but the control ("snapshot view metadata and expected M4 command inputs") refers to M4, which is far downstream. A mismatch caught at M4 would require re-extraction and re-processing of all upstream artifacts. | Sprint §8, line 115. | Strengthen the control: add a PID-field-order contract test in M1-03 that snapshots the exact view column indices against spec §4.3 and integrate argv-flag verification into view completion validation. |
| **Medium** | Completeness | §5.3, §6 | The "forbidden-input" and "shuffled-label" audit primitives are named but never defined. The sprint does not list which fields are forbidden, how shuffle-label probes are constructed, or what failure thresholds apply. | Sprint §5.3: "Implement forbidden-input, pT/eta control, pileup diagnostic, missingness, and shuffled-label audit primitives." No threshold, methodology, or field enumeration. Spec §3.2-§3.3 list audit-only fields (record_id, jet_pt, jet_eta, pv_z, n_vertices) but the sprint does not enumerate them. | In §5.3, list the forbidden-input fields by name (record_id, run, lumi, event, jet_pt, jet_eta, pv_z, n_vertices, generator truth) and define a minimum shuffled-label methodology (e.g., "binary label permutation preserving class balance; the resulting AUC must not exceed 0.5 + epsilon"). |
| **Medium** | Requirement | §5.2 and §10 | FR-DATA-008 specifies the scale grid as "10^3, 10^4, and provisional 10^5 jets per class, or an amended E0 grid." The sprint mentions "nested class-balanced subsets" but never states the actual scale sizes. | FR-DATA-008: "The system shall materialize deterministic subsets for 10^3, 10^4, and provisional 10^5 jets per class." Sprint: no explicit scale sizes. | Add the specific scale grid to §5.2 so subset tests can verify prefix-compatibility at known sizes. |
| **Low** | Clarity | §5.2 and §10 | The `INSUFFICIENT_CLASS_YIELD` error family is not named in the sprint, though it is required by FR-DATA-008. The sprint says "fail on insufficient class yield" (line 84) without the stable error code. | FR-DATA-008: "Raise INSUFFICIENT_CLASS_YIELD when either class cannot satisfy a requested scale." Sprint line 84: "fail on insufficient class yield." | Replace the prose with the stable error code: "fail with INSUFFICIENT_CLASS_YIELD when..." |
| **Low** | Clarity | §5.3 | "Add stale-state/view hash invalidation tests" is listed as the last task in WP 5.3. It is unclear whether "stale-state" refers to preprocessing.json hash changes or canonical dataset hash changes, and how invalidation interacts with the artifact lifecycle from `artifacts.py`. | Sprint §5.3, line 91; M1-02 `artifacts.py` implements completion-marker based resume; hash-change detection should be clarified. | Specify: "When the view's recorded preprocessing or split-manifest hash differs from the resolved artifact hash, reject view consumption with VIEW_STALE_HASH; test that stale-state invalidation integrates with the artifacts.py completion-marker contract." |
| **Low** | Clarity | §1, §11 | "Prove on deterministic cloud-generated fixtures" appears in §1, but §11 says "Pending document review confirmation..." — the word "prove" implies a stronger claim than the sprint's actual deliverables (local diagnostics only). The intro wording may mislead a reader about the evidence standard. | Sprint §1 vs. §11 and line 24: "Local execution is diagnostic-only." | Soften §1: "Demonstrate (diagnostic only, no formal evidence) that one canonical full-D dataset produces identity-equivalent A-D views..." |
| **Low** | Requirement | §4, File Structure | `src/particleml/metrics.py` is listed as "Create minimal" but the traceability matrix (FR-DATA-010) and FR-DATA-009 acceptance criteria expect shuffled-label probe pass/fail status retention. The sprint does not specify whether `metrics.py` stores audit outcomes or just computes them. | FR-DATA-009 acceptance criteria: "E0 confound and shuffled-label probes are retained with pass/fail status." Sprint §4: "Leakage/shuffled-label audit support only." | Clarify whether `metrics.py` or a separate audit module owns the persistent audit-report artifact required by FR-DATA-010. |
| **Low** | Risk | §8, Risk: HDF5 byte hashes vary due to library metadata | The control "define semantic/content hashing rules and pin h5py" is reasonable, but the sprint does not reference which artifact or specification section defines these rules. M1-03 is the first sprint that produces HDF5 artifacts, so the hashing rules should be defined here. | Sprint §8, line 114. No existing h5py hashing convention exists in the codebase. | Add a brief note in §5.1 or §8 referencing where semantic HDF5 hashing rules will be recorded (e.g., "define content hash over dataset arrays, not file metadata, as a pinned attribute in the canonical HDF5 root group"). |
| **Low** | Documentation | §2, Prerequisites | The sprint lists M1-02 completion commit `87a7c1a` but does not list the M1-02 modules that M1-03 depends on (`manifest.py`, `contracts.py`, `artifacts.py`, `cli.py`). An implementer must infer the dependency surface from external documents. | Sprint §2, line 38. M1-02 introduced `src/particleml/manifest.py`, `src/particleml/contracts.py`, `src/particleml/artifacts.py`, and extended `cli.py`. | Add under §2: "M1-02 modules available: `manifest.py` (split assignment, source manifest, stable jet IDs), `contracts.py` (enums, dataclasses, schema validators), `artifacts.py` (temporary write, hash, publish, COMPLETED.json), and CLI wiring in `cli.py`." |
| **Info** | Consistency | §7, Verification Commands vs. §6 | §7 lists `pytest -q tests/test_dataset.py tests/test_views.py tests/test_audit.py` as a targeted command, but §6 (TDD and Test Plan) includes "forbidden fields" coverage and §5.3 mentions "forbidden-input" primitives, which would logically live in `tests/test_audit.py`. The audit test file is included in §7's targeted command but its full scope (beyond leakage/shuffled-label) is not enumerated in §6. | Sprint §6 vs. §7, line 100. | In §6, list the minimum audit test coverage items (forbidden-input field enumeration, shuffled-label AUC bound, pileup diagnostic threshold, pT/eta control identity audit) so the verification command's scope is explicit. |
| **Info** | Clarity | §5.2 | "Implement required preprocessing policy with no scientific defaults" is tautological — "required" and "no defaults" convey the same constraint. It does not specify which fields are required or how the policy is loaded. | Sprint §5.2, line 82. Spec §4.1 lists the required policy fields. | Rephrase: "Implement preprocessing policy ingestion that reads and validates required fields (location/scale, particle cuts, PID vocabulary, track policy, D-field transform) from a versioned JSON policy; fail on missing, unknown, or ambiguous fields." |
| **Info** | Risk | §8, Risk: synthetic fixtures conceal real CMSSW edge cases | This risk correctly notes the limitation and defers E0, but the sprint does not reference an approved checklist or minimum fixture-coverage matrix that would define what constitutes adequate fixture diversity for a diagnostic sprint. | Sprint §8, line 116. No fixture coverage criteria are stated. | Add a minimum fixture coverage note: "Synthetic fixtures must exercise at least: empty jet, padded-to-max jet, non-finite value, duplicate identity, PID-unknown species, charge-zero candidate, and missing-track particle to ensure the pipeline fails-closed on each." |
| **Info** | Completeness | §4, File Structure | `tests/test_audit.py` responsibility is "Audit thresholds and leakage probes." The sprint does not define what thresholds apply, what a leakage probe constitutes, or how audit pass/fail is determined. | Sprint §4, line 68. No audit threshold policy is defined. | Reference the audit policy structure from spec §3.2 (charged-track fraction at most 1%, shuffled-label AUC bound, etc.) and state that audit thresholds are versioned configuration, not code constants. |
| **Info** | Completeness | §4 | `tests/fixtures/` creation lists "Deterministic compact ROOT policies/expected records" but does not specify whether these are stored as committed binary ROOT files, Python-generated ROOT via uproot, or pure JSON/NumPy mocks. | Sprint §4, line 65. The tech stack includes `uproot` and `h5py`. | Clarify the fixture format and state whether committed fixtures include binary .root files or whether they are generated on-the-fly by the test suite. |

---

## 3. Positive Findings

1. **Scope discipline** (lines 44-55): The sprint correctly excludes real CMS extraction, OmniLearned execution, and JetClass production. The included/excluded boundary is clear and consistent with the M1 milestone definition.

2. **FR mapping** (lines 38-40): All five required FRs are listed as prerequisites with correct file paths. The FR-to-work-package mapping is reasonable: FR-DATA-004 → WP 5.1, FR-DATA-007/008 → WP 5.2, FR-DATA-005/009 → WP 5.3.

3. **No-defaults stance** (line 82): The sprint correctly reiterates "no scientific defaults," which aligns with spec §3.2 and FR-DATA-007's constraint that policy values cannot come from environment variables or library defaults.

4. **Completion criteria** (lines 126-130): The criteria for A-D identity equivalence, no one-hot PID columns, and deferred E0 status are concrete, verifiable, and consistent with FR-DATA-005.

5. **Artifact lifecycle alignment** (implicit): The sprint notes that "canonical fixtures and views are content-addressed derived artifacts and can be rebuilt" (line 117), which aligns with ADR-010 and the artifact lifecycle from M1-02's `artifacts.py`.

6. **Separate subset/model seeds** (implicit in §5.2): The sprint's nested-subset design implicitly enforces the subset-seed ≠ model-seed constraint from FR-DATA-008, which is critical for RQ2 integrity.

---

## 4. Cross-Reference Matrix

| FR | Sprint coverage | Gaps |
|---|---|---|
| FR-DATA-004 | WP 5.1 covers conversion, layout, sorting, truncation, provenance | Missing: canonical feature order, gzip level 4 / jet-major chunks, PID encoding table, required min_pT/min_energy policy fields |
| FR-DATA-005 | WP 5.3 covers A-D views, no one-hot PID, identity equality | Missing: explicit OmniLearned argv per config, A/B PID omission confirmation, full-dimensional neutralization fallback gate |
| FR-DATA-007 | WP 5.2 covers preprocessing policy, train-only fit, canonical-JSON hash | Missing: preprocessing.json content enumeration, canonical JSON serialization rules, checkpoint-native transform documentation |
| FR-DATA-008 | WP 5.2 covers nested subsets, signal ranking, QCD round-robin, prefix compatibility | Missing: explicit scale grid (10^3, 10^4, 10^5), ranking formula, INSUFFICIENT_CLASS_YIELD error code, seed ≠ model_seed constraint |
| FR-DATA-009 | WP 5.3 covers forbidden-input, pT/eta control, pileup diagnostic, shuffled-label | Missing: forbidden-field enumeration, control-fit identity audit, shuffled-label threshold, pass/fail retention in audit report |

---

## 5. Recommendations

1. **Add a concrete layout/fields appendix or inline table** to §5.1 that mirrors spec §3.3, so the sprint is self-contained for implementers who may not have the specification at hand during coding.

2. **Specify the subset ranking algorithm** (signal: `SHA256(str(seed) + "\0" + jet_id)` → integer → sort; QCD: per-record queue → round-robin by ascending record_id) in §5.2 to ensure the implementation matches the FR byte-for-byte.

3. **Add explicit OmniLearned argv-generation tasks** to WP 5.3 so the A-D configuration → external flag mapping is tested within the sprint, not deferred to M2-02.

4. **Remove or annotate documentation-pipeline verification commands** from §7 to avoid confusion about what constitutes data-pipeline test coverage.

5. **Enumerate forbidden audit-input fields** by name in §5.3 and define a minimum shuffled-label bound so the audit test can verify pass/fail deterministically.

6. **Add M1-02 module dependency notes** to §2 so that `dataset.py` authors know exactly which public APIs are available from `manifest.py`, `contracts.py`, and `artifacts.py`.

7. **Strengthen the synthetic-fixture coverage description** in §8 with a minimum edge-case checklist to ensure the diagnostic pipeline exercises meaningful failure modes.

---

## 6. Verdict

The sprint document correctly scopes the data pipeline work, maps all required FRs, and respects the M1-02 boundary. It is **conditionally approvable** — the findings above are documentation precision and completeness issues, not architectural errors. The most actionable gaps are: (a) the ranking-algorithm description for subsets, (b) the OmniLearned argv-generation scope, and (c) the forbidden-field enumeration for audit primitives. All three should be addressed before implementation begins to avoid ambiguity and implementation drift.

*End of review.*
