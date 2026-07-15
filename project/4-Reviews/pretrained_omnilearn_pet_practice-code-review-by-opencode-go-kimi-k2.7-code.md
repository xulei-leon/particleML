# Code Review Report

**File reviewed:** `src/notebooks/pretrained_omnilearn_pet_practice.ipynb`  
**Review type:** Code review  
**Reviewer:** opencode-go/kimi-k2.7-code  
**Date:** 2026-07-08

## Scope and Summary

This notebook is a preparatory / rehearsal artifact for loading and eventually fine-tuning a pretrained OmniLearn / PET-style jet foundation model on JetClass data. It performs environment inventory, optional reference-repo detection, HDF5 discovery, schema validation, feature-configuration mapping, checkpoint hashing, command-template printing, and a tiny PyTorch smoke test.

The notebook is well documented and intentionally conservative (no automatic downloads, no full training). However, several correctness, reproducibility, and maintainability issues should be addressed before it is relied on as a gate between project preparation and formal E0/E0.5/E1 experiments.

## Findings

| Severity | Type | Location | Issue | Evidence | Recommendation |
|----------|------|----------|-------|----------|----------------|
| High | Risk / Correctness | Cell 1 (`PROJECT_ROOT` detection), lines 66–73 | Project-root detection is fragile and can silently point to the wrong directory. It relies on `Path.cwd()` and on a directory named `notebooks`; if the notebook is run from any other `notebooks` folder, exported to a `.py` script, or opened via a symlink, `DATA_DIR`, `REFERENCE_DIR`, and checkpoint searches will target the wrong paths. | `PROJECT_ROOT = Path.cwd()` followed by `if PROJECT_ROOT.name == "notebooks": PROJECT_ROOT = PROJECT_ROOT.parents[1]`. | Add a validation step after resolution, e.g. assert that `(PROJECT_ROOT / "src" / "notebooks").exists()` and `(PROJECT_ROOT / "README.md").exists()`. Consider using `ipynbname` or an explicit `PROJECT_ROOT = Path("...").resolve()` override for notebooks. |
| High | Correctness | Cell "Environment Inventory", lines 142–159 | Package version lookups for `torch_geometric` and `torch_cluster` will report `MISSING` even when the packages are installed, because their PyPI distribution names use hyphens (`torch-geometric`, `torch-cluster`), not underscores. | `REFERENCE_STACK = ["torch_geometric", "torch_cluster", ...]` and `PACKAGE_NAME_MAP = {"sklearn": "scikit-learn", "EnergyFlow": "EnergyFlow"}` does not remap these names. | Expand `PACKAGE_NAME_MAP` to map import names to distribution names: `"torch_geometric": "torch-geometric"`, `"torch_cluster": "torch-cluster"`. Verify all `REFERENCE_STACK` entries similarly. |
| Medium | Correctness / Risk | Cell "Inspect One Batch-Like Slice", line 430 | JSON output is truncated at 6000 characters with a string slice, which can produce invalid / partial JSON and mislead the user. | `print(json.dumps(tiny_report, indent=2)[:6000])`. | Truncate the underlying data structure before serialization, or print a summary object. If truncation is required, truncate a list-of-items structure so the printed text remains valid JSON. |
| Medium | Risk | Cell "E0.5 Adapter-Loading Spike Checklist", lines 725–747 | The run-record cell depends on variables (`checkpoint_files`, `checkpoint_report`, `env_report`) defined in earlier cells. Running cells out of order raises `NameError`. | `run_record_template = {..., "checkpoint_path": str(checkpoint_files[0]) if checkpoint_files else None, ...}` directly references earlier cell state. | Either recompute the needed state inside this cell or guard with a helper that returns a default when variables are undefined. Document the required execution order in the markdown above the cell. |
| Medium | Maintainability | Cell 1, lines 47–54 | `subprocess`, `shutil`, and `os` are imported but never used. | Imports listed in the first code cell; no references elsewhere. | Remove unused imports to reduce noise and speed up import time. If kept for future cells, move them closer to where they are used. |
| Medium | Correctness / Risk | Cell "Local HDF5 Discovery", lines 278–291 | `summarize_hdf5_file` silently drops top-level keys beyond `max_keys` without warning the user. | `keys = list(handle.keys())[:max_keys]`. | Emit a warning when `len(handle.keys()) > max_keys`, or increase the default and make truncation explicit in the printed summary. |
| Medium | Correctness / Risk | Cell "OmniLearn Input-Contract Check", lines 363–365 | When all required datasets are missing, `n_values` is empty and no leading-dimension disagreement issue is recorded. | `n_values = [shape[0] for shape in [data_shape, jet_shape, pid_shape] if shape]` followed by `if len(set(n_values)) > 1`. | Add a separate issue when `n_values` is empty (e.g., "no datasets available to compare"). Also guard against zero-length shapes. |
| Medium | Risk / Reproducibility | Cell "Optional OmniLearn Reference Checkout", lines 209–232 | The reference checkout check records only path existence and a static URL; it does not capture the actual commit hash, tag, or date of the cloned repository. | `describe_reference_checkout` checks for `README.md`, `requirements.txt`, etc., but never runs `git -C {REFERENCE_DIR} rev-parse HEAD`. | Add a `git_commit` field to the reference report by running `subprocess.check_output(["git", "-C", str(REFERENCE_DIR), "rev-parse", "HEAD"], text=True).strip()` when `.git` exists. |
| Low | Performance | Cell "Inspect One Batch-Like Slice", lines 415–416 | The per-particle absolute-sum array is computed twice in succession. | `report["data_abs_sum_first_particles"] = np.abs(data).sum(axis=-1).tolist()` and `report["nonzero_particle_counts"] = (np.abs(data).sum(axis=-1) > 0)...`. | Compute `abs_sum = np.abs(data).sum(axis=-1)` once and reuse it. |
| Low | Maintainability | Cell "Official Command Templates", lines 589–622 | `format_command` is defined but never used; all commands are formatted inline. | `def format_command(parts: Sequence[str]) -> str: ...` has no callers. | Either use `format_command` consistently for all command construction, or remove it. |
| Low | Risk / Reproducibility | Cell "E0.5 Adapter-Loading Spike Checklist", line 728 | The run-record template hardcodes `git_commit` as `None` instead of capturing the current commit automatically. | `"git_commit": None,` with no programmatic fill. | Populate `git_commit` programmatically with `subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, text=True).strip()` and handle the case when the directory is not a git repo. |
| Low | Correctness / Risk | Cell "Pretrained Checkpoint Inventory", lines 534–536 | The checkpoint heuristic matches any filename containing the substring `"checkpoint"`, which can include README files, logs, or unrelated artifacts. | `return any(name.endswith(suffix) for suffix in CHECKPOINT_SUFFIXES) or "checkpoint" in name`. | Restrict the substring match to known extensions or remove it and rely only on the suffix whitelist. If kept, document why. |
| Low | Correctness | Cell "Local HDF5 Discovery", line 258 | `.h5py` is included as an HDF5 suffix, which is non-standard and may confuse users. | `HDF5_SUFFIXES = {".h5", ".hdf5", ".h5py"}`. | Remove `.h5py` or add a comment explaining that it is a project-specific convention. Standard JetClass files use `.h5` or `.hdf5`. |
| Info | Maintainability | Entire notebook | The notebook is monolithic (~785 lines) and mixes environment checks, data inspection, feature mapping, checkpoint inventory, command templates, smoke tests, and record keeping. | Single file containing all rehearsal logic. | Consider splitting into focused notebooks (e.g., `01_environment.ipynb`, `02_data_inventory.ipynb`, `03_checkpoint_inventory.ipynb`) or extracting reusable helpers into `data/utils.py` and importing them. |
| Info | Test | Entire notebook | There are no automated tests or assertions for the helper functions (`discover_hdf5_files`, `check_omnilearn_input_contract`, `validate_feature_config`, etc.). | No `assert`, `pytest`, or unit-test cells. | Add a small test cell with synthetic HDF5 files and invalid configurations to verify that helpers raise the expected errors and return correct shapes. This is especially important before E0.5. |
| Info | Documentation | Cell "Passing Criteria for This Practice Notebook" | The passing criteria are clear, but there is no explicit failure / escalation path if criteria are not met. | Criteria list states what should be true, not what to do when it is false. | Add a short "If any criterion fails" subsection with owner, issue-tracking location, and whether the project should proceed to E0. |

## Positive Observations

- The notebook is explicitly conservative: it does not download data or run full training by default, which limits accidental resource consumption.
- Optional dependencies (`h5py`, `torch`) are handled gracefully with try/except blocks, allowing partial execution in incomplete environments.
- The `InputContractResult` dataclass and feature-config validators provide a typed, reusable interface for the A–D feature abstractions.
- SHA-256 hashing of checkpoint files supports reproducibility and provenance tracking.
- All text and comments are in English, consistent with `AGENTS.md`.

## Action Priority

1. Fix `PROJECT_ROOT` detection and add post-resolution assertions (High).
2. Correct `torch_geometric` / `torch_cluster` package-name mapping (High).
3. Add guards against out-of-order cell execution and invalid JSON truncation (Medium).
4. Capture the OmniLearn reference commit hash and current git commit in the run record (Medium).
5. Remove unused imports and dead helper code, and add basic smoke tests for helper functions (Low).
