"""Run one diagnostic OmniLearned fine-tune on a small real CMS 2015 artifact.

This script is intended for the particleML Jetson Docker image. Jetson cannot
decode RunIIFall15MiniAODv2 with the project's x86_64 CMSSW 7_6_7 boundary, so
the input URLs must point to a canonical HDF5 file and preprocessing JSON made
from those records on a qualified CMSSW host. The script downloads both files,
verifies their hashes and record identities, downloads the official pretrain_s
checkpoint, builds a tiny Config-A custom dataset, fine-tunes for one epoch,
evaluates it, and records latency. Its output is never formal E0-E3 evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
import urllib.request
import venv
from pathlib import Path
from typing import Any

import h5py  # type: ignore[import-untyped]
import numpy as np

from particleml.contracts import FeatureConfig
from particleml.views import SubsetJet, materialize_view, select_nested_subsets

OMNILEARNED_REVISION = "5091595d226b6021e967ab2ecfff832f40c026f6"
OMNILEARNED_ARCHIVE = (
    "https://github.com/ViniciusMikuni/OmniLearned/archive/"
    f"{OMNILEARNED_REVISION}.zip"
)
CHECKPOINT_URL = (
    "https://portal.nersc.gov/cfs/dasrepo/omnilearned/checkpoints/"
    "best_model_pretrain_s.pt"
)
CHECKPOINT_BYTES = 34_605_223
SIGNAL_RECORD_ID = 19980
QCD_RECORD_IDS = {18355, 18358, 18373, 18376, 18377}
SPLIT_SIZES = {"train": 32, "validation": 8, "test": 8}
OMNILEARNED_SPLITS = {"train": "train", "validation": "val", "test": "test"}
STORAGE_CAP_BYTES = 160 * 1024**3
DOWNLOAD_CAP_BYTES = 20 * 1024**3

OMNILEARNED_DEPENDENCIES = (
    "numpy==2.2.4",
    "h5py==3.13.0",
    "scikit-learn==1.6.1",
    "einops==0.8.1",
    "requests==2.32.3",
    "pytorch-optimizer==3.5.0",
    "torchdiffeq==0.2.5",
    "diffusers==0.32.2",
    "typer==0.15.2",
    "tqdm==4.67.1",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_size(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def validate_sha256(value: str, label: str) -> str:
    normalized = value.lower()
    if len(normalized) != 64 or any(char not in "0123456789abcdef" for char in normalized):
        raise ValueError(f"{label} must be a 64-character SHA-256")
    return normalized


def download(
    url: str,
    output: Path,
    *,
    expected_sha256: str | None = None,
    expected_bytes: int | None = None,
) -> dict[str, Any]:
    if not url.startswith("https://"):
        raise ValueError(f"download URL must use HTTPS: {url}")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        digest = sha256_file(output)
        size = output.stat().st_size
        if (expected_sha256 is None or digest == expected_sha256) and (
            expected_bytes is None or size == expected_bytes
        ):
            return {"url": url, "path": str(output), "bytes": size, "sha256": digest}
        raise RuntimeError(f"existing download has the wrong identity: {output}")

    request = urllib.request.Request(url, headers={"User-Agent": "particleML-jetson-smoke/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        declared = response.headers.get("Content-Length")
        declared_bytes = int(declared) if declared is not None else None
        if declared_bytes is not None and declared_bytes > DOWNLOAD_CAP_BYTES:
            raise RuntimeError(f"refusing {declared_bytes} byte download; per-file cap is 20 GiB")
        if directory_size(output.parents[1]) + (declared_bytes or 0) > STORAGE_CAP_BYTES:
            raise RuntimeError("the Jetson work directory would exceed the 160 GiB cap")
        temporary = output.with_suffix(output.suffix + ".part")
        digest = hashlib.sha256()
        size = 0
        try:
            with temporary.open("xb") as stream:
                while block := response.read(1024 * 1024):
                    size += len(block)
                    if size > DOWNLOAD_CAP_BYTES:
                        raise RuntimeError("download exceeded the 20 GiB per-file cap")
                    stream.write(block)
                    digest.update(block)
            observed = digest.hexdigest()
            if expected_bytes is not None and size != expected_bytes:
                raise RuntimeError(f"download size mismatch: expected {expected_bytes}, got {size}")
            if expected_sha256 is not None and observed != expected_sha256:
                raise RuntimeError(
                    f"download SHA-256 mismatch: expected {expected_sha256}, got {observed}"
                )
            temporary.replace(output)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    return {"url": url, "path": str(output), "bytes": size, "sha256": observed}


def install_omnilearned(work: Path) -> tuple[Path, float]:
    environment = work / "omnilearned-venv"
    python = environment / "bin" / "python"
    marker = environment / ".particleml-omnilearned-revision"
    if marker.is_file() and marker.read_text(encoding="utf-8").strip() == OMNILEARNED_REVISION:
        return python, 0.0

    started = time.monotonic()
    venv.EnvBuilder(with_pip=True, system_site_packages=True).create(environment)
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-cache-dir", *OMNILEARNED_DEPENDENCIES],
        check=True,
    )
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-cache-dir", "--no-deps", OMNILEARNED_ARCHIVE],
        check=True,
    )
    subprocess.run(
        [
            str(python),
            "-c",
            (
                "import torch; from packaging.version import Version; "
                "assert torch.cuda.is_available(), 'CUDA is unavailable'; "
                "assert Version(torch.__version__.split('+')[0]) >= Version('2.5.1'), "
                "f'OmniLearned needs torch>=2.5.1, found {torch.__version__}'"
            ),
        ],
        check=True,
    )
    marker.write_text(OMNILEARNED_REVISION + "\n", encoding="utf-8")
    return python, time.monotonic() - started


def inspect_canonical(canonical: Path) -> tuple[list[SubsetJet], dict[str, str], str]:
    with h5py.File(canonical, "r") as source:
        required = {
            "identity/jet_id",
            "identity/record_id",
            "labels/pid",
            "split/name",
            "particles/continuous",
            "particles/pid_type",
            "particles/mask",
        }
        missing = sorted(name for name in required if name not in source)
        if missing:
            raise RuntimeError(f"canonical HDF5 is missing {missing}")
        ids = source["identity/jet_id"].asstr()[:].tolist()
        records = np.asarray(source["identity/record_id"][:], dtype=np.int64)
        labels = np.asarray(source["labels/pid"][:], dtype=np.int8)
        splits = source["split/name"].asstr()[:].tolist()
        source_manifest_sha256 = str(source.attrs.get("source_manifest_sha256", ""))

    if not (len(ids) == len(records) == len(labels) == len(splits)):
        raise RuntimeError("canonical identity, label, record, and split lengths differ")
    for record, label in zip(records, labels, strict=True):
        if label == 1 and int(record) != SIGNAL_RECORD_ID:
            raise RuntimeError("signal jet is not from CMS record 19980")
        if label == 0 and int(record) not in QCD_RECORD_IDS:
            raise RuntimeError(f"QCD jet uses an unapproved CMS record: {record}")
        if label not in (0, 1):
            raise RuntimeError(f"unsupported class label: {label}")
    if len(source_manifest_sha256) != 64:
        raise RuntimeError("canonical file lacks a valid source_manifest_sha256")

    rows = [
        SubsetJet(int(record), jet_id, int(label))
        for jet_id, record, label in zip(ids, records, labels, strict=True)
    ]
    split_by_id = dict(zip(ids, splits, strict=True))
    split_payload = json.dumps(
        sorted(split_by_id.items()), separators=(",", ":"), ensure_ascii=True
    ).encode()
    return rows, split_by_id, hashlib.sha256(split_payload).hexdigest()


def choose_small_subset(
    rows: list[SubsetJet], split_by_id: dict[str, str]
) -> dict[str, dict[str, list[str]]]:
    selected: dict[str, dict[str, list[str]]] = {}
    for offset, (split, size) in enumerate(SPLIT_SIZES.items()):
        candidates = [row for row in rows if split_by_id.get(row.jet_id) == split]
        qcd_records = {row.record_id for row in candidates if row.label == 0}
        selected[split] = select_nested_subsets(
            candidates,
            (size,),
            subset_seed=20260720 + offset,
            active_qcd_record_ids=qcd_records,
        )[size]
    return selected


def build_custom_dataset(
    canonical: Path,
    preprocessing: Path,
    selected: dict[str, dict[str, list[str]]],
    split_hash: str,
    output: Path,
) -> dict[str, int]:
    identities = output / "selected-identities.json"
    combined = {
        "qcd": [jet for split in SPLIT_SIZES for jet in selected[split]["qcd"]],
        "top": [jet for split in SPLIT_SIZES for jet in selected[split]["top"]],
    }
    identities.parent.mkdir(parents=True, exist_ok=True)
    identities.write_text(json.dumps(combined, sort_keys=True) + "\n", encoding="utf-8")
    diagnostic_view = output / "diagnostic-view-a.h5"
    materialize_view(
        canonical,
        preprocessing,
        identities,
        split_hash,
        FeatureConfig.A,
        diagnostic_view,
    )

    counts: dict[str, int] = {}
    with h5py.File(diagnostic_view, "r") as source:
        ids = source["jet_id"].asstr()[:].tolist()
        data = np.asarray(source["data"][:], dtype=np.float32)
        labels = np.asarray(source["label"][:], dtype=np.int64)
    position = {jet_id: index for index, jet_id in enumerate(ids)}
    for project_split, omnilearned_split in OMNILEARNED_SPLITS.items():
        ordered = [*selected[project_split]["qcd"], *selected[project_split]["top"]]
        indices = np.asarray([position[jet_id] for jet_id in ordered], dtype=np.int64)
        destination = output / "custom" / omnilearned_split / "cms2015-smoke.h5"
        destination.parent.mkdir(parents=True, exist_ok=True)
        with h5py.File(destination, "w") as target:
            target.create_dataset(
                "data", data=data[indices], compression="gzip", compression_opts=4
            )
            target.create_dataset(
                "pid", data=labels[indices], compression="gzip", compression_opts=4
            )
            target.attrs["source"] = "CMS 2015 RunIIFall15MiniAODv2 particleML canonical"
            target.attrs["feature_config"] = "A"
            target.attrs["formal_evidence_eligible"] = False
        counts[project_split] = len(indices)
    diagnostic_view.unlink()
    return counts


def run_logged(
    argv: list[str], *, environment: dict[str, str], log: Path, timeout_seconds: int
) -> float:
    print("Running:", " ".join(argv))
    started = time.monotonic()
    try:
        completed = subprocess.run(
            argv,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        log.write_text(str(output), encoding="utf-8")
        raise RuntimeError(f"command timed out after {timeout_seconds}s; see {log}") from exc
    log.write_text(completed.stdout, encoding="utf-8")
    print(completed.stdout)
    if completed.returncode != 0:
        raise RuntimeError(f"command returned {completed.returncode}; see {log}")
    return time.monotonic() - started


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical-url", required=True)
    parser.add_argument("--canonical-sha256", required=True)
    parser.add_argument("--preprocessing-url", required=True)
    parser.add_argument("--preprocessing-sha256", required=True)
    parser.add_argument(
        "--workdir",
        type=Path,
        default=Path("/workspace/artifacts/jetson-cms2015-omnilearned-smoke"),
    )
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    canonical_sha = validate_sha256(args.canonical_sha256, "canonical SHA-256")
    preprocessing_sha = validate_sha256(
        args.preprocessing_sha256, "preprocessing SHA-256"
    )
    work = args.workdir.resolve()
    if work.exists() and (work / "diagnostic-result.json").exists():
        raise RuntimeError(f"completed diagnostic already exists: {work}")
    work.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(work).free < 30 * 1024**3:
        raise RuntimeError("at least 30 GiB of free space is required before starting")

    total_started = time.monotonic()
    timings: dict[str, float] = {}
    assets: dict[str, Any] = {}

    started = time.monotonic()
    assets["canonical"] = download(
        args.canonical_url,
        work / "inputs" / "canonical.h5",
        expected_sha256=canonical_sha,
    )
    assets["preprocessing"] = download(
        args.preprocessing_url,
        work / "inputs" / "preprocessing.json",
        expected_sha256=preprocessing_sha,
    )
    assets["checkpoint"] = download(
        CHECKPOINT_URL,
        work / "outputs" / "best_model_pretrain_s.pt",
        expected_bytes=CHECKPOINT_BYTES,
    )
    timings["downloads_seconds"] = time.monotonic() - started

    rows, split_by_id, split_hash = inspect_canonical(Path(assets["canonical"]["path"]))
    selected = choose_small_subset(rows, split_by_id)
    started = time.monotonic()
    counts = build_custom_dataset(
        Path(assets["canonical"]["path"]),
        Path(assets["preprocessing"]["path"]),
        selected,
        split_hash,
        work / "data",
    )
    timings["view_seconds"] = time.monotonic() - started

    omnilearned_python, timings["install_seconds"] = install_omnilearned(work)
    executable = omnilearned_python.parent / "omnilearned"
    environment = dict(os.environ)
    environment.update(
        {
            "MASTER_ADDR": "127.0.0.1",
            "MASTER_PORT": "29521",
            "RANK": "0",
            "LOCAL_RANK": "0",
            "WORLD_SIZE": "1",
            "PYTHONUNBUFFERED": "1",
        }
    )
    data_root = work / "data"
    output_root = work / "outputs"
    output_root.mkdir(parents=True, exist_ok=True)

    timings["index_seconds"] = run_logged(
        [str(executable), "dataloader", "--dataset", "custom", "--folder", str(data_root)],
        environment=environment,
        log=work / "index.log",
        timeout_seconds=args.timeout_seconds,
    )
    timings["fine_tune_seconds"] = run_logged(
        [
            str(executable),
            "train",
            "--output_dir",
            str(output_root),
            "--save-tag",
            "cms2015_jetson_smoke",
            "--dataset",
            "custom",
            "--path",
            str(data_root),
            "--size",
            "small",
            "--epoch",
            "1",
            "--iterations",
            "2",
            "--batch",
            "8",
            "--num-workers",
            "0",
            "--nevts",
            str(counts["train"]),
            "--use-amp",
            "--fine-tune",
            "--pretrain-tag",
            "pretrain_s",
        ],
        environment=environment,
        log=work / "fine-tune.log",
        timeout_seconds=args.timeout_seconds,
    )
    timings["evaluate_seconds"] = run_logged(
        [
            str(executable),
            "evaluate",
            "--input_dir",
            str(output_root),
            "--output_dir",
            str(output_root),
            "--save-tag",
            "cms2015_jetson_smoke",
            "--dataset",
            "custom",
            "--path",
            str(data_root),
            "--size",
            "small",
            "--batch",
            "8",
            "--num-workers",
            "0",
        ],
        environment=environment,
        log=work / "evaluate.log",
        timeout_seconds=args.timeout_seconds,
    )

    timings["total_seconds"] = time.monotonic() - total_started
    used = directory_size(work)
    if used > STORAGE_CAP_BYTES:
        raise RuntimeError("diagnostic exceeded the 160 GiB storage cap")
    result = {
        "status": "diagnostic_completed",
        "formal_evidence_eligible": False,
        "model": "OmniLearned PET small / pretrain_s",
        "omnilearned_revision": OMNILEARNED_REVISION,
        "dataset": "CMS 2015 RunIIFall15MiniAODv2",
        "feature_config": "A",
        "selected_jets": counts,
        "assets": assets,
        "timings": timings,
        "workdir_bytes": used,
        "outputs": sorted(str(path.relative_to(work)) for path in output_root.glob("*")),
    }
    (work / "diagnostic-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
