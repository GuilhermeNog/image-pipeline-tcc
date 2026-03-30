import cv2
import numpy as np

from app.engine.registry import OperationRegistry


@OperationRegistry.register(
    name="dilate",
    params_schema={
        "kernel": {
            "type": "int",
            "min": 1,
            "max": 21,
            "default": 3,
            "step": 2,
            "label": "Kernel Size",
        },
        "iterations": {
            "type": "int",
            "min": 1,
            "max": 10,
            "default": 1,
            "label": "Iterations",
        },
    },
)
def dilate(
    image: np.ndarray, kernel: int = 3, iterations: int = 1
) -> np.ndarray:
    k = np.ones((kernel, kernel), np.uint8)
    return cv2.dilate(image, k, iterations=iterations)


@OperationRegistry.register(
    name="erode",
    params_schema={
        "kernel": {
            "type": "int",
            "min": 1,
            "max": 21,
            "default": 3,
            "step": 2,
            "label": "Kernel Size",
        },
        "iterations": {
            "type": "int",
            "min": 1,
            "max": 10,
            "default": 1,
            "label": "Iterations",
        },
    },
)
def erode(
    image: np.ndarray, kernel: int = 3, iterations: int = 1
) -> np.ndarray:
    k = np.ones((kernel, kernel), np.uint8)
    return cv2.erode(image, k, iterations=iterations)
