# particleML Literature Reference Dossier Design

## Objective

Create a publication-oriented, English-language literature reference dossier for the particleML project. The dossier will support a future paper on controlled particle-feature ablations during fine-tuning of an OmniLearned/PET-style jet foundation model on JetClass top-versus-QCD tagging.

## Audience and Use

The primary reader is the project researcher preparing experiments and a manuscript. The dossier must help the reader decide which sources support the Introduction, Related Work, Methods, Evaluation, Limitations, and Future Work sections. It is a research input, not a substitute for the final manuscript literature review.

## Deliverable

The final deliverable is one verified DOCX document stored under `docs/references/`. It will contain approximately 30 high-value sources and use the numbered bibliography presentation observed in `docs/references/Group-Report.pdf`: bracketed sequential numbers, complete author and title information, venue or preprint metadata, year, DOI where available, arXiv identifier where applicable, and a stable URL.

Internal builders, extracted metadata, and page renders are quality-assurance artifacts and are not part of the user-facing delivery.

## Scope

The source corpus will cover seven evidence areas:

1. Jet foundation models: OmniLearn, OmniJet-alpha, and OmniLearned.
2. Jet datasets and benchmark tasks: JetClass and binary top tagging.
3. Particle-set architectures and baselines: PET, Particle Transformer, ParticleNet, Deep Sets, PFN, and EFN.
4. Particle-level feature representation, permutation symmetry, and physics-informed inductive bias.
5. Pretraining, fine-tuning, transfer learning, and label/data efficiency.
6. Evaluation and reproducibility: ROC AUC, uncertainty intervals, repeated seeded runs, calibration where relevant, and reproducible reporting.
7. Adjacent tasks used for context or future work: jet generation and anomaly detection.

General foundation-model sources will be included only when they directly clarify terminology or transfer-learning claims. Sources unrelated to the project's research questions will be excluded even if they are broadly influential.

## Search and Selection Method

Searches will prioritize arXiv, INSPIRE-HEP, DOI/Crossref metadata, journal publisher pages, official dataset records, and official repositories. Search terms will combine project entities and concepts, including `OmniLearn`, `OmniJet`, `OmniLearned`, `JetClass`, `top tagging`, `particle transformer`, `particle cloud`, `jet foundation model`, `jet generation`, `anomaly detection`, `transfer learning`, `feature ablation`, and `ROC AUC uncertainty`.

Inclusion requires direct relevance to at least one evidence area and verifiable bibliographic existence. Seminal older papers may be retained without a date limit. Recent sources are preferred for fast-moving foundation-model and jet-ML claims. Secondary web summaries are excluded when a primary paper, official record, or authoritative documentation exists.

## Verification Standard

Every included source must be checked against at least one authoritative record. Sources with a DOI will be checked for DOI resolution and metadata agreement. Preprints will be checked on arXiv and, where possible, INSPIRE-HEP. Dataset records will be checked against their official DOI or repository page. Published and preprint versions of the same work will be deduplicated, with the published version preferred while retaining the arXiv identifier when useful.

An entry is excluded if its existence, title, author list, year, or identifier cannot be confirmed. The dossier will distinguish peer-reviewed publications, preprints, datasets, and software or official documentation. Evidence grades will describe source suitability for this computational-physics literature task rather than mechanically applying biomedical study-design levels.

## Document Structure

The DOCX will use the following structure:

1. Title and scope statement.
2. Search strategy, inclusion criteria, exclusion criteria, and verification date.
3. Thematic roadmap explaining how each evidence area supports the planned paper.
4. Annotated source catalogue grouped by evidence area. Each annotation will state the source type, verification route, project relevance, central contribution, and recommended manuscript use.
5. Coverage and gap analysis identifying well-supported claims and areas that still need experimental evidence or newer literature.
6. Formal numbered reference list matching the reference style of `Group-Report.pdf`.
7. Search limitations and an AI-assistance disclosure.

## Visual Design

The document will use the Documents skill's `compact_reference_guide` preset because the content is a dense research reference. It will use US Letter portrait pages, restrained academic typography, clear heading hierarchy, generous margins, and page numbers. Repeated metadata will be presented as compact labeled paragraphs rather than prose-heavy tables. Tables will be used only for genuinely comparative information, such as the coverage matrix.

## Quality Gates

The deliverable is complete only when all of the following are true:

- Approximately 30 relevant sources are included, with no fabricated or unresolved reference.
- Core project sources and benchmark sources are represented.
- Every entry records a verification route and manuscript use.
- Published/preprint duplicates are resolved consistently.
- The final bibliography uses bracketed sequential numbering and complete identifiers.
- The DOCX contains no internal tool citation tokens or placeholders.
- The DOCX is rendered to PNG pages and every page is visually inspected for clipping, overlap, broken tables, missing glyphs, and poor page breaks.
- A final structural check confirms that the reference count, annotations, URLs, and section headings match the verified source corpus.

## Explicit Boundaries

This task will not draft the full paper, claim that planned experiments have been completed, or treat benchmark improvements as scientifically significant without comparable protocols and uncertainty. It will not download large datasets or reproduce model training. It will not include unverifiable references for apparent completeness.
