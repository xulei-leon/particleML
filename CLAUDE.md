# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a research project exploring foundation model architectures for jet physics in high-energy physics (HEP). The goal is to develop and compare neural network backbones that can perform multiple jet-physics tasks (tagging, generation, anomaly detection) via transfer learning.

Reference paper: `docs/references/Group-Report.pdf` — a comparative study of OmniJet-α (autoregressive, VQ-VAE tokenization) vs. OmniLearn (Point-Edge-Transformer, continuous set-based) for jet foundation models.

## Tech Stack

- Python 3.x (ML research ecosystem)
- TensorFlow or PyTorch (both used in reference implementations; prefer the one the target model uses)
- h5py for JetClass dataset I/O
- Jupyter notebooks for exploratory analysis

## Planned Project Structure

```
physics-foundation-models/
├── data/          # Data loading, preprocessing, dataloader classes
├── models/        # Model architectures (PET, autoregressive, custom)
├── training/      # Training scripts and configs
├── evaluation/    # Benchmarking: accuracy, AUC, Wasserstein distance
├── notebooks/     # EDA and visualization
└── docs/          # References and notes
```

## Domain-Specific Conventions

- **Jet representation**: Particles are represented as sets of 4-momentum features (pT, η, φ, mass) plus optional particle ID (charge, type). Models treat jets as either ordered sequences (by descending pT) or unordered point clouds.
- **Primary dataset**: JetClass — simulated jets across 10 classes, stored as HDF5 files with `data` (particle features), `jet` (jet-level features), and `pid` (labels) datasets.
- **Core metrics**: Accuracy and AUC for classification; Wasserstein distance for generation quality. Report standard errors from 5-repeat runs with random seeding.
- **Binary classification baseline**: Top-tagging (t→bqq') vs. QCD background is the standard benchmark task.
