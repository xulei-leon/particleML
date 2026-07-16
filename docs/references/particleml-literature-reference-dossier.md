# Literature Reference Dossier

*Jet foundation models, particle-level feature availability, and JetClass top tagging*

**Verified sources:** 34  
**Search date:** 15 July 2026

**Purpose:** This dossier supplies a verified literature base for a publication-oriented study of how nested particle-level feature sets affect fine-tuning of an OmniLearned/PET-style backbone on JetClass binary top-versus-QCD tagging. It is a source map and reference catalogue, not a substitute for reading the cited papers.

**How to use it:** Start with the thematic roadmap, use the annotations to select evidence for a manuscript section, then cite the formal numbered reference list after checking the complete source.

## Search Strategy and Selection

A targeted scoping search was conducted on 15 July 2026 using project seed sources and direct HTTPS queries to Crossref, arXiv, INSPIRE-HEP, Zenodo, and official proceedings or journal pages. The final corpus contains **34 sources**. Every final verification endpoint returned HTTP 200, and every DOI, arXiv identifier, title, author set, and year was checked against an authoritative record.

**Inclusion:** Direct relevance to a planned paper section; resolvable authoritative metadata; a distinct scientific role; primary peer-reviewed evidence when available; and explicit preprint labels.

**Exclusion:** Unresolved or mismatched metadata, duplicate versions, secondary summaries, indirect general relevance, and sources redundant with stronger project-aligned evidence.

**Verification boundary:** Bibliographic existence and record-level claims were checked. Full-text reading is not claimed for every source; core papers must be read before claim-level manuscript citation.

## Thematic Roadmap

The themes below map the verified corpus to the planned paper. Counts refer to each source's primary theme; several sources can support more than one manuscript section.

**Table 1. Literature coverage by evidence theme.**

| Evidence theme | Sources | Primary contribution | Manuscript use |
|---|---:|---|---|
| Jet Foundation Models | 6 | Defines the OmniLearn/OmniLearned and OmniJet lineages, multi-task claims, and current pretraining directions. | Introduction; Related Work |
| Datasets and Top Tagging | 5 | Establishes JetClass provenance, binary top-tagging context, and community benchmark expectations. | Introduction; Methods |
| Particle-Set Architectures | 5 | Explains permutation-invariant, attention, graph, PET, and Lorentz-equivariant backbones. | Related Work; Methods |
| Feature Representation and Physics Priors | 3 | Connects particle-level information, IRC safety, symmetry, and learned low-level representations. | Introduction; Methods |
| Pretraining and Transfer | 4 | Supplies transfer-learning terminology, feature-transfer evidence, and the foundation-model frame. | Introduction; Methods |
| Evaluation and Reproducibility | 5 | Supports AUC comparison, dependence-aware uncertainty, repeated runs, and reproducible reporting. | Evaluation; Limitations |
| Generation and Anomaly Detection | 6 | Places the tagging study within the wider multi-task jet-foundation-model agenda. | Related Work; Future Work |

*Coverage is strongest for the model lineage, particle-set architectures, and evaluation methods. The central unresolved question is the controlled effect of downstream feature availability under a fixed pretrained checkpoint and data protocol.*

## Annotated Source Catalogue

Entries are grouped by their primary evidence role. Source numbers match the formal reference list. Annotations separate what a source contributes from how it should be used and from the limits of that use.

### Jet Foundation Models

#### Source 1 | A Method to Simultaneously Facilitate All Jet Physics Tasks

*Vinicius Mikuni and Benjamin Nachman (2025). Physical Review D.*

- **Source and evidence:** Peer-reviewed publication; Core peer-reviewed primary source.
- **Verification:** INSPIRE-HEP DOI record, Crossref metadata, and arXiv 2502.14652
- **Central contribution:** Shows that a representation trained on a multiclass jet task can support classification, generation, likelihood-ratio estimation, anomaly detection, detector-domain changes, and collision-system changes.
- **Project relevance:** Defines the OmniLearn jet-foundation-model approach that motivates the project's pretrained PET-style backbone.
- **Recommended manuscript use:** Related Work
- **Limitation:** Its tasks, datasets, and feature interfaces are broader than the project's controlled JetClass feature-ablation protocol.

#### Source 2 | Solving Key Challenges in Collider Physics with Foundation Models

*Vinicius Mikuni and Benjamin Nachman (2025). Physical Review D.*

- **Source and evidence:** Peer-reviewed publication; Core peer-reviewed application study.
- **Verification:** INSPIRE-HEP arXiv record, Crossref DOI metadata, and arXiv 2404.16091
- **Central contribution:** Applies a jet foundation model to reconstruction-compute reduction, high-dimensional uncertainty quantification, and model-agnostic new-physics searches.
- **Project relevance:** Demonstrates downstream scientific uses of a jet foundation model beyond a proof-of-principle benchmark.
- **Recommended manuscript use:** Related Work
- **Limitation:** The article evaluates application case studies rather than isolating the effect of particle-level feature availability.

#### Source 3 | OmniJet-alpha: The First Cross-Task Foundation Model for Particle Physics

*Joschka Birk, Anna Hallin, and Gregor Kasieczka (2024). Machine Learning: Science and Technology.*

- **Source and evidence:** Peer-reviewed publication; Core peer-reviewed primary source.
- **Verification:** Crossref DOI metadata and arXiv 2403.05618
- **Central contribution:** Introduces a higher-fidelity particle tokenization and demonstrates transfer from unsupervised jet generation to supervised jet tagging.
- **Project relevance:** Provides the principal tokenized autoregressive contrast to continuous PET-style jet foundation models.
- **Recommended manuscript use:** Related Work
- **Limitation:** Its tokenizer and autoregressive backbone impose a different feature interface and compute profile from the project's main model.

#### Source 4 | Foundation Model Framework for All Tasks Involving Jet Physics

*Wahid Bhimji, Chris Harris, Vinicius Mikuni, and Benjamin Nachman (2026). Physical Review D.*

- **Source and evidence:** Peer-reviewed publication; Core peer-reviewed primary source.
- **Verification:** INSPIRE-HEP, Crossref DOI metadata, and arXiv 2510.24066
- **Central contribution:** Upgrades OmniLearn with revised training, more than one billion training jets, public software, and demonstrations on top tagging, b-tagging, and anomaly detection.
- **Project relevance:** Supplies the pretrained OmniLearned framework and checkpoint family targeted by the current research plan.
- **Recommended manuscript use:** Related Work
- **Limitation:** Its broad state-of-the-art claims do not by themselves establish causal effects of individual input-feature groups.

#### Source 5 | Enhancing Next Token Prediction Based Pre-Training for Jet Foundation Models

*Joschka Birk, Anna Hallin, Gregor Kasieczka, Nikol Madzharova, Ian Pang, and David Shih (2025). arXiv preprint.*

- **Source and evidence:** Verified preprint or report; Verified recent preprint.
- **Verification:** arXiv abstract metadata
- **Central contribution:** Reports improved downstream classification from continuous input vectors and combined masked-particle and generative pretraining without sacrificing generation quality.
- **Project relevance:** Updates the OmniJet line with hybrid continuous inputs and combined pretraining objectives relevant to representation design.
- **Recommended manuscript use:** Related Work
- **Limitation:** The work was a preprint at the search date and requires cautious use for settled performance claims.

#### Source 6 | Aspen Open Jets: Unlocking LHC Data for Foundation Models in Particle Physics

*Oz Amram, Luca Anzalone, Joschka Birk, et al. (2025). Machine Learning: Science and Technology.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed dataset and transfer study.
- **Verification:** Crossref DOI metadata and arXiv 2412.10504
- **Central contribution:** Introduces roughly 178 million CMS Open Data jets and reports that OmniJet-alpha pretraining improves generation on simulated JetClass top and QCD jets.
- **Project relevance:** Provides evidence for pretraining on experimental open data and transfer under a substantial domain shift.
- **Recommended manuscript use:** Introduction
- **Limitation:** Its downstream task is generative transfer rather than the project's supervised feature-ablation study.

### Datasets and Top Tagging

#### Source 7 | Particle Transformer for Jet Tagging

*Huilin Qu, Congqiao Li, and Sitian Qian (2022). Proceedings of the 39th International Conference on Machine Learning, PMLR 162.*

- **Source and evidence:** Peer-reviewed publication; Core peer-reviewed benchmark and methods paper.
- **Verification:** Official PMLR proceedings page and arXiv 2202.03772
- **Central contribution:** Presents a 100-million-jet, ten-class dataset and a transformer that incorporates pairwise particle interactions and benefits from pretraining.
- **Project relevance:** Introduces both the JetClass benchmark and the particle-interaction-aware transformer architecture used as a reference for PET-style modeling.
- **Recommended manuscript use:** Methods
- **Limitation:** The headline study is multiclass tagging; the project must define and freeze its own binary top-versus-QCD extraction.

#### Source 8 | JetClass: A Large-Scale Dataset for Deep Learning in Jet Physics

*Huilin Qu, Congqiao Li, and Sitian Qian (2022). Zenodo.*

- **Source and evidence:** Authoritative dataset record; Authoritative primary dataset record.
- **Verification:** Official Zenodo record and DOI metadata
- **Central contribution:** Provides the large simulated jet corpus used for JetClass benchmarking and the project's top-versus-QCD study.
- **Project relevance:** Defines the provenance and public file release for the project's primary dataset.
- **Recommended manuscript use:** Methods
- **Limitation:** A repository record does not specify the project's exact file subset, split manifest, feature transformations, or leakage controls.

#### Source 9 | Maximizing Boosted Top Identification by Minimizing N-Subjettiness

*Jesse Thaler and Ken Van Tilburg (2012). Journal of High Energy Physics.*

- **Source and evidence:** Peer-reviewed publication; Seminal peer-reviewed jet-substructure paper.
- **Verification:** Crossref DOI metadata and journal record
- **Central contribution:** Develops N-subjettiness observables and demonstrates their use for discriminating boosted hadronic top jets.
- **Project relevance:** Establishes the classical boosted-top-tagging context against which learned particle-level representations are motivated.
- **Recommended manuscript use:** Introduction
- **Limitation:** It predates modern particle-cloud networks and is a physics-observable baseline rather than a foundation-model study.

#### Source 10 | The Machine Learning Landscape of Top Taggers

*Gregor Kasieczka, Tilman Plehn, Anja Butter, Kyle Cranmer, Dipsikha Debnath, et al. (2019). SciPost Physics.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed community benchmark.
- **Verification:** Crossref DOI metadata and arXiv 1902.09914
- **Central contribution:** Compares a wide range of low-level-input top taggers and finds broadly similar performance across substantially different architectures.
- **Project relevance:** Provides a shared boosted-top-tagging comparison landscape and cautions against overinterpreting architecture-only differences.
- **Recommended manuscript use:** Related Work
- **Limitation:** The benchmark predates current jet foundation models and does not test pretrained feature-ablation protocols.

#### Source 11 | JetNet: A Python Package for Accessing Open Datasets and Benchmarking Machine Learning Methods in High Energy Physics

*Raghav Kansal, Carlos Pareja, Zichun Hao, and Javier Duarte (2023). Journal of Open Source Software.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed research-software paper.
- **Verification:** Crossref DOI metadata and JOSS record
- **Central contribution:** Packages jet datasets, evaluation metrics, and reference workflows to improve benchmarking consistency in HEP machine learning.
- **Project relevance:** Documents a reproducible interface for open jet datasets and common generation and tagging benchmarks.
- **Recommended manuscript use:** Methods
- **Limitation:** Its packaged datasets and defaults do not replace the project's explicit JetClass provenance and split manifest.

### Particle-Set Architectures

#### Source 12 | Deep Sets

*Manzil Zaheer, Satwik Kottur, Siamak Ravanbakhsh, Barnabas Poczos, Ruslan Salakhutdinov, and Alexander J. Smola (2017). Advances in Neural Information Processing Systems.*

- **Source and evidence:** Peer-reviewed publication; Foundational peer-reviewed methods paper.
- **Verification:** Official NeurIPS proceedings page and arXiv 1703.06114
- **Central contribution:** Characterizes permutation-invariant set functions and gives a practical sum-decomposition neural architecture.
- **Project relevance:** Provides the mathematical basis for a simple permutation-invariant baseline over jet constituents.
- **Recommended manuscript use:** Methods
- **Limitation:** The basic aggregation form does not explicitly model pairwise particle interactions or Lorentz structure.

#### Source 13 | Set Transformer: A Framework for Attention-Based Permutation-Invariant Neural Networks

*Juho Lee, Yoonho Lee, Jungtaek Kim, Adam R. Kosiorek, Seungjin Choi, and Yee Whye Teh (2019). Proceedings of the 36th International Conference on Machine Learning, PMLR 97.*

- **Source and evidence:** Peer-reviewed publication; Foundational peer-reviewed methods paper.
- **Verification:** Official PMLR proceedings page and arXiv 1810.00825
- **Central contribution:** Introduces attention modules for permutation-invariant learning and an inducing-point mechanism that reduces self-attention cost.
- **Project relevance:** Supplies a general attention-based set architecture relevant to unordered variable-length particle inputs.
- **Recommended manuscript use:** Methods
- **Limitation:** It is a domain-general set model and does not encode jet-specific pairwise physics or detector features.

#### Source 14 | Jet Tagging via Particle Clouds

*Huilin Qu and Loukas Gouskos (2020). Physical Review D.*

- **Source and evidence:** Peer-reviewed publication; Core peer-reviewed jet-architecture paper.
- **Verification:** Crossref DOI metadata and arXiv 1902.08570
- **Central contribution:** Adapts dynamic graph convolution to unordered particle clouds and reports strong performance on representative tagging benchmarks.
- **Project relevance:** Establishes the particle-cloud representation and a strong graph-based benchmark for jet tagging.
- **Recommended manuscript use:** Related Work
- **Limitation:** ParticleNet is a supervised task-specific architecture, not a pretrained cross-task foundation model.

#### Source 15 | Point Cloud Transformers Applied to Collider Physics

*Vinicius Mikuni and Florencia Canelli (2021). Machine Learning: Science and Technology.*

- **Source and evidence:** Peer-reviewed publication; Core peer-reviewed architecture paper.
- **Verification:** Crossref DOI metadata and arXiv 2102.05073
- **Central contribution:** Adapts transformer-based relation learning to unordered collider point clouds and evaluates it on boosted-particle jet tagging.
- **Project relevance:** Provides the PET precursor that directly informs the OmniLearn and OmniLearned backbone family.
- **Recommended manuscript use:** Methods
- **Limitation:** The study focuses on supervised tagging and predates the full multi-task foundation-model training regime.

#### Source 16 | An Efficient Lorentz Equivariant Graph Neural Network for Jet Tagging

*Shiqi Gong, Qi Meng, Jue Zhang, et al. (2022). Journal of High Energy Physics.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed physics-informed architecture paper.
- **Verification:** Crossref DOI metadata and arXiv 2201.08187
- **Central contribution:** Introduces LorentzNet with Minkowski-dot-product message passing and reports competitive tagging with improved efficiency at small training sizes.
- **Project relevance:** Provides a high-performing comparison for how explicit Lorentz symmetry can alter data efficiency and generalization.
- **Recommended manuscript use:** Related Work
- **Limitation:** It tests a different inductive bias and architecture, so performance cannot be directly attributed to the project's feature ladder.

### Feature Representation and Physics Priors

#### Source 17 | Energy Flow Networks: Deep Sets for Particle Jets

*Patrick T. Komiske, Eric M. Metodiev, and Jesse Thaler (2019). Journal of High Energy Physics.*

- **Source and evidence:** Peer-reviewed publication; Foundational peer-reviewed jet-representation paper.
- **Verification:** Crossref DOI metadata and arXiv 1810.05165
- **Central contribution:** Specializes Deep Sets to jets, introduces EFNs and PFNs, and shows how per-particle feature choices determine the allowed information content.
- **Project relevance:** Directly distinguishes IRC-safe energy-flow inputs from particle-flow models that admit charge, flavor, and other particle features.
- **Recommended manuscript use:** Methods
- **Limitation:** The quark-versus-gluon demonstrations do not isolate the same feature groups or use a pretrained foundation-model backbone.

#### Source 18 | Energy Flow Polynomials: A Complete Linear Basis for Jet Substructure

*Patrick T. Komiske, Eric M. Metodiev, and Jesse Thaler (2018). Journal of High Energy Physics.*

- **Source and evidence:** Peer-reviewed publication; Foundational peer-reviewed physics-representation paper.
- **Verification:** Crossref DOI metadata and arXiv 1712.07124
- **Central contribution:** Constructs a complete linear basis for infrared- and collinear-safe jet observables and demonstrates strong linear tagging performance.
- **Project relevance:** Provides an interpretable basis for discussing which physically meaningful information is available to learned low-level representations.
- **Recommended manuscript use:** Introduction
- **Limitation:** The basis excludes non-IRC-safe information such as particle identity and charge that the project's richer feature views may exploit.

#### Source 19 | Symmetries, Safety, and Self-Supervision

*Barry M. Dillon, Gregor Kasieczka, Hans Olischlager, Tilman Plehn, Peter Sorrenson, and Lorenz Vogel (2022). SciPost Physics.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed self-supervised representation study.
- **Verification:** Crossref DOI metadata and arXiv 2108.04253
- **Central contribution:** Introduces JetCLR, a contrastive permutation-invariant transformer representation, and evaluates it with linear probes on top and QCD jets.
- **Project relevance:** Connects permutation invariance, physical symmetries, and self-supervised jet representations to label-efficient downstream tagging.
- **Recommended manuscript use:** Related Work
- **Limitation:** Its contrastive pretraining objective and linear-probe evaluation differ from end-to-end fine-tuning of OmniLearned.

### Pretraining and Transfer

#### Source 20 | A Survey on Transfer Learning

*Sinno Jialin Pan and Qiang Yang (2010). IEEE Transactions on Knowledge and Data Engineering.*

- **Source and evidence:** Peer-reviewed publication; Foundational peer-reviewed review.
- **Verification:** Crossref DOI metadata and IEEE record
- **Central contribution:** Organizes transfer learning by problem setting and method family and formalizes when knowledge is moved between domains or tasks.
- **Project relevance:** Supplies standard terminology for source tasks, target tasks, domains, and transfer assumptions.
- **Recommended manuscript use:** Introduction
- **Limitation:** The survey predates modern foundation models and does not address HEP-specific simulation or feature-schema constraints.

#### Source 21 | How Transferable Are Features in Deep Neural Networks?

*Jason Yosinski, Jeff Clune, Yoshua Bengio, and Hod Lipson (2014). Advances in Neural Information Processing Systems.*

- **Source and evidence:** Peer-reviewed publication; Foundational peer-reviewed transfer study.
- **Verification:** arXiv metadata and NeurIPS 2014 journal reference
- **Central contribution:** Empirically distinguishes layer specialization from optimization difficulties when features are transferred and fine-tuned across tasks.
- **Project relevance:** Provides a conceptual basis for separating transferable backbone representations from task-specific input adapters and upper layers.
- **Recommended manuscript use:** Methods
- **Limitation:** The experiments use image networks, so the conclusions motivate rather than validate jet-specific adapter choices.

#### Source 22 | On the Opportunities and Risks of Foundation Models

*Rishi Bommasani, Drew A. Hudson, Ehsan Adeli, et al. (2021). arXiv preprint.*

- **Source and evidence:** Verified preprint or report; Authoritative foundation-model framing report.
- **Verification:** arXiv abstract metadata and Stanford CRFM report record
- **Central contribution:** Defines the foundation-model paradigm and surveys its technical principles, cross-domain opportunities, inherited risks, and evaluation challenges.
- **Project relevance:** Provides the broad definition of models trained at scale and adapted to multiple downstream tasks used in the paper's framing.
- **Recommended manuscript use:** Introduction
- **Limitation:** It is a broad cross-domain report and cannot support HEP-specific performance or reproducibility claims.

#### Source 23 | Machine Learning at the Energy and Intensity Frontiers of Particle Physics

*Alexander Radovic, Mike Williams, David Rousseau, Michael Kagan, et al. (2018). Nature.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed field review.
- **Verification:** Crossref DOI metadata and Nature record
- **Central contribution:** Reviews machine-learning applications, opportunities, and deployment constraints across particle-physics experiments.
- **Project relevance:** Places jet machine learning and transferable learned representations within the wider HEP analysis ecosystem.
- **Recommended manuscript use:** Introduction
- **Limitation:** The review predates jet foundation models and therefore provides context rather than direct evidence for the planned comparison.

### Evaluation and Reproducibility

#### Source 24 | Evaluation Metrics and Statistical Tests for Machine Learning

*Oona Rainio, Jarmo Teuho, and Riku Klen (2024). Scientific Reports.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed methodological review.
- **Verification:** Crossref DOI metadata and publisher record
- **Central contribution:** Reviews common ML evaluation metrics and statistical tests and discusses when each is appropriate.
- **Project relevance:** Supports explicit metric selection and the distinction between descriptive performance and inferential comparison.
- **Recommended manuscript use:** Evaluation
- **Limitation:** Its examples are domain-general and do not prescribe HEP-specific operating points or systematic uncertainties.

#### Source 25 | Comparing the Areas Under Two or More Correlated Receiver Operating Characteristic Curves: A Nonparametric Approach

*Elizabeth R. DeLong, David M. DeLong, and Daniel L. Clarke-Pearson (1988). Biometrics.*

- **Source and evidence:** Peer-reviewed publication; Foundational statistical methodology.
- **Verification:** Crossref DOI metadata and journal record
- **Central contribution:** Derives covariance-aware comparisons for two or more correlated ROC curves.
- **Project relevance:** Provides a standard nonparametric method for comparing ROC AUCs evaluated on the same examples.
- **Recommended manuscript use:** Evaluation
- **Limitation:** Seed-to-seed training variability and nested data subsampling require additional hierarchical or resampling treatment.

#### Source 26 | Approximate Statistical Tests for Comparing Supervised Classification Learning Algorithms

*Thomas G. Dietterich (1998). Neural Computation.*

- **Source and evidence:** Peer-reviewed publication; Foundational peer-reviewed statistical comparison paper.
- **Verification:** Crossref DOI metadata and journal record
- **Central contribution:** Analyzes approximate tests for classifier comparisons and documents inflated error rates from common resampling procedures.
- **Project relevance:** Warns that naïve reuse of train/test splits can invalidate significance tests when comparing learning algorithms.
- **Recommended manuscript use:** Evaluation
- **Limitation:** The recommended procedures were developed before modern deep-learning seed and compute variance became central concerns.

#### Source 27 | Inference for the Generalization Error

*Claude Nadeau and Yoshua Bengio (2003). Machine Learning.*

- **Source and evidence:** Peer-reviewed publication; Foundational peer-reviewed statistical methodology.
- **Verification:** Crossref DOI metadata and Springer record
- **Central contribution:** Studies variance estimation for generalization error and proposes corrections for dependence induced by repeated data reuse.
- **Project relevance:** Supports corrected uncertainty reasoning when performance estimates share overlapping training data.
- **Recommended manuscript use:** Evaluation
- **Limitation:** Its analytical assumptions may not fully capture stochastic deep-network optimization or the project's nested feature views.

#### Source 28 | Improving Reproducibility in Machine Learning Research: A Report from the NeurIPS 2019 Reproducibility Program

*Joelle Pineau, Philippe Vincent-Lamarre, Koustuv Sinha, et al. (2021). Journal of Machine Learning Research.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed reproducibility program report.
- **Verification:** Official JMLR article page
- **Central contribution:** Reports the design and outcomes of a large conference reproducibility program and identifies practical reporting interventions.
- **Project relevance:** Supports artifact, checklist, code, and reporting practices needed for a credible multi-seed computational study.
- **Recommended manuscript use:** Evaluation
- **Limitation:** It provides process evidence rather than a domain-specific recipe for JetClass training and uncertainty analysis.

### Generation and Anomaly Detection

#### Source 29 | Denoising Diffusion Probabilistic Models

*Jonathan Ho, Ajay Jain, and Pieter Abbeel (2020). Advances in Neural Information Processing Systems.*

- **Source and evidence:** Peer-reviewed publication; Foundational peer-reviewed generative-model paper.
- **Verification:** arXiv metadata and NeurIPS 2020 proceedings record
- **Central contribution:** Develops a practical denoising diffusion objective and demonstrates high-quality generative modeling through iterative noise reversal.
- **Project relevance:** Provides the diffusion-model basis for modern particle-cloud generators used as future-work context.
- **Recommended manuscript use:** Related Work
- **Limitation:** The experiments use image data and do not address variable-length particle sets or HEP validation metrics.

#### Source 30 | PC-JeDi: Diffusion for Particle Cloud Generation in High Energy Physics

*Matthew Leigh, Debajyoti Sengupta, Guillaume Quetant, John Andrew Raine, Knut Zoch, and Tobias Golling (2024). SciPost Physics.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed jet-generation primary study.
- **Verification:** Crossref DOI metadata and arXiv 2303.05376
- **Central contribution:** Introduces a transformer score model for top and gluon jet generation and evaluates it with multiple fidelity metrics.
- **Project relevance:** Demonstrates diffusion-based conditional generation directly on permutation-equivariant particle clouds.
- **Recommended manuscript use:** Future Work
- **Limitation:** Generation quality and sampling speed are distinct outcomes from supervised tagging AUC and feature ablation.

#### Source 31 | EPiC-GAN: Equivariant Point Cloud Generation for Particle Jets

*Erik Buhmann, Gregor Kasieczka, and Jesse Thaler (2023). SciPost Physics.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed jet-generation primary study.
- **Verification:** Crossref DOI metadata and arXiv 2301.08128
- **Central contribution:** Uses equivariant deep-set layers and a global latent vector to generate particle jets without expensive pairwise message passing.
- **Project relevance:** Provides an efficient variable-multiplicity point-cloud generator aligned with the project's set-based representation context.
- **Recommended manuscript use:** Future Work
- **Limitation:** It studies adversarial generation rather than transfer learning or controlled changes in input features.

#### Source 32 | LHC Hadronic Jet Generation Using Convolutional Variational Autoencoders with Normalizing Flows

*Breno Orzari, Nadezda Chernyavskaya, Raphael Cobe, Javier Duarte, Jefferson Fialho, et al. (2023). Machine Learning: Science and Technology.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed jet-generation primary study.
- **Verification:** INSPIRE-HEP, Crossref DOI metadata, and arXiv 2310.13138
- **Central contribution:** Combines convolutional variational autoencoders with normalizing flows to generate LHC hadronic jets and benchmark fidelity.
- **Project relevance:** Supplies a contrasting latent-variable generation pipeline and examples of jet-generation validation.
- **Recommended manuscript use:** Future Work
- **Limitation:** Its image-like convolutional representation is not directly comparable to OmniLearned particle-set fine-tuning.

#### Source 33 | Anomaly Detection for Resonant New Physics with Machine Learning

*Jack H. Collins, Kiel Howe, and Benjamin Nachman (2018). Physical Review Letters.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed anomaly-detection methods paper.
- **Verification:** INSPIRE-HEP, Crossref DOI metadata, and arXiv 1805.02664
- **Central contribution:** Introduces a weakly supervised resonant anomaly search that uses sidebands and auxiliary features to enhance a bump hunt.
- **Project relevance:** Provides a canonical model-agnostic collider-anomaly use case for transferable low-level representations.
- **Recommended manuscript use:** Future Work
- **Limitation:** Its signal-localization assumptions and search statistic differ from generic representation-level anomaly detection.

#### Source 34 | The LHC Olympics 2020: A Community Challenge for Anomaly Detection in High Energy Physics

*Gregor Kasieczka, Benjamin Nachman, David Shih, Oz Amram, Anders Andreassen, et al. (2021). Reports on Progress in Physics.*

- **Source and evidence:** Peer-reviewed publication; Peer-reviewed community benchmark report.
- **Verification:** Crossref DOI metadata and arXiv 2101.08320
- **Central contribution:** Synthesizes a large community challenge using hidden-signal black boxes and compares diverse unsupervised and weakly supervised methods.
- **Project relevance:** Defines standard datasets, evaluation lessons, and practical failure modes for model-agnostic collider anomaly detection.
- **Recommended manuscript use:** Future Work
- **Limitation:** The challenge focuses on anomaly-search performance and does not test the project's feature-ablation hypothesis.

## Coverage and Research Gaps

The literature strongly supports the existence of transferable jet representations, the importance of permutation-aware particle-set models, and the use of JetClass as a large-scale benchmark. It does not yet answer the project's central causal comparison.

- **Matched feature-ablation evidence:** No retained study isolates nested particle-level feature groups while keeping the raw JetClass files, split, pretrained checkpoint, training schedule, and evaluation pipeline fixed.
- **Checkpoint and pretraining overlap:** The paper must document the OmniLearned checkpoint's pretraining corpus and avoid claiming out-of-domain transfer if JetClass or the same top/QCD task family appears in pretraining.
- **Feature-schema validity:** Config D remains publication-ready only if every impact-parameter feature is traced to a real JetClass column and passes leakage, masking, and transformation audits.
- **Independent validation:** Most model-family evidence is authored by the teams introducing the methods. A simple fixed Deep Sets/PFN baseline and independent reproduction strengthen feature-ranking claims.
- **Uncertainty and dependence:** AUC intervals on one test set do not replace repeated-seed uncertainty. Nested data sizes and shared examples create dependence that must be reflected in comparisons.
- **External and multi-task generalization:** Generation, anomaly detection, and transfer to other detector domains remain future work until the core JetClass feature-ablation result is stable.

## References

Numbered format follows the reference presentation in Group-Report.pdf. DOI and arXiv fields are included only when confirmed in the verified corpus.

[1] Vinicius Mikuni and Benjamin Nachman. "A Method to Simultaneously Facilitate All Jet Physics Tasks." In: Physical Review D 111.5, 054015 (2025). doi: 10.1103/PhysRevD.111.054015. arXiv: 2502.14652. url: https://doi.org/10.1103/PhysRevD.111.054015.

[2] Vinicius Mikuni and Benjamin Nachman. "Solving Key Challenges in Collider Physics with Foundation Models." In: Physical Review D 111.5, L051504 (2025). doi: 10.1103/PhysRevD.111.L051504. arXiv: 2404.16091. url: https://doi.org/10.1103/PhysRevD.111.L051504.

[3] Joschka Birk, Anna Hallin, and Gregor Kasieczka. "OmniJet-alpha: The First Cross-Task Foundation Model for Particle Physics." In: Machine Learning: Science and Technology 5.3, 035031 (2024). doi: 10.1088/2632-2153/ad66ad. arXiv: 2403.05618. url: https://doi.org/10.1088/2632-2153/ad66ad.

[4] Wahid Bhimji, Chris Harris, Vinicius Mikuni, and Benjamin Nachman. "Foundation Model Framework for All Tasks Involving Jet Physics." In: Physical Review D 113.3, 032020 (2026). doi: 10.1103/knmd-f5jm. arXiv: 2510.24066. url: https://doi.org/10.1103/knmd-f5jm.

[5] Joschka Birk, Anna Hallin, Gregor Kasieczka, Nikol Madzharova, Ian Pang, and David Shih. "Enhancing Next Token Prediction Based Pre-Training for Jet Foundation Models." In: arXiv preprint (2025). arXiv: 2512.04149. url: https://arxiv.org/abs/2512.04149.

[6] Oz Amram, Luca Anzalone, Joschka Birk, et al. "Aspen Open Jets: Unlocking LHC Data for Foundation Models in Particle Physics." In: Machine Learning: Science and Technology 6.3, 030601 (2025). doi: 10.1088/2632-2153/ade58f. arXiv: 2412.10504. url: https://doi.org/10.1088/2632-2153/ade58f.

[7] Huilin Qu, Congqiao Li, and Sitian Qian. "Particle Transformer for Jet Tagging." In: Proceedings of the 39th International Conference on Machine Learning, PMLR 162 18281-18292 (2022). arXiv: 2202.03772. url: https://proceedings.mlr.press/v162/qu22b.html.

[8] Huilin Qu, Congqiao Li, and Sitian Qian. "JetClass: A Large-Scale Dataset for Deep Learning in Jet Physics." In: Zenodo Record 6619768 (2022). doi: 10.5281/zenodo.6619768. url: https://zenodo.org/records/6619768.

[9] Jesse Thaler and Ken Van Tilburg. "Maximizing Boosted Top Identification by Minimizing N-Subjettiness." In: Journal of High Energy Physics 2012.2, 093 (2012). doi: 10.1007/JHEP02(2012)093. arXiv: 1108.2701. url: https://doi.org/10.1007/JHEP02(2012)093.

[10] Gregor Kasieczka, Tilman Plehn, Anja Butter, Kyle Cranmer, Dipsikha Debnath, et al. "The Machine Learning Landscape of Top Taggers." In: SciPost Physics 7.1, 014 (2019). doi: 10.21468/SciPostPhys.7.1.014. arXiv: 1902.09914. url: https://doi.org/10.21468/SciPostPhys.7.1.014.

[11] Raghav Kansal, Carlos Pareja, Zichun Hao, and Javier Duarte. "JetNet: A Python Package for Accessing Open Datasets and Benchmarking Machine Learning Methods in High Energy Physics." In: Journal of Open Source Software 8.90, 5789 (2023). doi: 10.21105/joss.05789. url: https://doi.org/10.21105/joss.05789.

[12] Manzil Zaheer, Satwik Kottur, Siamak Ravanbakhsh, Barnabas Poczos, Ruslan Salakhutdinov, and Alexander J. Smola. "Deep Sets." In: Advances in Neural Information Processing Systems 30 (2017). arXiv: 1703.06114. url: https://proceedings.neurips.cc/paper/2017/hash/f22e4747da1aa27e363d86d40ff442fe-Abstract.html.

[13] Juho Lee, Yoonho Lee, Jungtaek Kim, Adam R. Kosiorek, Seungjin Choi, and Yee Whye Teh. "Set Transformer: A Framework for Attention-Based Permutation-Invariant Neural Networks." In: Proceedings of the 36th International Conference on Machine Learning, PMLR 97 3744-3753 (2019). arXiv: 1810.00825. url: https://proceedings.mlr.press/v97/lee19d.html.

[14] Huilin Qu and Loukas Gouskos. "Jet Tagging via Particle Clouds." In: Physical Review D 101.5, 056019 (2020). doi: 10.1103/PhysRevD.101.056019. arXiv: 1902.08570. url: https://doi.org/10.1103/PhysRevD.101.056019.

[15] Vinicius Mikuni and Florencia Canelli. "Point Cloud Transformers Applied to Collider Physics." In: Machine Learning: Science and Technology 2.3, 035027 (2021). doi: 10.1088/2632-2153/ac07f6. arXiv: 2102.05073. url: https://doi.org/10.1088/2632-2153/ac07f6.

[16] Shiqi Gong, Qi Meng, Jue Zhang, et al. "An Efficient Lorentz Equivariant Graph Neural Network for Jet Tagging." In: Journal of High Energy Physics 2022.7, 030 (2022). doi: 10.1007/JHEP07(2022)030. arXiv: 2201.08187. url: https://doi.org/10.1007/JHEP07(2022)030.

[17] Patrick T. Komiske, Eric M. Metodiev, and Jesse Thaler. "Energy Flow Networks: Deep Sets for Particle Jets." In: Journal of High Energy Physics 2019.1, 121 (2019). doi: 10.1007/JHEP01(2019)121. arXiv: 1810.05165. url: https://doi.org/10.1007/JHEP01(2019)121.

[18] Patrick T. Komiske, Eric M. Metodiev, and Jesse Thaler. "Energy Flow Polynomials: A Complete Linear Basis for Jet Substructure." In: Journal of High Energy Physics 2018.4, 013 (2018). doi: 10.1007/JHEP04(2018)013. arXiv: 1712.07124. url: https://doi.org/10.1007/JHEP04(2018)013.

[19] Barry M. Dillon, Gregor Kasieczka, Hans Olischlager, Tilman Plehn, Peter Sorrenson, and Lorenz Vogel. "Symmetries, Safety, and Self-Supervision." In: SciPost Physics 12.6, 188 (2022). doi: 10.21468/SciPostPhys.12.6.188. arXiv: 2108.04253. url: https://doi.org/10.21468/SciPostPhys.12.6.188.

[20] Sinno Jialin Pan and Qiang Yang. "A Survey on Transfer Learning." In: IEEE Transactions on Knowledge and Data Engineering 22.10, 1345-1359 (2010). doi: 10.1109/TKDE.2009.191. url: https://doi.org/10.1109/TKDE.2009.191.

[21] Jason Yosinski, Jeff Clune, Yoshua Bengio, and Hod Lipson. "How Transferable Are Features in Deep Neural Networks?." In: Advances in Neural Information Processing Systems 27, 3320-3328 (2014). arXiv: 1411.1792. url: https://arxiv.org/abs/1411.1792.

[22] Rishi Bommasani, Drew A. Hudson, Ehsan Adeli, et al. "On the Opportunities and Risks of Foundation Models." In: arXiv preprint (2021). arXiv: 2108.07258. url: https://arxiv.org/abs/2108.07258.

[23] Alexander Radovic, Mike Williams, David Rousseau, Michael Kagan, et al. "Machine Learning at the Energy and Intensity Frontiers of Particle Physics." In: Nature 560.7716, 41-48 (2018). doi: 10.1038/s41586-018-0361-2. arXiv: 1807.02876. url: https://doi.org/10.1038/s41586-018-0361-2.

[24] Oona Rainio, Jarmo Teuho, and Riku Klen. "Evaluation Metrics and Statistical Tests for Machine Learning." In: Scientific Reports 14.1, 6086 (2024). doi: 10.1038/s41598-024-56706-x. url: https://doi.org/10.1038/s41598-024-56706-x.

[25] Elizabeth R. DeLong, David M. DeLong, and Daniel L. Clarke-Pearson. "Comparing the Areas Under Two or More Correlated Receiver Operating Characteristic Curves: A Nonparametric Approach." In: Biometrics 44.3, 837-845 (1988). doi: 10.2307/2531595. url: https://doi.org/10.2307/2531595.

[26] Thomas G. Dietterich. "Approximate Statistical Tests for Comparing Supervised Classification Learning Algorithms." In: Neural Computation 10.7, 1895-1923 (1998). doi: 10.1162/089976698300017197. url: https://doi.org/10.1162/089976698300017197.

[27] Claude Nadeau and Yoshua Bengio. "Inference for the Generalization Error." In: Machine Learning 52.3, 239-281 (2003). doi: 10.1023/A:1024068626366. url: https://doi.org/10.1023/A:1024068626366.

[28] Joelle Pineau, Philippe Vincent-Lamarre, Koustuv Sinha, et al. "Improving Reproducibility in Machine Learning Research: A Report from the NeurIPS 2019 Reproducibility Program." In: Journal of Machine Learning Research 22.164, 1-20 (2021). url: https://jmlr.org/papers/v22/20-303.html.

[29] Jonathan Ho, Ajay Jain, and Pieter Abbeel. "Denoising Diffusion Probabilistic Models." In: Advances in Neural Information Processing Systems 33, 6840-6851 (2020). arXiv: 2006.11239. url: https://arxiv.org/abs/2006.11239.

[30] Matthew Leigh, Debajyoti Sengupta, Guillaume Quetant, John Andrew Raine, Knut Zoch, and Tobias Golling. "PC-JeDi: Diffusion for Particle Cloud Generation in High Energy Physics." In: SciPost Physics 16.1, 018 (2024). doi: 10.21468/SciPostPhys.16.1.018. arXiv: 2303.05376. url: https://doi.org/10.21468/SciPostPhys.16.1.018.

[31] Erik Buhmann, Gregor Kasieczka, and Jesse Thaler. "EPiC-GAN: Equivariant Point Cloud Generation for Particle Jets." In: SciPost Physics 15.4, 130 (2023). doi: 10.21468/SciPostPhys.15.4.130. arXiv: 2301.08128. url: https://doi.org/10.21468/SciPostPhys.15.4.130.

[32] Breno Orzari, Nadezda Chernyavskaya, Raphael Cobe, Javier Duarte, Jefferson Fialho, et al. "LHC Hadronic Jet Generation Using Convolutional Variational Autoencoders with Normalizing Flows." In: Machine Learning: Science and Technology 4.4, 045023 (2023). doi: 10.1088/2632-2153/ad04ea. arXiv: 2310.13138. url: https://doi.org/10.1088/2632-2153/ad04ea.

[33] Jack H. Collins, Kiel Howe, and Benjamin Nachman. "Anomaly Detection for Resonant New Physics with Machine Learning." In: Physical Review Letters 121.24, 241803 (2018). doi: 10.1103/PhysRevLett.121.241803. arXiv: 1805.02664. url: https://doi.org/10.1103/PhysRevLett.121.241803.

[34] Gregor Kasieczka, Benjamin Nachman, David Shih, Oz Amram, Anders Andreassen, et al. "The LHC Olympics 2020: A Community Challenge for Anomaly Detection in High Energy Physics." In: Reports on Progress in Physics 84.12, 124201 (2021). doi: 10.1088/1361-6633/ac36b9. arXiv: 2101.08320. url: https://doi.org/10.1088/1361-6633/ac36b9.

## Search Limitations and Disclosure

1. **Limitation 1:** This is a targeted scoping review aligned with the current research plan, not an exhaustive systematic review or meta-analysis.
2. **Limitation 2:** Authoritative metadata and abstracts were checked, but record verification is not a claim that every full text has been read end to end.
3. **Limitation 3:** No subscription-only citation index was used, and literature published after 15 July 2026 is not represented.
4. **Limitation 4:** Recent preprints and new model releases should be refreshed immediately before manuscript submission.
5. **Limitation 5:** Statistical methods must be adapted to the dependence structure created by shared JetClass splits, nested training sizes, and repeated stochastic training runs.

### AI-Assistance Disclosure

AI-assisted tools were used for literature discovery, metadata normalization, source verification support, and document formatting. All included references were checked against the authoritative records identified in the verification audit; inclusion does not imply that every full text has been read by the researcher.
