import cv2
import numpy as np

from app.engine.registry import OperationRegistry


@OperationRegistry.register(
    name="canny",
    params_schema={
        "threshold1": {
            "type": "int",
            "min": 0,
            "max": 500,
            "default": 100,
            "label": "Threshold 1",
        },
        "threshold2": {
            "type": "int",
            "min": 0,
            "max": 500,
            "default": 200,
            "label": "Threshold 2",
        },
    },
)
def canny(
    image: np.ndarray, threshold1: int = 100, threshold2: int = 200
) -> np.ndarray:
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(image, threshold1, threshold2)
