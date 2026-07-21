# Development and Debugging Environments

## 1. Purpose

This guide is the operational entry point for developing, testing, and
debugging particleML. It defines five separate execution environments and the
evidence each environment may produce:

| Environment | Primary responsibility | Evidence boundary |
|---|---|---|
| Jetson Orin Nano Super 8GB Docker | Primary package development, ARM64/CUDA debugging, deterministic fixtures, and tiny model checks | Diagnostic only; cannot pass a formal experiment gate |
| Local Windows and PowerShell | Optional package, contract, and documentation checks when the Jetson is unavailable | Diagnostic only; cannot pass a formal experiment gate |
| GitHub Actions | Commit-bound package build, lint, typing, tests, and documentation checks | Authoritative repository verification when retained against the tested commit |
| Qualified POSIX CMSSW host | CMS EDM decoding, truth matching, compact ROOT extraction, and E0 measurements | Required for formal CMSSW and E0 evidence |
| RunPod GPU environment | OmniLearned integration, PyTorch execution, GPU smoke tests, and E1-E3 training | Required for formal model and training evidence |

Passing a local fixture does not promote E0, E0.5, E1, E2, or E3. A formal
status change requires the qualified environment and retained artifacts defined
by the software requirements and traceability matrix.

The primary daily setup is the
[Jetson Orin Nano Super 8GB Debugging Guide](./jetson-orin-nano-debugging.md).
It uses a JetPack-compatible NVIDIA PyTorch iGPU image and the repository's
`containers/jetson/Dockerfile`. Windows remains an optional CPU-oriented
fallback described in the
[Local PC Debugging Guide](./local-pc-debugging.md).

## 2. Local Python Environment

### 2.1 Prerequisites

Use the following supported tools:

- Windows 10 or 11 with PowerShell;
- Git;
- Python 3.10, 3.11, or 3.12, with Python 3.12 recommended for local work;
- Node.js 20 or newer and pnpm 10.33.0 for the documentation site; and
- sufficient local storage for compact test fixtures, not production CMS data.

A standard Python virtual environment is the documented baseline. Conda may be
used, but contributors must still install the same locked dependencies and the
editable project package.

### 2.2 Bootstrap

Run these commands from the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --requirement requirements-ci.lock
python -m pip install --no-deps --editable .
```

The editable install is mandatory. The package reads its version from installed
distribution metadata, so adding `src` to `PYTHONPATH` is not an equivalent
installation.

Confirm that the environment is usable:

```powershell
python -c "import importlib.metadata as m; import particleml; print(m.version('particleml-research'))"
particleml --help
```

Deactivate the environment with `deactivate` when work is complete.

### 2.3 Documentation Dependencies

Install the locked JavaScript dependencies once:

```powershell
pnpm install --frozen-lockfile
```

The Python CI lock already contains the dependency needed by the software
documentation validator. For a documentation-only environment, use
`requirements-docs.txt` instead of `requirements-ci.lock`.

## 3. Local Debugging Workflow

### 3.1 Fast Feedback

Start with the narrowest relevant test:

```powershell
pytest -x -vv tests\test_manifest.py
pytest -x -vv tests\test_views.py::test_ad_identity_equivalence
```

Use `-x` while diagnosing one failure, then remove it before the final full
test run. Do not update a golden value until the corresponding scientific or
serialized contract has been reviewed.

For CLI behavior, inspect the resolved help and exercise a temporary or fixture
output path. Formal artifact paths are immutable and must not be reused for
experimentation.

### 3.2 Complete Local Checks

Run the repository checks from the activated environment:

```powershell
ruff check
mypy src\particleml
pytest
python scripts\validate_software_docs.py
pnpm test
pnpm docs:build
git diff --check
```

`ruff check` and `mypy` are check-only commands. Do not use an automatic rewrite
mode as part of verification. The VitePress development server is available for
interactive documentation review:

```powershell
pnpm docs:dev
```

### 3.3 Interpreting Results

Local success establishes that the implementation behaves correctly against
repository fixtures. It does not establish that:

- the CMSSW extractor compiles or runs against the selected CMS records;
- decoded impact-parameter units and primary-vertex semantics are correct;
- the official OmniLearned checkpoint and custom-data index are compatible;
- GPU forward, backward, or tiny-loss checks pass; or
- any E1-E3 experiment condition has completed.

Those statements require retained evidence from the environments below.

## 4. GitHub Actions Verification

The Python workflow tests Python 3.10, 3.11, and 3.12. Its installation order
is the reference order for a clean environment:

1. install `requirements-ci.lock`;
2. install the project with `python -m pip install --no-deps --editable .`;
3. build the package;
4. run Ruff, Mypy, pytest, and the software documentation validator; and
5. run the documentation tests and build in the documentation job.

Only retained workflow results associated with the exact tested commit may be
used as authoritative repository verification. A local result copied into a
planning document is not equivalent to a CI record.

## 5. Qualified CMSSW Environment

### 5.1 Boundary and Identity

Formal extraction uses:

```text
CMSSW release: 7_6_7
Container: cmsopendata/cmssw_7_6_7-slc6_amd64_gcc493
GlobalTag: 76X_mcRun2_asymptotic_RunIIFall15DR76_v1
Host: authorized POSIX host near sufficiently fast EOS or XRootD access
```

Before execution, the operator must resolve and retain the container digest,
qualified-host identifier, exact Git commit, source-manifest SHA-256, CMS record
ID, canonical PFN, frozen split, and signal/background declaration. Mutable
image tags or unresolved provenance values are insufficient for formal evidence.

Local Windows may run `tests/test_cmssw_contract.py`, but it is not a supported
CMSSW runtime and must not emulate extraction output as formal evidence.

### 5.2 Qualification Sequence

On the qualified host:

1. start the pinned CMSSW environment and create a CMSSW 7.6.7 work area;
2. place `cmssw/ParticleMLExtractor` under the work area's `src` directory;
3. compile the committed plugin and configuration;
4. set `PARTICLEML_QUALIFIED_HOST_ID` to the approved host identifier;
5. run one TT qualification file and one QCD qualification file first;
6. inspect products, daughter resolution, truth traversal, units, PV semantics,
   cutflow, timing, and output integrity; and
7. retain the compact ROOT output, structured job record, logs, hashes, commit,
   manifest identity, and container identity.

Wrap every `cmsRun` attempt with the committed job-record helper:

```bash
python cmssw/ParticleMLExtractor/test/run_extraction.py \
  --record /qualified/input/source-record.json \
  --log /qualified/output/job-record.json \
  cmsRun cmssw/ParticleMLExtractor/python/extract_cfg.py \
  inputFiles=<CANONICAL_PFN> \
  outputFile=<OUTPUT_ROOT> \
  maxEvents=<QUALIFICATION_EVENT_LIMIT> \
  recordId=<CMS_RECORD_ID> \
  canonicalPFN=<CANONICAL_PFN> \
  split=<train|validation|test> \
  sourceManifestSha256=<SHA256> \
  gitCommit=<COMMIT> \
  containerDigest=<DIGEST> \
  isSignal=<True|False>
```

The placeholders must be replaced from the frozen manifest and qualified-host
record. Do not store an example command containing invented formal values.

## 6. RunPod GPU Environment

### 6.1 Image and Persistent Storage

The RunPod definition is `containers/runpod/Dockerfile`. It pins the base image
by digest, installs `containers/runpod/requirements.lock`, installs particleML
as an editable package, and sets the default artifact root to
`/workspace/artifacts`.

Build the image from the repository root when preparing a new immutable image:

```bash
docker build --file containers/runpod/Dockerfile --tag particleml-runpod:local .
```

Push and deploy only through the approved registry workflow. Record the final
immutable image digest rather than the local tag. Mount persistent storage at
`/workspace/artifacts`; do not keep formal data, checkpoints, predictions, or
run records only on an ephemeral pod disk.

### 6.2 Environment Record

Copy `containers/runpod/environment-record.template.json` into the retained run
area and populate every runtime identity field from the live pod:

- capture timestamp;
- image digest;
- dependency-lock SHA-256;
- CUDA and driver versions;
- PyTorch version;
- GPU model; and
- GPU VRAM in MiB.

The record must remain secret-free. Never add API keys, tokens, passwords,
private keys, credentials, or environment dumps that may contain them.

### 6.3 GPU Debugging Sequence

Use this order so that expensive work never runs ahead of its evidence gate:

1. verify the image, lock hash, package version, CUDA, PyTorch, GPU, storage,
   and environment record;
2. validate the completed canonical dataset, preprocessing state, A-D views,
   and their hashes;
3. build and validate the official OmniLearned custom-data indices;
4. audit the immutable checkpoint and tensor-loading report;
5. run finite forward and backward checks for A, B, C, and D;
6. run a tiny fine-tune and retain evidence that loss decreases;
7. pass E0.5 before starting the E1 pilot; and
8. pass each later gate before executing its dependent matrix.

Use the project CLI to resolve commands from versioned configuration. Retain
the resolved argument arrays and hashes. Do not replace argument arrays with
shell strings or inject unrecorded defaults through environment variables.

## 7. Troubleshooting

### `PackageNotFoundError: particleml-research`

The source tree is visible, but the distribution metadata is not installed.
Activate the intended virtual environment and run:

```powershell
python -m pip install --no-deps --editable .
```

### Mypy reports missing imports or library stubs

Confirm that the active interpreter is the virtual-environment interpreter and
that `requirements-ci.lock`, not only the runtime or documentation dependency
set, was installed. Remaining type errors after that check are code defects and
must not be hidden with a global ignore.

### A PyTorch test is skipped locally

PyTorch is an optional local boundary. A skip is expected when PyTorch is not
installed, but it does not provide E3 or GPU evidence. Run the corresponding
test in the pinned RunPod environment before relying on the model path.

### `cmsRun` is not found

The command is being executed outside the qualified CMSSW environment. Move the
attempt to the pinned POSIX CMSSW host; do not install an unrelated local CMS
package as a substitute.

### A gate reports `blocked_external_evidence`

The local contract is working as designed and has retained a missing external
dependency. Inspect the reported missing evidence, produce it in the qualified
environment, and rerun the gate aggregator. Do not convert the status to passed
by editing the artifact.

### An artifact is stale, incomplete, or already exists

Do not overwrite it. Verify its `COMPLETED.json`, input hashes, configuration
hash, and payload hashes. Correct the upstream input or create a new run or
artifact identity. Partial directories and failed attempts must remain visible
according to the artifact lifecycle contract.

### PowerShell blocks virtual-environment activation

Use an execution policy approved by the local administrator, or invoke the
virtual-environment interpreter directly as `.venv\Scripts\python.exe`. Do not
change machine-wide policy solely for this project.

## 8. Completion Checklist

Before requesting review of a code or documentation change, confirm:

- the intended virtual environment is active and the editable package imports;
- the narrow regression test and the full relevant suite pass;
- Ruff, Mypy, and documentation checks have been run and failures are reported;
- the documentation site builds when documentation changed;
- no formal artifact, credential, or large data file has entered Git; and
- claims in the change description do not exceed the environment that produced
  the retained evidence.
