from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORPUS_PATH = ROOT / "docs" / "references" / "literature-dossier" / "source-corpus.json"
OUTPUT_PATH = ROOT / "docs" / "references" / "particleml-literature-reference-dossier.md"

THEME_ORDER = [
    "jet_foundation_models",
    "datasets_and_top_tagging",
    "particle_set_architectures",
    "feature_representation",
    "pretraining_and_transfer",
    "evaluation_and_reproducibility",
    "generation_and_anomaly_detection",
]

THEME_LABELS = {
    "jet_foundation_models": "Jet Foundation Models",
    "datasets_and_top_tagging": "Datasets and Top Tagging",
    "particle_set_architectures": "Particle-Set Architectures",
    "feature_representation": "Feature Representation and Physics Priors",
    "pretraining_and_transfer": "Pretraining and Transfer",
    "evaluation_and_reproducibility": "Evaluation and Reproducibility",
    "generation_and_anomaly_detection": "Generation and Anomaly Detection",
}

THEME_ROADMAP = {
    "jet_foundation_models": (
        "Defines the OmniLearn/OmniLearned and OmniJet lineages, multi-task claims, and current pretraining directions.",
        "Introduction; Related Work",
    ),
    "datasets_and_top_tagging": (
        "Establishes JetClass provenance, binary top-tagging context, and community benchmark expectations.",
        "Introduction; Methods",
    ),
    "particle_set_architectures": (
        "Explains permutation-invariant, attention, graph, PET, and Lorentz-equivariant backbones.",
        "Related Work; Methods",
    ),
    "feature_representation": (
        "Connects particle-level information, IRC safety, symmetry, and learned low-level representations.",
        "Introduction; Methods",
    ),
    "pretraining_and_transfer": (
        "Supplies transfer-learning terminology, feature-transfer evidence, and the foundation-model frame.",
        "Introduction; Methods",
    ),
    "evaluation_and_reproducibility": (
        "Supports AUC comparison, dependence-aware uncertainty, repeated runs, and reproducible reporting.",
        "Evaluation; Limitations",
    ),
    "generation_and_anomaly_detection": (
        "Places the tagging study within the wider multi-task jet-foundation-model agenda.",
        "Related Work; Future Work",
    ),
}

SECTION_ORDER = [
    "References",
    "Annotated Source Catalogue",
    "Coverage and Research Gaps",
    "Thematic Roadmap",
    "Search Strategy and Selection",
    "Search Limitations and Disclosure",
]


def load_corpus(path: Path = CORPUS_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_corpus(corpus: dict[str, Any]) -> None:
    errors: list[str] = []
    sources = corpus.get("sources", [])
    metadata = corpus.get("metadata", {})

    if metadata.get("search_date") != "2026-07-15":
        errors.append("metadata.search_date must be 2026-07-15")
    if metadata.get("reference_style") != "Group-Report numbered style":
        errors.append("metadata.reference_style is incorrect")
    if not 28 <= len(sources) <= 35:
        errors.append("source count must be between 28 and 35")

    keys = [source.get("citation_key", "") for source in sources]
    titles = [source.get("title", "").casefold() for source in sources]
    dois = [source.get("doi", "").casefold() for source in sources if source.get("doi")]
    if len(keys) != len(set(keys)):
        errors.append("citation keys must be unique")
    if len(titles) != len(set(titles)):
        errors.append("titles must be unique")
    if len(dois) != len(set(dois)):
        errors.append("DOIs must be unique")
    if {source.get("theme") for source in sources} != set(THEME_ORDER):
        errors.append("all seven themes must be represented")

    required = {
        "citation_key",
        "theme",
        "source_type",
        "authors",
        "title",
        "year",
        "venue",
        "url",
        "verification_url",
        "verification_status",
        "verification_route",
        "evidence_grade",
        "project_relevance",
        "central_contribution",
        "manuscript_use",
        "limitations",
    }
    for index, source in enumerate(sources, start=1):
        missing = sorted(key for key in required if not source.get(key))
        if missing:
            errors.append(f"source {index} is missing required values: {', '.join(missing)}")
        if source.get("verification_status") != "verified":
            errors.append(f"source {index} is not verified")
        doi = source.get("doi", "")
        if doi and not re.fullmatch(r"10\.\d{4,9}/\S+", doi):
            errors.append(f"source {index} has an invalid DOI")

    if errors:
        raise ValueError("Invalid source corpus:\n- " + "\n- ".join(errors))


def _display_author(name: str) -> str:
    if name.casefold() == "et al.":
        return "et al."
    if "," not in name:
        return name
    family, given = (part.strip() for part in name.split(",", 1))
    return f"{given} {family}".strip()


def format_authors(authors: list[str]) -> str:
    displayed = [_display_author(author) for author in authors]
    if displayed and displayed[-1] == "et al.":
        return ", ".join(displayed[:-1]) + ", et al."
    if len(displayed) > 6:
        return ", ".join(displayed[:3]) + ", et al."
    if len(displayed) == 1:
        return displayed[0]
    if len(displayed) == 2:
        return f"{displayed[0]} and {displayed[1]}"
    return ", ".join(displayed[:-1]) + f", and {displayed[-1]}"


def format_reference(number: int, source: dict[str, Any]) -> str:
    authors = format_authors(source["authors"])
    author_sentence = authors if authors.endswith(".") else f"{authors}."
    venue = source.get("venue", "")
    details: list[str] = []
    volume = str(source.get("volume", ""))
    if volume and not re.search(rf"(?<!\d){re.escape(volume)}(?!\d)", venue):
        details.append(volume)
    if source.get("issue"):
        details[-1] = f"{details[-1]}.{source['issue']}" if details else str(source["issue"])
    if source.get("pages_or_article"):
        details.append(str(source["pages_or_article"]))

    publication_bits = [venue]
    if details:
        publication_bits.append(", ".join(details))
    publication_bits.append(f"({source['year']})")
    publication = " ".join(bit for bit in publication_bits if bit)

    identifiers: list[str] = []
    if source.get("doi"):
        identifiers.append(f"doi: {source['doi']}")
    if source.get("arxiv"):
        identifiers.append(f"arXiv: {source['arxiv']}")
    identifiers.append(f"url: {source['url']}")
    return (
        f"[{number}] {author_sentence} \"{source['title']}.\" In: {publication}. "
        + ". ".join(identifiers)
        + "."
    )


def _table_cell(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _labeled(label: str, value: str) -> str:
    return f"**{label}:** {value}"


def _source_type_label(source_type: str) -> str:
    return {
        "peer_reviewed": "Peer-reviewed publication",
        "preprint": "Verified preprint or report",
        "dataset": "Authoritative dataset record",
        "official_documentation": "Official documentation",
    }[source_type]


def _reorder_top_level_sections(lines: list[str]) -> list[str]:
    preamble: list[str] = []
    sections: dict[str, list[str]] = {}
    current_title: str | None = None

    for line in lines:
        if line.startswith("## "):
            current_title = line.removeprefix("## ")
            if current_title in sections:
                raise ValueError(f"Duplicate top-level section: {current_title}")
            sections[current_title] = [line]
        elif current_title is None:
            preamble.append(line)
        else:
            sections[current_title].append(line)

    missing = [title for title in SECTION_ORDER if title not in sections]
    unexpected = [title for title in sections if title not in SECTION_ORDER]
    if missing or unexpected:
        raise ValueError(
            f"Top-level section mismatch; missing={missing}, unexpected={unexpected}"
        )

    ordered = preamble
    for title in SECTION_ORDER:
        ordered.extend(sections[title])
    return ordered


def render_markdown(corpus: dict[str, Any]) -> str:
    validate_corpus(corpus)
    sources = corpus["sources"]
    source_count = len(sources)
    lines: list[str] = [
        "# Literature Reference Dossier",
        "",
        "*Jet foundation models, particle-level feature availability, and JetClass top tagging*",
        "",
        f"**Verified sources:** {source_count}  ",
        "**Search date:** 15 July 2026",
        "",
        _labeled(
            "Purpose",
            "This dossier supplies a verified literature base for a publication-oriented study of how "
            "nested particle-level feature sets affect fine-tuning of an OmniLearned/PET-style backbone "
            "on JetClass binary top-versus-QCD tagging. It is a source map and reference catalogue, not "
            "a substitute for reading the cited papers.",
        ),
        "",
        _labeled(
            "How to use it",
            "Start with the thematic roadmap, use the annotations to select evidence for a manuscript "
            "section, then cite the formal numbered reference list after checking the complete source.",
        ),
        "",
        "## Search Strategy and Selection",
        "",
        "A targeted scoping search was conducted on 15 July 2026 using project seed sources and direct "
        "HTTPS queries to Crossref, arXiv, INSPIRE-HEP, Zenodo, and official proceedings or journal "
        f"pages. The final corpus contains **{source_count} sources**. Every final verification endpoint "
        "returned HTTP 200, and every DOI, arXiv identifier, title, author set, and year was checked "
        "against an authoritative record.",
        "",
        _labeled(
            "Inclusion",
            "Direct relevance to a planned paper section; resolvable authoritative metadata; a distinct "
            "scientific role; primary peer-reviewed evidence when available; and explicit preprint labels.",
        ),
        "",
        _labeled(
            "Exclusion",
            "Unresolved or mismatched metadata, duplicate versions, secondary summaries, indirect general "
            "relevance, and sources redundant with stronger project-aligned evidence.",
        ),
        "",
        _labeled(
            "Verification boundary",
            "Bibliographic existence and record-level claims were checked. Full-text reading is not claimed "
            "for every source; core papers must be read before claim-level manuscript citation.",
        ),
        "",
        "## Thematic Roadmap",
        "",
        "The themes below map the verified corpus to the planned paper. Counts refer to each source's "
        "primary theme; several sources can support more than one manuscript section.",
        "",
        "**Table 1. Literature coverage by evidence theme.**",
        "",
        "| Evidence theme | Sources | Primary contribution | Manuscript use |",
        "|---|---:|---|---|",
    ]

    counts = Counter(source["theme"] for source in sources)
    for theme in THEME_ORDER:
        focus, manuscript_use = THEME_ROADMAP[theme]
        lines.append(
            "| "
            + " | ".join(
                _table_cell(value)
                for value in (THEME_LABELS[theme], counts[theme], focus, manuscript_use)
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "*Coverage is strongest for the model lineage, particle-set architectures, and evaluation "
            "methods. The central unresolved question is the controlled effect of downstream feature "
            "availability under a fixed pretrained checkpoint and data protocol.*",
            "",
            "## Annotated Source Catalogue",
            "",
            "Entries are grouped by their primary evidence role. Source numbers match the formal reference "
            "list. Annotations separate what a source contributes from how it should be used and from the "
            "limits of that use.",
        ]
    )

    numbered = {source["citation_key"]: index for index, source in enumerate(sources, start=1)}
    for theme in THEME_ORDER:
        lines.extend(["", f"### {THEME_LABELS[theme]}"])
        for source in (item for item in sources if item["theme"] == theme):
            number = numbered[source["citation_key"]]
            source_and_evidence = (
                f"{_source_type_label(source['source_type'])}; {source['evidence_grade']}."
            )
            lines.extend(
                [
                    "",
                    f"#### Source {number} | {source['title']}",
                    "",
                    f"*{format_authors(source['authors'])} ({source['year']}). {source['venue']}.*",
                    "",
                    f"- {_labeled('Source and evidence', source_and_evidence)}",
                    f"- {_labeled('Verification', source['verification_route'])}",
                    f"- {_labeled('Central contribution', source['central_contribution'])}",
                    f"- {_labeled('Project relevance', source['project_relevance'])}",
                    f"- {_labeled('Recommended manuscript use', source['manuscript_use'])}",
                    f"- {_labeled('Limitation', source['limitations'])}",
                ]
            )

    lines.extend(
        [
            "",
            "## Coverage and Research Gaps",
            "",
            "The literature strongly supports the existence of transferable jet representations, the "
            "importance of permutation-aware particle-set models, and the use of JetClass as a large-scale "
            "benchmark. It does not yet answer the project's central causal comparison.",
            "",
        ]
    )
    gaps = [
        (
            "Matched feature-ablation evidence",
            "No retained study isolates nested particle-level feature groups while keeping the raw "
            "JetClass files, split, pretrained checkpoint, training schedule, and evaluation pipeline fixed.",
        ),
        (
            "Checkpoint and pretraining overlap",
            "The paper must document the OmniLearned checkpoint's pretraining corpus and avoid claiming "
            "out-of-domain transfer if JetClass or the same top/QCD task family appears in pretraining.",
        ),
        (
            "Feature-schema validity",
            "Config D remains publication-ready only if every impact-parameter feature is traced to a real "
            "JetClass column and passes leakage, masking, and transformation audits.",
        ),
        (
            "Independent validation",
            "Most model-family evidence is authored by the teams introducing the methods. A simple fixed "
            "Deep Sets/PFN baseline and independent reproduction strengthen feature-ranking claims.",
        ),
        (
            "Uncertainty and dependence",
            "AUC intervals on one test set do not replace repeated-seed uncertainty. Nested data sizes and "
            "shared examples create dependence that must be reflected in comparisons.",
        ),
        (
            "External and multi-task generalization",
            "Generation, anomaly detection, and transfer to other detector domains remain future work until "
            "the core JetClass feature-ablation result is stable.",
        ),
    ]
    lines.extend(f"- {_labeled(label, value)}" for label, value in gaps)

    lines.extend(
        [
            "",
            "## References",
            "",
            "Numbered format follows the reference presentation in Group-Report.pdf. DOI and arXiv fields "
            "are included only when confirmed in the verified corpus.",
            "",
        ]
    )
    for number, source in enumerate(sources, start=1):
        lines.extend([format_reference(number, source), ""])

    lines.extend(
        [
            "## Search Limitations and Disclosure",
            "",
        ]
    )
    limitations = [
        "This is a targeted scoping review aligned with the current research plan, not an exhaustive "
        "systematic review or meta-analysis.",
        "Authoritative metadata and abstracts were checked, but record verification is not a claim that "
        "every full text has been read end to end.",
        "No subscription-only citation index was used, and literature published after 15 July 2026 is not "
        "represented.",
        "Recent preprints and new model releases should be refreshed immediately before manuscript submission.",
        "Statistical methods must be adapted to the dependence structure created by shared JetClass splits, "
        "nested training sizes, and repeated stochastic training runs.",
    ]
    lines.extend(f"{index}. {_labeled(f'Limitation {index}', value)}" for index, value in enumerate(limitations, start=1))
    lines.extend(
        [
            "",
            "### AI-Assistance Disclosure",
            "",
            "AI-assisted tools were used for literature discovery, metadata normalization, source verification "
            "support, and document formatting. All included references were checked against the authoritative "
            "records identified in the verification audit; inclusion does not imply that every full text has "
            "been read by the researcher.",
            "",
        ]
    )
    return "\n".join(_reorder_top_level_sections(lines))


def build_markdown(
    corpus_path: Path = CORPUS_PATH,
    output_path: Path = OUTPUT_PATH,
) -> Path:
    markdown = render_markdown(load_corpus(corpus_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(".tmp.md")
    if temporary.exists():
        temporary.unlink()
    temporary.write_text(markdown, encoding="utf-8", newline="\n")
    os.replace(temporary, output_path)
    return output_path


def build_document(
    corpus_path: Path = CORPUS_PATH,
    output_path: Path = OUTPUT_PATH,
) -> Path:
    """Backward-compatible alias for callers of the former DOCX builder."""
    return build_markdown(corpus_path=corpus_path, output_path=output_path)


def main() -> None:
    output = build_markdown()
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
