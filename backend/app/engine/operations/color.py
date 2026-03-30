import cv2
import numpy as np

from app.engine.registry import OperationRegistry


@OperationRegistry.register(name="grayscale", params_schema={})
def grayscale(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


@OperationRegistry.register(
    name="brightness",
    params_schema={
        "value": {
            "type": "int",
            "min": -100,
            "max": 100,
            "default": 0,
            "label": "Brightness",
        }
    },
)
def brightness(image: np.ndarray, value: int = 0) -> np.ndarray:
    return cv2.convertScaleAbs(image, alpha=1.0, beta=value)


@OperationRegistry.register(
    name="contrast",
    params_schema={
        "value": {
            "type": "float",
            "min": 0.5,
            "max": 3.0,
            "default": 1.0,
            "step": 0.1,
            "label": "Contrast",
        }
    },
)
def contrast(image: np.ndarray, value: float = 1.0) -> np.ndarray:
    return cv2.convertScaleAbs(image, alpha=value, beta=0)
