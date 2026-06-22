# HSF Model Training Reading Priority

Source: https://hsf-training.github.io/hsf-training-ml-webpage/09-Model_Training/index.html

This page is useful as a short reference for basic HEP machine-learning training. For this project, it should be used mainly to understand simple supervised training workflows, not as a source for foundation-model architecture design.

## Reading Priority

| Priority | Page Content | What to Focus On | Relevance to This Project |
|---|---|---|---|
| H | Train / validation split | Understand why validation data is separated from training data. | Needed for reproducible top-tagging experiments and checkpoint selection. |
| H | Mini-batch training | Understand batch size, iteration, and epoch. | JetClass is too large to train in one full pass through memory. |
| H | PyTorch `Dataset` / `DataLoader` | Understand how samples become mini-batches. | Directly relevant to future JetClass HDF5 data loading. |
| H | Basic neural-network training loop | Understand forward pass, loss, `backward()`, optimizer step, and gradient reset. | Core workflow for all future PyTorch baselines and fine-tuning scripts. |
| H | Training vs evaluation mode | Understand `model.train()`, `model.eval()`, and `torch.no_grad()`. | Required for correct validation and testing. |
| H | Validation loop | Understand how to evaluate loss and accuracy without updating weights. | Needed before running reliable baseline experiments. |
| H | Accuracy discussion | Understand why accuracy alone can be limited. | This project should eventually report AUC and background rejection, not only accuracy. |
| M | Random forest example | Know that it is a simple non-neural baseline. | Useful for intuition, but not central to this project's neural foundation-model direction. |
| M | Simple MLP architecture | Know what linear layers and activations do. | Useful for learning neural-network mechanics, but too simple for particle-cloud modeling. |
| M | Optimizer choice | Know what an optimizer does and recognize common choices. | Detailed optimizer comparison can wait until the baseline pipeline works. |
| M | Training curves | Know how to spot overfitting or underfitting from loss/accuracy curves. | Useful for debugging early baseline runs. |
| L | Detailed random forest theory | Do not spend much time on split criteria, tree internals, or ensemble theory. | It will not drive the main PET / OmniLearn-style research contribution. |
| L | Exhaustive MLP tuning | Do not spend much time optimizing the tutorial MLP. | The main models will use set-based or attention-based particle representations. |
| L | Exact tutorial dataset details | Do not memorize the page's example dataset. | The real project data source is JetClass. |
| L | Advanced performance tricks | Do not focus on distributed training, mixed precision, or speed tuning here. | These matter later only after the basic pipeline is correct. |

## Practical Reading Goal

After reading this page, the main goal is to be able to explain and modify a simple PyTorch classification training loop. It is enough if you can understand how data enters the model, how loss is computed, how parameters are updated, and how validation is run.

Do not spend excessive time on the random forest section or on optimizing the tutorial MLP. For this project, the page is only a bridge toward JetClass data loading, PyTorch baselines, and later PET / OmniLearn-style models.
