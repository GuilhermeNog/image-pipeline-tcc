from collections.abc import Callable
from typing import Any

import numpy as np

from app.engine.registry import OperationRegistry


class PipelineExecutor:
    def execute(
        self,
        image: np.ndarray,
        operations: list[dict[str, Any]],
        on_step: Callable[[int, int, str, np.ndarray], None] | None = None,
    ) -> list[np.ndarray]:
        results: list[np.ndarray] = []
        current = image.copy()
        total = len(operations)

        for i, op in enumerate(operations):
            op_type = op["type"]
            params = op.get("params", {})
            func = OperationRegistry.get(op_type)
            current = func(current, **params)
            results.append(current)

            if on_step:
                on_step(i + 1, total, op_type, current)

        return results
