# particleML Literature Search and Verification Audit

Search date: 2026-07-15  
Scope: literature needed for a paper on controlled particle-feature availability during fine-tuning of an OmniLearned/PET-style jet foundation model on JetClass binary top tagging.  
Review type: targeted, reproducible scoping review; not a PRISMA systematic review or meta-analysis.

## Search Strategy

The search used a seed-and-expansion strategy. Seed records came from `docs/references/Group-Report.pdf`, `README.md`, `docs/plan/research-plan-v0.3.md`, and `docs/preparation/research-preparation-stage.md`. Each seed was resolved through direct HTTPS requests to an authoritative bibliographic or publication record. The search then expanded around the seven evidence areas in the approved design.

Authoritative sources and direct request patterns:

- Crossref DOI metadata: `https://api.crossref.org/works/{doi}`.
- Crossref title resolution: `https://api.crossref.org/works?query.title={exact-title}&rows=3`.
- arXiv identifier batches: `https://export.arxiv.org/api/query?id_list={comma-separated-arxiv-ids}`.
- INSPIRE-HEP DOI and arXiv resolution: `https://inspirehep.net/api/literature?q=doi:{doi}` and `https://inspirehep.net/api/literature?q=arxiv:{id}`.
- JetClass dataset record: `https://zenodo.org/api/records/6619768`.
- Official proceedings and journal pages at PMLR, NeurIPS, JMLR, APS, IOP, Springer, SciPost, Nature, IEEE, MIT Press, and JOSS.

Exact entity and title query families:

- `OmniLearn`, `A Method to Simultaneously Facilitate All Jet Physics Tasks`, and `arxiv:2502.14652`.
- `Solving Key Challenges in Collider Physics with Foundation Models` and `arxiv:2404.16091`.
- `OmniJet-alpha`, `OmniLearned`, `Enhancing Next Token Prediction Based Pre-Training for Jet Foundation Models`, and `Aspen Open Jets`.
- `JetClass`, `Particle Transformer for Jet Tagging`, `ParticleNet`, `Point Cloud Transformers Applied to Collider Physics`, `Deep Sets`, `Set Transformer`, and `LorentzNet`.
- `Energy Flow Networks`, `Energy Flow Polynomials`, `Symmetries Safety and Self-Supervision`, `top tagging`, and `N-subjettiness`.
- `transfer learning`, `transferable features`, `foundation models`, and `machine learning particle physics review`.
- `ROC AUC`, `correlated ROC curves`, `classification algorithm statistical tests`, `generalization error`, and `machine learning reproducibility`.
- `particle cloud generation`, `PC-JeDi`, `EPiC-GAN`, `diffusion probabilistic models`, `jet generation`, `resonant anomaly detection`, and `LHC Olympics`.

Screening summary:

- Unique targeted candidates assessed: 39.
- Candidates retained after relevance, version, and metadata checks: 34.
- Candidates excluded after full metadata assessment: 5.
- Published/preprint duplicates retained as a single source record: 17.
- Final source types: 30 peer-reviewed publications, 2 verified preprints, 1 dataset record, and 1 foundation-model framing report recorded as a preprint.

Every final `verification_url` was requested directly over HTTPS on 2026-07-15. All 34 returned HTTP 200 at the final verification pass.

## Inclusion and Exclusion Criteria

Inclusion required all of the following:

1. Direct relevance to at least one of the seven evidence areas.
2. A resolvable authoritative record with matching title, authors, year, and DOI or arXiv identifier where applicable.
3. A specific role in the planned paper: Introduction, Related Work, Methods, Evaluation, Limitations, or Future Work.
4. Primary peer-reviewed evidence when available; seminal methods and statistics papers were allowed without a recency limit.
5. For recent preprints, a clear need not already met by a published source and an explicit preprint label.

Exclusion applied when any of the following held:

- The record could not be independently resolved.
- DOI metadata resolved to a different paper.
- A published version duplicated a preprint without adding a distinct scientific object.
- The source was a secondary summary when a primary record was available.
- Relevance was general rather than actionable for the current research questions.
- The candidate duplicated a better aligned generation, anomaly-detection, transfer-learning, or evaluation source.

No journal in the final corpus showed a predatory-publishing signal. The venues are established journals, major peer-reviewed conference proceedings, arXiv, or an official Zenodo record. Potential intellectual conflicts are present because several authors introduce and evaluate their own model families; the dossier treats those papers as primary-method sources, not independent comparative validation.

## Source Verification Log

- `mikuni2025_omnilearn` - VERIFIED through INSPIRE-HEP, Crossref, and arXiv 2502.14652. The DOI is `10.1103/PhysRevD.111.054015`.
- `mikuni2025_key_challenges` - VERIFIED through INSPIRE-HEP, Crossref, and arXiv 2404.16091. This is a distinct Physical Review D Letter, not the OmniLearn methods article.
- `birk2024_omnijet_alpha` - VERIFIED through Crossref and arXiv 2403.05618; published DOI and journal metadata agree.
- `bhimji2026_omnilearned` - VERIFIED through INSPIRE-HEP, Crossref, and arXiv 2510.24066; the final 2026 Physical Review D article supersedes a preprint-only citation.
- `birk2025_next_token_pretraining` - VERIFIED through arXiv 2512.04149; retained as a current preprint and labeled accordingly.
- `amram2025_aspen_open_jets` - VERIFIED through Crossref and arXiv 2412.10504; published metadata and the 178-million-jet dataset description agree.
- `qu2022_particle_transformer` - VERIFIED through the official PMLR proceedings page and arXiv 2202.03772.
- `qu2022_jetclass_dataset` - VERIFIED through the official Zenodo API record and DOI `10.5281/zenodo.6619768`.
- `thaler2012_nsubjettiness` - VERIFIED through Crossref DOI metadata and the Springer JHEP record.
- `kasieczka2019_top_taggers` - VERIFIED through Crossref and arXiv 1902.09914.
- `kansal2023_jetnet` - VERIFIED through Crossref and the JOSS article record.
- `zaheer2017_deep_sets` - VERIFIED through the official NeurIPS proceedings page and arXiv 1703.06114.
- `lee2019_set_transformer` - VERIFIED through the official PMLR proceedings page and arXiv 1810.00825.
- `qu2020_particlenet` - VERIFIED through Crossref and arXiv 1902.08570.
- `mikuni2021_point_cloud_transformer` - VERIFIED through Crossref and arXiv 2102.05073.
- `gong2022_lorentznet` - VERIFIED through Crossref and arXiv 2201.08187.
- `komiske2019_energy_flow_networks` - VERIFIED through Crossref and arXiv 1810.05165.
- `komiske2018_energy_flow_polynomials` - VERIFIED through Crossref and arXiv 1712.07124.
- `dillon2022_jetclr` - VERIFIED through Crossref and arXiv 2108.04253.
- `pan2010_transfer_learning` - VERIFIED through Crossref and the IEEE journal record.
- `yosinski2014_transferable_features` - VERIFIED through arXiv 1411.1792 and its NeurIPS 2014 journal reference.
- `bommasani2021_foundation_models` - VERIFIED through arXiv 2108.07258 and the Stanford CRFM report record; retained as a framing report rather than HEP performance evidence.
- `radovic2018_ml_particle_physics` - VERIFIED through Crossref and the Nature article record.
- `rainio2024_evaluation_metrics` - VERIFIED through Crossref and the Scientific Reports article record.
- `delong1988_correlated_roc` - VERIFIED through Crossref and the Biometrics record.
- `dietterich1998_classifier_tests` - VERIFIED through Crossref and the Neural Computation record.
- `nadeau2003_generalization_error` - VERIFIED through Crossref and the Springer Machine Learning record.
- `pineau2021_reproducibility` - VERIFIED through the official JMLR article page.
- `ho2020_ddpm` - VERIFIED through arXiv 2006.11239 and its NeurIPS 2020 proceedings reference.
- `leigh2024_pc_jedi` - VERIFIED through Crossref and arXiv 2303.05376.
- `buhmann2023_epic_gan` - VERIFIED through Crossref and arXiv 2301.08128.
- `orzari2023_jet_generation` - VERIFIED through INSPIRE-HEP, Crossref, and arXiv 2310.13138.
- `collins2018_resonant_anomaly` - VERIFIED through INSPIRE-HEP, Crossref, and arXiv 1805.02664.
- `kasieczka2021_lhc_olympics` - VERIFIED through Crossref and arXiv 2101.08320.

## Deduplication and Version Decisions

1. `arXiv:2404.16091` and `arXiv:2502.14652` were not merged. INSPIRE-HEP confirms that they are two different papers with different titles and DOIs: the former is “Solving Key Challenges in Collider Physics with Foundation Models,” while the latter is “A Method to Simultaneously Facilitate All Jet Physics Tasks.” The Group Report and repository preparation note had conflated the OmniLearn title with `arXiv:2404.16091`; the final corpus corrects this.
2. OmniLearned is cited as the 2026 Physical Review D publication with DOI `10.1103/knmd-f5jm`, while retaining arXiv 2510.24066 for traceability.
3. OmniJet-alpha, Aspen Open Jets, PC-JeDi, EPiC-GAN, JetCLR, ParticleNet, PET, LorentzNet, and the LHC Olympics are represented by their published versions, with arXiv identifiers retained.
4. Particle Transformer and the JetClass Zenodo record were both retained because one is a peer-reviewed methods/dataset paper and the other is the authoritative data-release artifact.
5. `Enhancing Next Token Prediction Based Pre-Training for Jet Foundation Models` remains a preprint because no verified published version was identified at the search date.
6. No duplicate DOI or case-normalized title remains in `source-corpus.json`.

## Excluded Candidates

- `Scaling Laws for Neural Language Models` (arXiv:2001.08361) - verified but excluded because language-model loss scaling is too indirect for the paper's controlled JetClass feature question.
- `DijetGAN` (DOI `10.1007/JHEP08(2019)110`) - verified but excluded because PC-JeDi, EPiC-GAN, and the particle-level CVAE/flow paper provide more direct modern jet-generation coverage.
- `Classification without Labels: Learning from Mixed Samples in High Energy Physics` (DOI `10.1007/JHEP10(2017)174`) - verified but excluded to keep anomaly-detection coverage focused on resonant search and community benchmark evidence.
- `Anomaly Detection with Density Estimation` (DOI `10.1103/PhysRevD.101.075042`) - verified but excluded because the current paper treats anomaly detection as future context, not a benchmarked task.
- `Weakly Supervised Classification in High Energy Physics` (DOI `10.1007/JHEP05(2017)145`) - verified but excluded because it overlaps the retained resonant anomaly-search motivation without directly informing the feature-ablation protocol.

An incorrect candidate DOI, `10.1103/PhysRevD.106.056007`, was also rejected during lookup because Crossref resolves it to “Waveforms from Amplitudes,” not JetCLR. JetCLR was corrected to DOI `10.21468/SciPostPhys.12.6.188` before inclusion; this metadata error is not counted as an excluded scientific candidate.

## Search Limitations

- This was a targeted project review, not an exhaustive systematic review. Search completeness was optimized for the current research questions and manuscript sections.
- Metadata and abstracts were inspected through authoritative records. A successful record verification does not mean that every full text was read end to end.
- No subscription-only citation index was used. Scopus and Web of Science coverage was not independently audited.
- Citation counts and journal metrics were not used as inclusion thresholds because they can disadvantage recent work and do not establish methodological suitability.
- Recent fast-moving literature may change after 2026-07-15. The preprint record should be refreshed before manuscript submission.
- Evaluation papers from biostatistics and general machine learning support statistical procedures, but their assumptions must be checked against nested JetClass splits, repeated seeds, and deep-network optimization variance.
- Intellectual conflicts are unavoidable for primary model papers; independent reproduction evidence should be added if the project later produces or finds a closely matched benchmark.
- The researcher should read the complete core papers before making claim-level citations in the final manuscript. This dossier verifies bibliographic existence and provides source-supported orientation; it is not a human-read attestation.
