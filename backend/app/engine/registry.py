from collections.abc import Callable
from typing import Any

import numpy as np


class OperationRegistry:
    _operations: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, params_schema: dict):
        def decorator(func: Callable[[np.ndarray, ...], np.ndarray]):
            cls._operations[name] = {
                "func": func,
                "params_schema": params_schema,
            }
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Callable:
        if name not in cls._operations:
            raise KeyError(f"Unknown operation: {name}")
        return cls._operations[name]["func"]

    @classmethod
    def get_schema(cls, name: str) -> dict:
        if name not in cls._operations:
            raise KeyError(f"Unknown operation: {name}")
        return cls._operations[name]["params_schema"]

    @classmethod
    def list_operations(cls) -> list[dict]:
        return [
            {"name": name, "params": data["params_schema"]}
            for name, data in cls._operations.items()
        ]

    @classmethod
    def has(cls, name: str) -> bool:
        return name in cls._operations
