# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Researcher Context

This project is part of a computational physics research portfolio by a University of Toronto physics undergraduate (junior, Fall 2028 expected graduation). The researcher's work spans Bayesian inference (dark matter halo concentration-mass relation, PyMC 5 MCMC) and particle physics (UCL computational physics collaboration, in progress).

**Research focus:** Computational physics — applying statistical and machine learning methods to data-intensive problems across physics domains, from astrophysical inference to collider phenomenology.

**Graduate goal:** Physics PhD or Physics academic master's (Fall 2027/2028 intake), with parallel interest in computational/data science master's programs.

**Technical skills:** Python (4.0 in two courses), Bayesian MCMC (PyMC 5), scientific computing. Currently building deep learning expertise through this project.

## Project Overview

This is a research project exploring foundation model architectures for jet physics in high-energy physics (HEP). The goal is to develop and compare neural network backbones that can perform multiple jet-physics tasks (tagging, generation, anomaly detection) via transfer learning.

Reference paper: `docs/references/omnijet-omnilearn-group-report.pdf` — a comparative study of OmniJet-α (autoregressive, VQ-VAE tokenization) vs. OmniLearn (Point-Edge-Transformer, continuous set-based) for jet foundation models.

## Tech Stack

- Python 3.x (ML research ecosystem)
- TensorFlow or PyTorch (both used in reference implementations; prefer the one the target model uses)
- h5py for canonical CMS-derived HDF5 and model-view I/O
- Jupyter notebooks for exploratory analysis

## Approved Target Project Structure

```
particleML/
├── cmssw/ParticleMLExtractor/ # Pinned CMS extraction boundary
├── src/particleml/             # Conversion, views, model integration, experiments
├── configs/                    # Versioned experiment configurations
├── schemas/                    # Run, split, and prediction contracts
├── tests/                      # Unit, contract, and integration tests
└── docs/                       # Research and authoritative software documentation
```

## Language Convention

All text content in this project, including code and comments, must be written in English.

## Domain-Specific Conventions

- **Jet representation**: Particles are represented as sets of 4-momentum features (pT, η, φ, mass) plus optional particle ID (charge, type). Models treat jets as either ordered sequences (by descending pT) or unordered point clouds.
- **Current formal dataset**: public CMS 2015 `RunIIFall15MiniAODv2` simulation, extracted through pinned CMSSW into one canonical full-D HDF5 dataset. JetClass remains learning and literature-comparison material, not the v0.4 production corpus.
- **Core metrics**: Accuracy and AUC for classification; Wasserstein distance for generation quality. Report standard errors from 5-repeat runs with random seeding.
- **Binary classification baseline**: Top-tagging (t→bqq') vs. QCD background is the standard benchmark task.
