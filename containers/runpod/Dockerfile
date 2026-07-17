FROM pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime@sha256:923f687790bec78081c357e71dcd5dcef80b0cc00f6c34484902a5e83362c854

LABEL org.opencontainers.image.title="particleML RunPod environment"
LABEL org.opencontainers.image.description="Pinned modern Python and GPU boundary for particleML cloud work"
LABEL org.opencontainers.image.source="https://github.com/xulei-leon/particleML"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PARTICLEML_ARTIFACT_ROOT=/workspace/artifacts

WORKDIR /workspace/particleML

COPY containers/runpod/requirements.lock /tmp/particleml-runpod-requirements.lock
RUN python -m pip install --no-cache-dir -r /tmp/particleml-runpod-requirements.lock

COPY pyproject.toml README.md LICENSE ./
COPY src/particleml ./src/particleml
RUN python -m pip install --no-cache-dir --no-deps -e .

CMD ["/bin/bash"]
