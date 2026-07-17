"""Frozen masked Deep Sets/PFN baseline with an optional PyTorch runtime."""

from __future__ import annotations

import importlib
from dataclasses import asdict, dataclass
from typing import Any, Protocol, cast

import numpy as np
from numpy.typing import NDArray

from particleml.contracts import ConfigurationError, ExternalDependencyError, IntegrityError


class TorchModule(Protocol):
    """Small structural type for the dynamically imported PyTorch module."""

    def __call__(self, features: object, mask: object) -> object: ...

    def parameters(self) -> object: ...

    def state_dict(self) -> object: ...


@dataclass(frozen=True)
class BaselineConfig:
    """Pre-E3 frozen baseline architecture and optimization policy."""

    input_dim: int
    phi_hidden_dims: tuple[int, ...] = (64, 64)
    latent_dim: int = 64
    head_hidden_dims: tuple[int, ...] = (64,)
    pooling: str = "sum"
    optimizer: str = "adamw"
    learning_rate: float = 0.001
    weight_decay: float = 0.0001
    max_epochs: int = 50
    early_stopping_patience: int = 5

    def __post_init__(self) -> None:
        dimensions = (
            self.input_dim,
            *self.phi_hidden_dims,
            self.latent_dim,
            *self.head_hidden_dims,
        )
        if any(value <= 0 for value in dimensions):
            raise ConfigurationError(
                "BASELINE_DIMENSION", "all network dimensions must be positive"
            )
        if self.pooling != "sum" or self.optimizer != "adamw":
            raise ConfigurationError(
                "BASELINE_POLICY", "only frozen sum pooling and AdamW are allowed"
            )
        if self.learning_rate <= 0 or self.weight_decay < 0 or self.max_epochs <= 0:
            raise ConfigurationError("BASELINE_POLICY", "optimizer or stopping policy is invalid")

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["phi_hidden_dims"] = list(self.phi_hidden_dims)
        value["head_hidden_dims"] = list(self.head_hidden_dims)
        return value


def validate_masked_batch(
    features: NDArray[np.floating[Any]], mask: NDArray[np.bool_ | np.integer[Any]]
) -> tuple[NDArray[np.float64], NDArray[np.bool_]]:
    """Validate the batch/particle mask contract without consuming global variables."""

    feature_array = np.asarray(features, dtype=np.float64)
    mask_array = np.asarray(mask)
    if feature_array.ndim != 3 or mask_array.ndim != 2:
        raise IntegrityError("BASELINE_SHAPE", "features must be BxPxF and mask must be BxP")
    if feature_array.shape[:2] != mask_array.shape:
        raise IntegrityError("BASELINE_SHAPE", "feature and mask particle axes differ")
    if not np.isfinite(feature_array).all() or not np.isin(mask_array, (0, 1)).all():
        raise IntegrityError("BASELINE_INPUT", "features must be finite and mask must be binary")
    if np.any(np.count_nonzero(mask_array, axis=1) == 0):
        raise IntegrityError("BASELINE_EMPTY_JET", "every jet must contain a real particle")
    return feature_array, mask_array.astype(np.bool_)


def masked_sum_pool(
    encoded_particles: NDArray[np.floating[Any]],
    mask: NDArray[np.bool_ | np.integer[Any]],
) -> NDArray[np.float64]:
    """Sum encoded real particles while making arbitrary padding values irrelevant."""

    encoded = np.asarray(encoded_particles, dtype=np.float64)
    mask_array = np.asarray(mask)
    if encoded.ndim != 3 or mask_array.shape != encoded.shape[:2]:
        raise IntegrityError("BASELINE_SHAPE", "encoded particles and mask are not aligned")
    if not np.isfinite(encoded).all() or not np.isin(mask_array, (0, 1)).all():
        raise IntegrityError("BASELINE_INPUT", "encoded particles or mask are invalid")
    return np.asarray(
        np.sum(encoded * mask_array.astype(np.float64)[..., None], axis=1),
        dtype=np.float64,
    )


def baseline_parameter_count(config: BaselineConfig) -> int:
    """Compute the exact trainable dense-layer parameter count from frozen dimensions."""

    phi = (config.input_dim, *config.phi_hidden_dims, config.latent_dim)
    head = (config.latent_dim, *config.head_hidden_dims, 1)
    return sum(left * right + right for left, right in zip(phi, phi[1:])) + sum(
        left * right + right for left, right in zip(head, head[1:])
    )


def build_torch_deep_sets_pfn(config: BaselineConfig, *, model_seed: int) -> TorchModule:
    """Build the frozen PyTorch model only inside an environment that provides PyTorch."""

    if model_seed < 0:
        raise ConfigurationError("BASELINE_SEED", "model seed must be non-negative")
    try:
        torch = importlib.import_module("torch")
        nn = importlib.import_module("torch.nn")
    except ImportError as exc:
        raise ExternalDependencyError(
            "BASELINE_TORCH_MISSING", "PyTorch is required in the qualified E3 environment"
        ) from exc
    torch.manual_seed(model_seed)

    def mlp(dimensions: tuple[int, ...], *, final_activation: bool) -> Any:
        layers: list[Any] = []
        for index, (left, right) in enumerate(zip(dimensions, dimensions[1:])):
            layers.append(nn.Linear(left, right))
            if final_activation or index < len(dimensions) - 2:
                layers.append(nn.ReLU())
        return nn.Sequential(*layers)

    module_base = nn.Module

    class _DeepSetsPFN(module_base):  # type: ignore[misc, valid-type]
        def __init__(self) -> None:
            super().__init__()
            self.phi = mlp(
                (config.input_dim, *config.phi_hidden_dims, config.latent_dim),
                final_activation=True,
            )
            self.head = mlp(
                (config.latent_dim, *config.head_hidden_dims, 1),
                final_activation=False,
            )

        def forward(self, features: Any, mask: Any) -> object:
            if features.ndim != 3 or mask.ndim != 2:
                raise ValueError("features must be BxPxF and mask must be BxP")
            encoded: Any = self.phi(features)
            masked: Any = encoded * mask.to(dtype=encoded.dtype).unsqueeze(-1)
            pooled = masked.sum(dim=1)
            return cast(object, self.head(pooled).squeeze(-1))

    return cast(TorchModule, _DeepSetsPFN())
