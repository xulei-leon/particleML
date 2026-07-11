# OmniLearn Practice Notebook Commenting Design

## Objective

Turn `src/notebooks/pretrained_omnilearn_pet_practice.ipynb` into a teaching-oriented notebook for a learner entering jet-physics foundation-model work, without changing its executable behavior, default paths, experiment gates, or research claims.

## Audience and Language

The primary audience is an undergraduate computational-physics researcher who knows Python and scientific computing but is still building deep-learning and HEP-ML expertise. All notebook content remains in English, following the repository language convention.

## Annotation Strategy

Use two complementary layers:

1. Expand Markdown cells with section goals, scientific context, expected inputs and outputs, interpretation guidance, and common failure modes.
2. Add code comments and docstrings around non-obvious implementation details, including tensor shapes, masking, schema validation, feature slicing, checkpoint grouping, hashing, and smoke-test behavior.

Comments should explain intent and assumptions rather than restating obvious syntax. Imports, simple assignments, and straightforward print statements do not require line-by-line narration.

## Required Coverage

The annotations must cover:

- project-root and path resolution;
- practice dependencies versus the complete OmniLearn reference stack;
- GPU and CUDA detection limitations;
- official checkout recognition and version provenance;
- HDF5 discovery and the `data`, `jet`, and `pid` contract;
- the difference between structural validation and physics validation;
- tiny-slice inspection, finite-value checks, padding, and particle masks;
- nested A-D feature configurations and why real column mappings must be verified;
- helper sanity tests and their limited evidentiary scope;
- checkpoint component grouping and SHA-256 provenance;
- dry-run command templates and platform adaptation;
- the masked-set PyTorch smoke test and why it is not OmniLearn/PET;
- the E0.5 adapter-loading checklist and run-record fields;
- the distinction between practice output and formal experimental evidence.

## Behavioral Constraints

- Preserve code-cell order and execution flow.
- Do not change constants, paths, random seeds, model dimensions, commands, feature policies, or passing criteria.
- Do not resolve `COLUMN_MAP` or claim feature semantics that have not been verified from real data and preprocessing sources.
- Do not add downloads, training runs, network calls, or heavyweight computation.
- Do not present the tiny classifier as an OmniLearn or PET implementation.

## Verification

After editing:

1. Parse the file as valid notebook JSON.
2. Confirm the notebook contains the expected cell structure and metadata.
3. Compile every Python code cell after removing notebook-only magic lines where necessary.
4. Inspect the diff to confirm changes are documentation-only and no executable statements were altered unintentionally.
5. Check that no placeholder annotations such as `TODO` or `TBD` were introduced.

## Success Criteria

A learner should be able to understand why each section exists, what its output means, what it cannot establish, and how it supports the transition from preparation to E0/E0.5/E1 experiments. The notebook must remain executable under the same conditions as before the annotation work.
