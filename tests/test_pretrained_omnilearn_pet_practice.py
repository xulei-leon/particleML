from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import h5py
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_NOTEBOOK = REPO_ROOT / "src" / "notebooks" / "pretrained_omnilearn_pet_practice.ipynb"
PREPARATION_NOTEBOOK = REPO_ROOT / "src" / "notebooks" / "jetclass_preparation.ipynb"
FEATURE_LADDER_PATH = REPO_ROOT / "src" / "config" / "jetclass_feature_ladder.json"


def execute_notebook(path: Path) -> dict[str, object]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    namespace: dict[str, object] = {"__name__": "__main__"}
    with redirect_stdout(io.StringIO()):
        for cell_index, cell in enumerate(notebook["cells"]):
            if cell.get("cell_type") != "code":
                continue
            source = "".join(cell.get("source", []))
            exec(compile(source, f"{path}#cell-{cell_index}", "exec"), namespace)
    return namespace


class OmniLearnPracticeNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.namespace = execute_notebook(TARGET_NOTEBOOK)

    def test_hdf5_discovery_excludes_checkpoint_roots(self) -> None:
        discover_hdf5_files = self.namespace["discover_hdf5_files"]
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            data_path = base_dir / "train" / "sample.h5"
            checkpoint_path = base_dir / "checkpoints" / "model.weights.h5"
            data_path.parent.mkdir()
            checkpoint_path.parent.mkdir()
            with h5py.File(data_path, "w") as handle:
                handle.create_dataset("data", data=np.zeros((1, 2, 3), dtype=np.float32))
            with h5py.File(checkpoint_path, "w") as handle:
                handle.create_dataset("weight", data=np.zeros((1,), dtype=np.float32))

            discovered = discover_hdf5_files(base_dir, excluded_dirs=[checkpoint_path.parent])

        self.assertEqual(discovered, [data_path])

    def test_particle_mask_uses_documented_source_column(self) -> None:
        derive_particle_mask = self.namespace["derive_particle_mask"]
        data = np.asarray(
            [[[0.0, 0.0, 1.0, 0.0], [3.0, 2.0, 0.0, 4.0], [0.0, 0.0, 0.0, 0.0]]],
            dtype=np.float32,
        )

        mask = derive_particle_mask(data, mask_feature_index=2)

        np.testing.assert_array_equal(mask, np.asarray([[True, False, False]]))

    def test_both_notebooks_use_one_shared_feature_ladder(self) -> None:
        ladder = json.loads(FEATURE_LADDER_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            ladder["config_groups"],
            {
                "A": ["kinematics"],
                "B": ["kinematics", "charge"],
                "C": ["kinematics", "charge", "pid"],
                "D": ["kinematics", "charge", "pid", "impact_parameter"],
            },
        )
        for notebook_path in (TARGET_NOTEBOOK, PREPARATION_NOTEBOOK):
            source = notebook_path.read_text(encoding="utf-8")
            self.assertIn("jetclass_feature_ladder.json", source)

    def test_feature_groups_expand_multi_column_pid(self) -> None:
        resolve_feature_names = self.namespace["resolve_feature_names"]
        column_groups = {
            "kinematics": ["pt", "eta", "phi", "energy"],
            "charge": ["charge"],
            "pid": ["pid_e", "pid_mu", "pid_gamma"],
            "impact_parameter": ["d0", "d0err", "dz", "dzerr"],
        }

        feature_names = resolve_feature_names("C", column_groups)

        self.assertEqual(feature_names, ["pt", "eta", "phi", "energy", "charge", "pid_e", "pid_mu", "pid_gamma"])

    def test_tensorflow_checkpoint_components_form_one_artifact(self) -> None:
        group_checkpoint_artifacts = self.namespace["group_checkpoint_artifacts"]
        sha256_artifact = self.namespace["sha256_artifact"]
        with tempfile.TemporaryDirectory() as tmpdir:
            directory = Path(tmpdir)
            index_path = directory / "model.ckpt.index"
            shard_path = directory / "model.ckpt.data-00000-of-00001"
            pointer_path = directory / "checkpoint"
            index_path.write_bytes(b"index")
            shard_path.write_bytes(b"weights-v1")
            pointer_path.write_text('model_checkpoint_path: "model.ckpt"', encoding="utf-8")

            artifacts = group_checkpoint_artifacts([pointer_path, shard_path, index_path])
            first_hash = sha256_artifact(artifacts[0][1])
            shard_path.write_bytes(b"weights-v2")
            second_hash = sha256_artifact(artifacts[0][1])

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0][0], directory / "model.ckpt")
        self.assertEqual(set(artifacts[0][1]), {index_path, shard_path})
        self.assertNotEqual(first_hash, second_hash)

    def test_readiness_reports_are_explicit(self) -> None:
        env_report = self.namespace["env_report"]
        reference_report = self.namespace["reference_report"]
        self.assertIsInstance(env_report["practice_ready"], bool)
        self.assertIsInstance(env_report["reference_stack_ready"], bool)
        self.assertIsInstance(reference_report["recognizable"], bool)
        self.assertIsInstance(reference_report["reference_ready"], bool)

    def test_reference_requirements_check_versions_and_missing_packages(self) -> None:
        check_reference_requirements = self.namespace["check_reference_requirements"]
        with tempfile.TemporaryDirectory() as tmpdir:
            requirements_path = Path(tmpdir) / "requirements.txt"
            requirements_path.write_text(
                "numpy<0\nparticleml-definitely-missing-package==1.0\n",
                encoding="utf-8",
            )

            report = check_reference_requirements(requirements_path)

        self.assertTrue(report["checked"])
        self.assertFalse(report["compatible"])
        self.assertEqual(report["missing"], ["particleml-definitely-missing-package"])
        self.assertEqual(report["incompatible"][0]["package"], "numpy")

    def test_run_record_matches_v03_schema(self) -> None:
        run_record = self.namespace["run_record_template"]
        self.assertIn(run_record["input_adapter_policy"], {"adapter_swap", "fixed_dim_neutralization"})
        for required_field in (
            "hyperparameters",
            "runtime_seconds",
            "peak_gpu_memory_mb",
            "best_validation_epoch",
        ):
            self.assertIn(required_field, run_record)
        for required_hardware_field in ("gpu_names", "gpu_vram_mb", "cuda_version"):
            self.assertIn(required_hardware_field, run_record["hardware_spec"])


if __name__ == "__main__":
    unittest.main()
