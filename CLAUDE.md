# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Researcher Context

This project is part of a computational physics research portfolio by a University of Toronto physics undergraduate (junior, Fall 2028 expected graduation). The researcher's work spans Bayesian inference (dark matter halo concentration-mass relation, PyMC 5 MCMC) and particle physics (UCL computational physics collaboration, in progress).

**Research focus:** Computational physics — applying statistical and machine learning methods to data-intensive problems across physics domains, from astrophysical inference to collider phenomenology.

**Graduate goal:** Physics PhD or Physics academic master's (Fall 2027/2028 intake), with parallel interest in computational/data science master's programs.

**Technical skills:** Python (4.0 in two courses), Bayesian MCMC (PyMC 5), scientific computing. Currently building deep learning expertise through this project.

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
particleML/
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
