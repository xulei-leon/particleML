# Physics Foundation Models

## Project Background

Foundation models are emerging as powerful tools in high-energy physics (HEP), particularly for jet physics at particle colliders like the LHC. Jets—collimated streams of particles produced from high-energy collisions—must be accurately reconstructed, classified, and modeled to understand fundamental particle interactions and to search for new physics.

Traditional deep learning models for jet physics are task-specific: they are trained for individual tasks (tagging, generation, anomaly detection) on specific datasets, particle types, and detector geometries. This specialization makes them computationally expensive to train and limits their applicability across the diverse landscape of HEP experiments.

Foundation models address these limitations by learning general representations of jet structure through pretraining on large datasets, then adapting to specific downstream tasks via transfer learning (fine-tuning). This approach promises:
- **Multi-task capability**: A single backbone model that can perform jet tagging, generation, anomaly detection, and more
- **Data efficiency**: Improved performance on tasks where labeled data is scarce
- **Computational efficiency**: Reduced training cost by reusing pretrained backbones

## Research Inspiration

This project is inspired by and builds upon the comparative study of two pioneering foundation models for jet physics:

- **OmniJet-α** (Birk et al., 2024): The first foundation model for particle physics, inspired by LLM architectures. It uses VQ-VAE tokenization and autoregressive sequence modeling, treating jets as ordered sequences of particle constituents.

- **OmniLearn** (Mikuni & Nachman, 2025): A Point-Edge-Transformer (PET) based model that treats jet constituents as continuous, unordered point clouds—a representation more naturally aligned with the physical structure of jets.

Key findings from the comparative study that guide this project:
1. Both models successfully demonstrate foundation model capability—performing both jet tagging and generation with clear benefits from transfer learning
2. The dimensionality and richness of input particle representations is the primary determinant of peak performance, regardless of architecture
3. Discrete tokenization (as in OmniJet-α) introduces only marginal information loss for classification, but continuous set-based architectures (as in OmniLearn) offer greater flexibility and faster convergence on small datasets
4. Architecture alignment with the natural structure of jets (unordered sets of particles) is important for sample efficiency, though sufficient data may overcome representational mismatches

## Research Direction

This project aims to explore and develop foundation model architectures for jet physics, focusing on:

- **Representation learning**: Investigating how different particle-level input representations—kinematic features, particle identification, charge, energy/momentum fractions—affect foundation model performance across tasks

- **Architecture design**: Comparing set-based (transformer/PET) vs. sequence-based (autoregressive) architectures, and exploring hybrid approaches that combine the strengths of both paradigms

- **Transfer learning dynamics**: Understanding how pretraining strategies (generative vs. supervised), backbone freezing strategies, and dataset size affect downstream task performance

- **Multi-task evaluation**: Systematic benchmarking across jet tagging, generation, anomaly detection, and likelihood ratio estimation tasks

- **Generalization**: Evaluating model transferability across different jet types, detector geometries, and simulated-to-real data domains

## Key References

- Birk, J., Hallin, A., & Kasieczka, G. (2024). "OmniJet-α: the first cross-task foundation model for particle physics." *Machine Learning: Science and Technology*, 5(3), 035031.
- Mikuni, V. & Nachman, B. (2025). "OmniLearn: A Method to Simultaneously Facilitate All Jet Physics Tasks." *Physical Review D*, 111(5), 054015.
- Bhimji, W. et al. (2025). "OmniLearned: A Foundation Model Framework for All Tasks Involving Jet Physics." arXiv:2510.24066.

## Dataset

The primary dataset used for training and evaluation is **JetClass**, a large-scale benchmark dataset of simulated jets spanning ten jet classes, widely used in HEP deep learning research.

## Project Structure

```
physics-foundation-models/
├── docs/
│   └── references/       # Reference papers and literature
├── data/                 # Data loading and preprocessing
├── models/               # Model architectures (OmniJet-α, OmniLearn, custom)
├── training/             # Training scripts and configurations
├── evaluation/           # Evaluation and benchmarking scripts
├── notebooks/            # Exploratory analysis and visualization
└── README.md
```
