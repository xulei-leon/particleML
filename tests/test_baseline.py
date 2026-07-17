from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from particleml.baseline import (
    BaselineConfig,
    baseline_parameter_count,
    build_torch_deep_sets_pfn,
    masked_sum_pool,
    validate_masked_batch,
)
from particleml.contracts import ExternalDependencyError, IntegrityError


def test_mask_and_padding_invariance() -> None:
    encoded = np.asarray(
        [
            [[1.0, 2.0], [3.0, 4.0], [999.0, -999.0]],
            [[5.0, 6.0], [777.0, 888.0], [-1.0, -2.0]],
        ]
    )
    mask = np.asarray([[1, 1, 0], [1, 0, 1]], dtype=np.int8)
    pooled = masked_sum_pool(encoded, mask)
    mutated = encoded.copy()
    mutated[mask == 0] = np.asarray([12345.0, -54321.0])
    assert np.array_equal(pooled, masked_sum_pool(mutated, mask))
    assert np.array_equal(pooled, np.asarray([[4.0, 6.0], [4.0, 4.0]]))


def test_shape_mask_and_parameter_record_contract() -> None:
    features = np.ones((2, 3, 4), dtype=np.float32)
    mask = np.asarray([[1, 1, 0], [1, 0, 0]], dtype=np.int8)
    validated_features, validated_mask = validate_masked_batch(features, mask)
    assert validated_features.shape == (2, 3, 4)
    assert validated_mask.dtype == np.bool_
    config = BaselineConfig(input_dim=4, phi_hidden_dims=(8,), latent_dim=6, head_hidden_dims=(5,))
    assert baseline_parameter_count(config) == (4 * 8 + 8) + (8 * 6 + 6) + (6 * 5 + 5) + (5 + 1)
    assert config.to_dict()["pooling"] == "sum"
    with pytest.raises(IntegrityError, match="BASELINE_EMPTY_JET"):
        validate_masked_batch(features, np.asarray([[1, 0, 0], [0, 0, 0]]))


def test_frozen_baseline_parameter_records_match_implementation() -> None:
    root = Path(__file__).resolve().parents[1]
    policy = json.loads((root / "configs/e3/baseline-policy.json").read_text(encoding="utf-8"))
    for feature in ("A", "D"):
        config = BaselineConfig(
            input_dim=policy["input_dimensions"][feature],
            phi_hidden_dims=tuple(policy["phi_hidden_dims"]),
            latent_dim=policy["latent_dim"],
            head_hidden_dims=tuple(policy["head_hidden_dims"]),
            pooling=policy["pooling"],
            optimizer=policy["optimizer"],
            learning_rate=policy["learning_rate"],
            weight_decay=policy["weight_decay"],
            max_epochs=policy["max_epochs"],
            early_stopping_patience=policy["early_stopping_patience"],
        )
        assert baseline_parameter_count(config) == policy["parameter_counts"][feature]


def test_torch_boundary_is_explicit_when_dependency_is_absent() -> None:
    if importlib.util.find_spec("torch") is not None:
        pytest.skip("PyTorch is present; the qualified-runtime shape test covers this boundary")
    with pytest.raises(ExternalDependencyError, match="BASELINE_TORCH_MISSING"):
        build_torch_deep_sets_pfn(BaselineConfig(input_dim=4), model_seed=1)


def test_torch_model_shape_and_padding_when_available() -> None:
    torch = pytest.importorskip("torch")
    config = BaselineConfig(input_dim=4, phi_hidden_dims=(8,), latent_dim=6, head_hidden_dims=(5,))
    model = build_torch_deep_sets_pfn(config, model_seed=3)
    features = torch.randn(2, 5, 4)
    mask = torch.tensor([[1, 1, 1, 0, 0], [1, 1, 0, 0, 0]], dtype=torch.bool)
    changed = features.clone()
    changed[~mask] = 10000.0
    first = model(features, mask)
    second = model(changed, mask)
    assert tuple(first.shape) == (2,)
    assert torch.allclose(first, second)
    actual = sum(parameter.numel() for parameter in model.parameters())
    assert actual == baseline_parameter_count(config)
