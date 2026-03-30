import numpy as np
import pytest

from app.engine.registry import OperationRegistry


@pytest.fixture(autouse=True)
def clear_registry():
    OperationRegistry._operations.clear()
    yield
    OperationRegistry._operations.clear()


class TestOperationRegistry:
    def test_register_and_get(self):
        @OperationRegistry.register(
            name="test_op",
            params_schema={"value": {"type": "int", "min": 0, "max": 100, "default": 50}},
        )
        def test_op(image: np.ndarray, value: int = 50) -> np.ndarray:
            return image

        func = OperationRegistry.get("test_op")
        assert func is test_op

    def test_get_unknown_operation_raises(self):
        with pytest.raises(KeyError, match="Unknown operation: nonexistent"):
            OperationRegistry.get("nonexistent")

    def test_list_operations(self):
        @OperationRegistry.register(name="op_a", params_schema={"x": {"type": "int"}})
        def op_a(image, x=1):
            return image

        @OperationRegistry.register(name="op_b", params_schema={})
        def op_b(image):
            return image

        ops = OperationRegistry.list_operations()
        names = [o["name"] for o in ops]
        assert "op_a" in names
        assert "op_b" in names

    def test_registered_operation_is_callable(self):
        @OperationRegistry.register(name="double", params_schema={})
        def double(image: np.ndarray) -> np.ndarray:
            return image * 2

        img = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        result = OperationRegistry.get("double")(img)
        np.testing.assert_array_equal(result, np.array([[2, 4], [6, 8]], dtype=np.uint8))
