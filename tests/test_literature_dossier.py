from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "docs" / "references" / "literature-dossier" / "source-corpus.json"
AUDIT = ROOT / "docs" / "references" / "literature-dossier" / "search-audit.md"
REQUIRED_THEMES = {
    "jet_foundation_models",
    "datasets_and_top_tagging",
    "particle_set_architectures",
    "feature_representation",
    "pretraining_and_transfer",
    "evaluation_and_reproducibility",
    "generation_and_anomaly_detection",
}
VALID_SOURCE_TYPES = {
    "peer_reviewed",
    "preprint",
    "dataset",
    "official_documentation",
}
VALID_MANUSCRIPT_USES = {
    "Introduction",
    "Related Work",
    "Methods",
    "Evaluation",
    "Limitations",
    "Future Work",
}


def load_corpus() -> dict[str, object]:
    return json.loads(CORPUS.read_text(encoding="utf-8"))


class LiteratureDossierTests(unittest.TestCase):
    def test_verified_corpus_contract(self) -> None:
        corpus = load_corpus()
        metadata = corpus["metadata"]
        sources = corpus["sources"]

        self.assertEqual(metadata["search_date"], "2026-07-15")
        self.assertEqual(metadata["reference_style"], "Group-Report numbered style")
        self.assertGreaterEqual(len(sources), 28)
        self.assertLessEqual(len(sources), 35)
        self.assertEqual({source["theme"] for source in sources}, REQUIRED_THEMES)
        self.assertEqual(len({source["citation_key"] for source in sources}), len(sources))
        self.assertEqual(len({source["title"].casefold() for source in sources}), len(sources))

        dois = [source["doi"].casefold() for source in sources if source.get("doi")]
        self.assertEqual(len(dois), len(set(dois)))

        for source in sources:
            with self.subTest(citation_key=source["citation_key"]):
                self.assertEqual(source["verification_status"], "verified")
                self.assertTrue(source["authors"])
                self.assertTrue(source["title"])
                self.assertGreaterEqual(source["year"], 1980)
                self.assertLessEqual(source["year"], 2026)
                self.assertIn(source["source_type"], VALID_SOURCE_TYPES)
                self.assertTrue(source["verification_url"].startswith("https://"))
                self.assertTrue(source["url"].startswith("https://"))
                self.assertTrue(source["verification_route"])
                self.assertTrue(source["evidence_grade"])
                self.assertTrue(source["project_relevance"])
                self.assertTrue(source["central_contribution"])
                self.assertIn(source["manuscript_use"], VALID_MANUSCRIPT_USES)
                self.assertTrue(source["limitations"])
                if source.get("doi"):
                    self.assertRegex(source["doi"], re.compile(r"10\.\d{4,9}/\S+"))

    def test_search_audit_covers_every_source(self) -> None:
        audit = AUDIT.read_text(encoding="utf-8")
        corpus = load_corpus()

        for source in corpus["sources"]:
            with self.subTest(citation_key=source["citation_key"]):
                self.assertIn(source["citation_key"], audit)

        for heading in (
            "## Search Strategy",
            "## Inclusion and Exclusion Criteria",
            "## Source Verification Log",
            "## Deduplication and Version Decisions",
            "## Excluded Candidates",
            "## Search Limitations",
        ):
            self.assertIn(heading, audit)


if __name__ == "__main__":
    unittest.main()
