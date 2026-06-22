# Document Review — `hsf-model-training-learn.html`

**Reviewer:** ark-code-latest
**Date:** 2026-06-22
**Artifact reviewed:** `docs/preparation/hsf-model-training-learn.html` (12-slide offline HTML deck, 771 lines)
**Companion material consulted:** `docs/preparation/hsf-model-training-learn.md` (markdown source), `docs/preparation/hsf-model-training-priority.md` (reading-priority spec), `AGENTS.md`
**Review type:** Document review — pedagogical fitness for a stated learner goal

---

## Learner goal being evaluated

> A senior undergraduate physics student who is **new to ML and neural networks**, has **not yet mastered neural-network concepts**, and needs the document to **quickly understand neural-network principles** *and* the **processing/training workflow** before approaching the HSF material and the JetClass foundation-model project.

The goal has two inseparable halves:
- **(a) Principles** — *what a neural network is, what it computes, and how it learns* (the *why*).
- **(b) Workflow** — *the PyTorch mechanics that implement training, validation, and prediction* (the *how*).

A document that delivers only (b) leaves the student able to *type* a training loop without *understanding* it — which blocks the later project goals of debugging, tuning, and extending models.

---

## Verdict (summary)

The deck is an **excellent PyTorch-mechanics reference** and succeeds on half (b). The five-step training loop (`zero_grad → forward → loss → backward → step`), the correct cross-entropy-on-logits guidance, the `train()`/`eval()`/`no_grad()` distinctions, the train/val/test role separation, and the JetClass-transfer table are all accurate, well-sequenced, and project-aware. The HEP-specific validation-split warning (slide 5) and the AUC-vs-accuracy distinction (slide 10) are genuinely valuable touches that connect the tutorial to this project.

It **does not yet satisfy half (a)** — the explicit primary goal. The deck *names* every core principle (neuron, weight, ReLU, gradient, backpropagation, optimizer, loss, logits) but almost never *explains* one. There is no statement that a neuron is a weighted sum plus bias, that `nn.Linear` computes `y = Wx + b`, that the diagram's edges *are* the learnable weights, that ReLU is `max(0, x)`, that a gradient is the slope of the loss, or why moving against it reduces error. Backpropagation — arguably the single most important principle for a beginner — appears only as the caption "Compute parameter gradients." A reader who is genuinely "new to neural networks" will finish able to *run* the loop but not to *explain what it does or why it works*.

Critically, the student's existing physics knowledge (potential-energy minimization, entropy, Boltzmann factors, numerical optimization) is a natural bridge to every missing concept, and the deck uses **none of it**.

**Net: strong mechanics tutorial, incomplete principles tutorial.** The findings below are ordered to close the principles gap first, then fix rendering/layout issues that affect "quick visual comprehension."

---

## Findings

| Severity | Type | Location | Issue | Evidence | Recommendation |
|---|---|---|---|---|---|
| Critical | Requirement | Whole deck; esp. Slide 6 "MLP" (HTML 518–597) | **The deck never explains what a neural network actually computes.** There is no statement that a neuron is a weighted sum plus bias, that `nn.Linear` computes `y = Wx + b`, or that the edges in the diagram *are* the learnable weights. The primary goal ("understand neural-network principles") is therefore unmet for a true beginner — they see circles and lines with no mathematical meaning. | Slide 6 draws input/hidden/output circles + connecting lines and shows `self.hidden = nn.Linear(input_size, hidden_size)` (584), but the only prose is "The MLP is useful for learning the mechanics" (592). No definition of weight, bias, or what a layer does. | Add one **principles slide before slide 6**: a single neuron computing `out = activation(Σ wᵢxᵢ + b)`, with the diagram's edges labeled "each line = one learnable weight." State plainly: "training = adjusting these weights to reduce the loss." |
| Critical | Requirement | Cover feedback arrow (HTML 332–334); Slide 8 step "backward" (HTML 635) | **Backpropagation and gradient descent — the core learning principle — are never explained.** `backward()` is captioned only "Compute parameter gradients"; `step` is "Update model parameters." A beginner is told *which function to call* but never what a gradient is, why moving against it reduces error, or what the learning rate controls. Without this, "how a neural network learns" remains a black box. | Slide 8 lists the five ops with one-line captions (632–636); no slide defines "gradient" or gives the downhill intuition. The cover SVG shows a feedback loop (334) with no label. | Add a **"How learning works" slide**: loss as a surface, gradient = direction of steepest increase, optimizer step = small move downhill, learning rate = step size. A 1-D loss-vs-weight parabola with a ball rolling down communicates this in one figure. Bridge to the student's physics background: "this is potential-energy minimization in parameter space." |
| High | Clarity | Slide 6 (HTML 532, 538, 588) | **ReLU / activation functions are named but never explained.** A beginner sees "Hidden + ReLU" and `F.relu(self.hidden(x))` with no statement of what ReLU does (`max(0, x)`) or *why a nonlinearity is needed* — without it, stacked linear layers collapse to one linear map and the network cannot learn non-linear decision boundaries. | "Hidden + ReLU" label (532) and `x = F.relu(self.hidden(x))` (588); no prose anywhere in the deck. | Add one line + a tiny `max(0, x)` sketch: "ReLU zeroes out negatives; this nonlinearity is what lets the network learn non-linear boundaries. Without it, any depth of linear layers is equivalent to a single linear layer." |
| High | Requirement | Slide 8 training loop (HTML 638–649) | **The epoch concept is missing from the HTML**, and there is no outer `for epoch in range(...)` loop. The deck shows the train loop iterating `train_loader` once, so a beginner cannot see that training *repeats over many epochs* and validates *between* them. The word "epoch" appears nowhere in the deck. | HTML loop iterates `train_loader` once with no epoch wrapper (644–649). The markdown source *does* define epoch in a table (`hsf-model-training-learn.md:96–102`), but that table was dropped from the HTML. The priority doc rates "batch size, iteration, and epoch" as **High** (`hsf-model-training-priority.md:12`). | Wrap the loop in `for epoch in range(num_epochs):`, define epoch ("one full pass over the training data"), and show train-then-validate happening *each* epoch. Port the batch/epoch/shuffle definition table back from the `.md` source. |
| High | Clarity | Slide 7 (HTML 599–622); Slide 8 caption (HTML 634) | **Loss / cross-entropy is never explained conceptually.** Slide 7 is entirely about the logits-vs-probabilities API trap; the only definition of loss is "Measure classification error" (634). A beginner does not learn what cross-entropy *measures* or why minimizing it improves classification. The term **logit** is also used throughout without definition. | Slide 7 cards contrast correct/avoid usage (607–615); no sentence on what the loss number means. "Logits" appears on slides 1, 6, 7, 8, 9, 10 without definition. | Add one sentence: "Cross-entropy is high when the model is confidently wrong and near zero when confidently right; training drives it down." Define **logit** explicitly ("an unbounded raw class score; softmax turns logits into probabilities that sum to 1"). Optionally bridge to the entropy the student knows from statistical mechanics. |
| High | Requirement | Slide 5 (HTML 486–516); Slide 9 | **The *purpose* of validation — detecting overfitting — is not stated**, and training/validation loss curves are absent. Slide 5 says validation "Checks behavior" and "helps choose checkpoints" but never names overfitting, the concept that makes validation matter. | Slide 5 cards (494–508); no mention of overfitting or loss curves anywhere. Priority doc rates "training curves / overfitting" as Medium and "why accuracy alone is limited" as High (`hsf-model-training-priority.md:17,21`). | Add one line and a small sketch: "If training loss keeps falling while validation loss rises, the model is overfitting — it is memorizing rather than generalizing. Validation is how you catch this and decide when to stop." |
| Medium | Clarity | Slide 8 (HTML 636, 641) | **Optimizer and learning rate are unexplained**, and `learning_rate` is an undefined variable in copy-paste code. `SGD` and `lr=learning_rate` appear with no statement of what an optimizer does or that `lr` controls step size. | `optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)` (641); `learning_rate` is never assigned in the snippet, so the code is not runnable as shown. | Add a one-liner ("the optimizer applies the gradient update; `lr` sets how big each step is — too big diverges, too small is slow") and set `learning_rate = 0.01` so the snippet runs. Briefly note SGD = stochastic gradient descent (one batch at a time). |
| Medium | Consistency | Slide 6 `forward()` (HTML 580–591); Slide 7 (HTML 611–615); Slide 8 (HTML 646) | The model **computes softmax on every forward pass and returns `probabilities`**, yet Slide 7 then warns "Do not pass already-softmaxed probabilities into cross entropy." The training loop unpacks `logits, probabilities` but never uses `probabilities`. Returning a tensor the learner is told *not* to use for the loss is a foot-gun, wastes compute, and teaches a non-idiomatic pattern. | `probabilities = F.softmax(logits, dim=1); return logits, probabilities` (590–591); Slide 7 "Avoid" card (611–615); training loop unpacks both (646). | Prefer `return logits` and compute softmax only at inference/scoring. If keeping both for teaching, add a caption: "softmax is computed here only for inspection — the loss uses `logits`." |
| Medium | Consistency | Slides 4, 7, 9, 12 (HTML 442, 617, 670, 674–677, 747–751) | **Literal Markdown backticks render as visible backtick characters in HTML.** Inline code written as `` `DataLoader` ``, `` `model.train()` ``, `` `zero_grad` `` etc. shows raw backticks on screen because HTML does not interpret Markdown. This looks unpolished and can confuse a beginner about whether the backticks are part of the syntax. | e.g. Slide 4 `<p>A \`DataLoader\` lets...` (442); Slide 9 table cells `` `model.train()` `` / `` `model.eval()` `` (674–677); Slide 12 list items `` `zero_grad` `` (750–751). | Replace backtick text with styled `<code>...</code>` (add a `.code` CSS class), or drop the backticks entirely. |
| Medium | Risk | CSS `pre { max-height:520px; overflow:hidden }` (HTML 174–176); `.stage { overflow:hidden }` (54) | **Content can be silently clipped.** Fixed `16/9` slides with `overflow:hidden` plus long code blocks risk cutting off the bottom of dense slides. Clipping is invisible — the reader never knows text is missing, which is dangerous for a self-study artifact. | `overflow: hidden` on both `.stage` and `pre`; Slide 8 combines the `.steps` grid + a 12-line `<pre>` (631–649); Slide 6 has a long class definition (580–591). | Verify each slide at 1280×720 and in print; reduce per-slide content, raise/remove `max-height`, or allow `overflow:auto` on code blocks so nothing is lost. |
| Medium | Clarity | Slide 8 (HTML 632) | **`zero_grad` is described as "clear old gradients" but the reason gradients accumulate is never explained.** A beginner will not understand *why* PyTorch accumulates gradients by default or why clearing them is necessary per batch. | "Clear old gradients before the new batch" (632) — no "why." | Add one sentence: "PyTorch accumulates gradients by default; without `zero_grad`, gradients from successive batches would sum together and corrupt the update." |
| Medium | Requirement | Slide 10 (HTML 689–714); Slide 11 (HTML 728) | **"AUC over accuracy" is asserted but not motivated.** The deck says "Accuracy needs labels. AUC needs ranking scores" but never explains *why* AUC/background rejection matter for jet tagging (class imbalance; performance at a fixed signal efficiency). "Background rejection" (728) is used but undefined. The priority doc rates "why accuracy alone is limited" as **High**. | Slide 10 caption (709); Slide 11 table row "Accuracy → Accuracy, AUC, background rejection" (728). | Add one sentence on imbalance: "With far more QCD than top jets, a model can score high accuracy while missing most signal; AUC / background rejection measure separation across all thresholds, which is what matters for top tagging." Define background rejection briefly. |
| Low | Clarity | Slide 6 (HTML 580–591); Slide 8 | **No model instantiation is shown.** `model = ClassifierMLP(...)` never appears, so slides 6 and 8 are disconnected — a beginner cannot run the code end-to-end. | Slide 6 defines the class; Slide 8 uses `model(x_batch)` and `model.parameters()` without any `model = ClassifierMLP(input_size, hidden_size, num_classes)` line. | Add one instantiation line before the training loop, or note explicitly that the class must be instantiated first. |
| Low | Clarity | Slide 6 diagram (HTML 525–578) | **Softmax is shown as a box labeled "optional" but never defined.** A beginner does not learn that softmax exponentiates and normalizes logits into a probability distribution. The relationship between softmax and cross-entropy (that `F.cross_entropy` applies log-softmax internally) is stated as a rule but not as a concept. | Softmax box (572–574) labeled "softmax / optional"; slide 7 says "PyTorch applies the needed log-softmax internally" (609) with no formula. | Add one line: "softmax converts logits to probabilities via `exp(xᵢ)/Σexp(xⱼ)`; `F.cross_entropy` folds this in with a numerically stable log-softmax, which is why you feed it raw logits." |
| Low | Clarity | Cover (HTML 304–307); Slide 2 (HTML 348–352) | **Foundational terms assumed without definition** for a true beginner: "features," "labels," "supervised," "classification." Likely acceptable for a physics senior, but a one-line glossary would close the gap with the stated "new to ML" audience. | "features + labels" (317); "binary signal-vs-background classification" (349) with no definition. | Add a short "Vocabulary" callout on Slide 2: features = inputs, labels = correct answers, supervised = learning from labeled examples, classification = predicting a discrete class. |
| Low | Consistency | Slide 5 vs rest of deck (HTML 504–508) | The **test set is defined but its loop is never shown** (only train and validation loops appear). A beginner may not realize the test pass reuses the validation pattern. | Slide 5 "Test" card (504–508); no test snippet anywhere in the deck. | One line on Slide 10: "Test uses the same `eval()` + `no_grad()` pattern as validation, run once at the very end after model selection." |
| Low | Clarity | Slide 11 (HTML 716–738) | **No explanation of why JetClass requires particle-set models instead of an MLP.** The transfer table states the replacement but does not motivate it. The student may not understand that an MLP expects fixed-size ordered input, whereas jets are variable-size unordered sets where permutation invariance matters. | Slide 11 table row: "Simple MLP → Deep Sets, PET, OmniLearn-style backbone" (727) — no rationale. | Add a sentence: "MLPs need a fixed-size, ordered input, but jets are variable-size unordered sets of particles; swapping two particles should not change the label. Set-based models (Deep Sets, PET) enforce permutation invariance and handle variable-length inputs." |
| Info | Documentation | HTML vs `.md` source | The HTML **dropped two helpful tables that exist in the markdown source**: the batch/epoch/shuffle definitions (`hsf-model-training-learn.md:96–102`) and the line-by-line training-loop table (`hsf-model-training-learn.md:216–225`). These directly serve the beginner goal and the High-priority "batch size, iteration, epoch" item in the priority doc. | Compare `hsf-model-training-learn.md` sections 3 and 7 with HTML Slides 4 and 8. | Port these tables (or condensed versions) into the deck; they are exactly the conceptual scaffolding the HTML is currently missing. |
| Info | Clarity | Slide 12 checklist (HTML 746–753) | The "Minimum Passing Standard" checklist asks the student to "Explain why cross-entropy labels are integer class indices" and "Explain logits vs probabilities," but the deck itself does not fully explain these — it sets expectations the content does not meet. This is a useful self-assessment tool but its items should map back to slides that actually teach each concept. | Checklist items 2 and 3 (748–749); the deck states the integer-index rule (slide 3) and the logits-vs-probabilities API rule (slide 7) but not the underlying *why*. | Either add the missing explanations (see Critical/High findings) or soften the checklist wording to match what the deck teaches. Numbering checklist items to map them back to slides would also help. |

---

## Conceptual-gap checklist (does a beginner finish able to explain each principle?)

| Principle | Covered as *mechanic*? | Covered as *concept*? | Gap |
|---|---|---|---|
| What a neuron / weight / bias is | — | ❌ | **Critical** |
| Linear layer = `Wx + b` | code only | ❌ | **Critical** |
| Activation (ReLU) and why nonlinearity | name only | ❌ | High |
| What loss / cross-entropy measures | API trap only | ❌ | High |
| Logits vs probabilities | ✅ | partial | Medium |
| Softmax (what it computes) | box only | ❌ | Low |
| Gradient / backpropagation | function name | ❌ | **Critical** |
| Optimizer / learning rate | code only | ❌ | Medium |
| Epoch / iteration | ❌ (HTML) | ❌ | High |
| `zero_grad` (why clear) | ✅ | ❌ | Medium |
| Train / val / test roles | ✅ | ✅ | Good |
| `train()` / `eval()` / `no_grad()` | ✅ | ✅ | Good |
| Overfitting (why we validate) | — | ❌ | High |
| Metrics (accuracy vs AUC) | ✅ | partial | Medium |
| Transfer to JetClass | ✅ | ✅ | Good |

The deck is strong on the bottom half of this table (workflow discipline) and weak on the top half (what the network *is* and *how it learns*) — which is precisely the half the stated goal prioritizes.

---

## Visual / layout assessment (supports "quick learning"?)

**Strengths**
- Consistent slide template (eyebrow → title → grid body → footer breadcrumb); good use of color to distinguish data (teal) vs model (gold) vs avoid (red).
- The Slide 6 MLP topology, Slide 4 batching figure, and Slide 10 argmax-vs-score branch are the *right choice* of diagrams and genuinely help.
- SVGs carry `role="img"` and `aria-label`s — good accessibility hygiene.
- Print CSS (`@media print`, A4 landscape) enables clean PDF/handout export.
- 16:9 fixed aspect ratio prevents per-slide information overload.

**Weaknesses for a beginner**
- The diagrams illustrate **data flow** but never annotate **meaning** — e.g. Slide 6 edges aren't labeled as weights; the cover's backprop loop has no "gradients flow backward" label. The visuals show *where data goes*, not *what is learned*, so they don't yet carry the principles load.
- No figure for the two hardest concepts for newcomers: **gradient descent** (a loss-surface / ball-rolling-downhill figure) and **overfitting** (a train-vs-val loss curve). These are the highest-value diagrams to add and would each replace several sentences of text.
- `overflow:hidden` on fixed-ratio slides risks **silent clipping** of the densest slides (see Medium finding).
- Visible literal backticks (see Medium finding) reduce polish.
- No inter-slide navigation (keyboard arrows, prev/next). Acceptable for linear reading but reduces quick-reference value.

---

## Prioritized recommendations

1. **Add a "what a neuron computes" slide** (`Wx + b`, edges = weights, training = tuning weights). Place it before slide 6. *(Critical)*
2. **Add a "how learning works" slide** — loss surface + gradient-descent intuition + learning rate as step size. Bridge to the student's physics intuition (potential-energy minimization). *(Critical)*
3. **Explain ReLU, cross-entropy meaning, optimizer, epoch, and `zero_grad`** in one line each; wrap the loop in an epoch loop and define `learning_rate`. Port the batch/epoch and line-by-line tables back from the `.md` source. *(High)*
4. **Add overfitting + AUC motivation** lines with a small train/val loss-curve sketch. *(High/Medium)*
5. **Fix the `forward()` return** — return only `logits`; compute softmax at inference only. *(Medium)*
6. **Fix rendering:** replace literal Markdown backticks with `<code>`, and verify no slide clips under `overflow:hidden`. *(Medium)*
7. **Add model instantiation, softmax formula, test-loop note, and JetClass permutation-invariance motivation.** *(Low)*

With items 1–3, the deck would meet its stated primary goal: a physics student new to neural networks would leave understanding both *why* the network works and *how* to train it, rather than only the latter.

---

*End of review.*
