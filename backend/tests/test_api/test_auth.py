import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "john@example.com"
        assert data["name"] == "John Doe"
        assert data["email_verified"] is False

    async def test_register_duplicate_email(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "name": "John", "email": "dup@example.com", "password": "securepassword123",
        })
        response = await client.post("/api/v1/auth/register", json={
            "name": "Jane", "email": "dup@example.com", "password": "securepassword123",
        })
        assert response.status_code == 409

    async def test_register_weak_password(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "name": "John", "email": "john@example.com", "password": "short",
        })
        assert response.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "name": "John", "email": "login@example.com", "password": "securepassword123",
        })
        response = await client.post("/api/v1/auth/login", json={
            "email": "login@example.com", "password": "securepassword123",
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "name": "John", "email": "wrong@example.com", "password": "securepassword123",
        })
        response = await client.post("/api/v1/auth/login", json={
            "email": "wrong@example.com", "password": "wrongpassword",
        })
        assert response.status_code == 401

    async def test_login_nonexistent_email(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com", "password": "securepassword123",
        })
        assert response.status_code == 401


@pytest.mark.asyncio
class TestMe:
    async def test_me_authenticated(self, authenticated_client: AsyncClient):
        response = await authenticated_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

    async def test_me_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestVerifyEmail:
    async def test_verify_email_success(self, client: AsyncClient, db_session):
        await client.post("/api/v1/auth/register", json={
            "name": "John", "email": "verify@example.com", "password": "securepassword123",
        })
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "verify@example.com", "password": "securepassword123",
        })
        token = login_resp.json()["access_token"]

        from sqlalchemy import select
        from app.models.user import User
        result = await db_session.execute(select(User).where(User.email == "verify@example.com"))
        user = result.scalar_one()
        code = user.email_verification_token

        response = await client.post(
            "/api/v1/auth/verify-email",
            json={"code": code},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
