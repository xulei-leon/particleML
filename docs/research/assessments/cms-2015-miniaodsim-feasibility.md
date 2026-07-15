# CMS 2015 MINIAODSIM Feasibility Analysis for A-D Fine-Tuning

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-07-13
- Verification Status: ANALYZED
- Version Label: cms2015_miniaodsim_feasibility_v1
- Scope: Public CMS 2015 simulated data for top-versus-QCD fine-tuning of an OmniLearned PET-style checkpoint

## Executive Decision

**Decision: CONDITIONAL GO.** CMS 2015 MINIAODSIM is a technically suitable public source for retaining the nested A-D feature study. Real files contain AK8 jets, packed particle-flow candidates, generator particles, generator-level AK8 jets, primary vertices, particle kinematics, PID, and the stored quantities needed to recover transverse and longitudinal impact parameters and their uncertainties.

The main risk is not feature availability. It is extraction cost and signal yield. The candidate source corpus is 3.542 TiB, and a preliminary scan found only 5 reconstructed AK8 jets satisfying the nominal kinematic selection in the first 1,000 inclusive TT events, before hadronic-top truth matching. Full extraction must therefore run near CERN or on infrastructure with a good EOS/XRootD connection. It should not run over the full corpus from the current local connection.

This analysis does **not** pass project gate E0. A CMSSW pilot must still validate jet-daughter references, decoded physical impact-parameter values, truth labels, missing-value rates, and matched-top yield.

## 1. Research Scope

The revised primary experiment remains a nested feature-availability study:

| Configuration | Particle-level view | Scientific contrast |
|---|---|---|
| A | Kinematics | Four-momentum baseline |
| B | A + electric charge | Incremental value of charge |
| C | B + particle identity | Incremental value of PID beyond charge |
| D | C + impact-parameter information | Incremental value of track displacement information |

Every configuration must be fine-tuned and evaluated separately. Test-time masking is not a substitute for configuration-specific fine-tuning.

The study therefore fine-tunes one pretrained OmniLearned checkpoint separately on each A-D feature view to measure the incremental value of charge, PID, and impact-parameter information.

The task remains binary boosted-top tagging, but JetClass is replaced by a public CMS 2015 full-detector-simulation corpus that is not listed in the OmniLearned pretraining corpus.

## 2. Frozen Candidate Source Corpus

### 2.1 Signal

Use one inclusive TT production and do not mix extensions during the first study:

| Record | Process | Events | Files | Size | DOI |
|---:|---|---:|---:|---:|---|
| 19980 | `TT_TuneCUETP8M1_13TeV-powheg-pythia8`, RunIIFall15MiniAODv2 ext3 | 97,994,442 | 2,413 | 3.051 TiB | [10.7483/OPENDATA.CMS.JJEM.1DKC](https://doi.org/10.7483/OPENDATA.CMS.JJEM.1DKC) |

Only reconstructed AK8 jets matched to a fully hadronic generator-level top decay are signal examples. Other jets from TT events must not be relabeled as QCD background.

### 2.2 Background

Use the Pythia8 QCD samples from the same 2015 MiniAOD production campaign:

| Record | Generator-level pT bin | Events | Files | Size | DOI |
|---:|---|---:|---:|---:|---|
| 18373 | 470-600 GeV | 3,977,770 | 89 | 0.121 TiB | [10.7483/OPENDATA.CMS.5DBS.XCW8](https://doi.org/10.7483/OPENDATA.CMS.5DBS.XCW8) |
| 18376 | 600-800 GeV | 3,979,884 | 91 | 0.126 TiB | [10.7483/OPENDATA.CMS.3Y72.BWW4](https://doi.org/10.7483/OPENDATA.CMS.3Y72.BWW4) |
| 18377 | 800-1,000 GeV | 3,973,224 | 98 | 0.130 TiB | [10.7483/OPENDATA.CMS.SGRV.4ABD](https://doi.org/10.7483/OPENDATA.CMS.SGRV.4ABD) |
| 18355 | 1,000-1,400 GeV | 2,953,982 | 89 | 0.100 TiB | [10.7483/OPENDATA.CMS.WOP0.TFY9](https://doi.org/10.7483/OPENDATA.CMS.WOP0.TFY9) |
| 18358 | 1,400-1,800 GeV | 395,725 | 9 | 0.014 TiB | [10.7483/OPENDATA.CMS.N49K.1FTR](https://doi.org/10.7483/OPENDATA.CMS.N49K.1FTR) |

These are `QCD_Pt_*` generator-level samples, not reconstructed-jet-pT bins. The first three records are the primary extraction set, but the pilot must plot selected reconstructed AK8 jet pT by record before the two higher bins can be excluded.

The classifier uses class-balanced samples with jet-pT and eta control fitted on the training split; raw event counts from the QCD records are not treated as a physical mixture. Freeze and record the per-record extraction and sampling mixture. If a result is explicitly reported for a physically weighted QCD spectrum, obtain per-record generator cross sections from CMS metadata, store the derived weights in provenance, and apply them only in that declared analysis. Record identity, bin identity, and weights must never enter model inputs.

### 2.3 Corpus integrity snapshot

The CERN Open Data API returned:

- 6 dataset records;
- 2,789 file entries, all marked online;
- 2,789 unique PFNs;
- 0 duplicate PFNs;
- 113,275,027 total events;
- 3,894,380,452,202 raw bytes, or 3.542 TiB;
- CC0-1.0 license metadata for the checked TT and QCD records.

The canonical manifest snapshot was formed from sorted lines with this format:

```text
record_id<TAB>pfn<TAB>adler32_checksum<TAB>size_bytes<LF>
```

Its SHA-256 on 2026-07-13 was:

```text
29ba19ff67480498d6f16e195bf91362b115da8a9a766862fe0fab7b469237d7
```

This hash identifies the source-file set used by this feasibility analysis, but the snapshot cannot be independently reconstructed from the repository because the manifest itself is not yet committed. The extractor must materialize and commit the persistent manifest before formal E0 data production.

## 3. Direct File Inspection

Two real files were opened remotely through HTTPS range requests with Uproot 5.7.5. This inspected the actual ROOT metadata rather than relying only on documentation.

| Sample | Source file | Adler-32 | File size | Events | Event branches |
|---|---|---|---:|---:|---:|
| TT | `00DF0A73-17C2-E511-B086-E41D2D08DE30.root` | `3349a8f4` | 1,432,170,200 bytes | 41,812 | 2,063 |
| QCD 470-600 | `004A5302-BBB8-E511-8558-0023AEEEB559.root` | `fc61a05f` | 1,380,426,087 bytes | 41,382 | 2,031 |

Both files contain the required EDM products:

| Requirement | Product observed in both files | Status |
|---|---|---|
| Reconstructed AK8 jets | `patJets_slimmedJetsAK8__PAT` | Verified in file metadata |
| Particle-flow constituents | `patPackedCandidates_packedPFCandidates__PAT` | Verified in file metadata |
| Generator particles | `recoGenParticles_prunedGenParticles__PAT` | Verified in file metadata |
| Generator-level AK8 jets | `recoGenJets_slimmedGenJetsAK8__PAT` | Verified in file metadata |
| Primary vertices | `recoVertexs_offlineSlimmedPrimaryVertices__PAT` | Verified in file metadata |

The QCD file also exposes the following split `pat::PackedCandidate` data members:

- `packedPt_`, `packedEta_`, `packedPhi_`, and `packedM_`;
- `pdgId_` and `qualityFlags_`;
- `packedDxy_` and `packedDz_`;
- `packedCovarianceDxyDxy_` and `packedCovarianceDzDz_`.

The corresponding CMSSW 7.6 `pat::PackedCandidate` interface provides `charge()`, `pdgId()`, `dxy()`, `dz()`, `dxyError()`, and `dzError()`. The error accessors recover the square roots of the stored covariance elements. See the pinned [CMSSW_7_6_X PackedCandidate header](https://github.com/cms-sw/cmssw/blob/CMSSW_7_6_X/DataFormats/PatCandidates/interface/PackedCandidate.h) and the [CMS MiniAOD Open Data guide](https://opendata.cern.ch/docs/cms-getting-started-miniaod).

This is sufficient to establish schema feasibility. It is not a replacement for CMSSW decoding because raw packed members are compressed representations and jet-daughter references must be resolved through CMS data formats.

## 4. A-D Feature Mapping

Use `slimmedJetsAK8` as the jet collection and take its packed daughters as constituents. Sort constituents by descending transverse momentum and keep at most 150 particles, matching the OmniLearned pretraining limit.

| Config | Training feature | CMS source | Required processing | Missing-value rule |
|---|---|---|---|---|
| A | `delta_eta` | Candidate and AK8 jet `eta()` | Candidate eta minus jet eta | None for retained candidates |
| A | `delta_phi` | Candidate and AK8 jet `phi()` | Wrapped to `[-pi, pi)` | None |
| A | `log_pt` | Candidate `pt()` | Natural log after a positive minimum cut | None after cut |
| A | `log_energy` | Candidate `energy()` | Natural log after a positive minimum cut | None after cut |
| B | `charge` | Candidate `charge()` | Cast to a small integer or float scalar | Zero is a physical neutral value |
| C | `pid_type` | Candidate `pdgId()` | Map `abs(pdgId)` to charged hadron (211), neutral hadron (130), photon (22), electron (11), muon (13), or unknown | Unknown category, never generator ancestry |
| D | `dxy_raw` | Candidate `dxy()` | Store the decoded value relative to the candidate's associated PV reference; expected CMSSW unit is cm and must be validated | Zero for neutral/no-track candidates |
| D | `dxy_error_raw` | Candidate `dxyError()` | Store the decoded uncertainty in the same physical unit and validate it in CMSSW | Zero for neutral/no-track candidates |
| D | `dz_raw` | Candidate `dz(0)` | Store the decoded value relative to primary-vertex index 0; expected CMSSW unit is cm and must be validated | Zero for neutral/no-track candidates |
| D | `dz_error_raw` | Candidate `dzError()` | Store the decoded uncertainty in the same physical unit and validate it in CMSSW | Zero for neutral/no-track candidates |

Important design rules:

1. Store decoded raw impact-parameter values in the extraction output. Freeze transforms only after plotting the training-split distributions.
2. Do not freeze an ad-hoc `tanh` transform. At E0.5, either reproduce the checkpoint's documented impact-parameter convention exactly or normalize decoded raw values using parameters fitted on the training split only. Record units, scales, and the chosen transform.
3. Define PID as the particle-species vocabulary in the table without charge sign because Config B already contains charge. This keeps the B-to-C contrast interpretable. Freeze the mapping before E1, and initialize the categorical PID input adapter from scratch.
4. For neutral candidates and candidates without usable track details, set D features to zero and record a separate audit count. PID and charge distinguish ordinary neutral entries from charged entries with missing track information.
5. If more than 1% of retained charged candidates lack usable track details, the missing-value policy must be reviewed before E1.
6. No generator truth, process identifier, record identifier, file identifier, or class-derived feature may enter the model input.
7. Use `offlineSlimmedPrimaryVertices` index 0 for `dz(0)`. Record candidate PV association, reconstructed-vertex multiplicity, and PV-z distributions by class. Match or reweight pileup only if a training-split diagnostic shows a material class mismatch.

The final compact dataset should be produced once with the full D schema. A-D views should be sliced from that single source tensor so that all configurations use identical jets, particle ordering, masks, and splits.

## 5. Labels, Selection, and Confound Control

### 5.1 Jet selection

Primary selection:

```text
500 GeV <= jet pT < 1000 GeV
abs(jet eta) < 2.0
anti-kt R = 0.8 via slimmedJetsAK8
```

Apply the pT cut to the corrected `slimmedJetsAK8::pt()` value exposed by MiniAOD. Record the jet-correction metadata used by the CMSSW release and global tag; any uncorrected-pT sensitivity study must be named explicitly.

Do not apply a top-mass or Soft-Drop mass window in the primary sample. Such a cut would alter the tagging problem and could hide or exaggerate the value of constituent features.

### 5.2 Signal label

A signal jet must satisfy all of the following in the CMSSW extractor:

1. identify generator top quarks with `abs(pdgId) == 6` and the CMSSW last-copy status flag, then match within `deltaR(jet, top) < 0.8`;
2. identify a hadronic `top -> b W -> b q q'` decay from `prunedGenParticles`;
3. require `deltaR(daughter, reconstructed jet axis) < 0.8` separately for the `b`, `q`, and `q'` daughters;
4. reject the jet if more than one eligible last-copy top lies within the matching radius.

The exact generator-status and mother-daughter traversal must be unit-tested on hand-inspected events before bulk extraction. Reconstructed-to-`slimmedGenJetsAK8` matching should be recorded as a pilot diagnostic, not added as a signal-label requirement.

### 5.3 Background label

Background jets come only from the selected QCD records. Do not use unmatched jets from TT events as background, because their event environment is process-dependent.

### 5.4 Distribution control

Top and QCD samples must be matched or reweighted in jet `pT` and `eta` using parameters estimated from the training split only. Jet mass should remain unconstrained in the primary result; a mass-matched result may be added as a sensitivity study after the core analysis is stable.

Compare reconstructed-vertex multiplicity and PV-z distributions between classes on the training split. Apply a frozen pileup matching or reweighting rule only if this diagnostic finds a material mismatch, and report results before and after the correction.

No event weight, generator-bin label, or global dataset identifier may be used as an input feature.

## 6. Split and Reproducibility Policy

Split by source file before extracting jets. A deterministic rule is:

```text
canonical_pfn = exact PFN field from the sorted manifest, encoded as UTF-8
bucket = integer(SHA256(canonical_pfn)) mod 10
bucket 0 -> test
bucket 1 -> validation
bucket 2-9 -> training
```

Do not lowercase, strip protocol prefixes, or otherwise normalize the PFN before hashing. After selection and truth matching, report files, events, and jets by class and split; E1 requires adequate validation and test counts, not merely an approximately balanced file count.

This keeps all jets from one event and one source file in the same split. The extractor must save:

- CMS record ID, canonical PFN, Adler-32 checksum, and file size;
- run, luminosity block, event number, jet index, and source-file identity;
- split assignment and split-rule version;
- extraction code commit and CMSSW container digest;
- raw and selected event/jet counts at every cut;
- feature missingness, non-finite counts, truncation rates, and normalization statistics;
- final HDF5 file hashes and source-manifest hash.

Normalization, PID vocabulary, optional reweighting, and any impact-parameter scale factors must be fitted on the training split only and then frozen.

## 7. Pretraining-Overlap Assessment

The [OmniLearned paper](https://arxiv.org/html/2510.24066) lists JetClass, JetClass2, Aspen Open Jets, ATLAS Top Tagging, H1 DIS, CMS QCD, and CMS BSM in pretraining. Its CMS component is described as real or simulated proton-proton collisions associated with the 2016 CMS release. The proposed corpus is the separate 2015 `RunIIFall15MiniAODv2` production.

| Overlap dimension | Assessment | Permitted claim |
|---|---|---|
| Exact CMS dataset records | No proposed 2015 record is listed in the published pretraining corpus | Dataset-record-disjoint downstream corpus |
| Exact events/files | Low risk; 2015 PFNs are distinct from the described 2016 CMS component | Confirm again against any checkpoint manifest released later |
| Detector family | Overlaps: both use CMS-like or CMS detector information | Cross-year/cross-corpus adaptation, not cross-detector novelty |
| Physics classes | Overlaps: OmniLearned has seen top-like and QCD jets | Not an unseen-class experiment |
| Task semantics | Overlaps: top tagging is an established downstream task | Feature-availability transfer study |

Recommended manuscript wording:

> The downstream corpus consists of CMS 2015 RunIIFall15 MINIAODSIM records not listed in the OmniLearned pretraining corpus. The model had previously encountered top-like and QCD jet classes, so this experiment tests cross-corpus adaptation under controlled feature availability rather than unseen-class transfer.

Do not claim that the model has never seen top or QCD jets.

## 8. Yield, Storage, and Access Feasibility

### 8.1 Preliminary AK8 yield

The first 1,000 events in the inspected TT file contained:

- 375 reconstructed `slimmedJetsAK8` jets;
- 5 jets with `500 <= pT < 1000 GeV` and `abs(eta) < 2`;
- 4 events containing at least one such jet.

This is a small, non-random prefix sample and is not a final yield estimate. It is also measured before hadronic-top truth matching. At the observed raw rate, 100,000 kinematically selected AK8 candidates would require approximately 20 million TT events and roughly 0.68 TB (0.62 TiB) of raw input. Truth matching will reduce the yield further, so this is a lower bound on required input.

The scan used the stored MiniAOD jet pT exposed through Uproot; its correction level was not independently validated. Production yields must be re-measured with the corrected `slimmedJetsAK8::pt()` convention in CMSSW.

A yield pilot over at least 5-10 TT files is mandatory before approving the `10^5`-per-class training scale. It must report the full efficiency chain from reconstructed jets through kinematic selection, top matching, hadronic decay, daughter containment, and ambiguity rejection; matched signal jets per file; and the projected matched yield for the full TT corpus. If `10^5` is infeasible, the next research-plan revision must change `n_max` and every dependent `auc_gap_fraction` definition explicitly.

### 8.2 Local access test

Two single-range HTTPS tests from the current machine measured:

| Test | Bytes received | Duration | Mean rate |
|---|---:|---:|---:|
| TT | 1,048,576 | 36.96 s | 28,370 B/s |
| QCD | 5,191,760 before timeout | 60.00 s | 86,526 B/s |

These are path diagnostics, not stable bandwidth benchmarks. They nevertheless show that a local TB-scale scan is operationally unsuitable. Use CERN-adjacent compute, an institutional cluster with XRootD access, or cloud compute with measured high-throughput access to EOS.

Do not download the entire source corpus. Stream files, write compact intermediate outputs, and retain the immutable source manifest.

### 8.3 Software environment

CMS records specify:

- CMSSW `7_6_7`;
- container `cmsopendata/cmssw_7_6_7-slc6_amd64_gcc493`;
- global tag `76X_mcRun2_asymptotic_RunIIFall15DR76_v1`.

The official image is documented in the [CMS Docker guide](https://opendata.cern.ch/docs/cms-guide-docker). The local Docker CLI was present, but the Linux engine was unavailable during this analysis; pulling a multi-gigabyte CMSSW image over the measured local path was therefore not attempted.

The minimum production pipeline is:

```text
CMS MINIAODSIM
  -> one CMSSW EDAnalyzer with fixed cuts and truth matching
  -> compact flat ROOT output with raw A-D fields and provenance
  -> one Python/h5py conversion into OmniLearned-compatible HDF5
```

The [OmniLearned custom-data documentation](https://github.com/ViniciusMikuni/OmniLearned/blob/5091595d226b6021e967ab2ecfff832f40c026f6/README.md#creating-your-own-dataset) confirms the required HDF5 `data`, jet-label `pid`, and optional `global` entries. Store jet-level variables in provenance or `global` for audit, but do not feed them to the primary classifier.

## 9. E0 Exit Gates for This Dataset

E0 remains blocked until one CMSSW pilot produces all of the following:

| Gate | Pass criterion |
|---|---|
| Jet daughters | AK8 daughter references resolve to packed candidates for both TT and QCD |
| A-C fields | Kinematics, charge, and PID are finite and have documented vocabularies |
| D fields | CMSSW-decoded `dxy`, `dz`, and errors validate the documented PV-reference semantics and cm units; vertex and PV-z distributions are reported by class |
| Missingness | Charged no-track rate is measured; policy passes the 1% review threshold |
| Labels | Hand-inspected events confirm last-copy traversal, geometric daughter containment, ambiguity rejection, and the gen-AK8 diagnostic |
| Yield | The full matched-signal efficiency chain and corpus projection support the chosen `n_max`; projected raw bytes and files fit the active budget |
| Split | File-level deterministic split has no PFN or event overlap and has adequate selected-jet counts by class |
| Leakage | No truth or process fields enter model tensors; the shuffled-label AUC 95% bootstrap interval contains 0.5 |
| Output | A-D tensors derive from one full tensor and pass shape, mask, NaN/Inf, and padding tests |
| Schema | Required products are validated for every opened file, with multiple TT and QCD files sampled during the pilot |
| Extraction cost | Pilot CPU time, wall time, source bytes, compact-output size, and production-host throughput support the active budget |

If the matched-top yield makes `10^5` signal jets impractical, reduce the largest training scale only after the measured pilot is recorded. Do not silently lower the jet `pT` threshold because that changes the study domain.

## 10. Required Changes to Research Plan v0.3

The current [research plan v0.3](../plans/research-plan-v0.3.md) is still written around JetClass. Before implementation, a new revision must:

1. replace JetClass with the frozen CMS 2015 record set;
2. replace JetClass column names with the CMS-to-A-D mapping in this document;
3. update the overlap statement from same-corpus adaptation to dataset-record-disjoint cross-corpus adaptation;
4. add CMSSW extraction and raw-data throughput to E0 and the compute budget;
5. revise the signal-label definition to generator-matched hadronic tops;
6. add the PID-without-charge-sign rule and missing-track audit;
7. retain the existing A-D fine-tune-without-X protocol and paired evaluation design.
8. define the QCD-record mixture, corrected-jet-pT convention, pileup diagnostic, and exact split hash input;
9. revise `n_max` and dependent metrics if the measured matched-top yield cannot support `10^5` jets per class;
10. add measured CMSSW CPU, throughput, and storage costs from the pilot.

This feasibility document does not itself change the approved experimental matrix.

## 11. Reproduction Log

Inspection environment:

```text
Windows / PowerShell
Python 3.14.4
Uproot 5.7.5
Awkward 2.10.0
fsspec 2026.6.0
```

Production environment to pin during E0:

```text
CMSSW 7_6_7
cmsopendata/cmssw_7_6_7-slc6_amd64_gcc493 image digest
76X_mcRun2_asymptotic_RunIIFall15DR76_v1 global tag
```

The CMSSW container performs EDM decoding and extraction. The separate modern Python environment performs inspection and compact ROOT-to-HDF5 conversion; their dependencies and artifact hashes must be recorded independently.

Evidence sources accessed on 2026-07-13:

- CERN Open Data record API for records 19980, 18373, 18376, 18377, 18355, and 18358;
- HTTPS range access to one TT and one QCD ROOT file;
- CMSSW `CMSSW_7_6_X` `PackedCandidate.h`;
- CMS MiniAOD and Docker documentation;
- OmniLearned paper and repository at commit `5091595d226b6021e967ab2ecfff832f40c026f6`.

Observed ROOT checks used for this report:

```text
Events tree existence and entry count
required EDM product names
split PackedCandidate member names
AK8 pT/eta scan over the first 1,000 TT events
```

### Verification limitation

No CMSSW event loop was completed in this environment. Consequently, this report verifies source availability, file integrity metadata, required product presence, packed member presence, API-level feature access, and a preliminary reconstructed-jet yield. It does not verify decoded constituent values, jet-daughter linkage, generator-decay traversal, or final HDF5 output. Those items remain explicit E0 gates rather than inferred successes.
