import os
import uuid

import cv2
import numpy as np

from app.config import settings


def get_upload_dir(user_id: uuid.UUID) -> str:
    path = os.path.join(settings.STORAGE_PATH, "uploads", str(user_id))
    os.makedirs(path, exist_ok=True)
    return path


def get_results_dir(job_id: uuid.UUID) -> str:
    path = os.path.join(settings.STORAGE_PATH, "results", str(job_id))
    os.makedirs(path, exist_ok=True)
    return path


def save_upload(user_id: uuid.UUID, filename: str, content: bytes) -> str:
    upload_dir = get_upload_dir(user_id)
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


def save_step_result(job_id: uuid.UUID, step_number: int, operation_name: str, image: np.ndarray) -> str:
    results_dir = get_results_dir(job_id)
    filename = f"step_{step_number}_{operation_name}.png"
    file_path = os.path.join(results_dir, filename)
    cv2.imwrite(file_path, image)
    return file_path


def load_image(file_path: str) -> np.ndarray:
    image = cv2.imread(file_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {file_path}")
    return image


def delete_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)


def delete_directory(dir_path: str) -> None:
    import shutil

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
