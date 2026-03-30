import cv2
import numpy as np

from app.engine.registry import OperationRegistry

ROTATE_CODES = {
    90: cv2.ROTATE_90_CLOCKWISE,
    180: cv2.ROTATE_180,
    270: cv2.ROTATE_90_COUNTERCLOCKWISE,
}


@OperationRegistry.register(
    name="resize",
    params_schema={
        "width": {
            "type": "int",
            "min": 1,
            "max": 4096,
            "default": 640,
            "label": "Width",
        },
        "height": {
            "type": "int",
            "min": 1,
            "max": 4096,
            "default": 480,
            "label": "Height",
        },
    },
)
def resize(
    image: np.ndarray, width: int = 640, height: int = 480
) -> np.ndarray:
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


@OperationRegistry.register(
    name="rotate",
    params_schema={
        "angle": {
            "type": "select",
            "options": [90, 180, 270],
            "default": 90,
            "label": "Angle",
        }
    },
)
def rotate(image: np.ndarray, angle: int = 90) -> np.ndarray:
    code = ROTATE_CODES.get(angle)
    if code is None:
        return image
    return cv2.rotate(image, code)
