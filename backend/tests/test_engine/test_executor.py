import numpy as np
import pytest

from app.engine.executor import PipelineExecutor
import app.engine.operations  # noqa: F401


def make_color_image(width=100, height=100):
    return np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)


class TestPipelineExecutor:
    def test_execute_single_operation(self):
        executor = PipelineExecutor()
        results = executor.execute(make_color_image(), [{"type": "grayscale"}])
        assert len(results) == 1
        assert len(results[0].shape) == 2

    def test_execute_multiple_operations(self):
        executor = PipelineExecutor()
        operations = [
            {"type": "grayscale"},
            {"type": "blur", "params": {"kernel": 5}},
            {"type": "threshold", "params": {"value": 127}},
        ]
        results = executor.execute(make_color_image(), operations)
        assert len(results) == 3
        unique = np.unique(results[2])
        assert all(v in [0, 255] for v in unique)

    def test_execute_empty_pipeline(self):
        executor = PipelineExecutor()
        results = executor.execute(make_color_image(), [])
        assert len(results) == 0

    def test_execute_with_callback(self):
        executor = PipelineExecutor()
        operations = [
            {"type": "grayscale"},
            {"type": "blur", "params": {"kernel": 3}},
        ]
        progress = []

        def on_step(step, total, operation, result):
            progress.append(
                {"step": step, "total": total, "operation": operation}
            )

        executor.execute(make_color_image(), operations, on_step=on_step)
        assert len(progress) == 2
        assert progress[0] == {
            "step": 1,
            "total": 2,
            "operation": "grayscale",
        }
        assert progress[1] == {
            "step": 2,
            "total": 2,
            "operation": "blur",
        }

    def test_execute_unknown_operation_raises(self):
        executor = PipelineExecutor()
        with pytest.raises(KeyError, match="Unknown operation"):
            executor.execute(
                make_color_image(), [{"type": "nonexistent_op"}]
            )
