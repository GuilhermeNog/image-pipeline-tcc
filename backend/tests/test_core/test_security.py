import pytest

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token


class TestPasswordHashing:
    def test_hash_password_returns_hash(self):
        hashed = hash_password("mysecretpassword")
        assert hashed != "mysecretpassword"
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        hashed = hash_password("mysecretpassword")
        assert verify_password("mysecretpassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("mysecretpassword")
        assert verify_password("wrongpassword", hashed) is False


class TestJWT:
    def test_create_access_token(self):
        token = create_access_token(subject="user-uuid-123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        token = create_access_token(subject="user-uuid-123")
        payload = decode_token(token, token_type="access")
        assert payload["sub"] == "user-uuid-123"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        token = create_refresh_token(subject="user-uuid-123")
        assert isinstance(token, str)

    def test_decode_refresh_token(self):
        token = create_refresh_token(subject="user-uuid-123")
        payload = decode_token(token, token_type="refresh")
        assert payload["sub"] == "user-uuid-123"
        assert payload["type"] == "refresh"

    def test_decode_access_token_as_refresh_fails(self):
        token = create_access_token(subject="user-uuid-123")
        with pytest.raises(ValueError, match="Invalid token type"):
            decode_token(token, token_type="refresh")

    def test_decode_refresh_token_as_access_fails(self):
        token = create_refresh_token(subject="user-uuid-123")
        with pytest.raises(ValueError, match="Invalid token type"):
            decode_token(token, token_type="access")
