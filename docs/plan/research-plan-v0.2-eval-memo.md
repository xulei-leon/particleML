# Research Direction Evaluation Memo

## 1. Purpose and Bottom-Line Assessment

This memo evaluates the proposed research direction of varying model architecture, training-data scale, and input feature set to study jet-tagging performance. The central conclusion is that the direction is scientifically worthwhile, but it should not be pursued as a broad, equally weighted benchmark across all three axes.

The project should instead be framed as a **structured input-feature ablation study**, with training-data scale treated as a secondary analysis axis and architecture variation treated as a control. This formulation preserves the scientific value of the original idea while substantially improving interpretability, feasibility, and publication potential.

In practical terms, the main research question should be narrowed to the following form:

> How does particle-level input feature richness affect jet-tagging performance and data efficiency in a pretrained PET-style jet foundation model?

This framing gives the study a clear analytical center. It also prevents the project from expanding into a diffuse benchmark in which changes in model, representation, and labeled-data scale are difficult to disentangle.

## 2. Relationship to Research Plan v0.2

The current [research-plan-v0.2.html](/D:/code/physics-foundation-models/docs/plan/research-plan-v0.2.html) already resolves an important part of the earlier scope problem. In particular, v0.2:

- fixes binary top tagging on JetClass as the primary task,
- adopts a pretrained PET-style backbone as the main experimental system,
- defines an explicit feature-configuration ladder,
- and introduces decision gates together with a minimum viable paper structure.

As a result, v0.2 has already moved the project away from an unconstrained "compare everything" design. That is a major improvement and should be preserved.

The remaining issue is not the absence of structure, but the absence of a sufficiently explicit hierarchy among the experimental variables. Model choice, data scale, and feature set all remain visible in v0.2, yet the document does not state sharply enough that only one of these should define the primary scientific claim. The present memo therefore recommends a final clarification step: **input representation should be the principal axis of inquiry; data scale should test robustness and data efficiency; architecture variation should remain interpretive control rather than main narrative.**

## 3. Recommended Framing and Scientific Rationale

The project should be described as a feature-ablation study rather than as a multi-factor comparison of models, data sizes, and inputs. This change is not cosmetic. It improves the scientific design in four ways.

First, it strengthens interpretability. If feature set, architecture, and sample size are all treated as equally important variables, any observed performance difference becomes difficult to attribute. A cleaner hierarchy makes it possible to argue that the main result concerns representation, while the auxiliary analyses test whether that result survives under different data regimes and limited baseline comparisons.

Second, it improves scope control. A full three-axis benchmark scales quickly in cost and complexity once seeds, controls, and reproducibility requirements are added. By contrast, a feature-centered study still supports meaningful comparisons without creating an experimental matrix too large for an undergraduate-led project.

Third, it yields a clearer paper contribution. A focused empirical claim about particle-level input representation is easier to defend than a broad claim attempting to rank all relevant design choices in jet tagging at once. Even a null or near-null result remains publishable if the study is well controlled and the uncertainty is reported carefully.

Fourth, it aligns with the logic already implicit in v0.2. The existing plan is already closest to a feature-ablation paper; the revision recommended here simply makes that logic explicit and removes residual ambiguity in the project description.

Under this framing, the project should no longer be presented as a general study of "changing different models, training-data sizes, and input features." That wording suggests symmetric treatment of all variables and invites scope creep. The revised wording should instead emphasize a single main question with two supporting axes: feature representation as the core question, labeled-data scale as the scaling context, and model variation as a limited control.

## 4. Feasibility, Risks, and Recommended Experimental Boundaries

The revised direction is feasible and well matched to the current project environment. JetClass provides a standard benchmark; binary top tagging offers a manageable and recognizable primary task; the pretrained PET-style backbone gives the study a stable starting point; and the planned feature ladder can be implemented within one preprocessing pipeline. From a methodological perspective, the metrics already anticipated in v0.2, especially ROC AUC and background rejection at fixed signal efficiency, are appropriate for the intended analysis.

The main risks arise not from the core idea, but from uncontrolled expansion. If baseline architectures are added too aggressively, the study may drift into a benchmark paper without sufficient novelty. If feature definitions are not generated from a single preprocessing specification, apparent feature effects may be contaminated by preprocessing differences. If too many experiments are launched before the core ablation stabilizes, compute and analysis effort will be diverted away from the most publication-relevant result. Finally, if the final write-up gives equal weight to every secondary comparison, the central scientific message will be diluted.

For these reasons, the recommended experimental boundary is straightforward: the study should remain centered on one backbone, one primary binary task, one unified feature-specification pipeline, and a limited set of controls that are justified by interpretation rather than by breadth. Additional architectures or extra tasks should be included only if they materially clarify the main feature-ablation result.

The recommended structure is summarized below.

| Scope level | Design | Purpose |
|---|---|---|
| Minimum viable study | One pretrained backbone, four feature configurations, multiple data scales | Sufficient for the core scientific claim |
| Strong study | Minimum viable study plus random-initialization control and Deep Sets baseline | Strengthens interpretation of transfer and inductive bias |
| Extended study | Strong study plus one stronger baseline or one limited multi-class extension | Optional extension if the core study is already complete |

This structure preserves ambition without sacrificing completion discipline.

## 5. Next Steps

The immediate task is not to broaden the project further, but to translate the revised framing into a sharper execution document.

The next revision of the research plan should:

1. rewrite the project summary so that feature ablation is the dominant theme rather than one variable among many;
2. state the primary research question explicitly in feature-ablation terms;
3. freeze binary top tagging on JetClass as the main task for the core paper;
4. formalize feature configurations A-D in a single preprocessing specification;
5. classify all non-core experiments as either required controls or optional extensions;
6. define a compact run matrix with seed counts, data scales, and decision gates tied to scope control.

One operational rule should guide future planning: **if a proposed experiment does not directly strengthen the answer to the feature-representation question, it should be deferred.**

The most useful follow-up document is therefore not another general evaluation note, but a cleaned and formalized `v0.3` research plan that incorporates this hierarchy explicitly. At that point, the project would have a stable scientific framing, a defensible experimental boundary, and a practical path from implementation to manuscript.
