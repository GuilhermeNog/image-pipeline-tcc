import cv2
import numpy as np

from app.engine.registry import OperationRegistry

THRESHOLD_TYPES = {
    "binary": cv2.THRESH_BINARY,
    "binary_inv": cv2.THRESH_BINARY_INV,
    "trunc": cv2.THRESH_TRUNC,
    "tozero": cv2.THRESH_TOZERO,
    "tozero_inv": cv2.THRESH_TOZERO_INV,
}


@OperationRegistry.register(
    name="blur",
    params_schema={
        "kernel": {
            "type": "int",
            "min": 1,
            "max": 31,
            "default": 5,
            "step": 2,
            "label": "Kernel Size",
        }
    },
)
def blur(image: np.ndarray, kernel: int = 5) -> np.ndarray:
    k = kernel if kernel % 2 == 1 else kernel + 1
    return cv2.GaussianBlur(image, (k, k), 0)


@OperationRegistry.register(
    name="threshold",
    params_schema={
        "value": {
            "type": "int",
            "min": 0,
            "max": 255,
            "default": 127,
            "label": "Threshold Value",
        },
        "type": {
            "type": "select",
            "options": ["binary", "binary_inv", "trunc", "tozero", "tozero_inv"],
            "default": "binary",
            "label": "Type",
        },
    },
)
def threshold(
    image: np.ndarray, value: int = 127, type: str = "binary"
) -> np.ndarray:
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh_type = THRESHOLD_TYPES.get(type, cv2.THRESH_BINARY)
    _, result = cv2.threshold(image, value, 255, thresh_type)
    return result
