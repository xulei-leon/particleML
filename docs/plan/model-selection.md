# Model Selection for Foundation-Model Fine-Tuning

## Conclusion

The recommended foundation model for this project is a **pretrained OmniLearn/PET-style backbone**, fine-tuned on the project's JetClass top-vs-QCD task and any later project-specific jet dataset that passes the feature-schema checks.

More precisely:

> Use an OmniLearn/PET-style continuous point-cloud backbone as the main architecture. When a reliable and input-compatible pretrained OmniLearn/PET checkpoint is available, initialize from that checkpoint and fine-tune on the project data. If the pretrained checkpoint cannot be reproduced, fall back to the same PET-style backbone with random initialization and report the study as a controlled PET-style feature-ablation experiment rather than a full foundation-model transfer study.

This choice keeps the project centered on the strongest current research question: how particle-level input feature richness affects jet-tagging performance and data efficiency under a fixed task, dataset split, preprocessing pipeline, and evaluation protocol.

## Recommended Model Role

| Model or condition | Recommended role | Suitable as the foundation model for fine-tuning? | Reason |
|---|---|---:|---|
| Pretrained OmniLearn/PET | Primary foundation-model starting point | Yes | It combines the PET-style particle-set architecture with pretrained weights, so it directly supports the foundation-model workflow: reuse a learned jet representation and fine-tune it on the project's target task. |
| OmniLearn/PET-style backbone | Main architecture family | Yes, if initialized from pretrained weights; otherwise it is the architecture only | The architecture is well aligned with jets as continuous, unordered, variable-length particle sets. However, without pretrained weights it is not itself a pretrained foundation model. |
| Same PET-style backbone, random initialization | Initialization control | No | This condition tests whether observed gains come from pretraining or from architecture and input features alone. It is important for interpretation, but it should not replace the pretrained model as the main foundation-model condition unless the checkpoint is unavailable. |
| Deep Sets | Low-complexity baseline | No | It is useful as a simple permutation-invariant baseline for checking whether the feature-ablation trend appears without a transformer-style backbone. Its role is control, not primary foundation-model transfer. |
| ParticleNet or EdgeConv-style model | Optional stronger task-specific baseline | No | It can provide a stronger point-cloud comparison after the core PET and Deep Sets experiments are stable, but it adds implementation and tuning cost and should not define the first study. |
| OmniJet-alpha | Literature contrast and background model | Not recommended for the first stage | It uses VQ-VAE tokenization plus autoregressive sequence modeling. That route is less convenient for this project's feature-ablation focus and would require a larger tokenizer and sequence-model reproduction effort. |
| OmniLearned | Future reference | Not for the first stage | It is relevant as a successor framework, but the current project documents do not place it in the first experimental matrix. |

## Why Pretrained OmniLearn/PET Should Be Selected

The main reason is that the project is not trying to prove that one architecture is globally best. It is trying to quantify how much particle-level feature richness matters for top tagging. A PET-style model is the best fit for this because it can process jet constituents as a masked particle set and can naturally support nested feature configurations such as kinematics only, kinematics plus charge, kinematics plus PID, and fuller particle-observable representations.

Pretrained OmniLearn/PET is stronger than a randomly initialized PET-style backbone for the project's stated foundation-model goal. A pretrained checkpoint allows the project to test whether a representation learned before the target task improves data efficiency or final performance after fine-tuning. This directly matches the foundation-model pattern: pretrain once, then adapt to downstream data and tasks.

At the same time, the project should not make checkpoint availability a hard dependency. If the checkpoint is incompatible, unavailable, or unstable to reproduce, the same PET-style architecture can still support a publishable controlled feature-ablation study. In that fallback case, the claims must be narrower: the paper should discuss PET-style jet tagging and feature representation, not broad pretrained foundation-model superiority.

## Architecture vs. Pretrained Model

| Question | OmniLearn/PET-style backbone | Pretrained OmniLearn/PET |
|---|---|---|
| What is it? | The model architecture or architecture family | The same architecture initialized from pretrained weights |
| Does it include learned prior knowledge? | Only if pretrained weights are loaded | Yes |
| Is it enough to claim foundation-model fine-tuning? | Not if trained from scratch | Yes, if the checkpoint is reliable and the target fine-tuning protocol is documented |
| What does it test? | Whether PET-style particle-set modeling works for the task | Whether pretrained jet representations transfer to the project task |
| Main risk | Random initialization removes the transfer-learning claim | Checkpoint reproduction, software environment, and input-feature compatibility |

The distinction matters for writing and experiment design. The project can choose the **OmniLearn/PET-style backbone** as its architecture, but the foundation model that should be fine-tuned is the **pretrained OmniLearn/PET instance**.

## Comparison With Alternatives

OmniJet-alpha is an important reference because it demonstrated a cross-task foundation model for particle physics. However, it represents particles through VQ-VAE tokenization and autoregressive sequence modeling, which requires imposing an order on jet constituents. That makes it less convenient for this project's central feature-ablation question, especially when adding or removing charge, PID, and other particle-level features.

Deep Sets is valuable because it is simple and permutation-invariant. It should be used to check whether the observed feature gains are robust in a much lower-capacity set model. If the PET-style model improves with richer features but Deep Sets does not, that suggests architecture and feature representation interact. If both improve similarly, the case for feature richness becomes stronger and less architecture-specific.

ParticleNet or EdgeConv-style models can be added later as stronger point-cloud baselines. They should not be included before the core PET and Deep Sets experiments are complete, because adding strong baselines too early turns the project into a broad model benchmark and weakens the clean feature-representation focus.

## Practical Selection Rule

Use the following decision rule for the first implementation stage:

1. Try to reproduce the OmniLearn/PET reference workflow and load a pretrained checkpoint.
2. If the checkpoint loads and supports the selected feature interface, use **pretrained OmniLearn/PET + end-to-end fine-tuning** as the main condition.
3. Run the **same PET-style backbone with random initialization** as a control when compute permits.
4. Run **Deep Sets** as the required low-complexity baseline.
5. Add **ParticleNet or EdgeConv** only after the core feature-ablation results are stable.

This rule preserves the project's foundation-model motivation while keeping the first publishable study focused, feasible, and interpretable.

