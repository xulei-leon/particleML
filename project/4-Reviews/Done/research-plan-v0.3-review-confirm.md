# Research Plan v0.3 Review Confirm

**Reviewed Inputs**

- `docs/research/plans/research-plan-v0.3.md`
- `docs/4-Reviews/research-plan-v0.3-review-by-deepseek-v4-pro.md`
- `docs/4-Reviews/research-plan-v0.3-review-by-ark-code-latest.md`

**Review Date**

- 2026-07-01

## Overall Conclusion

The reviews are generally sound. Both reviewers agree that the v0.3 research direction is scientifically defensible and well matched to the project goal: an undergraduate computational physics project that can support a first-author thesis or paper and a graduate-school research narrative.

The target plan should not be accepted as execution-ready yet. The blocking issues are narrow: name the checkpoint, prove adapter loading before real pilots, define Config D candidates and leakage checks, and add concrete data/compute constraints. These are specification fixes, not a redesign.

Several suggestions are useful but should be kept small. Do not expand the plan into a broader benchmark, a full Bayesian-statistics side project, or extra large-data saturation runs unless the core E0-E2 path is already working.

## Decision Table

| No. | Severity | Type | Review Source | Original Comment Summary | Decision | Evidence | Follow-up Plan / Rejection Reason |
|---|---|---|---|---|---|---|---|
| 1 | Critical | Requirement | DeepSeek C1 | The pretrained PET-style checkpoint is unnamed. | Accept | `research-plan-v0.3.md` says "pretrained PET-style or OmniLearn-style backbone" but gives no repo, release, hash, license, input shape, or pretraining source. | Update §7 and §10 to name one primary checkpoint, one backup if available, weight hash, license, input dimensionality, normalization, output head, and `pretraining_source`. |
| 2 | Critical | Requirement | DeepSeek C2 | Config D is a placeholder and cannot be audited before E0. | Accept | §5 defines D only as "allowed non-truth particle observables"; §8 requires a feature dictionary for A-D before E1. | Add a candidate Config D column list before E0, marked provisional, then freeze the final list after E0 with source columns and exclusion rationale. |
| 3 | High | Risk | DeepSeek H1 | The plan lacks concrete GPU-hour estimates. | Accept | §11 counts runs but has no runtime, memory, GB, dollar range, or cap. | Add a compute subsection: E1 measured runtime per size, projected E2 GPU-hours, expected storage footprint, and a hard budget gate. |
| 4 | High | Risk | DeepSeek H2 | Charge neutralization to 0 is ambiguous and the sensitivity check is undefined. | Partial | §6 correctly flags the ambiguity; the review's proposed weight-norm check is not sufficient evidence of semantic contamination. | Define a fallback-only sensitivity check: prefer adapter-swap for charge; if neutralization is used, compare adapter vs neutralized Config B on a small fixed setting where technically possible, otherwise report the ambiguity as a limitation. |
| 5 | High | Requirement | DeepSeek H3 | Baseline priority is inconsistent across RQ3, E3, and MVP. | Accept | §2 calls a lightweight baseline required for a "minimum strong version"; §14 says it is only needed for publication. | Reconcile wording: core thesis MVP is E0-E2; publication-strength MVP adds Deep Sets/PFN; E3 must be explicitly completed or explicitly deferred. |
| 6 | High | Feasibility | DeepSeek H4 | Timeline has no academic-calendar buffer. | Accept | §12 totals roughly 10-18 weeks without term-time hours, exams, holidays, or failed-run buffer. | Add calendar modes: summer full-time vs semester part-time, 20-30% contingency, and a cut gate if E1 is not complete by a stated date. |
| 7 | Medium | Consistency | DeepSeek M1 | "PET-style" and "OmniLearn-style" are mixed. | Accept | §7 says "PET-style or OmniLearn-style"; other sections use only "PET-style." | Pick one canonical model name after checkpoint selection and use it throughout. |
| 8 | Medium | Correctness | DeepSeek M2 | `n_full` may imply saturation at 10^5 jets/class. | Partial | §2 defines `n_full` as largest training size, not necessarily full-data saturation. The issue is real, but adding a larger training size is outside the cost-controlled core plan. | Rename to `n_max` or define `auc_gap_fraction(config, n)` with `n_max = 10^5`; state it is relative to the largest measured size, not saturated full-data performance. |
| 9 | Medium | Clarity | DeepSeek M3 | Split policy is not specified as official JetClass or custom. | Accept | §4 says "Fixed train/validation/test manifest" without naming the source split rule. | State official JetClass split if used; otherwise document the custom split rule and reason. |
| 10 | Medium | Consistency | DeepSeek M4 | "Load pretrained weights ... when compatible" weakens the pretrained claim. | Accept | §6 step 3 permits undefined compatibility gaps. | Replace with: load all non-input compatible layers, and log every skipped layer with reason in the run record. |
| 11 | Medium | Risk | DeepSeek M5 | Risk register mixes preferred adapter risk with fallback neutralization risk. | Accept | §13 lists inherited full-feature weights even though §6 preferred adapter reinitializes the input adapter. | Split the risk entries into adapter path and fallback neutralization path. |
| 12 | Low | Clarity | DeepSeek L1 | Test-time masking appendix could conflict with main results. | Accept | §6 allows post-hoc masking as appendix diagnostic but does not say how to handle conflicting rankings. | Add one sentence: if masking conflicts with fine-tune-without-X, report the conflict as diagnostic only and keep fine-tuned results primary. |
| 13 | Low | Clarity | DeepSeek L2 | Metric smoke test lacks pass criteria. | Partial | §8 says AUC and background rejection must compute from predictions. The suggested published-baseline threshold may be too strong for a smoke test. | Add minimal pass criteria: random-score AUC near 0.5, no NaN/Inf metrics, and stable output schema; optional trivial baseline may be added if already cheap. |
| 14 | Low | Requirement | DeepSeek L3 | Run record lacks schema or validation rules. | Partial | §10 lists fields but not types or enums. A full JSON schema is useful but not required before the plan is accepted. | Add a compact run-record example or schema table with required fields and enums; defer formal JSON Schema until implementation. |
| 15 | Low | Documentation | DeepSeek L4 | E1 uses only one seed. | Partial | §8 E1 is primarily a pipeline/runtime pilot, not a statistical pilot. Extra seeds are useful but not required before E2. | Keep one-seed E1 as the minimum; optionally add a second seed at 10^3 if E1 runtime is cheap. |
| 16 | Low | Performance | DeepSeek L5 | Scope ladder does not enumerate 5-seed expansion runs. | Accept | §8 lists key reruns; §11 only gives a broad 45-55 run row. | Add an explicit expansion row listing which config/size pairs receive two extra seeds. |
| 17 | Info | Risk | DeepSeek I1 | Near-null result handling is good. | Accept | §13 frames near-null results as controlled negative evidence with uncertainty. | No document change required; preserve this wording. |
| 18 | Info | Documentation | DeepSeek I2 | One-sentence version is too long. | Accept | §16 is a long compound sentence and less useful for applications. | Replace with two shorter sentences. |
| 19 | Info | Documentation | DeepSeek I3 | Claim-boundary wording is strong. | Accept | §3 includes recommended wording and claims to avoid. | No document change required; preserve this section. |
| 20 | Critical | Requirement | Ark C1 | Checkpoint identity, hash, license, parameter count, corpus, and fallback are missing. | Accept | Same evidence as row 1, with additional missing metadata. | Fold this into the checkpoint specification update; include corpus overlap with JetClass and availability fallback. |
| 21 | Critical | Risk | Ark C2 | Adapter-swap feasibility is assumed. | Accept | §6 presents adapter-swap as a recipe; §13 only says fallback to neutralization if it fails. | Insert E0.5 before E1: load checkpoint, replace input adapter, verify non-input weight loading, finite A/B/C/D forward pass, gradient flow, and tiny loss decrease. |
| 22 | High | Risk | Ark H1 | Compute, memory, storage, provider, and price band are absent. | Accept | §11 has run counts only; §4 has no data acquisition or storage footprint. | Add data/storage and measured compute plan; avoid hard current price claims unless verified at purchase time. |
| 23 | High | Risk | Ark H2 | Config D lacks leakage acceptance testing. | Accept | §5 has inclusion rules, but §8 has no empirical leakage probe or review step. | Add E0 leakage audit for candidate D columns: source-column review, label-shuffle sanity check, and simple probe results logged in the feature dictionary. |
| 24 | High | Requirement | Ark H3 | Input adapter parametric form is unspecified. | Accept | §6 says "input projection or input adapter" but does not define linear layer, MLP, one-hot PID, or embeddings. | Freeze the minimal adapter form in E0, preferably a single linear projection over normalized continuous features plus one-hot categorical fields unless the selected checkpoint forces another form. |
| 25 | High | Correctness | Ark H4 | `normalized_gap_closed` lacks config indexing and uncertainty rule. | Accept | §2 formula has no config index, no denominator caveat, and no ratio CI method. | Define `auc_gap_fraction(config, n)` relative to `AUC(config, n_max)`, bootstrap the ratio from saved predictions, and fall back to raw AUC differences if the denominator is unstable. |
| 26 | High | Consistency | Ark H5 | PET vs OmniLearn naming changes interpretation. | Accept | Same evidence as row 7; Ark also notes the architecture family affects interpretation. | Resolve with the checkpoint decision and apply one term consistently. |
| 27 | High | Requirement | Ark H6 | JetClass acquisition and storage plan is missing. | Accept | §4 names JetClass but not file list, DOI/source, full vs top/QCD subset, local/cloud location, footprint, or dev slice. | Add a data acquisition/storage subsection with source, file subset, footprint estimate, dev slice, storage location, and file-set hash. |
| 28 | Medium | Risk | Ark M1 | Timeline lacks start date and hours/week assumption. | Accept | §12 gives durations only. | Add summer vs semester execution assumptions and a mid-project scope gate. |
| 29 | Medium | Risk | Ark M2 | "Key" 5-seed comparisons are undefined. | Partial | The issue is real; the review's arithmetic is not binding and may undercount the extra A runs needed for paired comparisons. | Define the key comparisons in the plan and calculate added runs explicitly after choosing whether A must also be rerun to seed 4-5 for each size. |
| 30 | Medium | Documentation | Ark M3 | Primary endpoint says "A vs C/D" ambiguously. | Accept | §8 primary endpoint does not distinguish C and D contrasts. | Rewrite endpoints as `AUC(C)-AUC(A)` and `AUC(D)-AUC(A)` at each training size; make `AUC(D)-AUC(C)` secondary or tertiary. |
| 31 | Medium | Consistency | Ark M4 | Charge neutralization sensitivity is undefined. | Partial | Same evidence as row 4. | Handle with the same fallback-only adapter-vs-neutralization diagnostic; do not add a separate full experiment unless the fallback is actually used. |
| 32 | Medium | Requirement | Ark M5 | Bootstrap details are underspecified. | Partial | §9 names bootstrap but not unit, replicate count, interval type, or seed. BCa and Bayesian checks are useful but not necessary for the minimal plan. | Specify per-jet paired bootstrap, at least 1000 replicates, fixed bootstrap seed, and percentile or BCa interval chosen before analysis; keep Bayesian posterior checks optional. |
| 33 | Medium | Requirement | Ark M6 | Run record omits dataset hash, pretraining source, hardware, runtime, and memory. | Accept | §10 has `data_manifest_hash` but not file-set hash, hardware, runtime, or peak memory. | Add `dataset_hash`, `pretraining_source`, `hardware_spec`, `runtime_seconds`, and `peak_gpu_memory_mb`. |
| 34 | Medium | Risk | Ark M7 | Fallback neutralization lacks contamination diagnostic. | Partial | §6 says fallback is weaker but only requires stating the limitation. If adapter-swap fails entirely, a direct adapter comparison may be impossible. | If fallback is used, add the strongest feasible diagnostic: compare adapter vs neutralization when adapter works for that config; otherwise log skipped layers and state contamination risk explicitly. |
| 35 | Medium | Documentation | Ark M8 | Config D needs candidate column names. | Accept | Same core evidence as row 2, with emphasis on reproducibility. | Add provisional candidate columns in §5 and freeze final columns during E0. |
| 36 | Medium | Requirement | Ark M9 | Deep Sets/PFN baseline is under-specified. | Accept | §7 names a baseline family but no implementation, size target, or hyperparameter starting point. | Pick one minimal baseline spec before E3, preferably an in-repo Deep Sets/PFN implementation with fixed model size and training protocol; do not add a large external dependency unless already installed. |
| 37 | Low | Clarity | Ark L1 | `normalized_gap_closed` is non-standard terminology. | Accept | The name could imply a different convention. | Rename to `auc_gap_fraction` or define the term once in Methods. |
| 38 | Low | Clarity | Ark L2 | "Expand only through decision gates" needs forward reference. | Accept | §1 references decision gates before §12. | Add "(see §12)" in the v0.3 change table. |
| 39 | Low | Consistency | Ark L3 | E1 pilot and §11 4-8 runs should be explicitly connected. | Accept | §8 E1 minimum is 2 configs x 2 sizes x 1 seed = 4 runs; §11 says 4-8 runs. | Add a parenthetical explaining that 4-8 corresponds to E1 depending on whether the optional second seed or baseline pilot is run. |
| 40 | Low | Documentation | Ark L4 | Artifact repository or DOI plan is missing. | Partial | Useful for applications, but not required before methods execution. | Add optional post-analysis output: GitHub release or Zenodo deposit for manifests, run records, figures, and prediction files if licensing permits. |
| 41 | Low | Documentation | Ark L5 | Pretraining data overlap with JetClass is not named. | Accept | The plan uses "fine-tuning" but does not say whether pretraining already used JetClass. | Add this under checkpoint metadata; if pretraining uses JetClass, state the study is downstream adaptation under controlled feature availability, not out-of-domain transfer. |
| 42 | Low | Risk | Ark L6 | Risk register omits checkpoint availability, GPU price spike, and calendar slippage. | Accept | §13 has no rows for these project-realistic constraints. | Add three risk rows with backup checkpoint, dollar cap, and cut-scope-not-quality mitigation. |
| 43 | Info | Consistency | Ark I1 | Paper title and repo name differ. | Reject | A research paper title does not need to match the repository name; the reviewer also says no action is required. | No change. Keep the paper-facing title independent from the repo handle. |
| 44 | Info | Documentation | Ark I2 | Venue target is absent. | Partial | A venue target helps applicant narrative, but locking venue rules now can distract from E0-E2. | Add a one-line optional target such as "arXiv preprint plus relevant ML4PS/HEP-ML workshop if results and timing permit"; do not make it an execution gate. |
| 45 | Info | Applicant-fit | Ark I3 | Add a Bayesian appendix to leverage the researcher's PyMC background. | Partial | The applicant-fit logic is valid, but a Bayesian side analysis is not required for the core physics/ML claim and risks scope creep. | Mention Bayesian uncertainty as optional future polish only; keep the required statistical plan to seed variation and paired bootstrap. |

## Needs Immediate Action

- Freeze the checkpoint specification, including source, hash, license, input shape, normalization, pretraining corpus, and backup.
- Add E0.5 adapter-loading validation before E1.
- Add provisional Config D candidate columns plus an E0 leakage audit.
- Add data acquisition/storage and measured compute/budget gates.
- Resolve PET/OmniLearn naming and checkpoint-dependent terminology.
- Specify input adapter form, exact primary endpoints, and bootstrap/run-record details.

## Can Be Deferred

- Formal JSON Schema for run records; a compact schema table is enough now.
- Extra pilot seed if E1 runtime is not cheap.
- Larger-than-10^5 saturation run.
- ParticleNet/ParT or broad architecture benchmarks.
- Zenodo DOI, venue targeting, and Bayesian appendix; useful for applicant polish, not required to start the core study.

## Final Status

`research-plan-v0.3.md` is scientifically acceptable as a direction document but not yet execution-ready. The minimum remaining work is a focused v0.3.1 patch that resolves checkpoint identity, adapter feasibility, Config D definition/leakage checks, data/storage/compute constraints, and the small consistency issues listed above.
