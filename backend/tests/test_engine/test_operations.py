import cv2
import numpy as np
import pytest


def make_color_image(width=100, height=100):
    return np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)


def make_gray_image(width=100, height=100):
    return np.random.randint(0, 256, (height, width), dtype=np.uint8)


class TestGrayscale:
    def test_converts_bgr_to_gray(self):
        from app.engine.operations.color import grayscale

        result = grayscale(make_color_image())
        assert len(result.shape) == 2

    def test_already_gray_returns_same(self):
        from app.engine.operations.color import grayscale

        result = grayscale(make_gray_image())
        assert len(result.shape) == 2


class TestBrightness:
    def test_increase_brightness(self):
        from app.engine.operations.color import brightness

        result = brightness(make_color_image(), value=50)
        assert result.shape == make_color_image().shape

    def test_decrease_brightness(self):
        from app.engine.operations.color import brightness

        img = np.full((10, 10, 3), 100, dtype=np.uint8)
        result = brightness(img, value=-50)
        assert result.mean() < 100


class TestContrast:
    def test_increase_contrast(self):
        from app.engine.operations.color import contrast

        result = contrast(make_color_image(), value=2.0)
        assert result.shape == make_color_image().shape


class TestBlur:
    def test_blur_reduces_noise(self):
        from app.engine.operations.filter import blur

        result = blur(make_color_image(), kernel=5)
        assert result.shape == make_color_image().shape


class TestThreshold:
    def test_binary_threshold(self):
        from app.engine.operations.filter import threshold

        result = threshold(make_gray_image(), value=127, type="binary")
        unique = np.unique(result)
        assert all(v in [0, 255] for v in unique)


class TestCanny:
    def test_canny_edge_detection(self):
        from app.engine.operations.edge import canny

        img = make_gray_image()
        result = canny(img, threshold1=100, threshold2=200)
        assert result.shape == img.shape
        assert result.dtype == np.uint8


class TestDilate:
    def test_dilate(self):
        from app.engine.operations.morphology import dilate

        result = dilate(make_gray_image(), kernel=3, iterations=1)
        assert result.shape == make_gray_image().shape


class TestErode:
    def test_erode(self):
        from app.engine.operations.morphology import erode

        result = erode(make_gray_image(), kernel=3, iterations=1)
        assert result.shape == make_gray_image().shape


class TestResize:
    def test_resize(self):
        from app.engine.operations.transform import resize

        result = resize(make_color_image(100, 100), width=50, height=50)
        assert result.shape[:2] == (50, 50)


class TestRotate:
    def test_rotate_90(self):
        from app.engine.operations.transform import rotate

        img = make_color_image(100, 200)
        result = rotate(img, angle=90)
        assert (
            result.shape[0] == 100
            and result.shape[1] == 200
            or result.shape[0] == 200
            and result.shape[1] == 100
        )

    def test_rotate_180(self):
        from app.engine.operations.transform import rotate

        img = make_color_image(100, 200)
        result = rotate(img, angle=180)
        assert result.shape == img.shape
