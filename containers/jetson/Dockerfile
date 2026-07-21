ARG JETSON_PYTORCH_IMAGE
FROM ${JETSON_PYTORCH_IMAGE}

LABEL org.opencontainers.image.title="particleML Jetson development environment"
LABEL org.opencontainers.image.description="ARM64 CUDA debugging environment for JetPack 6.x"
LABEL org.opencontainers.image.source="https://github.com/xulei-leon/particleML"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    XDG_CACHE_HOME=/tmp/particleml-cache \
    PARTICLEML_ARTIFACT_ROOT=/workspace/artifacts

WORKDIR /workspace/particleML

COPY requirements-ci.lock /tmp/particleml-requirements.lock
RUN python -m pip install --no-cache-dir --requirement /tmp/particleml-requirements.lock

COPY pyproject.toml README.md LICENSE ./
COPY src/particleml ./src/particleml
RUN python -m pip install --no-cache-dir --no-deps --editable .

CMD ["/bin/bash"]
