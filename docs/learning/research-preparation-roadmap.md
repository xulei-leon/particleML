# Research Project Preparation Stage

This document is based on `docs/research/plans/research-plan-v0.2.html`. It is written for a clear objective: reproduce and extend an OmniLearn/PET-style jet foundation model on the JetClass top-tagging task, and complete a systematic ablation study over input feature configurations A-D. The preparation stage is not about "learning deep learning in general"; it is about being able to reproduce experiments independently, read the reference code, and produce publication-quality experiment records reliably.

Recommended preparation time: 6-8 weeks. If time is tight, prioritize Weeks 1-4, because they determine whether the Week 2 Reproduction Gate can pass.

## 1. Overall Goal of the Preparation Stage

By the end of the preparation stage, you should be able to do the following:

1. Explain the JetClass data format, particle-level features, top-tagging labels, and why a fixed train/validation/test manifest is required.
2. Use Python to read HDF5 data, generate masked/padded particle tensors, and derive the A-D input configurations from the same raw dataset.
3. Read and run the OmniLearn reference workflow, and understand how PET/Particle Transformer-style models process unordered particle clouds.
4. Write a PyTorch training loop, fine-tuning script, metric computation script, and save reproducible experiment metadata in JSON format.
5. Read the core papers and clearly understand that this project is not "inventing a new foundation model from scratch"; it is a controlled feature-ablation empirical study.

## 2. Learning Method

Use a "project-driven + minimum necessary theory + small-scale reproduction" approach:

1. For each library, only study what is needed for this project, such as reading JetClass, implementing masks, training a binary classifier, and computing AUC.
2. For each paper, first focus on four things: research question, input representation, model architecture, and evaluation metrics. Read the training details and ablations on the second pass.
3. Leave one runnable artifact every week: a notebook, preprocessing script, baseline training script, metric report, or reading note.
4. Keep a `notes/reading-log.md` or equivalent document during the learning process to record "what this paper means for this project" instead of only copying the abstract.
5. Do not try to fully reproduce every paper during preparation. The hard requirement is: run the reference workflow, interpret the results, and locate data/model-dimension issues when they appear.

## 3. ML / Research Tool Learning List

| Tool / Library | Official URL | Suggested Time | Proficiency Target | Relation to Project Goal |
|---|---|---:|---|---|
| Python 3 | https://docs.python.org/3/ | 3-5 days | Use functions, classes, virtual environments, path handling, type hints, and exception handling comfortably; write reusable scripts rather than notebook-only code. | Foundation for all data processing, training, evaluation, and experiment logging. |
| NumPy | https://numpy.org/doc/ | 3-4 days | Understand array shapes, broadcasting, masking, padding, random seeds, and vectorized statistics. | Required for jet constituent tensors, feature normalization, and mask handling. |
| pandas | https://pandas.pydata.org/docs/ | 1-2 days | Organize experiment tables, use `groupby` and `merge`, and export CSV/Markdown summaries. | Useful for aggregating seeds, feature configs, AUC, background rejection, and run metadata. |
| h5py | https://docs.h5py.org/ | 2-3 days | Read HDF5 groups/datasets, understand lazy access, chunks, dtypes, and shapes; inspect `data`, `jet`, and `pid` datasets. | JetClass is stored in HDF5; preprocessing and manifest generation depend on it. |
| PyTorch | https://pytorch.org/docs/stable/index.html | 2-3 weeks | Master `Dataset/DataLoader`, tensor shapes, GPU device usage, autograd, training loops, checkpointing, and basic mixed precision. | Recommended framework for fine-tuning, the Deep Sets baseline, and a controllable training runner. |
| TensorFlow / Keras | https://www.tensorflow.org/api_docs | 4-6 days | Not required for full reimplementation, but you should read models/layers/callbacks/data pipelines and be able to run the reference code and map it to PyTorch. | The OmniLearn reference repository includes TensorFlow/Keras dependencies; you need to understand and reproduce the reference workflow. |
| PyTorch Geometric | https://pytorch-geometric.readthedocs.io/ | 3-5 days | Understand graph/point-cloud mini-batching and read EdgeConv/ParticleNet-style implementations. | Useful for the optional E4 ParticleNet/EdgeConv baseline and for understanding particle-cloud message passing. |
| scikit-learn | https://scikit-learn.org/stable/ | 3-4 days | Use ROC AUC, ROC curves, train/validation splitting, and bootstrap helpers correctly; know the metric input formats. | Top-tagging evaluation requires stable and reproducible AUC and background rejection calculations. |
| SciPy | https://docs.scipy.org/doc/scipy/ | 2-3 days | Use basic statistical tests, interpolation, and confidence-interval helpers. | Supports paired comparisons, learning-curve interpolation, and uncertainty estimates. |
| Matplotlib | https://matplotlib.org/stable/ | 3-4 days | Draw publication-ready line plots, error bars, and ROC curves; control figure size, labels, legends, and export formats. | The plan requires feature-ablation AUC curves, Delta AUC plots, and data-efficiency curves. |
| JupyterLab | https://jupyterlab.readthedocs.io/ | 1-2 days | Use notebooks for EDA, shape checks, and quick plotting; know when to move notebook logic into scripts. | Very useful for early JetClass exploration and preprocessing debugging, but formal experiments should be scripted. |
| Hydra | https://hydra.cc/docs/intro/ | 2-3 days | Manage `feature_config`, `seed`, `data_size`, `model_condition`, and `output_dir` with YAML. | E1-E3 involve many repeated runs, so config management reduces manual errors. |
| pytest | https://docs.pytest.org/ | 2-3 days | Write tests for preprocessing shapes, mask behavior, split manifests, and metric sanity checks. | Prevents subtle inconsistencies between feature configurations, which is one of the project's high-risk items. |
| Git | https://git-scm.com/book/en/v2 | 2-3 days | Use branches, commits, diffs, and tags confidently; record `git commit` for every formal experiment. | Experiment JSON should include the git commit, and paper results must be traceable. |
| Weights & Biases | https://docs.wandb.ai/ | 2-4 days | Log run configs, metrics, and artifacts; if W&B is not used, use an equivalent JSON/CSV logging workflow. | Helps manage 80+ core runs and avoid confusion between results and checkpoints. |
| Linux / CLI Basics | https://ubuntu.com/tutorials/command-line-for-beginners | 3-5 days | Use shell, ssh, tmux/screen, rsync/scp, and inspect GPU/disk/process status. | Required for cloud-GPU training, long-running experiments, data transfer, and failure recovery. |

## 4. Weekly Execution Roadmap

### Week 1: Data and Research Code Basics

Goal: read JetClass samples and write the smallest possible preprocessing notebook.

Tasks:

1. Read the JetClass documentation and Zenodo page: https://zenodo.org/records/6619768
2. Study the project-relevant parts of h5py, NumPy, and pandas.
3. Write a notebook that prints the shapes, dtypes, label distribution, and constituent-count distribution for `data`, `jet`, and `pid`.
4. Define the top-vs-QCD label selection method and write down the data-leakage risks.
5. Output: a `JetClass_EDA` notebook or equivalent script, plus a one-page data-structure note.

Passing criteria:

1. You can explain what each dimension means.
2. You can extract jets from a specific class in HDF5.
3. You can explain why all models must share the same held-out test set.

### Week 2: PyTorch Training Basics and Deep Sets Baseline

Goal: complete a simple baseline that can train, evaluate, and be reproduced before touching the more complex PET model.

Tasks:

1. Study PyTorch `Dataset/DataLoader`, training loops, loss functions, optimizers, and checkpointing.
2. Implement or adapt a Deep Sets binary classifier: per-particle MLP -> masked pooling -> jet-level MLP.
3. Train on a small top-vs-QCD subset and compute validation/test AUC.
4. Add pytest checks: mask excluded from pooling, padding does not change outputs, label counts are correct.
5. Output: a minimal baseline training script and a metric JSON file.

Passing criteria:

1. You can complete an end-to-end pipeline from data loading to AUC output on a small dataset.
2. Fixing the seed gives approximately repeatable results.
3. You know how to debug overfitting on a tiny batch.

### Week 3: Understanding Transformer / PET / Particle-Cloud Models

Goal: understand why PET/Particle Transformer is suitable for jet constituents and identify the model input interfaces.

Tasks:

1. Read the model-architecture sections of the Particle Transformer, ParticleNet, and Deep Sets papers.
2. Learn the basics of attention, permutation invariance/equivariance, pairwise features, and masked attention.
3. Compare against the OmniLearn reference implementation and annotate the data path, feature normalization, and mask usage.
4. Create a shape-tracing document: how the input tensor shapes become model output logits.
5. Output: `model-interface-notes.md`, mapping OmniLearn/PET input fields to the project's A-D feature configurations.

Passing criteria:

1. You can explain the differences between Deep Sets, ParticleNet/EdgeConv, and Particle Transformer/PET.
2. You can explain why this project prefers a continuous point-cloud backbone instead of an autoregressive token model first.
3. You can identify which interfaces must change when particle features are added or removed.

### Week 4: Reproduce the OmniLearn Reference Workflow

Goal: prepare for the Week 2 Reproduction Gate in the research plan.

Tasks:

1. Clone and read the official OmniLearn implementation: https://github.com/ViniciusMikuni/OmniLearn
2. Prepare the environment according to the official instructions, and run the reference workflow on a small dataset or example configuration first.
3. Record all environment details, data paths, checkpoints, fixes, and run commands.
4. Map the reference workflow inputs and outputs to the E1-E3 run matrix in this project.
5. Output: `reproduction-log.md`, including success evidence, failure issues, and next-step fixes.

Passing criteria:

1. The reference model can start and complete at least one small-scale training or evaluation run.
2. You can explain where the pretrained backbone, fine-tuning head, and feature input are configured.
3. You can decide whether the scope should be frozen to E1 or whether the project should first fall back to a PET architecture with available weights if the reference checkpoint is hard to reproduce.

### Week 5: Feature Configurations A-D and Experiment Management

Goal: generate A-D inputs from the same raw tensor source and avoid inconsistent feature encoding.

Tasks:

1. Implement a unified preprocessing function: input raw JetClass tensors, output A/B/C/D feature tensors and masks.
2. Add shape, dtype, NaN/Inf, mask, and normalization tests for each config.
3. Study Hydra or an equivalent YAML config setup, and store `feature_config`, `data_size`, `seed`, and `model_condition` in the config.
4. Generate a fixed split manifest and save source files, event IDs/hashes, and event counts.
5. Output: preprocessing spec, split manifest, and config examples.

Passing criteria:

1. The A-D differences come only from feature columns, not from sample selection or split.
2. Every run can be traced back to a manifest hash and preprocessing version.
3. You can quickly generate the E1 configuration table: 4 configs x 4 data sizes x 5 seeds.

### Week 6: Metrics, Statistics, and Figures

Goal: lock down the evaluation and plotting workflow before the large-scale formal training begins.

Tasks:

1. Study scikit-learn ROC AUC, ROC curves, and how to compute background rejection at fixed signal efficiency.
2. Implement a bootstrap 95% confidence interval; if DeLong comparisons are not available yet, mark them as optional validation.
3. Create plotting templates for Figures 1-4.
4. Simulate a complete result table using Deep Sets or a small OmniLearn run.
5. Output: metric script, plotting script, and a fake/small-run figure draft.

Passing criteria:

1. Given a set of prediction JSON/NPZ files, you can automatically generate AUC tables and figures.
2. The figures include seed variability or bootstrap uncertainty.
3. The result table can directly support the Methods/Results first draft.

### Weeks 7-8: Cloud GPU and Full End-to-End Dry Run

Goal: complete a low-cost end-to-end rehearsal before formal E1.

Tasks:

1. Learn the basic Linux/CLI workflow, including ssh, tmux, GPU monitoring, and data synchronization.
2. Run a reduced version of the matrix on a single GPU, for example two configs, two data sizes, and two seeds.
3. Verify whether checkpoints, JSON logging, metric scripts, and plotting scripts work end to end.
4. Estimate runtime, VRAM usage, storage, and budget.
5. Output: a pilot report that decides whether the project is ready for formal E1.

Passing criteria:

1. If any run crashes, you can diagnose it from the logs.
2. The output directory structure does not mix up config, seed, and checkpoint files.
3. Based on the pilot result, you can adjust batch size, epoch count, early stopping, and budget.

## 5. Required Papers and Reading Order

### First Tier: Directly Determines the Project Design

1. Mikuni, V. and Nachman, B. "OmniLearn: A Method to Simultaneously Facilitate All Jet Physics Tasks." arXiv:2404.16091.  
   URL: https://arxiv.org/abs/2404.16091  
   Focus: OmniLearn/PET backbone, continuous set-based representation, multi-task/foundation-model framing, and input-feature definitions.  
   Reading goal: align the paper's input representation with the A-D feature configurations in this project.

2. Qu, H., Li, C., and Qian, S. "Particle Transformer for Jet Tagging." arXiv:2202.03772.  
   URL: https://arxiv.org/abs/2202.03772  
   Focus: particle attention, pairwise interaction, masks, and jet-tagging benchmarks.  
   Reading goal: understand why PET / Particle Transformer is the main backbone reference for this project.

3. JetClass dataset paper / dataset documentation.  
   URL: https://zenodo.org/records/6619768  
   Focus: class definitions, dataset size, file structure, and standard tasks.  
   Reading goal: extract top-vs-QCD correctly and design a leakage-free split manifest.

4. `docs/references/omnijet-omnilearn-group-report.pdf`  
   Focus: the comparison between OmniJet-alpha and OmniLearn, the effect of input representation on performance, and the project motivation.  
   Reading goal: confirm the project's core claim that input representation richness may be a better first-paper focus than a broad architecture comparison.

### Second Tier: Baselines and Controls

5. Zaheer et al. "Deep Sets." arXiv:1703.06114.  
   URL: https://arxiv.org/abs/1703.06114  
   Focus: permutation-invariant set functions.  
   Reading goal: implement the E3 Deep Sets baseline and explain why it is a reasonable low-complexity control.

6. Qu and Gouskos. "Jet tagging via particle clouds." arXiv:1902.08570.  
   URL: https://arxiv.org/abs/1902.08570  
   Focus: ParticleNet, EdgeConv, and particle-cloud representations.  
   Reading goal: provide architecture grounding for the optional E4 baseline; if time is short, it is enough to understand the method and results table.

7. Birk, Hallin, and Kasieczka. "OmniJet-alpha: the first cross-task foundation model for particle physics." arXiv:2403.05618.  
   URL: https://arxiv.org/abs/2403.05618  
   Focus: VQ-VAE tokenization, autoregressive foundation modeling, and cross-task framing.  
   Reading goal: background contrast showing why this project is not starting with a tokenizer/autoregressive path.

### Third Tier: Statistics, Evaluation, and Writing Support

8. ROC/AUC and DeLong-style correlated ROC comparison materials.  
   Starting URL: https://scikit-learn.org/stable/modules/model_evaluation.html#roc-metrics  
   Reading goal: explain AUC, ROC, background rejection, and why paired comparisons are more appropriate than independent comparisons.

9. Bootstrap confidence interval basics.  
   Starting URL: https://docs.scipy.org/doc/scipy/reference/stats.html  
   Reading goal: report uncertainty for AUC or background rejection on a fixed test set.

10. Additional HEP jet-tagging benchmark papers.  
    Reading goal: learn the common metrics, figure styles, and baseline-reporting conventions in the field; read these in a focused batch before writing the Introduction/Related Work.

## 6. Deliverables to Produce During Preparation

By the end of the preparation stage, you should ideally have at least the following files or equivalent artifacts:

1. `docs/learning/reading-log.md`: a paper-reading log that records each paper's relationship to the project.
2. `notebooks/jetclass_eda.ipynb`: JetClass shape, label, constituent-count, and feature-distribution checks.
3. `data/preprocess.py` or an equivalent module: generate A-D feature configs from the raw HDF5 files.
4. `data/split_manifest.json`: a fixed train/validation/test split manifest.
5. `models/deepsets.py`: the minimal Deep Sets baseline.
6. `training/train_baseline.py`: a training script configurable by seed, data size, and feature config.
7. `evaluation/metrics.py`: AUC, ROC, background rejection, and bootstrap CI.
8. `evaluation/plots.py`: initial templates for Figures 1-4.
9. `docs/learning/reproduction-log.md`: a reproduction record for the OmniLearn reference workflow.
10. `docs/learning/pilot-report.md`: a time, memory, budget, and risk assessment for a reduced run matrix.

These files do not need to be paper-quality yet, but they must show that the project has moved from "reading a plan" into "building an executable research system."

## 7. Preparation Stage Exit Criteria

Only move to the formal E1 core pretrained feature-ablation experiments if all of the following are true:

1. The JetClass top/QCD data extraction and split manifest are fixed.
2. A-D feature configs can be generated from the same preprocessing library and pass shape/mask/normalization tests.
3. At least one baseline can complete the full training, evaluation, and plotting pipeline.
4. The OmniLearn reference workflow has been run successfully, or the reason it cannot be reproduced has been clearly recorded together with a fallback route.
5. The metric scripts can output AUC, background rejection, and uncertainty.
6. Every run saves the run ID, git commit, manifest hash, feature config, seed, hyperparameters, best validation epoch, and final test metrics.

If item 4 fails, follow the risk-control plan in the research proposal: freeze the scope to E1, reduce baseline and optional extensions, and prioritize completing the core ablation cleanly.

## 8. Mapping to the Research Plan

| Research Plan Requirement | Preparation Work |
|---|---|
| RQ1: effect of adding PID, charge, and energy/momentum fraction on AUC | Learn to build a unified preprocessing pipeline that generates A-D feature configs and a fixed metric pipeline. |
| RQ2: data efficiency | Learn to configure data sizes and plot AUC vs. log(sample size) curves. |
| RQ3: pretrained transfer vs random initialization | Run the OmniLearn reference workflow and understand fine-tuning and the random-init control. |
| E3 Deep Sets baseline | Complete the minimal Deep Sets baseline in Week 2. |
| Figures 1-4 | Prepare plotting templates in Week 6 so figures are not created only after experiments finish. |
| Reproducibility | Use Git, pytest, Hydra/JSON logging, split manifests, and run metadata. |
| Risk: reference implementation is hard to reproduce | Set up a reproduction log and fallback decision in Week 4. |
| Risk: subtle feature-encoding mismatch | Build one preprocessing library instead of separate encoders for each model. |

## 9. What Not to Spend Too Much Time On Early

These topics may be useful to know, but they should not displace the main preparation work:

1. Pretraining a foundation model from scratch.
2. Full reproduction of the OmniJet-alpha VQ-VAE tokenizer and autoregressive pipeline.
3. The entire multi-task benchmark suite for generation and anomaly detection.
4. Heavy hyperparameter search.
5. Large-scale cloud-GPU training, unless the small-scale pilot already works.

The most important early criterion is whether you can execute E1 with a low error rate and make every result traceable, comparable, plottable, and paper-ready.
