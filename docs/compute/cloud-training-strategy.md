# Cloud Training Strategy

Cloud-only compute note for a `max $500` budget. The dataset is not fixed yet, and the project may move from JetClass to another jet dataset or train a model from scratch.

## Recommended Stack

| Layer | Default choice | Backup / escalation | Why this layer exists | Budget role |
|---|---|---|---|---|
| Debugging | Colab | Low-cost RunPod / Vast.ai `4090` | Notebook checks, loader validation, tiny overfit tests, shape/mask debugging | `10%-20%` |
| Main training | RunPod / Vast.ai `48GB` class | `A40`, `A6000`, `L40S` | Stable single-GPU training, repeat runs, main experiments, from-scratch pretraining | `60%-75%` |
| High-memory backup | Short `A100 80GB` rental | Only if `48GB` is still memory-bound | Rescue option for unusually large batches, larger models, or memory-heavy pretraining | `10%-20% buffer` |

## GPU Comparison

| GPU | VRAM | Memory bandwidth | Useful compute figure | RunPod price | `500 USD` hours | Best role |
|---|---:|---:|---|---:|---:|---|
| `RTX 4090` | `24GB GDDR6X` | `1008 GB/s` | `82.6 TFLOPS FP32` | `$0.69/hr` secure, `$0.34/hr` community | `725 hr` at secure rate | Best debug / pilot card |
| `A40` | `48GB GDDR6 ECC` | `696 GB/s` | `37.4 TFLOPS FP32`, `299.4 TFLOPS FP16 tensor*` | `$0.44/hr` | `1136 hr` | Best low-cost 48GB workhorse |
| `RTX A6000` | `48GB GDDR6 ECC` | `768 GB/s` | `38.7 TFLOPS FP32`, `309.7 TFLOPS tensor` | `$0.49/hr` | `1020 hr` | Safer 48GB option if available |
| `L40S` | `48GB GDDR6 ECC` | `864 GB/s` | `91.6 TFLOPS FP32`, `733 TFLOPS FP16/BF16`, `1466 FP8*` | `$0.86/hr` | `581 hr` | Highest-throughput 48GB option |
| `A100 PCIe` | `80GB HBM2e` | `1935 GB/s` | `19.5 TFLOPS FP32`, `156 TFLOPS TF32`, `312 TFLOPS FP16/BF16` | `$1.39/hr` | `360 hr` | High-memory backup / rescue |

`*` With sparsity where shown in the NVIDIA datasheets.

## Provider Comparison

| Provider | Pricing model | Strengths | Risks / costs | Best use here |
|---|---|---|---|---|
| Colab | Session / subscription based | Fastest start, easiest notebook iteration | Interruptions, weak fit for long training | First code checks only |
| RunPod | Fixed pod pricing; community + secure clouds; per-second billing | Best default balance of ease, catalog breadth, and predictable cloud operations | Price varies by GPU class; keep an eye on storage and instance choice | Default provider for debug + main training |
| Vast.ai | Marketplace pricing; hosts set prices; compute + storage + bandwidth billed separately | Often the cheapest route, especially for high-end cards | Host variability, bandwidth/storage overhead, more ops work | Cost-first fallback for `4090` and `48GB` rentals |
| Google Cloud | Fixed GPU prices; spot discounts can be large | Standardized platform, reliable infrastructure | Usually less cost-effective under a `500 USD` cap | Use if you already have credits or want GCP conventions |

## Budget Model

| Bucket | Suggested spend | What it pays for |
|---|---:|---|
| Debugging | `$50-$100` | Colab sessions, cheap GPU validation, tiny pilot runs |
| Main training | `$300-$375` | Real training runs on `48GB` cards |
| Buffer | `$50-$100` | Failed jobs, reruns, checkpoint recovery, storage overhead |

## Storage and Workflow

| Item | Rule |
|---|---|
| Raw data | Store on persistent cloud volume or object storage, not on GPU VRAM |
| Processed data | Cache near the training instance to avoid idle GPU time |
| Checkpoints | Keep separate from runtime disks |
| Early validation | Start with a tiny subset before scaling to the full dataset |
| Escalation rule | If `24GB` keeps OOMing, move to `48GB`; if `48GB` is still memory-bound, use a short `A100 80GB` run |

## Practical Recommendation

| Situation | Pick |
|---|---|
| Need to debug code or confirm tensor shapes | `Colab` or cheap `4090` |
| Need the cheapest serious training card | `A40` or `RTX A6000` |
| Need the best 48GB throughput | `L40S` |
| Need maximum headroom for a hard memory problem | Short `A100 80GB` rental |
| Need the lowest operational friction overall | `RunPod` |
| Need the lowest possible price and can accept variability | `Vast.ai` |

## References

- RunPod pricing: <https://www.runpod.io/gpu-models/rtx-4090>, <https://www.runpod.io/gpu-models/a40>, <https://www.runpod.io/gpu-models/a100-pcie>, <https://www.runpod.io/gpu-models/l40s>, <https://www.runpod.io/gpu-models/>
- NVIDIA specs: <https://www.nvidia.com/en-us/data-center/a100/>, <https://www.nvidia.com/en-us/data-center/l40s/>, <https://www.nvidia.com/en-us/design-visualization/rtx-a6000/>, <https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a40/proviz-print-nvidia-a40-datasheet-us-nvidia-1469711-r8-web.pdf>, <https://images.nvidia.com/aem-dam/Solutions/geforce/ada/nvidia-ada-gpu-architecture.pdf>
- Google Cloud GPU pricing: <https://cloud.google.com/compute/gpus-pricing>
- Vast.ai pricing: <https://docs.vast.ai/documentation/pricing>, <https://docs.vast.ai/billing>
