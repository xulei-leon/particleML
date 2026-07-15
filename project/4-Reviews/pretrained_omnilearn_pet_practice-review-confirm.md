# pretrained_omnilearn_pet_practice Review Confirm

**Reviewed Inputs**
- `src/notebooks/pretrained_omnilearn_pet_practice.ipynb`
- `docs/4-Reviews/pretrained_omnilearn_pet_practice-code-review-by-opencode-go-kimi-k2.7-code.md`
- `docs/4-Reviews/pretrained_omnilearn_pet_practice-code-review-by-ark-code-latest.md`
- `README.md`
- `AGENTS.md`
- `docs/plan/research-plan-v0.3.md`

**Review Date**
- 2026-07-08

## Overall Conclusion

The reviews are generally sound. The notebook is a preparation artifact, not a formal E0 result, so findings that improve safety, correctness, and reproducibility should be fixed now. Claims requiring real JetClass data or saved executed outputs cannot be completed in this repository state because `data/jetclass/` is empty.

The target is acceptable after applying the accepted and partial fixes below. Deferred items should be revisited when the project extracts notebook helpers into reusable modules or adds a real JetClass dev slice.

## Decision Table

| No. | Severity | Type | Review Source | Original Comment Summary | Decision | Evidence | Follow-up Plan / Rejection Reason |
|---|---|---|---|---|---|---|---|
| 1 | High | Correctness | Kimi C1 / GLM C7 | Project root detection can silently point at the wrong directory. | Accept | The notebook derives all data, reference, and checkpoint paths from `PROJECT_ROOT`; current code has no final assertion. | Add explicit root resolution with validation for `README.md` and `src/notebooks`, and raise a clear error if unresolved. |
| 2 | High | Correctness | Kimi C2 / GLM C2 | `torch_geometric` and `torch_cluster` use wrong distribution names for version lookup. | Accept | `PACKAGE_NAME_MAP` only maps `sklearn` and `EnergyFlow`. | Add `torch-geometric` and `torch-cluster` mappings and remove redundant identity mapping. |
| 3 | High | Test | GLM C1 | Notebook has no saved outputs, so it cannot demonstrate full passing criteria. | Partial | The artifact is a reusable practice notebook; real JetClass data is absent. Earlier local execution verified code cells under empty-data conditions. | Add clearer wording that saved-output execution with a real dev slice is required before treating it as E0 evidence; do not save synthetic outputs now. |
| 4 | Medium | Clarity | GLM C3 | OmniLearn and OmniLearned terminology is conflated. | Accept | `README.md` lists OmniLearn and OmniLearned separately; this notebook uses the OmniLearn repo URL. | Use OmniLearn/PET consistently and describe OmniLearned only as a later project candidate when relevant. |
| 5 | Medium | Reproducibility | Kimi C8 / GLM C4 | Reference checkout report does not capture git commit or tag. | Accept | `describe_reference_checkout` only checks expected files. | Add `git_commit`, `git_describe`, and `.git` presence when available. |
| 6 | Medium | Correctness | GLM C5 | One corrupt HDF5 file can abort all HDF5 inspection. | Accept | `h5py.File` is opened without exception isolation. | Return structured `error` entries from HDF5 summary and input-contract helpers; continue across files. |
| 7 | Medium | Correctness | GLM C6 | Placeholder feature names are likely not aligned with OmniLearn/JetClass relative features. | Accept | Current placeholders use `part_eta`, `part_phi`, and `part_energy_log`. | Rename placeholders to clearly provisional relative/log feature names and emphasize filling from actual preprocessing output. |
| 8 | Medium | Reproducibility | Kimi C4 / GLM C7 | Run-record cell depends on earlier cells and hardcodes provenance to `None`. | Accept | `checkpoint_files`, `checkpoint_report`, and `env_report` are direct earlier-cell references. | Guard with `globals().get`, auto-populate current git commit when available, and keep unavailable formal hashes as explicit `None`. |
| 9 | Medium | Maintainability | Kimi C5 / GLM C10 | `os`, `shutil`, and maybe `subprocess` imports are unused. | Partial | `subprocess` is needed after accepting git provenance fixes; `os` and `shutil` are unused. | Remove `os` and `shutil`; keep `subprocess` for git commit capture. |
| 10 | Medium | Correctness | Kimi C6 | Top-level HDF5 keys are silently truncated. | Accept | `keys = list(handle.keys())[:max_keys]` without metadata. | Record `truncated`, `total_top_level_keys`, and inspected key count in the summary. |
| 11 | Medium | Correctness | Kimi C7 | Missing all required datasets creates no comparable leading-dimension issue. | Accept | Empty `n_values` currently produces no dimensional check issue. | Add a no-comparable-datasets issue and zero-length leading-dimension checks. |
| 12 | Medium | Correctness | Kimi C3 | Tiny-slice JSON is truncated as raw text and can become invalid JSON. | Accept | `json.dumps(... )[:6000]` can cut braces or strings. | Truncate preview arrays before serialization and print valid JSON. |
| 13 | Low | Performance | Kimi C9 | Absolute per-particle sums are computed twice. | Accept | Same expression appears twice in `inspect_tiny_slice`. | Compute once and reuse. |
| 14 | Low | Maintainability | Kimi C10 / GLM C12 | `format_command` is dead code. | Accept | It has no callers. | Remove the helper. |
| 15 | Low | Reproducibility | Kimi C11 | Current git commit is not captured in run record. | Accept | `git_commit` is `None`. | Add a safe git helper and populate the run record. |
| 16 | Low | Correctness | Kimi C12 / GLM C9 | Checkpoint detection is too broad and TF shard matching is too narrow. | Accept | It matches any filename containing `checkpoint` and only one shard suffix. | Use suffix whitelist plus regex for TF data shards and checkpoint state files. |
| 17 | Low | Correctness | Kimi C13 / GLM C17 | `.h5py` is non-standard for JetClass HDF5 files. | Accept | JetClass/OmniLearn files use `.h5` or `.hdf5`. | Remove `.h5py` from default suffixes and update markdown. |
| 18 | Low | Test | GLM C14 | Tiny PyTorch smoke test prints pass/fail instead of asserting it. | Accept | It prints `finite_gradients` only. | Add assertions for logits shape, finite loss, and finite gradients. |
| 19 | Low | Security | GLM C15 | `sys.executable` may leak the local username in committed outputs. | Accept | Windows executable paths include `C:\Users\<user>`. | Store executable name in shared `env_report`; do not store the full path in run records. |
| 20 | Low | Consistency | GLM C16 | Notebook path differs from README's planned top-level `notebooks/` layout. | Reject | User explicitly requested `src/notebooks/`; repository already contains `src/notebooks/jetclass_preparation.ipynb`. | Keep the notebook in the requested and existing location; broader README layout updates are outside this review. |
| 21 | Low | Documentation | GLM C18 | Command templates are bash-like despite a Windows local environment. | Partial | Official OmniLearn commands are bash-style, but the current environment is PowerShell. | Add a note that commands are official bash-style templates and should be adapted for PowerShell/Colab; keep official command shape unchanged. |
| 22 | Info | Test | Kimi C15 / GLM C20 | Helper functions lack automated tests. | Partial | The project currently has no `.py` modules or test directory. | Add a lightweight in-notebook helper sanity-test cell; defer full pytest extraction. |
| 23 | Info | Maintainability | Kimi C14 / GLM C21 | Notebook is monolithic and could be split. | Reject | This is a single practice artifact requested by the user; splitting now would add navigation overhead. | Defer until helpers are promoted into formal E0 preprocessing modules. |
| 24 | Info | Documentation | Kimi C16 | Passing criteria lack an explicit failure path. | Accept | The current section lists pass conditions only. | Add a failure/escalation subsection that keeps the project before E0/E0.5 until gaps are recorded. |
| 25 | Low | Maintainability | GLM C11 | `OMNILEARN_PAPER` and `JETCLASS_ZENODO` constants are unused. | Accept | They are defined and not referenced. | Use them in printed reference/data guidance rather than removing useful source links. |
| 26 | Low | Clarity | GLM C13 | `checkpoints` may be absent in a clean reference checkout. | Accept | Official README says checkpoints are provided, but a shallow clone may not have local weights. | Mark `checkpoints` as optional and expected to be populated separately. |
| 27 | Low | Performance | GLM C8 | Hashing up to 20 large checkpoints can block the notebook. | Partial | E0.5 requires hashes, but large files can be slow in an exploratory notebook. | Add a visible size field and configurable hashing limit; default remains suitable for practice and can be raised for formal E0.5. |

## Needs Immediate Action

- Fix path resolution, package-name mapping, terminology, HDF5 exception handling, reference/git provenance, run-record guards, checkpoint discovery, and smoke-test assertions.
- Add a lightweight helper sanity-test cell and a failure path in the passing criteria.

## Can Be Deferred

- Saving real executed outputs with a JetClass dev slice.
- Splitting the notebook or extracting helpers into formal modules.
- Moving notebook directories or changing repository layout.

## Final Status

Apply the accepted and partial notebook edits now. After validation, the notebook can remain a preparation artifact, but it should not be cited as E0/E0.5 evidence until run with a real JetClass dev slice and checkpoint metadata.
