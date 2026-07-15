# HSF Model Training Tutorial for This Project

Date: 2026-06-22  
Version: 2.0  
Source: https://hsf-training.github.io/hsf-training-ml-webpage/09-Model_Training/index.html

This tutorial explains the Neural Network part of the HSF Model Training page from the perspective of this project. The goal is to learn the PyTorch training workflow needed for JetClass top-tagging baselines and later PET / OmniLearn-style fine-tuning.

This is not a tutorial on foundation models. It is a tutorial on the basic supervised-training loop that will later be reused with more project-relevant jet models.

## 1. What the HSF Neural Network Example Does

The HSF page trains a small fully connected neural network, also called an MLP, to classify events as signal or background.

In the tutorial page, the input has already been prepared as arrays such as:

```text
X_train_scaled: training features
y_train: training labels
X_test_scaled: test features
y_test: test labels
```

The neural-network section then does the standard supervised-learning workflow:

```text
convert arrays to PyTorch tensors
split training data into train and validation subsets
wrap tensors with Dataset and DataLoader
define a small MLP
train with cross entropy and an optimizer
validate after each epoch
predict on the test set
```

For this project, the important part is the workflow. The exact HSF input variables are low priority because this project uses JetClass particle-level data.

## 2. Step 1: Convert Data to PyTorch Tensors

The HSF tutorial starts from processed NumPy-like arrays. PyTorch models cannot train directly on arbitrary arrays; they need tensors.

For classification with cross entropy, use:

```python
X_train_tensor = torch.as_tensor(X_train_scaled, dtype=torch.float32)
y_train_tensor = torch.as_tensor(y_train, dtype=torch.long)
```

The feature tensor should be floating point because model weights are floating point. The label tensor should be `torch.long` because `F.cross_entropy` expects class indices such as:

```text
0: background
1: signal
```

For this project, the same idea applies to JetClass, but the input shape will be different. A simple tabular example may use:

```text
batch x features
```

JetClass particle data will more likely use:

```text
batch x particles x features
```

The tutorial teaches the tensor conversion idea, not the final project input shape.

## 3. Step 2: Build a Dataset and DataLoader

After converting arrays to tensors, the tutorial wraps them into a dataset:

```python
train_data = torch.utils.data.TensorDataset(X_train_tensor, y_train_tensor)
```

This means each training item is a pair:

```text
(features_i, label_i)
```

Then a `DataLoader` creates mini-batches:

```python
train_loader = torch.utils.data.DataLoader(
    dataset=train_data,
    batch_size=32,
    shuffle=True,
)
```

The important ideas are:

| Concept | Meaning |
|---|---|
| `batch_size` | Number of samples processed before one parameter update |
| `shuffle=True` | Randomizes training order each epoch |
| mini-batch | A small subset of the dataset used for one training step |
| epoch | One full pass over the training dataset |

For JetClass, a custom `Dataset` will probably be needed instead of `TensorDataset`, because the data comes from HDF5 files and may include particle masks. But the training loop will still receive batches from a `DataLoader`.

## 4. Step 3: Split Train, Validation, and Test Data

The tutorial separates training and validation data. The roles are:

| Split | Used For | Updates Model Parameters? |
|---|---|---|
| Training | Learning model weights | Yes |
| Validation | Checking model behavior during training | No |
| Test | Final evaluation after model selection | No |

Do not treat validation as extra training data. Validation is used to decide whether the model is improving, overfitting, or ready for checkpoint selection.

For this project, be more careful than the simple tutorial example:

```text
Do not blindly take the first N samples as validation data.
```

HEP datasets may be ordered by file, process, class, or simulation condition. A safe project workflow should use a fixed split manifest or a shuffled split with a recorded random seed.

## 5. Step 4: Understand the MLP Model

The HSF neural network is a simple MLP. Conceptually, it has this structure:

```text
input features
  -> linear layer
  -> ReLU activation
  -> linear output layer
  -> logits
```

In PyTorch, a simplified version looks like:

```python
class ClassifierMLP(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()
        self.hidden = nn.Linear(input_size, hidden_size)
        self.output = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = F.relu(self.hidden(x))
        logits = self.output(x)
        probabilities = F.softmax(logits, dim=1)
        return logits, probabilities
```

The model returns two things:

| Output | Meaning | Used For |
|---|---|---|
| `logits` | Raw class scores before softmax | Training loss |
| `probabilities` | Softmax-normalized class probabilities | Optional probability interpretation |

For class prediction, probabilities are not always necessary. `logits.argmax(dim=1)` and `probabilities.argmax(dim=1)` give the same class because softmax preserves the score ordering.

For this project, the MLP itself is not the final model. It is only a simple way to understand how neural models produce class scores.

## 6. Step 5: Use Cross Entropy Correctly

The tutorial uses cross entropy for classification:

```python
loss = F.cross_entropy(logits, y_batch)
```

The key rule is:

```text
cross_entropy takes raw logits, not softmax probabilities
```

Do this:

```python
loss = F.cross_entropy(logits, y_batch)
```

Do not do this:

```python
loss = F.cross_entropy(probabilities, y_batch)
```

PyTorch's cross-entropy function internally applies the needed log-softmax operation. Passing already-softmaxed probabilities is a common mistake.

## 7. Step 6: Understand the Training Loop

This is the most important part of the HSF neural-network section.

A compact training step looks like this:

```python
seed = 42
torch.manual_seed(seed)

optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

model.train()

for x_batch, y_batch in train_loader:
    optimizer.zero_grad()
    logits, probabilities = model(x_batch)
    loss = F.cross_entropy(logits, y_batch)
    loss.backward()
    optimizer.step()
```

Line by line:

| Line | Meaning |
|---|---|
| `torch.manual_seed(seed)` | Makes random behavior more reproducible. |
| `optimizer = ...` | Chooses how model parameters will be updated. |
| `model.train()` | Puts the model in training mode. |
| `optimizer.zero_grad()` | Clears old gradients before computing new ones. |
| `model(x_batch)` | Runs the forward pass. |
| `F.cross_entropy(...)` | Computes classification loss. |
| `loss.backward()` | Computes gradients for trainable parameters. |
| `optimizer.step()` | Updates model parameters using gradients. |

The most important sequence to memorize is:

```text
zero_grad
forward
loss
backward
step
```

This sequence will still appear when the MLP is replaced by Deep Sets, PET, or an OmniLearn-style backbone.

## 8. Step 7: Understand the Validation Loop

Validation checks the model without updating its parameters.

```python
model.eval()

with torch.no_grad():
    for x_batch, y_batch in valid_loader:
        logits, probabilities = model(x_batch)
        loss = F.cross_entropy(logits, y_batch)
        predictions = logits.argmax(dim=1)
```

The important differences from training are:

| Training | Validation |
|---|---|
| `model.train()` | `model.eval()` |
| Gradients are computed | Gradients are disabled |
| `loss.backward()` is called | `loss.backward()` is not called |
| `optimizer.step()` updates weights | No parameter update happens |

Use `torch.no_grad()` only for validation, testing, or inference. Do not wrap the training forward/backward pass in `torch.no_grad()`, because gradients will not be computed.

## 9. Step 8: Make Predictions

The tutorial predicts the class with the largest score:

```python
predictions = logits.argmax(dim=1)
```

For two-class classification, this returns:

```text
0 or 1
```

This is enough for accuracy. For AUC or ROC curves, however, you usually need a continuous score, such as the signal-class logit or probability:

```python
signal_score = logits[:, 1]
```

For this project, AUC is more important than raw accuracy for formal top-tagging evaluation.

## 10. How This Transfers to JetClass

The HSF tutorial uses a simple event-level MLP. This project will use jet data, so the input is more structured.

| HSF Tutorial | This Project |
|---|---|
| Small tabular input | JetClass particle-level features |
| Signal vs background | Top jet vs QCD background |
| Simple MLP | Deep Sets, PET, OmniLearn-style backbone |
| Accuracy | Accuracy, AUC, background rejection |
| Basic train/test arrays | HDF5 loading, masks, fixed splits |

The conceptual training loop remains similar:

```text
load a batch
run model forward
compute loss
backpropagate
update parameters
validate
log metrics
```

The model and data loader become more complex, but the training logic stays recognizable.

## 11. Low-Priority Material on the HSF Page

The HSF page also discusses material that is not central to this project.

Random forest can be skimmed as a classical baseline example, but it is not expected to be part of the main project. The project direction is neural particle-set modeling, especially Deep Sets, PET, and OmniLearn-style backbones.

The exact tutorial feature names, such as the lepton transverse-momentum variables used in the HSF example, do not need to be memorized. JetClass uses particle-level jet constituents, so the data interface will be different.

If the page uses old PyTorch `Variable` syntax, treat it as legacy style. In modern PyTorch, tensors already support autograd, so new project code should use tensors directly.

## 12. Common Mistakes to Avoid

| Mistake | Correct Practice |
|---|---|
| Passing softmax probabilities into `F.cross_entropy` | Pass raw logits. |
| Forgetting `optimizer.zero_grad()` | Clear gradients before each training step. |
| Calling `optimizer.step()` during validation | Never update parameters during validation. |
| Using `torch.no_grad()` in training | Use it only for validation, testing, or inference. |
| Treating accuracy as the only metric | Add AUC and background rejection for jet tagging. |
| Taking the first samples as validation without checking order | Use shuffled or manifest-based splits. |
| Copying old `Variable` code | Use modern PyTorch tensors directly. |
| Tuning the tutorial MLP too much | Move on to project-relevant baselines once the loop is understood. |

## 13. Minimum Passing Standard

After studying this tutorial, you should be able to:

1. Explain the difference between tensors, datasets, dataloaders, and batches.
2. Explain why labels for `F.cross_entropy` are integer class indices.
3. Explain the difference between logits and probabilities.
4. Write the basic PyTorch training sequence: `zero_grad`, forward, loss, backward, step.
5. Write a validation loop using `model.eval()` and `torch.no_grad()`.
6. Explain why validation and test data should not update model parameters.
7. Explain why JetClass top-tagging should eventually report AUC, not only accuracy.

If these points are clear, the HSF neural-network section has served its purpose for this project. The next step is to implement a small JetClass top-vs-QCD baseline and then move toward particle-set models.
