# particleML Literature Reference Dossier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a verified, publication-oriented DOCX literature reference dossier for the particleML paper project, using the numbered reference style observed in `Group-Report.pdf`.

**Architecture:** Store normalized and verified bibliographic records in a machine-readable JSON corpus, validate the corpus deterministically, and generate the DOCX from that corpus with a dedicated Python builder. Render the DOCX to PNG pages and audit both document structure and every rendered page before delivery.

**Tech Stack:** Direct HTTPS requests to arXiv, INSPIRE-HEP, Crossref/DOI, publishers, and official repositories; bundled Python 3; `python-docx`; standard-library `unittest`; the Documents skill renderer; LibreOffice.

## Global Constraints

- All repository artifacts, prose, code, and comments must be in English.
- Do not use a webservice abstraction; issue direct HTTP or HTTPS requests.
- Do not include a reference whose existence or metadata cannot be confirmed.
- Prefer published versions over duplicate preprints while retaining useful arXiv identifiers.
- Use approximately 30 high-value sources and cover all seven evidence areas in the approved design.
- Use bracketed sequential numbering and complete author/title/venue/year/DOI/arXiv/URL metadata in the formal bibliography.
- Do not claim that planned experiments are complete.
- Do not use subagents without explicit human confirmation; execute this plan inline by default.
- Use the bundled Python runtime at `C:\Users\xulei\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
- Use standard-library `unittest` because neither available Python runtime includes `pytest`; run existing project tests with the system Python and DOCX-specific tests with the bundled Python runtime.
- Render and visually inspect every final DOCX page before delivery.

---

## File Map

- Create: `docs/references/literature-dossier/source-corpus.json` - normalized verified source records and annotations.
- Create: `docs/references/literature-dossier/search-audit.md` - reproducible search queries, verification endpoints, inclusion/exclusion notes, and deduplication record.
- Create: `docs/references/literature-dossier/build_literature_dossier.py` - corpus validator and DOCX generator.
- Create: `tests/test_literature_dossier.py` - structural and corpus-integrity tests.
- Create: `docs/references/particleml-literature-reference-dossier.docx` - final user-facing deliverable.
- Create temporarily: `.codex-tmp/literature-dossier-render/` - internal PNG/PDF render output; do not deliver it.

## Task 1: Freeze the Corpus Contract and Candidate Pool

**Files:**
- Create: `tests/test_literature_dossier.py`
- Create: `docs/references/literature-dossier/source-corpus.json`

**Interfaces:**
- Consumes: approved design at `docs/superpowers/specs/2026-07-15-particleml-literature-reference-dossier-design.md`.
- Produces: a JSON object with top-level `metadata` and `sources`; every source has a stable `citation_key` used by the builder and tests.

- [ ] **Step 1: Write the corpus-contract test**

```python
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "docs" / "references" / "literature-dossier" / "source-corpus.json"
REQUIRED_THEMES = {
    "jet_foundation_models",
    "datasets_and_top_tagging",
    "particle_set_architectures",
    "feature_representation",
    "pretraining_and_transfer",
    "evaluation_and_reproducibility",
    "generation_and_anomaly_detection",
}


def load_corpus():
    return json.loads(CORPUS.read_text(encoding="utf-8"))


class LiteratureDossierTests(unittest.TestCase):
  def test_verified_corpus_contract(self):
    corpus = load_corpus()
    sources = corpus["sources"]
    assert 28 <= len(sources) <= 35
    assert {source["theme"] for source in sources} == REQUIRED_THEMES
    assert len({source["citation_key"] for source in sources}) == len(sources)
    assert len({source["title"].casefold() for source in sources}) == len(sources)
    dois = [source["doi"].casefold() for source in sources if source.get("doi")]
    assert len(dois) == len(set(dois))
    for source in sources:
        assert source["verification_status"] == "verified"
        assert source["authors"]
        assert source["title"]
        assert 1980 <= source["year"] <= 2026
        assert source["source_type"] in {
            "peer_reviewed", "preprint", "dataset", "official_documentation"
        }
        assert source["verification_url"].startswith("https://")
        assert source["url"].startswith("https://")
        assert source["project_relevance"]
        assert source["central_contribution"]
        assert source["manuscript_use"] in {
            "Introduction", "Related Work", "Methods", "Evaluation",
            "Limitations", "Future Work"
        }
        if source.get("doi"):
            assert re.fullmatch(r"10\.\d{4,9}/\S+", source["doi"])
```

- [ ] **Step 2: Run the test and verify that it fails before the corpus exists**

Run:

```powershell
python -m unittest tests.test_literature_dossier.LiteratureDossierTests.test_verified_corpus_contract -v
```

Expected: ERROR because `source-corpus.json` does not exist; this is the intentional RED state for the missing data artifact.

- [ ] **Step 3: Use this exact candidate pool for direct verification**

The initial pool is deliberately larger than the final target so failed or weak entries can be removed without reducing coverage:

1. OmniLearn.
2. OmniJet-alpha.
3. OmniLearned.
4. Enhancing next-token-prediction pretraining for jet foundation models.
5. Aspen Open Jets.
6. Particle Transformer for Jet Tagging.
7. ParticleNet.
8. Energy Flow Networks / Particle Flow Networks.
9. Deep Sets.
10. Set Transformer.
11. Point cloud transformers applied to collider physics / PET.
12. LorentzNet.
13. N-subjettiness.
14. The Machine Learning Landscape of Top Taggers.
15. JetClass official Zenodo record.
16. JetNet.
17. Representation learning for jets through contrastive learning / JetCLR.
18. A general transfer-learning survey by Pan and Yang.
19. Transferability of features in deep neural networks by Yosinski et al.
20. On the Opportunities and Risks of Foundation Models.
21. Neural scaling laws by Kaplan et al.
22. Denoising Diffusion Probabilistic Models.
23. PC-JeDi.
24. EPiC-GAN.
25. DijetGAN.
26. LHC hadronic jet generation with convolutional VAEs and normalizing flows.
27. Classification without labels.
28. CWoLa hunting.
29. The LHC Olympics 2020 community anomaly-detection challenge report.
30. Evaluation metrics and statistical tests for machine learning by Rainio et al.
31. DeLong et al. on correlated ROC curves.
32. Dietterich on approximate statistical tests for classification algorithms.
33. Nadeau and Bengio on generalization-error variance.
34. Improving reproducibility in machine learning research.
35. Machine learning at the energy and intensity frontiers of particle physics.

For each candidate, use DOI metadata when available and arXiv/INSPIRE for HEP preprints. Remove a candidate if authoritative metadata cannot be confirmed or if its contribution is redundant. The final corpus must retain 28-35 entries and all seven themes.

- [ ] **Step 4: Create the corpus using the fixed schema**

Use this exact source-object schema for every entry:

```json
{
  "citation_key": "stable_author_year_slug",
  "theme": "jet_foundation_models",
  "source_type": "peer_reviewed",
  "authors": ["Family, Given", "Family, Given"],
  "title": "Complete title",
  "year": 2025,
  "venue": "Complete venue name",
  "volume": "111",
  "issue": "5",
  "pages_or_article": "054015",
  "doi": "10.1103/PhysRevD.111.054015",
  "arxiv": "2404.16091",
  "url": "https://doi.org/10.1103/PhysRevD.111.054015",
  "verification_url": "https://api.crossref.org/works/10.1103/PhysRevD.111.054015",
  "verification_status": "verified",
  "verification_route": "Crossref DOI metadata and arXiv abstract record",
  "evidence_grade": "Core peer-reviewed primary source",
  "project_relevance": "Direct foundation-model architecture and transfer-learning reference.",
  "central_contribution": "Introduces the continuous PET-based multi-task framework used by the project.",
  "manuscript_use": "Related Work",
  "limitations": "The paper's benchmark protocol is not identical to the project's controlled feature ablation."
}
```

Top-level metadata must record `title`, `scope`, `search_date` as `2026-07-15`, `reference_style` as `Group-Report numbered style`, and the authoritative endpoints used.

- [ ] **Step 5: Run the corpus-contract test**

Run the `unittest` command from Step 2.

Expected: PASS with one passed test.

- [ ] **Step 6: Commit the frozen corpus contract and corpus**

```powershell
git add tests/test_literature_dossier.py docs/references/literature-dossier/source-corpus.json
git commit -m "docs: add verified particleML literature corpus"
```

## Task 2: Document the Reproducible Search and Verification Audit

**Files:**
- Create: `docs/references/literature-dossier/search-audit.md`
- Modify: `tests/test_literature_dossier.py`

**Interfaces:**
- Consumes: all `verification_url` and `verification_route` fields from the corpus.
- Produces: a human-readable audit with enough endpoint and query detail to repeat the search.

- [ ] **Step 1: Add an audit-coverage test**

```python
AUDIT = ROOT / "docs" / "references" / "literature-dossier" / "search-audit.md"


def test_search_audit_covers_every_source(self):
    audit = AUDIT.read_text(encoding="utf-8")
    corpus = load_corpus()
    for source in corpus["sources"]:
        assert source["citation_key"] in audit
    for heading in (
        "## Search Strategy",
        "## Inclusion and Exclusion Criteria",
        "## Source Verification Log",
        "## Deduplication and Version Decisions",
        "## Search Limitations",
    ):
        assert heading in audit
```

- [ ] **Step 2: Run the new test and verify that it fails**

Run:

```powershell
python -m unittest tests.test_literature_dossier.LiteratureDossierTests.test_search_audit_covers_every_source -v
```

Expected: FAIL because `search-audit.md` does not exist.

- [ ] **Step 3: Write the audit from recorded HTTP evidence**

The audit must list the search date, exact query families, endpoints, inclusion/exclusion rules, one verification-log line per `citation_key`, and explicit published-versus-preprint decisions. Record failed candidates and why they were excluded. Do not claim full-text verification unless the full source was actually inspected.

- [ ] **Step 4: Run both corpus and audit tests**

Run:

```powershell
python -m unittest tests.test_literature_dossier -v
```

Expected: both tests PASS.

- [ ] **Step 5: Commit the audit**

```powershell
git add tests/test_literature_dossier.py docs/references/literature-dossier/search-audit.md
git commit -m "docs: record literature search and verification audit"
```

## Task 3: Build the DOCX Generator

**Files:**
- Create: `docs/references/literature-dossier/build_literature_dossier.py`
- Modify: `tests/test_literature_dossier.py`
- Create: `docs/references/particleml-literature-reference-dossier.docx`

**Interfaces:**
- Consumes: `source-corpus.json` and `search-audit.md`.
- Produces: `particleml-literature-reference-dossier.docx` and exposes `validate_corpus`, `format_reference`, and `build_document` functions.

- [ ] **Step 1: Add formatter and DOCX-structure tests**

```python
import importlib.util
from docx import Document

BUILDER = ROOT / "docs" / "references" / "literature-dossier" / "build_literature_dossier.py"
OUTPUT = ROOT / "docs" / "references" / "particleml-literature-reference-dossier.docx"


def load_builder():
    spec = importlib.util.spec_from_file_location("literature_dossier_builder", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reference_formatter_matches_numbered_style(self):
    builder = load_builder()
    source = load_corpus()["sources"][0]
    rendered = builder.format_reference(1, source)
    assert rendered.startswith("[1] ")
    assert source["title"] in rendered
    if source.get("doi"):
        assert f"doi: {source['doi']}" in rendered
    if source.get("arxiv"):
        assert f"arXiv: {source['arxiv']}" in rendered


def test_generated_docx_has_required_sections_and_reference_count(self):
    document = Document(OUTPUT)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    for heading in (
        "Search Strategy and Selection",
        "Thematic Roadmap",
        "Annotated Source Catalogue",
        "Coverage and Research Gaps",
        "References",
        "Search Limitations and Disclosure",
    ):
        assert heading in text
    sources = load_corpus()["sources"]
    assert sum(1 for paragraph in document.paragraphs if re.match(r"^\[\d+\] ", paragraph.text)) == len(sources)
```

- [ ] **Step 2: Run the formatter test and verify that it fails**

Run:

```powershell
& 'C:\Users\xulei\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_literature_dossier.LiteratureDossierTests.test_reference_formatter_matches_numbered_style -v
```

Expected: FAIL because the builder does not exist.

- [ ] **Step 3: Implement the builder**

The builder must:

1. Load and validate the corpus before writing.
2. Use US Letter portrait with 1-inch margins.
3. Apply the Documents skill `compact_reference_guide` numeric tokens after reading `references/design_presets.md`.
4. Create a concise title block, footer page numbers, real heading styles, and real numbered/bulleted lists where lists are used.
5. Create one thematic coverage table with explicit fixed geometry and repeated header rows.
6. Create grouped annotated entries with source type, evidence grade, verification route, contribution, project relevance, manuscript use, and limitation.
7. Format the final bibliography with `[n]` prefixes and hanging indents; include DOI, arXiv, and stable URL only when present in the verified corpus.
8. Add search limitations and this disclosure: `AI-assisted tools were used for literature discovery, metadata normalization, source verification support, and document formatting. All included references were checked against the authoritative records identified in the verification audit; inclusion does not imply that every full text has been read by the researcher.`
9. Write atomically to the final DOCX path and fail on validation errors.

Use this formatter logic exactly:

```python
def format_reference(number, source):
    authors = ", ".join(source["authors"])
    venue = source.get("venue", "")
    details = []
    if source.get("volume"):
        details.append(f"vol. {source['volume']}")
    if source.get("issue"):
        details.append(f"no. {source['issue']}")
    if source.get("pages_or_article"):
        details.append(source["pages_or_article"])
    publication = ", ".join(part for part in [venue, *details, str(source["year"])] if part)
    identifiers = []
    if source.get("doi"):
        identifiers.append(f"doi: {source['doi']}")
    if source.get("arxiv"):
        identifiers.append(f"arXiv: {source['arxiv']}")
    identifiers.append(f"url: {source['url']}")
    return f"[{number}] {authors}. \"{source['title']}.\" {publication}. " + ". ".join(identifiers) + "."
```

- [ ] **Step 4: Generate the DOCX**

Run:

```powershell
& 'C:\Users\xulei\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' docs/references/literature-dossier/build_literature_dossier.py
```

Expected: exit code 0 and a non-empty `docs/references/particleml-literature-reference-dossier.docx`.

- [ ] **Step 5: Run all structural tests**

Run:

```powershell
& 'C:\Users\xulei\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_literature_dossier -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit the builder and first DOCX**

```powershell
git add docs/references/literature-dossier/build_literature_dossier.py tests/test_literature_dossier.py docs/references/particleml-literature-reference-dossier.docx
git commit -m "docs: generate particleML literature reference dossier"
```

## Task 4: Render, Inspect, Revise, and Complete the Audit

**Files:**
- Modify as needed: `docs/references/literature-dossier/build_literature_dossier.py`
- Regenerate: `docs/references/particleml-literature-reference-dossier.docx`
- Create temporarily: `.codex-tmp/literature-dossier-render/page-*.png`

**Interfaces:**
- Consumes: structurally passing DOCX.
- Produces: visually verified final DOCX with no QA intermediates included in delivery.

- [ ] **Step 1: Render the DOCX to PNG and PDF for internal QA**

Run:

```powershell
New-Item -ItemType Directory -Force -Path '.codex-tmp/literature-dossier-render' | Out-Null
& 'C:\Users\xulei\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Users\xulei\.codex\plugins\cache\openai-primary-runtime\documents\26.709.11516\skills\documents\render_docx.py' 'D:\code\particleML\docs\references\particleml-literature-reference-dossier.docx' --output_dir 'D:\code\particleML\.codex-tmp\literature-dossier-render' --emit_pdf
```

Expected: one `page-N.png` per page and a non-empty PDF.

- [ ] **Step 2: Inspect every PNG at full readable resolution**

Check every page for clipped text, overlap, broken or over-wide tables, missing glyphs, inconsistent headings, awkward page breaks, cramped annotation blocks, isolated headings, malformed URLs, and reference-list hanging indents. Record the page count and any defect in working notes.

- [ ] **Step 3: Revise and re-render until every page passes**

Make layout fixes only in the builder, regenerate the DOCX, rerun `unittest`, rerender all pages, and reinspect every page. Repeat until no visual defect remains.

- [ ] **Step 4: Run final requirement-by-requirement checks**

Run:

```powershell
& 'C:\Users\xulei\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_literature_dossier -v
Get-Item 'docs/references/particleml-literature-reference-dossier.docx' | Select-Object FullName,Length,LastWriteTime
git status --short
```

Confirm: 28-35 verified sources; all seven themes; all formal references numbered; no unresolved identifiers; core OmniLearn/OmniJet/OmniLearned, JetClass, top-tagging, architecture, feature, transfer, evaluation, generation, and anomaly-detection coverage; every rendered page inspected.

- [ ] **Step 5: Commit any final QA revisions**

```powershell
git add docs/references/particleml-literature-reference-dossier.docx docs/references/literature-dossier/build_literature_dossier.py
git commit -m "docs: finalize verified literature reference dossier"
```

- [ ] **Step 6: Deliver exactly one link to the final DOCX**

The user-facing final response must link only `docs/references/particleml-literature-reference-dossier.docx`, briefly state the verified reference count and render result, and omit internal render files and builder links.
