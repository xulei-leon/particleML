# hsf-model-training-learn Review Confirm

**Reviewed Inputs**

- `docs/learning/hsf-model-training-tutorial.md`
- `docs/4-Reviews/hsf-model-training-learn-review-by-deepseek-v4-pro.md`
- `docs/4-Reviews/hsf-model-training-learn-review-by-ark-code-latest.md`
- `AGENTS.md`

**Review Date**

- 2026-06-22

## Overall Conclusion

Both review reports were generally sound for the earlier long-form version of `hsf-model-training-learn.md`. The strongest findings were valid: the old document violated the repository English-only convention, was too long for quick project preparation, contained fragile Markdown math, and did not clearly connect the HSF tutorial to this jet-foundation-model project.

The target document has since been rewritten into an English project-focused tutorial. Most high-priority review findings are now resolved by replacement rather than small local edits. Two remaining useful suggestions were applied during this confirmation pass: adding a safe-validation-split warning and adding reproducibility seed awareness.

The current artifact is acceptable as a project-focused preparation tutorial. It is not a line-by-line reproduction of the HSF page; instead, it teaches the PyTorch training workflow that this project needs before moving into JetClass baselines and PET / OmniLearn-style models. After applying this confirmation, the previously deferred metadata and optimizer-context improvements have also been added.

## Decision Table

| No. | Severity | Type | Review Source | Original Comment Summary | Decision | Evidence | Follow-up Plan / Rejection Reason |
|---|---|---|---|---|---|---|---|
| 1 | Critical | Requirement | DeepSeek C1; Ark C2 | The old document was written in Chinese and violated the repository English-only rule. | Accept | `AGENTS.md` requires all text content to be written in English. The current `docs/learning/hsf-model-training-tutorial.md` is now English. | Resolved by rewriting the document in English. No further action. |
| 2 | Critical | Correctness | Ark C1 | The old SGD formula was mathematically wrong and missing the gradient-descent minus sign. | Accept | The old formula block no longer exists. The current document avoids the detailed SGD formula and explains `optimizer.step()` operationally. | Resolved by removing the risky formula from this quick-learning note. No further action. |
| 3 | High | Correctness | DeepSeek C2; Ark C3 | The old math expressions used invalid Markdown delimiters and would not render correctly. | Accept | The current document contains no display-math blocks or bracket-delimited formulas. | Resolved by simplifying the document and removing fragile math notation. No further action. |
| 4 | High | Correctness | DeepSeek C3; Ark C4 | The old SGD block was corrupted by Markdown heading syntax. | Accept | The current document no longer contains that block. | Resolved by removing the malformed formula section. No further action. |
| 5 | Medium | Requirement | DeepSeek C6; Ark C6 | The old note did not state its relationship to the project goals. | Accept | The current introduction says the note identifies PyTorch training concepts needed for JetClass top-tagging baselines and PET / OmniLearn-style fine-tuning. | Resolved by adding project framing in the introduction and takeaway. No further action. |
| 6 | Medium | Risk | Ark C5 | The old note repeated the tutorial's first-100 validation split without warning that ordered HEP data can make this unsafe. | Accept | The current priority table includes `Safe validation split`, and the confusion table warns to shuffle or use a fixed manifest for ordered HEP datasets. | Resolved during this confirmation pass. No further action. |
| 7 | Medium | Test | Ark C7 | The old note did not discuss seeding or the project's multi-repeat reproducibility convention. | Accept | The current priority table includes `Reproducibility seed` and links it to the 5-repeat seeded-run convention from `AGENTS.md`. | Resolved during this confirmation pass. No further action. |
| 8 | Medium | Maintainability | DeepSeek C4; Ark C18 | The old document reproduced deprecated `Variable` usage too prominently. | Accept | The current document marks `Deprecated Variable usage` as `L` priority and says modern PyTorch tensors already support autograd. | Resolved by replacing the old detailed legacy-code section with a direct low-priority warning. No further action. |
| 9 | Medium | Documentation | DeepSeek C5; Ark C8 | The old reference links were inconsistent, multi-line, and included tracking parameters. | Accept | The current document uses one direct `Source:` URL and no long reference-definition block. | Resolved by simplifying citation style. No further action. |
| 10 | Medium | Consistency | DeepSeek C7; Ark C11 | The old hyperparameter table should have shown `input_size = 2` directly instead of `len(ML_inputs)`. | Reject | The current document no longer contains the old hyperparameter table. It intentionally avoids tutorial-specific variable memorization. | No change needed because the entire old section was removed as out of scope for a quick project-priority note. |
| 11 | Low | Clarity | DeepSeek C8; Ark C20 | The old architecture diagram mixed `num_classes` and `out_dim`. | Reject | The current document no longer contains the old ASCII architecture diagram. It only states that an MLP maps inputs to logits through linear layers and activations. | No change needed because the detailed diagram was removed to keep the note concise. |
| 12 | Low | Clarity | DeepSeek C9 | The old training-loop snippet lacked enough local optimizer context. | Accept | The current training snippet now includes `optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)` before the loop. | Resolved by adding a minimal optimizer setup line without turning the note into a full runnable tutorial. |
| 13 | Low | Correctness | DeepSeek C10; Ark C13 | The validation loop should warn that `torch.no_grad()` is for evaluation only. | Accept | The current validation-loop section says it evaluates without updating parameters; the confusion table explains validation does not update model parameters. | Resolved at the concept level. No further action required for this short note. |
| 14 | Low | Documentation | DeepSeek C11; Ark C12 | The old inline citation style was awkward and references appeared far below first use. | Accept | The current document uses a single source URL at the top. | Resolved by replacing the citation style. No further action. |
| 15 | Info | Clarity | DeepSeek C12; Ark C15 | The old note correctly caught that the tutorial text says two hidden layers while code shows one hidden layer; reviewers suggested emphasizing it. | Reject | The current note is not a line-by-line correction of the HSF page and no longer discusses this discrepancy. | Not adopted because the rewritten document intentionally focuses on project-priority concepts, not source-page errata. |
| 16 | Info | Correctness | Ark C16 | The old note correctly corrected the tutorial's inaccurate `dloss/dx` comment; reviewer suggested keeping or expanding this. | Reject | The current note summarizes `loss.backward()` as part of the training loop and does not preserve detailed source-code commentary. | Not adopted because retaining source-page errata would make the document longer than needed for quick preparation. |
| 17 | Info | Documentation | DeepSeek C13; Ark C19 | The old note warned that accuracy can mislead but did not sufficiently connect to AUC or project metrics. | Accept | The current priority table says jet-tagging results should later include AUC and background rejection. | Resolved by adding project-specific metric framing. No further action. |
| 18 | Info | Maintainability | DeepSeek C14; Ark C14 | The old document lacked metadata such as title, date, version, and source URL. | Accept | The current document now has a clear title, date, version, and source URL. | Resolved by adding minimal metadata at the top of the document. |
| 19 | Low | Performance | Ark C10 | Prediction can use `argmax` on logits instead of softmax probabilities. | Accept | The current validation example now uses `predictions = logits.argmax(dim=1)` and notes that softmax is only needed for probability scores. | Resolved during this confirmation pass. No further action. |
| 20 | Low | Documentation | Ark C9 | The old note did not explain why training loss was multiplied by batch size for accumulation. | Reject | The current note no longer contains the old detailed loss-accumulation line. | No change needed because epoch-loss bookkeeping is outside the current quick-priority scope. |

## Needs Immediate Action

- None. The blocking and confirmed follow-up issues identified by both reviews have been resolved in the current document.

## Can Be Deferred

- None for the current scope.

## Final Status

`docs/learning/hsf-model-training-tutorial.md` should be accepted in its current form as a project-focused tutorial. The review findings were useful, but after the rewrite and the confirmation-pass updates, no remaining issue blocks use of the document.
