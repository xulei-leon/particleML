# JetClass Project Overview

This document is a learning summary of JetClass, limited to content directly relevant to this project.  
The goal of this project is not a general survey of JetClass, but to use it as the **data foundation for a jet foundation model**, serving the core tasks in `docs/plan/research-plan-v0.2.html`:

- Use **JetClass top-tagging** as the primary experimental task
- Study the impact of **input representation** on model performance
- Use **OmniLearn / PET-style continuous point-cloud backbones** as the main reference
- Compare different feature configurations and training conditions with a unified, reproducible pipeline

---

## 1. JetClass's Role in This Project

JetClass is not the research conclusion itself, but the carrier of the research conclusions.

Its role in this project can be summarized as:

| Role | Meaning |
|---|---|
| Dataset | Provides unified jet-level supervised learning data |
| Task carrier | Supports top-tagging and input representation ablation experiments |
| Benchmark platform | Used to compare different backbones, feature configurations, and training strategies |
| Reproducible baseline | Facilitates fixed splits, fixed metrics, and fixed experiment logging |

Therefore, the focus of learning JetClass is not "how big it is", but rather:

1. Whether it is suitable as training and evaluation data for a jet foundation model
2. How it supports binary classification tasks like top-vs-QCD
3. How it works with A-D input configurations for systematic comparison
4. How it serves reproducible experiments rather than one-off demos

---

## 2. What Is JetClass

JetClass is a large-scale simulated dataset for **jet physics deep learning research**.  
It targets jet tagging tasks — determining which class of physical object or process a jet most resembles.

From this project's perspective, JetClass's most important value is not "how realistic the simulation is", but rather:

- Clean labels, suitable for supervised learning
- Large enough scale for training, validation, and test sets
- A public benchmark suitable for comparing different models and feature designs
- Capable of supporting systematic research on input features, pretraining, and transfer learning

Simplified analogy:

| Visual Classification Analogy | JetClass Counterpart |
|---|---|
| A single image | A single jet |
| Pixels / channels | Particle-level features inside a jet |
| Classification label | The physical source class of a jet |
| CNN / ViT | Jet foundation model / PET-style backbone |

---

## 3. Tasks This Project Actually Cares About

### 3.1 Primary Task: Top Tagging

Per the research plan, this project's primary task is **binary top tagging**:

- Input: particle-level information inside a jet
- Output: whether the jet is more likely a hadronic top jet or QCD background

This is more suitable as the core task of the first study than jumping straight into multi-class classification, because it:

- Has a clean problem definition
- Has clear metrics
- Connects well with literature and reference implementations
- Makes it easier to run stable ablation studies

### 3.2 Key Research Question

What this project really aims to answer is:

> On JetClass, how does the richness of input representation affect the top-tagging performance, data efficiency, and transfer value of PET / OmniLearn-style models?

Thus, JetClass is not merely a benchmark here, but an experimental platform for testing input design.

### 3.3 Evaluation Metrics This Project Cares About

Consistent with the research plan, JetClass-related experiments primarily look at:

- Accuracy
- ROC AUC
- Background rejection
- Mean and standard error from multi-seed repeated experiments

For feature ablation or data efficiency studies, priority goes to:

- AUC trends as a function of data size
- Relative improvements across different feature configurations
- Whether results are stable across different random seeds

---

## 4. Data Structure: What to Look At When Learning

JetClass raw data is typically organized as HDF5, distributed with compressed training, validation, and test packages.  
In this project, the most important thing is not memorizing file names, but understanding how the data is used by the model.

### 4.1 Common Data Objects

From the research preparation perspective, there are generally three categories of objects to care about:

| Object | Meaning | Usage |
|---|---|---|
| `data` | Particle-level features | Primary model input |
| `jet` | Jet-level features | Auxiliary information or additional input |
| `pid` | Labels | Supervised learning target |

Field naming may vary slightly across implementations, so always refer to official code and sample files when actually reading data.  
But what matters most for research is mapping these objects uniformly to:

- particle tensor
- jet-level metadata
- classification label
- mask / padding rules

### 4.2 Structural Questions This Project Must Confirm

During preparation, the following must be confirmed first:

1. Whether the number of particles per jet is fixed
2. How padding and masking are handled
3. The column ordering of particle-level features
4. Whether labels are binary or multi-class
5. How the training / validation / test split is fixed
6. How different input configurations A-D are derived from the same raw data

If these questions are not settled up front, subsequent model comparisons will easily suffer from uncontrolled differences.

---

## 5. Why JetClass Fits This Project

### 5.1 Clean Supervisory Signal

One of JetClass's greatest advantages is that it provides labels suitable for supervised learning.  
This means we can directly train classifiers and objectively compare the effects of different feature inputs and model architectures.

### 5.2 Supports Large-Scale, Unified Experimental Design

Research plan v0.2 is not about building a single model in isolation, but about running a systematic comparison:

- Input features from simple to rich
- Training data size from small to large
- Pretraining vs. random initialization comparison
- Baseline vs. main model comparison

JetClass is particularly well-suited for this kind of experimental design with "unified data, unified metrics, unified splits, unified logging."

### 5.3 Well-Suited for Input Representation Research

This project's focus is not on reinventing a completely new dataset, but on studying:

- Whether kinematics alone is sufficient
- Whether adding particle ID yields significant gains
- Whether adding charge, fraction, or other features continues to improve
- Whether richer input is truly more suitable for a foundation model than simple input

These questions are exactly the kind that are well-suited for ablation studies on JetClass.

### 5.4 Well-Suited as a Pretraining or Fine-Tuning Platform for Transfer Learning

One of the core directions in the research plan is evaluating:

- The value of a pretrained backbone
- Whether fine-tuning outperforms training from scratch
- Whether transfer to different data scales is more stable

JetClass provides a suitable unified platform for quantitatively testing these questions.

---

## 6. Limitations to Stay Aware Of

JetClass is important, but it is still **simulated data**, not a definitive real-experimental conclusion.

Therefore, in this project, always keep two points in mind:

1. Good performance on JetClass means the model works on this benchmark
2. This does not automatically mean it applies to real experimental data

In other words, JetClass is suitable for:

- Training
- Comparison
- Ablation
- Pretraining
- Mechanism analysis

But not suitable to be interpreted directly as a final physics discovery.

This is also why the project emphasizes:

- Fixed splits
- Logged seeds
- Independent test set evaluation
- Reported uncertainties
- Maintaining experimental reproducibility

---

## 7. Correspondence with Research Plan v0.2

JetClass learning materials should always serve the research plan, not be read independently of it.

| Research Plan Goal | What to Learn from This JetClass Section |
|---|---|
| Primary task: binary top tagging | Understand top-vs-QCD labels, inputs, and evaluation methods |
| Input representation research | Understand particle features, mask, padding, and A-D configurations |
| PET / OmniLearn backbone | Understand how continuous point-cloud input enters the model |
| Pretraining and transfer | Understand how JetClass serves as a pretraining / fine-tuning data platform |
| Reproducible comparison | Understand the importance of fixed splits, fixed seeds, fixed metrics |
| Writing up results | Be able to write publishable experimental narratives covering data, models, metrics, and limitations |

If a piece of knowledge does not help with these goals, it should be deprioritized.

---

## 8. Highest-Priority Items to Clarify When Learning JetClass

For this project, the highest-priority questions are:

1. What are JetClass's label definitions, and how is top-vs-QCD extracted
2. What a jet's input looks like in code
3. How mask and padding are implemented
4. How A-D feature configurations are derived from the same raw data
5. How to fix training, validation, and test splits
6. How to report results using AUC, background rejection, and seed repetitions
7. How JetClass serves comparative experiments for OmniLearn / PET-style backbones

Once these are clearly understood, subsequent modeling and experimentation will have a stable foundation.

---

## 9. Quick Preparation Checklist / Next Steps

This section is supplementary, aimed at turning JetClass learning into actionable steps.

### 9.1 First Round of Preparation

- Read the official JetClass documentation and related code
- Confirm data files, labels, and input fields
- Run a minimal one-off data read
- Check the shape, mask, and label distribution of each sample

### 9.2 Minimum Workflow Needed to Enter This Project

- Fix train / validation / test splits
- Generate A-D input configurations from raw data
- Run a simple baseline
- Compare against OmniLearn / PET-style reference implementations
- Log seed, configuration, and metrics for each experiment

### 9.3 Passing Criteria

If the following can be accomplished, the JetClass preparation phase is ready to support the main project line:

1. Capable of stably reading JetClass data
2. Can clearly explain the top-tagging task
3. Can generate A-D configurations from the same data source
4. Can complete one reproducible baseline training and evaluation
5. Can align results with research-plan v0.2

---

## 10. One-Sentence Summary

In this project, JetClass is not "a dataset overview to skim", but rather **the foundational data platform supporting input representation research for a jet foundation model**.  
The goal of this learning summary is to ensure that subsequent top-tagging, feature ablation, pretraining, and transfer experiments are all built on a unified, reproducible JetClass workflow consistent with the research plan.
