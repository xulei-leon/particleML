# Review Report: `docs/preparation/hsf-model-training-learn.html`

**Review type:** Document review  
**Reviewer:** deepseek-v4-pro  
**Date:** 2026-06-22  
**Target audience:** Senior undergraduate physics student, new to ML/neural networks, preparing for a jet-physics foundation-model project.

---

## Executive Summary

This 12-slide HTML tutorial deck translates the HSF Model Training material into a self-contained, slide-based learning resource aimed at a physics undergraduate with minimal ML background. It succeeds as a **PyTorch mechanics reference** — a student who already understands neural-network concepts can use it to memorize the training-loop boilerplate and avoid common pitfalls. However, it **does not** satisfy the primary goal of teaching neural-network principles to a beginner. The document is code-forward and terminology-dense, assuming foundational knowledge (gradients, loss landscapes, activation functions, matrix multiplication as a linear layer) that the target reader has not yet acquired. Conceptual gaps are pervasive: the document tells the reader *what* to do but rarely *why*, and it provides almost no physics intuition to anchor the mathematical abstractions.

**Verdict:** Useful as a *companion* reference after the student has learned fundamentals elsewhere, but inadequate as a standalone tutorial for an ML beginner.

---

## Findings Table

| Severity | Type | Location | Issue | Evidence | Recommendation |
|----------|------|----------|-------|----------|----------------|
| **High** | Clarity | Slide 6 (MLP diagram + code, lines 519–596) | `ClassifierMLP.forward()` returns both `logits` *and* `probabilities`, then Slide 7 correctly warns against passing probabilities to `cross_entropy`. A beginner will ask: "Why compute probabilities at all?" The dual output creates unnecessary cognitive dissonance. | `probabilities = F.softmax(logits, dim=1); return logits, probabilities` (line 590–591) vs. correct loss guidance on Slide 7 (line 608). | Return only `logits` from `forward()`. If probabilities are needed for inspection or AUC, compute them in a separate method or inline. This eliminates the contradiction and keeps the training path clean. |
| **High** | Clarity | Slide 8 (training loop, lines 638–649) | The training loop shows only the inner batch loop. There is **no outer epoch loop** shown anywhere in the document. A beginner will copy this code and wonder why it runs only once through the data. | `for x_batch, y_batch in train_loader:` (line 644) — no enclosing `for epoch in range(num_epochs):`. | Show the full nested loop: `for epoch in range(epochs):` wrapping the batch loop. This is essential for a beginner to understand the difference between an epoch and a batch — a distinction never made in the document. |
| **High** | Requirement | Entire document | **No explanation of what a gradient is, what gradient descent does, or why backpropagation works.** The document uses `loss.backward()` and `optimizer.step()` as incantations. A physics student can understand these concepts through analogies (e.g., potential energy minimization, force = negative gradient), but none are provided. | "Compute parameter gradients" (line 635) is the sole explanation of backpropagation. | Add a "Physics Intuition" sidebar or slide: (a) loss as a potential energy surface over parameter space, (b) gradient as the direction of steepest increase, (c) optimizer step as moving downhill, (d) analogy to numerical minimization in classical mechanics. This bridges the student's existing physics knowledge to the ML concepts. |
| **High** | Clarity | Slide 6 (lines 519–596) | The MLP slide shows network structure with circles and lines but **never explains what a linear layer computes** (matrix multiply + bias). A reader sees `nn.Linear(input_size, hidden_size)` with no intuition for what happens inside. | `self.hidden = nn.Linear(input_size, hidden_size)` (line 584) — no accompanying equation or prose. | Add a one-line equation: `h = ReLU(W·x + b)` above or beside the diagram. State explicitly that the "lines" in the SVG represent the weight matrix entries. This demystifies the black box. |
| **High** | Clarity | Slide 7 (lines 599–621) | **Cross entropy is never explained conceptually.** The slide only states the correct API call. There is no mention of entropy, information theory, or why this loss penalizes confident wrong predictions more than hesitant wrong ones — a concept a physics student could connect to Boltzmann distributions or statistical mechanics. | `loss = F.cross_entropy(logits, y_batch)` (line 608) with no explanatory prose. | Add a sentence: "Cross entropy measures how well the predicted probability distribution matches the true label distribution. It heavily penalizes confident mistakes — if the model says 99% class A when the truth is class B, the loss is much larger than if it says 51% A." Optionally connect to the Gibbs/entropy the student knows from statistical mechanics. |
| **High** | Requirement | Entire document | **No mention of epochs, overfitting, or early stopping.** A beginner will train indefinitely without understanding when to stop. The validation slide (9) shows how to run validation but not *what the validation loss curve means* or when to save a checkpoint. | Slide 9 (lines 655–682) only covers mechanics, not interpretation. | Add a small conceptual slide or callout: (a) training loss decreases as the model memorizes, (b) validation loss decreases then increases = overfitting, (c) stop training when validation loss plateaus or worsens. Without this, the student cannot use validation meaningfully. |
| **High** | Clarity | Slide 8 (line 641) | **Learning rate (`lr=learning_rate`) is used in code but never defined or explained.** The student sees `SGD(model.parameters(), lr=learning_rate)` with no intuition for what this hyperparameter controls. | `torch.optim.SGD(model.parameters(), lr=learning_rate)` (line 641) — the variable `learning_rate` is not defined or discussed. | Explain learning rate as the step size in parameter space: "too large, the optimizer overshoots the minimum; too small, training is slow." Include a brief note that 0.01–0.001 are typical starting values. |
| **Medium** | Clarity | Slide 6 (lines 519–596) | **ReLU is mentioned in text but never explained.** The SVG label says "Hidden + ReLU" and the code contains `F.relu(self.hidden(x))`, but a beginner does not know that ReLU is `max(0, z)` or why non-linearity is essential (without it, stacked linear layers collapse to a single linear layer). | `x = F.relu(self.hidden(x))` (line 588) — no prose explaining the activation function. | Add one sentence: "ReLU (Rectified Linear Unit) replaces negative values with zero: `ReLU(z) = max(0, z)`. Without a non-linearity like ReLU between layers, a deep network would be equivalent to a single linear layer and could not learn complex decision boundaries." |
| **Medium** | Clarity | Slide 8 (line 633) | **`zero_grad` is described as "clear old gradients" but the reason gradients accumulate is never explained.** A beginner will not understand *why* PyTorch accumulates gradients by default or why clearing them is necessary per batch. | "Clear old gradients before the new batch" (line 632) — no "why." | Add context: "PyTorch accumulates gradients by default (for RNNs and other advanced uses). For standard training, you must reset them before each batch, or gradients from multiple batches will sum together and corrupt the update." |
| **Medium** | Requirement | Slides 3, 11 (lines 389–422, 716–738) | **No explanation of why JetClass requires particle-set models (Deep Sets, PET) instead of MLPs.** The transfer table states the replacement but does not motivate it. The student may not understand that an MLP expects fixed-size input, whereas jets contain variable numbers of particles — and that permutation invariance matters for particle sets. | Slide 11 table row: "Simple MLP → Deep Sets, PET, OmniLearn-style backbone" (line 727) — no rationale. | Add a sentence: "MLPs require a fixed-size, ordered input — but jets are variable-size, unordered sets of particles. Swapping two particles should not change the jet's classification. Set-based models (Deep Sets, PET) enforce permutation invariance and handle variable-length inputs." |
| **Medium** | Clarity | Slide 10 (line 695) | `logits[:, 1]` as the signal score is stated without explanation. A beginner may not understand that in binary classification with 2 output neurons, class-1 logit (or the difference) serves as a ranking score. | `signal_score = logits[:, 1]` (line 695) — no prose. | Add: "For binary classification with 2 output neurons, `logits[:, 1]` is the raw score for the signal class. Higher values mean the model considers the jet more signal-like. ROC curves and AUC use the *ranking* of these scores, not the hard class predictions." |
| **Medium** | Correctness | Slide 6 (line 590) | Computing `F.softmax(logits, dim=1)` inside `forward()` and then also applying it implicitly via `F.cross_entropy` (which applies log-softmax internally) **doubles the softmax computation path** and can introduce subtle numerical issues. While not a bug (the returned probabilities are just unused during training per Slide 7), it is misleading. | Line 590–591. | Either remove softmax from `forward()` or document that probabilities are for inspection only, not for the loss. |
| **Medium** | Clarity | Slide 5 (lines 486–516) | The train/validation/test split slide correctly distinguishes the three roles but **does not explain what split ratios to use** (e.g., 70/15/15 or 80/10/10). A beginner will not know how much data to allocate. | Slides 5 — no ratio guidance. | Add a rule of thumb: "Typical splits: 70% train / 15% validation / 15% test, or 80/10/10 for large datasets. Validation needs enough data to produce stable loss estimates." |
| **Low** | Requirement | Entire document | **No discussion of numerical stability or mixed precision**, which is relevant when moving from toy data to real JetClass HDF5 files with 200 particles per jet and floating-point feature ranges. | N/A — missing content. | Add a brief note or callout on Slide 11: "JetClass features span wide ranges (pT, mass). Normalize/standardize features before training. Consider scaling pT by log for better numerical behavior." |
| **Low** | Usability | Slides 3, 4, 6, 7, 8, 9 (multiple) | Six out of twelve slides contain code blocks. While each is relevant, the **ratio of code to concept is heavily skewed toward code**. The document reads as a PyTorch API walkthrough rather than a neural-network concept tutorial. | Code blocks on slides 3 (line 399), 4 (line 432), 6 (line 580), 7 (line 608/613), 8 (line 638), 9 (line 663). | Reduce code snippets to minimal essential lines on concept-heavy slides (e.g., Slide 6 could drop the full class definition and show only the salient equations). Move full code to an appendix or adjacent reference file. |
| **Low** | Usability | Slider header structure | No inter-slide navigation (prev/next buttons, keyboard shortcuts). A student must scroll through all 12 slides linearly. This reduces usability as a quick-reference tool. | HTML body lacks navigation controls. | Consider adding minimal JavaScript for arrow-key navigation and a slide counter/dot indicator, or keep as-is with a note that the document is intended for linear reading. |
| **Info** | Documentation | Slide 12 (lines 739–767) | The "Minimum Passing Standard" checklist is an excellent self-assessment tool. It explicitly states what the student should be able to explain or write after studying. | Lines 746–753. | Keep this. Consider numbering the checklist items to map them back to the slides that teach each concept. |
| **Info** | Usability | CSS (lines 7–291) | The CSS is clean, well-organized with CSS custom properties for theming. The 16:9 slide aspect ratio, semantic color tokens, and print-friendly `@media print` block are well-executed. | Lines 8–21 (color tokens), lines 35–48 (deck/slide layout), lines 257–291 (print). | No changes needed. The visual design supports quick scanning and is suitable for both screen and printed handout use. |
| **Info** | Documentation | Slide 11 (lines 716–738) | The transfer table mapping HSF concepts to JetClass equivalents is effective and directly addresses the user's project context. | Lines 723–729. | Keep this. Consider expanding with a third column ("What changes") that explicitly notes the added complexity (variable particle counts, permutation invariance, HDF5 I/O). |
| **Info** | Clarity | Slide 1 (line 310–335) | The pipeline SVG on the cover slide provides a helpful high-level overview, but the **backpropagation feedback loop** (the golden curved arrow from Loss/Update back to Model) is a critical concept that may not be obvious to a first-time viewer. | Line 334 — the `#c9973a` path from Update back to Model region. | Add a small text label on the backprop arrow: "weight update (backprop)" to make the feedback loop explicit. |

---

## Detailed Assessment by Focus Area

### 1. Beginner-Friendliness for a Physics Student New to ML

**Rating: 2/5**

The document assumes comfort with: tensors, gradient computation, loss functions, activation functions, and the concept of iterative optimization. None of these are taught. A physics student strong in linear algebra and calculus has the mathematical prerequisites but lacks the domain-specific vocabulary and the *mental model* of what training a neural network actually means.

The single largest barrier is the absence of any physics analogy. The target student has studied Lagrangian/Hamiltonian mechanics, statistical physics, and numerical methods — all of which provide natural entry points for understanding neural network training (loss landscapes as potentials, gradient descent as following forces, softmax as a Boltzmann distribution, cross entropy as relative entropy). The document uses none of these bridges.

### 2. Clarity of Neural-Network Principles (Not Just PyTorch Mechanics)

**Rating: 1.5/5**

| Principle | Covered? | Quality |
|-----------|----------|---------|
| What is a neural network? | No | — |
| Linear layers (weights, biases) | No | Mentioned only as `nn.Linear()` |
| Activation functions (why non-linearity?) | No | ReLU named, not explained |
| Forward pass | Partial | Shown in code, not explained as function composition |
| Logits vs probabilities | Partial | Distinction stated as API rule, not as concept |
| Loss functions (cross entropy intuition) | No | API call only |
| Gradient descent (what are gradients?) | No | "Compute parameter gradients" is the sole text |
| Backpropagation (chain rule) | No | `loss.backward()` with no explanation |
| Optimizer step (parameter update) | No | `optimizer.step()` with no explanation |
| Epochs, batches, iterations | Partial | Batch concept is solid; epoch concept is missing |
| Overfitting and generalization | No | Not mentioned |
| Validation purpose | Good | Slide 5 and 9 are clear on mechanics |

The document teaches *what to type*, not *what is happening*. For a student who needs to later debug, tune, or extend these models (which this project explicitly requires), this gap is significant.

### 3. Visual Diagram Effectiveness

**Rating: 3.5/5**

Strengths:
- Pipeline overview (Slide 1) clearly shows the data→model→logits→loss→update flow with backprop feedback.
- Workflow diagram (Slide 2) maps arrays through tensor conversion, DataLoader, training, to prediction.
- Mini-batch visualization (Slide 4) shows shuffling and batching with distinct colors for batches — effective.
- MLP structure diagram (Slide 6) shows node layers and dense connectivity. The softmax block is a nice touch.
- Logits branching diagram (Slide 10) clearly distinguishes class prediction (argmax) from ranking score (AUC).

Weaknesses:
- The MLP diagram (Slide 6) shows geometric connectivity but labels nothing about weights, biases, or dimensions. A student sees lines between circles with no mathematical meaning attached.
- The backpropagation feedback arrow (Slide 1) is subtle (gold colored, same as the model box). It would benefit from an explicit label.
- No diagram explains the loss landscape or gradient descent — this is the single most impactful visualization for a physics student.

### 4. Conceptual Gaps Before the Student Can Understand HSF Material

The student needs to supplement this document with external resources covering:

1. **Gradient descent and optimization** — what gradients are, why we follow the negative gradient, what SGD does differently from vanilla GD.
2. **Backpropagation** — the chain rule applied through computational graphs. Without this, `loss.backward()` is magic.
3. **Loss functions** — what cross entropy actually measures, why it works for classification, the connection to maximum likelihood.
4. **Activation functions** — why non-linearity is essential (otherwise deep networks collapse to linear models), common choices (ReLU, GELU, sigmoid).
5. **Overfitting and regularization** — why validation loss can increase while training loss decreases, what dropout/weight decay do.
6. **Particle-set representations** — why permutation invariance matters for jets, how Deep Sets and PETs enforce it.
7. **Epochs** — the outer loop over the full dataset, the relationship between epochs, batches, and iterations.

### 5. Overly Dense, Code-Heavy, or Misleading Parts

- **Slide 6 code:** The full `ClassifierMLP` class definition (14 lines of code) could be replaced with a 2-line equation and a simplified diagram. The class structure is a PyTorch idiom, not a neural-network concept.
- **Slide 3/4 code:** Reasonably minimal and well-contextualized.
- **Slide 7:** The correct/avoid card pair is good, but the rationale ("PyTorch applies log-softmax internally") should be expanded with a one-sentence explanation of numerical stability.
- **Slide 8 code:** Missing the epoch loop is a significant omission (see findings table).
- **No misleading content was found**, except for the dual logits+probabilities return value pattern (see findings table).

### 6. HTML Slide Layout for Quick Learning

**Rating: 4/5**

- Clean visual hierarchy: eyebrow → title → body with grids → footer with breadcrumb.
- Semantic color system: brand teal for structure, amber for emphasis/warnings, red for "avoid" patterns, green-tinted background for readability.
- 16:9 fixed-aspect slides prevent information overload per slide.
- Grid layouts (2-column, 3-column) break content into digestible chunks.
- Code blocks have dark background with light text — good contrast.
- Callout boxes (amber left-border) effectively highlight warnings and project-specific notes.
- Print-friendly CSS enables PDF/handout export.
- No slide-to-slide navigation controls (keyboard arrows, dot indicators) — a minor usability gap.

---

## Summary of Recommendations (Priority-Ordered)

1. **Add a "Physics Intuition" narrative** — map gradient descent to potential minimization, softmax to Boltzmann factors, cross entropy to relative entropy. This single change would unlock the document for its target audience.

2. **Explain the five core concepts currently missing:** gradients, loss landscape, activation functions, epochs, and overfitting. These are prerequisites for the HSF material, not optional enrichment.

3. **Fix the `forward()` return value** — return only logits. Teach probability computation as a separate step for evaluation/prediction.

4. **Add the outer epoch loop** to the training loop code. Without it, the code is incomplete and misleading.

5. **Add equation-level annotations** to the MLP diagram: `h = ReLU(W₁x + b₁)`, `logits = W₂h + b₂`. Let the reader connect code to math.

6. **Motivate the MLP→particle-set transition** with one sentence about variable-length, unordered jet constituents and permutation invariance.

7. **Add inter-slide navigation** (optional but low-effort) for quick-review use.

---

*End of review.*
