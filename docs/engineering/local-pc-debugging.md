# Local PC Debugging Guide

## Purpose and Boundary

Use this guide to develop and debug the Python package on a local Windows PC.
It is appropriate for deterministic fixtures, contracts, manifest and split
logic, compact ROOT-to-HDF5 conversion, model-view construction, CLI behavior,
metrics, and documentation.

Local results are diagnostic only. They must not be used as evidence that CMS
extraction, a qualified checkpoint, GPU execution, or an E0--E3 experiment gate
has passed. Those activities belong to the qualified CMSSW host or the pinned
RunPod GPU environment described in
[Development and Debugging Environments](./development-and-debugging.md).

## Prerequisites

- Windows 10 or 11 with PowerShell and Git;
- Python 3.10--3.12 (Python 3.12 is recommended);
- Node.js 20+ and pnpm 10.33.0 for documentation work; and
- enough local storage for test fixtures, but not the production CMS corpus.

Run all commands from the repository root.

## Create or Refresh the Python Environment

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --requirement requirements-ci.lock
python -m pip install --no-deps --editable .
```

The editable install is required: the package version is read from installed
distribution metadata, so setting `PYTHONPATH=src` is not equivalent.

If PowerShell activation is blocked, use the environment interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --requirement requirements-ci.lock
.\.venv\Scripts\python.exe -m pip install --no-deps --editable .
```

Confirm the installation and CLI entry point:

```powershell
python -c "import importlib.metadata as m; import particleml; print(m.version('particleml-research'))"
particleml --help
```

## Fast Debugging Loop

Start with the narrowest test that covers the change. Keep `-x` while locating
one failure, then remove it before the final check.

```powershell
pytest -x -vv tests\test_manifest.py
pytest -x -vv tests\test_views.py::test_ad_identity_equivalence
pytest -x -vv tests\test_cli.py
```

Useful CLI smoke checks are:

```powershell
particleml --help
particleml manifest --help
particleml convert --help
particleml view --help
particleml evaluate --help
```

Use a temporary directory or a test fixture path for generated outputs. Do not
reuse an immutable formal-artifact path while experimenting. Do not update a
golden value unless its serialized or scientific contract has been reviewed.

## Full Local Verification

Before handing off a change, run the applicable complete checks:

```powershell
pytest
ruff check
mypy src\particleml
python scripts\validate_software_docs.py
git diff --check
```

For documentation changes, install the locked JavaScript dependencies and run:

```powershell
pnpm install --frozen-lockfile
pnpm test
pnpm docs:build
```

For interactive documentation review:

```powershell
pnpm docs:dev
```

## Optional Local PyTorch Smoke Tests

PyTorch is deliberately outside the default local dependency set. Without it,
the PyTorch-specific baseline test is expected to skip. Installing a compatible
CPU build is useful for local tensor-shape, padding, forward, and backward
smoke tests:

```powershell
python -m pip install torch
pytest -x -vv tests\test_baseline.py
```

If the PC has an NVIDIA GPU, use the PyTorch installation command compatible
with the installed driver and desired CUDA runtime. Treat such runs as local
diagnostics only; reproduce formal GPU results in the pinned RunPod image.

## What Must Not Run Locally

Do not use Windows as a substitute for the following qualified boundaries:

| Activity | Required environment |
| --- | --- |
| CMS EDM decoding, truth matching, `cmsRun`, and formal E0 measurement | Qualified POSIX host with CMSSW 7_6_7 |
| Official OmniLearned checkpoint qualification, CUDA smoke tests, and E1--E3 training | Pinned RunPod GPU image |
| Commit-bound repository verification | GitHub Actions |

Running `tests/test_cmssw_contract.py` locally checks the extraction contract;
it does not prove that the CMSSW plugin compiles or processes CMS data.

## Common Problems

### `PackageNotFoundError: particleml-research`

The source is visible but the distribution metadata is missing. Activate the
correct environment, then rerun:

```powershell
python -m pip install --no-deps --editable .
```

### A PyTorch test is skipped

This means PyTorch is absent from the local environment. Install it only when a
local model smoke test is needed; a skip does not block ordinary package,
contract, or data-pipeline debugging.

### `cmsRun` is not found

This is expected outside CMSSW. Move the extraction attempt to the qualified
POSIX CMSSW host rather than installing an unrelated local CMS package.

### A gate reports `blocked_external_evidence`

The local contract has detected missing qualified evidence. Produce and retain
that evidence in the required CMSSW or RunPod environment; do not edit the gate
artifact to mark it as passed.
