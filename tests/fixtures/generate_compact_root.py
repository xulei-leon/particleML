"""Generate compact ROOT fixtures on demand; no binary fixture is committed."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import awkward as ak
import numpy as np
import uproot


def default_jets() -> list[dict[str, Any]]:
    """Return a small two-class fixture spanning train, validation, and test."""

    base_particles = {
        "particle_pt": [10.0, 20.0, 20.0],
        "particle_eta": [0.2, 0.3, -0.1],
        "particle_phi": [3.12, -3.12, 0.4],
        "particle_energy": [12.0, 24.0, 25.0],
        "particle_charge": [1.0, 0.0, -1.0],
        "particle_pdg_id": [211, 22, -13],
        "particle_dxy": [0.01, 9.0, 8.0],
        "particle_dxy_error": [0.001, 9.0, 8.0],
        "particle_dz": [0.02, 9.0, 8.0],
        "particle_dz_error": [0.002, 9.0, 8.0],
        "particle_has_track_details": [True, False, False],
    }
    identities = [
        (18355, "root://example.invalid//store/test/file-8.root", "train", 0),
        (19980, "root://example.invalid//store/test/file-2.root", "train", 1),
        (18355, "root://example.invalid//store/test/file-0.root", "validation", 0),
        (19980, "root://example.invalid//store/test/file-7.root", "test", 1),
    ]
    jets: list[dict[str, Any]] = []
    for index, (record_id, pfn, split, target) in enumerate(identities, start=1):
        jets.append(
            {
                "record_id": record_id,
                "canonical_pfn": pfn,
                "run": index,
                "lumi": index + 10,
                "event": index + 100,
                "jet_index": 0,
                "split": split,
                "target": target,
                "jet_pt": 550.0 + index,
                "jet_eta": 0.1 * index,
                "jet_phi": 3.13 if index == 1 else 0.2,
                "pv_z": 0.01 * index,
                "n_vertices": 20 + index,
                **base_particles,
            }
        )
    return jets


def write_compact_root(path: Path, jets: list[dict[str, Any]] | None = None) -> Path:
    """Write the deterministic compact `jets` tree expected by M1-03."""

    rows = default_jets() if jets is None else jets
    jagged = [
        "particle_pt",
        "particle_eta",
        "particle_phi",
        "particle_energy",
        "particle_charge",
        "particle_pdg_id",
        "particle_dxy",
        "particle_dxy_error",
        "particle_dz",
        "particle_dz_error",
        "particle_has_track_details",
    ]
    branches: dict[str, object] = {}
    for name in rows[0]:
        values = [row[name] for row in rows]
        if name in jagged or name == "canonical_pfn" or name == "split":
            branches[name] = ak.Array(values)
        else:
            branches[name] = np.asarray(values)
    path.parent.mkdir(parents=True, exist_ok=True)
    with uproot.recreate(path) as root_file:
        root_file["jets"] = branches
    return path
