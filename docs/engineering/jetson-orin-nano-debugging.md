# Jetson Orin Nano Super 8GB Debugging Guide

## Purpose and Evidence Boundary

Use this guide to make a Jetson Orin Nano Super 8GB the primary daily Linux,
ARM64, CUDA, and PyTorch debugging host for particleML. The repository provides
a Jetson-specific Dockerfile so the project dependencies remain separate from
the JetPack host installation.

Jetson results are diagnostic only. They may establish that package code,
fixtures, command-line behavior, ARM64 dependencies, CUDA tensor operations,
and a tiny model update work on this device. They must not be used to mark E0,
E0.5, E1, E2, or E3 as passed. Formal CMS extraction still requires the pinned
CMSSW environment, and formal model or training evidence still requires the
pinned RunPod environment described in
[Development and Debugging Environments](./development-and-debugging.md).

## 1. Prepare the Jetson Host

### 1.1 Hardware

Use the NVIDIA power supply and active cooling suitable for Super mode. An NVMe
SSD is strongly recommended for the repository, Docker layers, and temporary
artifacts. An SD card works for initial setup but is a poor target for repeated
image builds and HDF5 access.

The 8 GB unified memory is shared by the CPU and GPU. Close browsers and desktop
applications before CUDA debugging. Do not copy the formal CMS corpus or large
checkpoints onto the device merely to test the environment.

### 1.2 JetPack 6.x

Install JetPack through NVIDIA's supported image or SDK Manager workflow. A
fresh developer kit or one still running JetPack 5.x may require a firmware
update before it can boot JetPack 6.x. Super mode availability also depends on
the installed firmware and JetPack release; do not select an undocumented
`nvpmodel` mode number.

After booting, record the actual host identity:

```bash
$ uname -m
aarch64

$ cat /etc/nv_tegra_release
# R36 (release), REVISION: 4.3, GCID: 38968081, BOARD: generic, EABI: aarch64, DATE: Wed Jan  8 01:49:37 UTC 2025
# KERNEL_VARIANT: oot
TARGET_USERSPACE_LIB_DIR=nvidia
TARGET_USERSPACE_LIB_DIR_PATH=usr/lib/aarch64-linux-gnu/nvidia
# Seeed Image Name mfi_recomputer-orin-nano-8g-j401-6.2-36.4.3-2026-02-05.tar.gz
# branch R36.4.3
# commit ID 453114c2cb5920e062f46df72765ba73ea6a773b

$ dpkg-query -W nvidia-jetpack nvidia-l4t-core
nvidia-jetpack  6.2.1+b38
nvidia-l4t-core 36.4.3-20250107174145

$ nvpmodel -q
NV Power Mode: 25W
1

$ free -h
               total        used        free      shared  buff/cache   available
Mem:           7.4Gi       1.5Gi       4.7Gi        21Mi       1.2Gi       5.7Gi
Swap:          3.7Gi          0B       3.7Gi

$ df -h
Filesystem       Size  Used Avail Use% Mounted on
/dev/nvme0n1p1   233G   18G  205G   8% /
tmpfs            3.8G  120K  3.8G   1% /dev/shm
tmpfs            1.5G   19M  1.5G   2% /run
tmpfs            5.0M  4.0K  5.0M   1% /run/lock
/dev/nvme0n1p10   63M  110K   63M   1% /boot/efi
tmpfs            763M  108K  762M   1% /run/user/1000
```

Expected architecture: `aarch64`. Stop if `nvidia-l4t-core` is missing or the
reported release does not match the JetPack installation you intended to use.

### 1.3 Docker and the NVIDIA Runtime

JetPack normally supplies Docker integration through the NVIDIA container
packages.

Install Docker and the NVIDIA runtime:

```bash
sudo apt update
sudo apt install -y curl nvidia-container

sudo apt install -y docker.io
```

Configure NVIDIA Runtime：

```bash
sudo nvidia-ctk runtime configure --runtime=docker

sudo systemctl daemon-reload
sudo systemctl enable --now docker
sudo systemctl restart docker
```

Verify it before changing the project:

```bash
$ docker --version
Docker version 29.1.3, build 29.1.3-0ubuntu3~22.04.2

$ sudo docker version
Client:
 Version:           29.1.3
 API version:       1.52
 Go version:        go1.24.4
 Git commit:        29.1.3-0ubuntu3~22.04.2
 Built:             Wed Apr 29 22:18:59 2026
 OS/Arch:           linux/arm64
 Context:           default

Server:
 Engine:
  Version:          29.1.3
  API version:      1.52 (minimum version 1.44)
  Go version:       go1.24.4
  Git commit:       29.1.3-0ubuntu3~22.04.2
  Built:            Wed Apr 29 22:18:59 2026
  OS/Arch:          linux/arm64
  Experimental:     false
 containerd:
  Version:          2.2.1
  GitCommit:
 runc:
  Version:          1.3.4-0ubuntu1~22.04.1
  GitCommit:
 docker-init:
  Version:          0.19.0
  GitCommit:

$ sudo docker info | grep -i runtime
 Runtimes: io.containerd.runc.v2 nvidia runc
 Default Runtime: runc

$ dpkg-query -W nvidia-container-toolkit nvidia-container-runtime
nvidia-container-runtime
nvidia-container-toolkit        1.16.2-1
```

If Docker requires `sudo`, either keep using `sudo docker` in the commands below
or add the development account to the `docker` group according to the local
administration policy, then log out and back in. Docker-group membership is
root-equivalent and should not be granted casually.

## 2. Select a JetPack-Compatible PyTorch Image

JetPack 6.x spans multiple Jetson Linux releases. A container tag that works on
one release is not automatically valid on another. Use the
[NVIDIA Frameworks Support Matrix](https://docs.nvidia.com/deeplearning/frameworks/support-matrix/index.html)
to select an NVIDIA Optimized PyTorch iGPU image compatible with the Jetson
Linux release reported by `nvidia-l4t-core`.

The expected image form is:

```text
nvcr.io/nvidia/pytorch:<verified-release>-py3-igpu
```

Do not substitute the repository's RunPod base image: it targets a discrete GPU
cloud environment, not Jetson ARM64 and JetPack. The older
[`l4t-pytorch` catalog](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-pytorch)
also does not provide a general JetPack 6.x compatibility promise.

Enter the image selected from the support matrix and reject a malformed value:

```bash
read -r -p "Verified NVIDIA PyTorch iGPU image: " PARTICLEML_JETSON_BASE
case "$PARTICLEML_JETSON_BASE" in
  nvcr.io/nvidia/pytorch:*-py3-igpu) ;;
  *) echo "Expected nvcr.io/nvidia/pytorch:<release>-py3-igpu" >&2; exit 1 ;;
esac
docker pull "$PARTICLEML_JETSON_BASE"
```

Record the immutable digest used for debugging:

```bash
docker image inspect "$PARTICLEML_JETSON_BASE" \
  --format '{{index .RepoDigests 0}}'
```

## 3. Build the particleML Development Image

Clone the repository onto the NVMe SSD and work from its root:

```bash
git clone https://github.com/xulei-leon/particleML.git
cd particleML
```

Build the Jetson image with the verified base image:

```bash
docker build \
  --build-arg JETSON_PYTORCH_IMAGE="$PARTICLEML_JETSON_BASE" \
  --file containers/jetson/Dockerfile \
  --tag particleml-jetson:dev \
  .
```

The Dockerfile reuses `requirements-ci.lock`; there is no second Jetson-only
Python dependency list. PyTorch comes from the NVIDIA base image because its
CUDA build must remain compatible with JetPack.

## 4. Start the Debugging Container

Create a disposable diagnostic artifact directory under the ignored `var/`
tree, then mount the working copy and artifacts into the container:

```bash
PARTICLEML_REPO="$(pwd)"
PARTICLEML_JETSON_ARTIFACTS="$PARTICLEML_REPO/var/jetson-artifacts"
mkdir -p "$PARTICLEML_JETSON_ARTIFACTS"

docker run --rm --interactive --tty \
  --runtime nvidia \
  --shm-size 1g \
  --volume "$PARTICLEML_REPO:/workspace/particleML" \
  --volume "$PARTICLEML_JETSON_ARTIFACTS:/workspace/artifacts" \
  --workdir /workspace/particleML \
  particleml-jetson:dev
```

The bind mount exposes current source edits at the same path used by the
editable installation. Rebuild the image only when the base image,
`requirements-ci.lock`, or package metadata changes. Source-only edits require
no rebuild.

The container runs as root by default. Keep generated files under
`/workspace/artifacts`; if they become root-owned on the host, restore ownership
only for that exact directory:

```bash
sudo chown -R "$(id -u):$(id -g)" var/jetson-artifacts
```

## 5. Verify the Environment

Run these checks inside the container.

### 5.1 Package and CLI

```bash
python -c "import importlib.metadata as m; import particleml; print(m.version('particleml-research'))"
particleml --help
python -m pytest -x -vv tests/test_manifest.py
```

### 5.2 CUDA and PyTorch

```bash
python - <<'PY'
import torch

assert torch.cuda.is_available(), "PyTorch cannot see Jetson CUDA"
x = torch.arange(16, device="cuda", dtype=torch.float32).reshape(4, 4)
y = x @ x.T
assert torch.isfinite(y).all()
print({
    "torch": torch.__version__,
    "cuda": torch.version.cuda,
    "device": torch.cuda.get_device_name(0),
    "allocated_mib": round(torch.cuda.memory_allocated() / 2**20, 1),
})
PY

python -m pytest -x -vv tests/test_baseline.py
```

### 5.3 Tiny Forward, Backward, and Loss-Decrease Check

This check uses synthetic tensors and the in-repository Deep Sets/PFN baseline.
It is intentionally small enough for the 8 GB device and writes no formal run
record:

```bash
python - <<'PY'
import torch

from particleml.baseline import BaselineConfig, build_torch_deep_sets_pfn

torch.manual_seed(7)
device = torch.device("cuda")
model = build_torch_deep_sets_pfn(
    BaselineConfig(input_dim=4, phi_hidden_dims=(16,), latent_dim=8, head_hidden_dims=(8,)),
    model_seed=7,
).to(device)
features = torch.randn(32, 12, 4, device=device)
mask = torch.ones(32, 12, dtype=torch.bool, device=device)
targets = (features[:, :, 0].mean(dim=1) > 0).float()
optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)
criterion = torch.nn.BCEWithLogitsLoss()

with torch.no_grad():
    initial = criterion(model(features, mask), targets).item()
for _ in range(40):
    optimizer.zero_grad(set_to_none=True)
    loss = criterion(model(features, mask), targets)
    loss.backward()
    assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters())
    optimizer.step()
final = criterion(model(features, mask), targets).item()
assert final < initial, (initial, final)
print({"initial_loss": initial, "final_loss": final})
PY
```

Passing this script proves only that this tiny diagnostic path can update on the
Jetson GPU. It does not qualify an OmniLearned checkpoint or an experiment gate.

## 6. Daily Debugging Loop

Start with the narrowest relevant check:

```bash
python -m pytest -x -vv tests/test_views.py::test_ad_identity_equivalence
python -m pytest -x -vv tests/test_cli.py
ruff check
mypy src/particleml
```

Before handing off a code change, run the applicable complete checks:

```bash
python -m pytest
ruff check
mypy src/particleml
python scripts/validate_software_docs.py
git diff --check
```

The Jetson image deliberately omits Node.js and pnpm. Documentation-site work
does not need CUDA; run `pnpm test` and `pnpm docs:build` on a Node.js 20+ host
or let GitHub Actions perform those checks.

## 7. Memory and Storage Discipline

- Use synthetic tensors or compact fixtures first. Increase batch size only
  after measuring free memory.
- Inspect device pressure with `tegrastats` on the host while the container is
  running.
- Reduce batch size or particle count after an out-of-memory error; do not mask
  a repeatable leak by adding swap.
- Keep Docker data and diagnostic artifacts on NVMe where possible.
- Never mount formal RunPod artifact directories read-write into this container.
- Do not run `jetson_clocks` continuously unless cooling and power delivery are
  appropriate; performance tuning is separate from correctness debugging.

## 8. Troubleshooting

### The image does not start or reports a driver/CUDA mismatch

Recheck `nvidia-l4t-core` and the support-matrix row used to select the iGPU
image. Rebuilding the project layer cannot fix an incompatible base image.

### `torch.cuda.is_available()` is false

Confirm the container was started with `--runtime nvidia`, the host runtime is
listed by `docker info`, and the selected image has the `-igpu` suffix. Test the
base image directly before debugging particleML:

```bash
docker run --rm --runtime nvidia "$PARTICLEML_JETSON_BASE" \
  python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"
```

### A Python dependency fails to install on ARM64

Confirm that the base image's Python version is within the project's supported
3.10--3.12 range. Do not install an x86 wheel or replace a locked dependency
silently. Record the failing package and either select a compatible NVIDIA image
or update the shared dependency policy in a reviewed change.

### The container is killed or PyTorch reports out of memory

Check `tegrastats` and `free -h`, close other applications, and retry with the
small synthetic check. A full checkpoint or production batch that does not fit
in 8 GB belongs on RunPod rather than being fragmented into a new Jetson-only
experiment path.

### Files under `var/jetson-artifacts` are owned by root

Stop the container and apply the narrowly scoped `chown` command in Section 4.
Do not recursively change ownership of the repository or a home directory.

## 9. Completion Checklist

- `aarch64`, JetPack, Jetson Linux, power mode, and free storage were inspected.
- The selected NVIDIA PyTorch `-igpu` image is compatible with the installed
  Jetson Linux release and its digest was recorded.
- The project image builds from `containers/jetson/Dockerfile`.
- The package import, CLI, narrow pytest, CUDA tensor, and tiny loss checks pass.
- Full applicable Python checks pass before handoff.
- All generated files remain under ignored diagnostic paths.
- No Jetson result is represented as formal E0--E3 evidence.

## References

- [JetPack installation and setup](https://docs.nvidia.com/jetson/jetpack/install-setup/index.html)
- [NVIDIA Frameworks Support Matrix](https://docs.nvidia.com/deeplearning/frameworks/support-matrix/index.html)
- [NVIDIA PyTorch release notes](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/index.html)
- [NVIDIA Container Toolkit installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
