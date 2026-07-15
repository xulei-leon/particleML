# CMS 2015 MINIAODSIM Feasibility Analysis Review Confirm

**Reviewed Inputs**

- `docs/research/assessments/cms-2015-miniaodsim-feasibility.md`
- `docs/4-Reviews/cms-2015-miniaodsim-feasibility-analysis-review-by-opencode-go-kimi-k2.7-code.md`
- `docs/4-Reviews/cms-2015-miniaodsim-feasibility-analysis-review-by-opencode-go-glm-5.2.md`
- `docs/research/plans/research-plan-v0.3.md`
- CMSSW `CMSSW_7_6_X` `PackedCandidate.h`
- CERN Open Data metadata for records 18376, 18377, 18355, and 18358

**Review Date**

- 2026-07-14

## Overall Conclusion

Both reviews correctly identify missing operational definitions, especially the QCD-bin mixture, matched-signal yield gate, jet-energy-correction convention, impact-parameter convention, and signal-match ambiguity. Several proposed remedies are too strong or factually inaccurate: a controlled classifier does not automatically require cross-section-weighted training, the selected CMS records are `QCD_Pt_*` samples rather than HT samples, and CMSSW 7.6 defines `PackedCandidate::dxy()` relative to the candidate's associated PV reference rather than the beamspot.

The target remains a valid **CONDITIONAL GO** feasibility analysis after the accepted clarifications below. It still does not pass E0; measured CMSSW pilot outputs remain required.

## Decision Table

| No. | Severity | Type | Review Source | Original Comment Summary | Decision | Evidence | Follow-up Plan / Rejection Reason |
|---:|---|---|---|---|---|---|---|
| 1 | High | Correctness | `Kimi 1` | QCD bins lack a cross-section weighting rule. | Partial | The document lacks a bin-mixture rule, but the experiment trains on controlled, class-balanced samples with train-derived pT/eta control; physical cross-section weighting is not automatically the correct training distribution. | Identify the records as `QCD_Pt` bins, freeze the extraction/sampling mixture from training data, store record provenance, and require cross-section weights only for explicitly physics-weighted evaluation. Never expose bin identity or weights to the model. |
| 2 | High | Risk | `Kimi 2` | The 100,000-signal target is unverified after truth matching. | Partial | Section 8.1 already labels the estimate a pre-match lower bound and Section 9 blocks E0 on a pilot, so the uncertainty is disclosed rather than hidden. The gate does not yet require the full efficiency chain or full-corpus projection. | Require the pilot to report kinematic, top-match, hadronic-decay, containment, and ambiguity-rejection yields and project matched signal for the corpus. If 100,000 is infeasible, revise `n_max` and dependent plan metrics explicitly. Do not add an unsupported branching-fraction estimate now. |
| 3 | High | Correctness | `Kimi 3` | Impact-parameter units and reference points are unclear. | Partial | CMSSW 7.6 `PackedCandidate.h` says `dxy()` is relative to the candidate PV reference and `dz(ipv)` is relative to the selected PV index; this conflicts with the reviewer's beamspot wording. The document does not state expected units or association details. | State the CMSSW accessor semantics, expected centimetre units, `dz(0)` convention, and required PV-association provenance; retain E0 validation before treating the values as verified. |
| 4 | High | Correctness | `Kimi 4` | The jet-pT correction level is unspecified. | Accept | The selection and preliminary scan say only `jet pT`; this can change yields and sample membership. | Define production selection on the corrected `slimmedJetsAK8::pt()` value, record correction metadata, and state that the preliminary Uproot scan did not independently validate the correction level. |
| 5 | Medium | Requirement | `Kimi 5` | The PID vocabulary is not implementable as written. | Accept | The target requires a documented vocabulary at E0 but gives no provisional `abs(pdgId)` mapping. | Add the minimal PF-species vocabulary: charged hadron, neutral hadron, photon, electron, muon, and unknown; ignore charge sign and freeze the mapping from training data before E1. |
| 6 | Medium | Risk | `Kimi 6` | PV choice and pileup diagnostics are missing for D features. | Partial | `offlineSlimmedPrimaryVertices` and `dz(0)` provide a deterministic primary convention, but class-dependent pileup can confound D. Mandatory reweighting is not justified before measuring a mismatch. | Use PV index 0, record vertex/PV distributions by class, and match or reweight pileup only if the training-split diagnostic shows a material mismatch. |
| 7 | Medium | Reproducibility | `Kimi 7` | `canonical PFN` is undefined. | Accept | The exact input string controls split assignment and is not currently specified. | Define it as the exact PFN string written in the sorted manifest, encoded as UTF-8 without case or protocol normalization; hash the full SHA-256 digest. |
| 8 | Medium | Clarity | `Kimi 8` | Daughter containment is ambiguous. | Accept | Section 5.2 does not distinguish geometric containment from constituent membership. | Define containment as `deltaR(daughter, reconstructed jet axis) < 0.8` for each of `b`, `q`, and `q'`. |
| 9 | Medium | Correctness | `Kimi 9` | Generator-bin bounds do not directly bound reconstructed jet pT. | Accept | CERN record titles identify these as `QCD_Pt_*` generator-level samples, and generated pT bins do not define reconstructed AK8 pT. | Correct the bin label and require per-record reconstructed-pT coverage in the pilot before excluding the two upper bins. |
| 10 | Low | Documentation | `Kimi 10` | “CC0-1.0 attribution metadata” is contradictory. | Accept | CC0-1.0 is a public-domain dedication and does not impose attribution. | Replace it with “CC0-1.0 license metadata.” |
| 11 | Low | Reproducibility | `Kimi 11` | The manifest hash is present without the manifest artifact. | Partial | The document explicitly says the persistent manifest is future extractor output, but the current snapshot cannot be independently reconstructed from the repository. | State this limitation and make committing the materialized manifest a prerequisite to formal E0 production; do not invent a file that is not currently available. |
| 12 | Low | Clarity | `Kimi 12` | Fine-tuning and feature availability are not connected explicitly. | Accept | The matrix implies the relationship but does not state it in one sentence. | Add one direct sentence explaining separate checkpoint fine-tuning on A-D to measure incremental feature value. |
| 13 | Info | Risk | `Kimi 13` | The access test covers HTTPS, not XRootD or grid access. | Reject | Section 8.2 already calls the measurements path diagnostics, not bandwidth benchmarks, and explicitly recommends CERN-adjacent/XRootD-capable infrastructure. | No duplicate prose is needed; the yield/compute pilot will record throughput on the actual production host. |
| 14 | High | Correctness | `GLM 1` | QCD bins require cross-section-weighted pooling. | Partial | Same underlying gap as Kimi 1, but physical weighting and controlled training sampling are separate choices. | Add a frozen bin-mixture policy and reserve cross-section weights for explicitly physics-weighted results. |
| 15 | High | Risk | `GLM 2` | Pre-match yield threatens the plan's fixed `n_max = 10^5`. | Partial | The target already permits reducing the largest scale only after measurement, while plan v0.3 fixes `n_max` at 100,000. The dependency must be explicit. | Add the full matched-yield chain and require a plan revision to `n_max` and `auc_gap_fraction` if the pilot cannot support 100,000 jets per class. |
| 16 | High | Correctness | `GLM 3` | Jet-energy-correction level and preliminary scan convention are unclear. | Accept | Same confirmed issue as Kimi 4, independently reasoned. | Use corrected `slimmedJetsAK8::pt()` for production and label the preliminary scan's correction-level limitation. |
| 17 | High | Correctness | `GLM 4` | IP reference points, units, and packed decoding are unclear. | Partial | The need for clarification is real, but the proposed beamspot statement conflicts with the pinned CMSSW header. Raw packed members are not physical values, which the target already acknowledges. | Document actual accessor semantics, expected centimetre units, and CMSSW-only decoding; validate physical values and errors in E0. |
| 18 | High | Correctness | `GLM 5` | The provisional `tanh` transform has no justified scale. | Accept | The target warns against an unrecorded dimensionful transform but still names an underspecified provisional formula. | Remove the provisional formula. At E0.5 either reproduce the checkpoint convention or fit a training-only normalization for raw decoded values. |
| 19 | High | Clarity | `GLM 6` | Ambiguous top matches and last-copy traversal are undefined. | Accept | Section 5.2 requires rejection but gives no executable ambiguity rule or status convention. | Reject jets with more than one eligible last-copy top within the matching radius; define the CMSSW `isLastCopy()` traversal and test it on inspected events. |
| 20 | Medium | Test | `GLM 7` | Gen-level AK8 jets are present but unused as a cross-check. | Partial | The bqq' containment rule is the label definition; gen-jet matching is not required to define it. A diagnostic is cheap and useful. | Add reconstructed-to-gen-AK8 matching as a pilot diagnostic only, not an extra signal-label requirement. |
| 21 | Medium | Requirement | `GLM 8` | PID categories are unspecified. | Accept | Same confirmed implementation gap as Kimi 5. | Add and freeze the minimal charge-sign-independent PF vocabulary. |
| 22 | Medium | Risk | `GLM 9` | TT and QCD pileup profiles may confound D. | Partial | Measuring class-conditional vertex distributions is warranted; mandatory pileup reweighting before evidence of mismatch is not. | Add a training-split pileup diagnostic and condition any matching/reweighting on the observed mismatch. |
| 23 | Medium | Correctness | `GLM 10` | The review assumes the records are HT bins and asks the document to choose HT or pThat. | Partial | CERN metadata titles are `QCD_Pt_470to600`, `QCD_Pt_600to800`, and so on; the reviewer's “almost certainly HT” claim is false, but the document's generic label is too vague. | Name them `QCD_Pt` generator-level bins and retain the valid warning that they do not directly bound reconstructed jet pT. |
| 24 | Medium | Reproducibility | `GLM 11` | The split uses undefined PFNs, only 32 bits, and may be imbalanced. | Partial | Undefined input and unmeasured post-selection bucket sizes are real gaps. A 32-bit digest prefix does not create event leakage, and modulo-10 balance is statistical rather than “non-deterministic.” | Define the PFN bytes, use the full digest for simplicity, retain file-level assignment, and require selected-jet counts by class and split before E1. |
| 25 | Medium | Consistency | `GLM 12` | The label-shuffle criterion is weaker than plan v0.3. | Accept | Plan v0.3 requires the shuffled-label AUC 95% bootstrap interval to contain 0.5; the target only says “near.” | Copy the exact plan criterion into the E0 leakage gate. |
| 26 | Medium | Risk | `GLM 13` | CMSSW CPU, wall-time, throughput, and storage are absent from the budget. | Partial | The target already requires adding extraction to the next plan revision, but no measurements exist before the pilot. | Require the pilot to report CPU time, wall time, source bytes, compact-output size, and production-host throughput, then use those measurements in the revised budget. |
| 27 | Low | Documentation | `GLM 14` | CC0 wording is contradictory. | Accept | Same confirmed wording error as Kimi 10. | Replace the wording once. |
| 28 | Low | Reproducibility | `GLM 15` | The hashed manifest is not committed. | Partial | Same scope distinction as Kimi 11: the snapshot is evidence for this analysis, while a committed canonical artifact is an E0 prerequisite. | State the present limitation and enforce the commit gate before formal production. |
| 29 | Low | Risk | `GLM 16` | Every staged file should receive a stronger per-file hash. | Reject | CERN publishes Adler-32 for transfer checking; computing SHA-256 would require rereading each staged ROOT file and adds large I/O cost without evidence of a current integrity failure. The sorted manifest already has a SHA-256 identity hash. | Keep the CMS-native per-file checksum and verify it during transfer; add stronger hashes only if the storage or publication system requires them. |
| 30 | Low | Clarity | `GLM 17` | The title/scope does not state the fine-tuning contrast directly. | Accept | Same confirmed clarity gap as Kimi 12. | Add the one-sentence relationship in Section 1. |
| 31 | Low | Risk | `GLM 18` | Two inspected files do not establish corpus-wide schema uniformity. | Partial | Campaign-level schema consistency is expected, but the extractor must not silently assume it. A full metadata sweep before any processing is unnecessary. | Validate required products for every opened file, fail fast on mismatch, and sample multiple files in the E0 pilot. |
| 32 | Info | Risk | `GLM 19` | The HTTPS probe cannot characterize production-host throughput. | Reject | The document already states exactly this limitation and does not generalize the measured rate to CERN-adjacent infrastructure. | No change beyond recording production-host throughput in the pilot. |
| 33 | Info | Reproducibility | `GLM 20` | The CMSSW and Python environments are not clearly separated. | Accept | Section 8.3 names CMSSW, while Section 11 lists only the inspection environment. | Split the reproduction log into inspection and production environments and require the CMSSW image digest in production provenance. |

## Needs Immediate Action

- Define corrected jet pT, QCD `Pt`-bin handling, exact PFN hashing, PID categories, daughter containment, and ambiguous-match rejection.
- Replace the provisional impact-parameter transform with an E0.5 decision and document the actual CMSSW accessor semantics.
- Strengthen E0 gates for matched yield, pileup diagnostics, split counts, schema checks, leakage, and measured extraction cost.

## Can Be Deferred

- Materializing the full source manifest, selecting any pileup or physics weighting, and fixing impact-parameter normalization remain measured E0/E0.5 outputs.
- Strong per-file hashes and a mandatory gen-jet label condition are not justified now.

## Final Status

Accept the document as a revised **CONDITIONAL GO** feasibility analysis after applying the accepted and partial changes. E0 remains blocked until the CMSSW pilot produces the required measurements.
