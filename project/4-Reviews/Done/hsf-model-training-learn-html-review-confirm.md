# hsf-model-training-learn.html Review Confirm

**Reviewed Inputs**

- `docs/learning/hsf-model-training-tutorial.html`
- `docs/4-Reviews/hsf-model-training-learn-review-by-deepseek-v4-pro.md`
- `docs/4-Reviews/hsf-model-training-learn-review-by-ark-code-latest.md`
- `docs/learning/hsf-model-training-tutorial.md`
- `docs/learning/hsf-model-training-reading-priority.md`
- `AGENTS.md`

**Review Date**

- 2026-06-22

## Overall Conclusion

Both reviews are technically sound and aligned with the stated learner goal. The current HTML succeeds as a clean PyTorch training-workflow reference, but it does not yet fully satisfy the stronger goal: helping a physics undergraduate who is new to ML quickly understand neural-network principles and the training process. The reviewers correctly identify that the deck explains API order better than it explains what a neural network computes, why gradients update weights, what loss means, and how validation reveals overfitting.

The target should not be accepted as complete for the user's stated learning goal yet. It can be accepted only as an intermediate workflow deck. The minimum remaining work is to add conceptual slides and visual explanations for neuron computation, linear layers, ReLU, loss/cross-entropy, gradient descent/backpropagation, epochs, overfitting, and the JetClass set-model transition.

## Decision Table

| No. | Severity | Type | Review Source | Original Comment Summary | Decision | Evidence | Follow-up Plan / Rejection Reason |
|---|---|---|---|---|---|---|---|
| 1 | Critical | Requirement | Ark C1; DeepSeek C4 | The deck does not explain what a neural network computes: weighted sums, bias terms, `nn.Linear`, or edges as learnable weights. | Accept | Slide 6 shows circles, edges, and `nn.Linear`, but no equation like `y = Wx + b` or explanation of weights/biases. The user explicitly wants neural-network principles, not only code order. | Add a principles slide before the MLP slide showing one neuron: inputs, weights, bias, weighted sum, activation, and output. Label diagram edges as learnable weights. |
| 2 | Critical | Requirement | Ark C2; DeepSeek C3 | Backpropagation, gradient descent, and gradient intuition are not explained. | Accept | Slide 8 only says `backward` computes parameter gradients and `step` updates parameters. The cover feedback arrow is unlabeled. | Add a "How learning works" slide with loss as a surface, gradient as steepest uphill direction, optimizer step as moving downhill, and learning rate as step size. Use a physics analogy: potential-energy minimization in parameter space. |
| 3 | High | Clarity | Ark C3; DeepSeek C8 | ReLU is named but not explained, including why nonlinearity matters. | Accept | Slide 6 labels "Hidden + ReLU" and uses `F.relu`, but gives no definition or motivation. | Add a compact ReLU explanation and sketch: `ReLU(z) = max(0, z)`. State that without nonlinear activation, stacked linear layers collapse into one linear map. |
| 4 | High | Requirement | Ark C4; DeepSeek C2 | The training loop lacks an outer epoch loop and does not teach epoch vs batch. | Accept | Slide 8 uses `for x_batch, y_batch in train_loader:` only. The HTML does not define epoch, though the Markdown source had an epoch definition. | Update Slide 8 to include `for epoch in range(num_epochs):`, define epoch, and show validation after each epoch. Port or recreate the batch/epoch/iteration explanation. |
| 5 | High | Clarity | Ark C5; DeepSeek C5 | Cross entropy is shown as an API call but not explained conceptually. | Accept | Slide 7 explains logits vs probabilities but not what cross entropy measures or why confident wrong predictions are penalized. | Add a short conceptual explanation: cross entropy is high when the model is confidently wrong and low when confidently right. Optionally connect to entropy/statistical mechanics intuition. |
| 6 | High | Requirement | Ark C6; DeepSeek C6 | Validation is shown mechanically but overfitting and stopping logic are missing. | Accept | Slides 5 and 9 say validation checks behavior but do not mention training vs validation loss curves or overfitting. | Add a visual train-loss vs validation-loss curve and explain that rising validation loss while training loss falls indicates overfitting. |
| 7 | Medium | Clarity | Ark C7; DeepSeek C7 | Optimizer and learning rate are used but not defined; `learning_rate` is undefined in code. | Accept | Slide 8 uses `torch.optim.SGD(..., lr=learning_rate)` without assigning `learning_rate` or explaining step size. | Define `learning_rate = 0.01` in the code and add a plain explanation: too large overshoots, too small trains slowly; SGD updates using one mini-batch at a time. |
| 8 | Medium | Maintainability | Ark C8; DeepSeek C1, C12 | `forward()` returns both logits and probabilities, which conflicts with the warning not to pass probabilities into cross entropy. | Accept | Slide 6 computes `probabilities = F.softmax(logits, dim=1)` and returns both; Slide 7 says loss must use logits; Slide 8 unpacks probabilities but does not use them. | Change the teaching model to return only `logits`. Compute softmax only on prediction/evaluation slides when probability-like scores are needed. |
| 9 | Medium | Consistency | Ark C9 | Markdown backticks appear literally in HTML instead of rendered inline code. | Accept | Examples include text such as `` `DataLoader` ``, `` `model.train()` ``, and `` `zero_grad` `` in HTML text/table cells. | Replace literal backticks with `<code>...</code>` and add CSS for inline code styling. |
| 10 | Medium | Risk | Ark C10 | Fixed slide layout with `overflow:hidden` can silently clip content. | Accept | `.stage` and `pre` use `overflow:hidden`; dense slides combine diagrams, code, and tables. | During the rewrite, reduce dense slides and verify at common browser size and print. Prefer splitting content across more slides over hidden overflow. |
| 11 | Medium | Clarity | Ark C11; DeepSeek C9 | `zero_grad()` is described but the reason for gradient accumulation is missing. | Accept | Slide 8 says "Clear old gradients" but not that PyTorch accumulates gradients by default. | Add one sentence: PyTorch accumulates gradients, so without `zero_grad()`, gradients from multiple batches would add together and corrupt the intended update. |
| 12 | Medium | Requirement | Ark C12; DeepSeek C10, C19 | AUC/background rejection is asserted but not motivated for jet tagging. | Accept | Slide 10 says AUC needs ranking scores; Slide 11 names background rejection but does not define it or explain class-imbalance motivation. | Add a short HEP metric explanation: QCD background can dominate, accuracy can mislead, AUC evaluates ranking across thresholds, and background rejection means rejecting background at a chosen signal efficiency. |
| 13 | Low | Clarity | Ark C13 | The deck defines the class but never instantiates the model before using it. | Accept | Slide 6 defines `ClassifierMLP`; Slide 8 uses `model.parameters()` and `model(x_batch)` without showing `model = ClassifierMLP(...)`. | Add a model-instantiation line before the optimizer setup or explicitly mark it as assumed. |
| 14 | Low | Clarity | Ark C14 | Softmax is shown as optional but not defined. | Accept | Slide 6 contains a "softmax optional" box; Slide 7 says cross entropy applies log-softmax internally without explaining softmax. | Add one sentence or formula: softmax turns logits into positive probabilities that sum to one; `F.cross_entropy` includes a stable log-softmax internally. |
| 15 | Low | Clarity | Ark C15 | Beginner vocabulary such as features, labels, supervised, and classification is assumed. | Partial | A senior physics undergraduate likely understands some of these terms after reading HSF, but the user explicitly describes the learner as new to ML. | Add a small vocabulary callout on Slide 2 defining features, labels, supervised learning, and classification. Keep it brief to avoid diluting the main tutorial. |
| 16 | Low | Consistency | Ark C16 | The test set is introduced but no test/evaluation loop is shown. | Accept | Slide 5 defines test set; only validation loop is shown later. | Add a note that test uses the same `eval()` + `no_grad()` pattern as validation and is run once after model selection. |
| 17 | Low | Clarity | Ark C17; DeepSeek C10 | The JetClass transfer slide says MLP becomes Deep Sets/PET but does not explain variable-length unordered particle sets. | Accept | Slide 11 maps "Simple MLP" to "Deep Sets, PET, OmniLearn-style backbone" but lacks motivation. `AGENTS.md` states jets are particle sets and models may be unordered point clouds. | Add a sentence: jets are variable-length unordered particle sets, so swapping particles should not change the label; set-based models handle this better than plain MLPs. |
| 18 | Info | Documentation | Ark C18 | Helpful tables from the Markdown source were dropped from the HTML. | Accept | The Markdown source includes batch/epoch and line-by-line training-loop tables; the HTML has only a shortened steps row and code block. | Reintroduce condensed versions of these tables where they support beginner understanding, especially batch/epoch definitions and training-loop line meanings. |
| 19 | Info | Clarity | Ark C19 | The checklist asks the learner to explain concepts that the deck does not yet fully teach. | Accept | Slide 12 asks the student to explain cross-entropy labels and logits vs probabilities, while the deck mostly states API rules. | After adding principle slides, revise the checklist to map each item to the slide that teaches it. |
| 20 | Low | Requirement | DeepSeek C13 | The deck lacks guidance on typical train/validation/test split ratios. | Partial | The deck correctly explains split roles and warns about ordered HEP data. Exact ratios depend on dataset size and project protocol, so a rigid rule could mislead. | Add a cautious rule of thumb only: common splits include 70/15/15 or 80/10/10, but formal project splits should follow the fixed manifest. |
| 21 | Low | Requirement | DeepSeek C14 | Numerical stability, feature normalization, and mixed precision are not discussed. | Partial | Feature normalization is relevant for JetClass preparation; mixed precision is not needed for a beginner neural-network-principles tutorial. | Add a short JetClass note about normalizing or scaling features. Defer mixed precision because it is an implementation optimization, not required for this learning goal. |
| 22 | Low | Usability | DeepSeek C15 | The deck is code-heavy and reads more like an API walkthrough than a principles tutorial. | Accept | Six of twelve slides include code blocks, and the highest-value principle explanations are missing. | Reduce code on principle slides and move larger snippets later or split them across slides. Use equations and diagrams for concepts before showing code. |
| 23 | Low | Usability | DeepSeek C16 | The deck lacks slide navigation. | Reject | The user did not ask for interactive navigation, and the document is an offline slide/handout that can be scrolled or printed. Adding JS would increase complexity. | Do not add navigation now. Keep the document dependency-free unless the user later asks for interactive browser controls. |
| 24 | Info | Documentation | DeepSeek C17 | The minimum passing checklist is useful. | Accept | Slide 12 provides concrete outcomes the learner should be able to explain. | Keep the checklist, but update it after adding concept slides so each item is taught explicitly in the deck. |
| 25 | Info | Usability | DeepSeek C18 | The CSS and print-friendly layout are well executed. | Accept | The HTML uses color variables, 16:9 slide structure, and print CSS. Static checks previously showed no external dependencies. | Keep the overall visual system. Verify layout again after adding more conceptual slides. |
| 26 | Info | Documentation | DeepSeek C19 | The HSF-to-JetClass transfer table is effective. | Accept | Slide 11 directly maps HSF tutorial concepts to this project. | Keep the transfer table and expand it with variable-length inputs, masks, fixed splits, and permutation invariance. |
| 27 | Info | Clarity | DeepSeek C20 | The cover feedback loop is useful but needs an explicit backprop label. | Accept | Slide 1 has a gold curved arrow from update toward model, but no text label explaining it. | Add a label such as "backprop + weight update" on the feedback arrow. |

## Needs Immediate Action

- Add a "what a neuron computes" slide: weighted sum, bias, activation, learnable weights.
- Add a gradient-descent / backpropagation slide using physics intuition.
- Add ReLU, cross-entropy, softmax, optimizer, learning-rate, epoch, and overfitting explanations.
- Fix the training-loop code to include epoch loop, defined learning rate, and model instantiation.
- Change the example model to return only logits, with softmax computed only for scoring/inspection.
- Fix literal backticks in HTML by using `<code>` elements.
- Add AUC/background-rejection motivation and JetClass set-model motivation.
- Re-check slide overflow after the added content.

## Can Be Deferred

- Interactive slide navigation can be deferred or skipped unless the user requests browser controls.
- Mixed precision can be deferred; it is not needed for beginner understanding.
- Exact split ratios can remain a cautious note rather than a hard rule because this project should eventually use fixed manifests.

## Final Status

`docs/learning/hsf-model-training-tutorial.html` should not be considered complete for the stated learning goal yet. It is a strong workflow deck, but it needs additional principle-focused slides and clearer visual explanations before it can function as a beginner-friendly neural-network tutorial for this project.
