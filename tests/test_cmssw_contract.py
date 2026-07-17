from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CMSSW = ROOT / "cmssw" / "ParticleMLExtractor"


def test_cmssw_boundary_files_are_nonempty_and_buildfile_is_well_formed() -> None:
    build = CMSSW / "BuildFile.xml"
    plugin = CMSSW / "plugins" / "ParticleMLExtractor.cc"
    config = CMSSW / "python" / "extract_cfg.py"

    assert build.stat().st_size > 0
    assert plugin.stat().st_size > 0
    assert config.stat().st_size > 0
    ET.fromstring(f"<build>{build.read_text(encoding='utf-8')}</build>")
    compile(config.read_text(encoding="utf-8"), str(config), "exec")


def test_extractor_source_freezes_selection_truth_and_failure_contracts() -> None:
    source = (CMSSW / "plugins" / "ParticleMLExtractor.cc").read_text(encoding="utf-8")
    config = (CMSSW / "python" / "extract_cfg.py").read_text(encoding="utf-8")
    boundary = source + config

    for token in (
        "slimmedJetsAK8",
        "packedPFCandidates",
        "prunedGenParticles",
        "offlineSlimmedPrimaryVertices",
        "500.0",
        "1000.0",
        "2.0",
        "0.8",
        "isLastCopy",
        "hasTrackDetails",
        "original_daughter_index",
        "EXTRACT_MISSING_PRODUCT",
        "EXTRACT_DAUGHTER_RESOLUTION",
        "EXTRACT_INVALID_PRIMARY_VERTEX",
        "EXTRACT_NONFINITE",
        "EXTRACT_AMBIGUOUS_TRUTH",
    ):
        assert token in boundary
    assert "h5py" not in source
    assert "tensorflow" not in source.lower()
    assert "torch" not in source.lower()


def test_extraction_configuration_is_pinned_and_provenance_complete() -> None:
    config = (CMSSW / "python" / "extract_cfg.py").read_text(encoding="utf-8")

    for token in (
        "76X_mcRun2_asymptotic_RunIIFall15DR76_v1",
        "cmsopendata/cmssw_7_6_7-slc6_amd64_gcc493",
        "recordId",
        "canonicalPFN",
        "sourceManifestSha256",
        "gitCommit",
        "containerDigest",
        "isSignal",
    ):
        assert token in config
    assert "UNRESOLVED" in config


def test_e0_configs_keep_host_discovery_unresolved() -> None:
    host = (ROOT / "configs" / "e0" / "host-qualification.json").read_text(
        encoding="utf-8"
    )
    policy = (ROOT / "configs" / "e0" / "e0-audit-policy.json").read_text(
        encoding="utf-8"
    )

    assert '"status": "unresolved"' in host
    assert '"cost_reserve_fraction": 0.25' in policy
    assert '"charged_no_track_fraction_max": 0.01' in policy
    assert '"provisional_n_max_per_class": 100000' in policy
