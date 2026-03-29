# Image Pipeline Processing System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fullstack image processing pipeline system where users upload images, compose processing pipelines via drag-and-drop, execute them asynchronously, and view real-time progress with intermediate previews.

**Architecture:** FastAPI backend with Celery workers for async pipeline execution, Redis for task brokering and pub/sub progress, PostgreSQL for persistence, and a React SPA with a 3-column editor (sidebar + canvas + preview). Auth uses JWT dual-token with httpOnly cookies.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Celery, Redis, PostgreSQL 16, OpenCV, React 18, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion, Zustand, Vite, Docker Compose

---

## File Structure

```
backend/
  app/
    __init__.py
    main.py                          # FastAPI app factory, middleware, CORS, lifespan
    config.py                        # pydantic-settings Settings class
    database.py                      # SQLAlchemy async engine + session factory
    models/
      __init__.py                    # Base model + import all models
      user.py                        # User SQLAlchemy model
      refresh_token.py               # RefreshToken model
      pipeline.py                    # Pipeline model
      job.py                         # Job model
      job_step.py                    # JobStep model
      image.py                       # Image metadata model
    schemas/
      __init__.py
      auth.py                        # Register, Login, Token, User DTOs
      pipeline.py                    # Pipeline CRUD DTOs
      job.py                         # Job + JobStep DTOs
      image.py                       # Upload response DTO
      operation.py                   # Operation list DTO
    api/
      __init__.py
      v1/
        __init__.py
        router.py                    # Include all v1 routers
        auth.py                      # Auth endpoints
        pipelines.py                 # Pipeline CRUD endpoints
        jobs.py                      # Job execution + listing endpoints
        images.py                    # Upload + serve endpoints
        operations.py                # List available operations
        websocket.py                 # WebSocket job progress
    services/
      __init__.py
      auth_service.py                # Register, login, refresh, logout logic
      token_service.py               # JWT create/verify, refresh token CRUD
      email_service.py               # Send verification + reset emails
      pipeline_service.py            # Pipeline CRUD logic
      job_service.py                 # Job creation, status, listing
      image_service.py               # Upload, validate, metadata
      storage_service.py             # File read/write abstraction
    engine/
      __init__.py
      registry.py                    # OperationRegistry class
      executor.py                    # PipelineExecutor class
      operations/
        __init__.py                  # Auto-register all operations
        color.py                     # grayscale, brightness, contrast
        filter.py                    # blur, threshold
        edge.py                      # canny
        morphology.py                # dilate, erode
        transform.py                 # resize, rotate
    workers/
      __init__.py
      celery_app.py                  # Celery instance + config
      tasks.py                       # execute_pipeline task
    core/
      __init__.py
      security.py                    # hash_password, verify_password, create_jwt, decode_jwt
      dependencies.py                # get_db, get_current_user, get_current_active_user
      exceptions.py                  # Custom HTTP exceptions
  tests/
    __init__.py
    conftest.py                      # Fixtures: test DB, client, auth headers
    test_engine/
      __init__.py
      test_registry.py
      test_operations.py
      test_executor.py
    test_services/
      __init__.py
      test_auth_service.py
      test_pipeline_service.py
      test_job_service.py
      test_image_service.py
    test_api/
      __init__.py
      test_auth.py
      test_pipelines.py
      test_jobs.py
      test_images.py
      test_operations.py
  alembic/
    env.py
    versions/
  alembic.ini
  requirements.txt
  Dockerfile
  .env.example

frontend/
  src/
    components/
      ui/                            # shadcn/ui (installed via CLI)
      auth/
        LoginForm.tsx
        RegisterForm.tsx
        VerifyEmailForm.tsx
        ForgotPasswordForm.tsx
        ResetPasswordForm.tsx
      editor/
        Sidebar.tsx
        Canvas.tsx
        Preview.tsx
        OperationCard.tsx
        StepCard.tsx
        ParameterControls.tsx
        ProgressOverlay.tsx
      layout/
        AppLayout.tsx
        Header.tsx
        ThemeToggle.tsx
        ProtectedRoute.tsx
      dashboard/
        PipelineList.tsx
        JobList.tsx
        StatsCards.tsx
    pages/
      LoginPage.tsx
      RegisterPage.tsx
      VerifyEmailPage.tsx
      ForgotPasswordPage.tsx
      ResetPasswordPage.tsx
      DashboardPage.tsx
      EditorPage.tsx
      JobHistoryPage.tsx
      JobDetailPage.tsx
    hooks/
      useAuth.ts
      useWebSocket.ts
      usePipeline.ts
      useDragAndDrop.ts
    services/
      api.ts
      auth.ts
      pipelines.ts
      jobs.ts
      images.ts
      operations.ts
    stores/
      authStore.ts
      pipelineStore.ts
      editorStore.ts
      themeStore.ts
    types/
      auth.ts
      pipeline.ts
      job.ts
      operation.ts
    lib/
      utils.ts
      cn.ts
    App.tsx
    main.tsx
    index.css
  tailwind.config.ts
  postcss.config.js
  tsconfig.json
  vite.config.ts
  package.json
  Dockerfile
  components.json                    # shadcn/ui config

docker-compose.yml
.gitignore
.env.example
```

---

## Phase 1: Project Foundation

### Task 1: Docker Compose + Project Skeleton

**Files:**
- Create: `docker-compose.yml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`

- [ ] **Step 1: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.eggs/
*.egg
venv/
.venv/

# Environment
.env
*.env.local

# Storage
storage/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
frontend/dist/

# Docker
*.log

# Testing
.pytest_cache/
.coverage
htmlcov/
```

- [ ] **Step 2: Create .env.example**

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/image_pipeline
DATABASE_URL_SYNC=postgresql://postgres:postgres@postgres:5432/image_pipeline

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_ACCESS_SECRET=change-me-to-a-random-secret-at-least-32-chars
JWT_REFRESH_SECRET=change-me-to-another-random-secret-at-least-32-chars
JWT_ACCESS_EXPIRATION_MINUTES=15
JWT_REFRESH_EXPIRATION_DAYS=7

# App
APP_NAME=Image Pipeline
BACKEND_CORS_ORIGINS=http://localhost:5173
STORAGE_PATH=./storage

# Email (for future use)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=noreply@imagepipeline.local
```

- [ ] **Step 3: Create backend/requirements.txt**

```txt
fastapi==0.115.12
uvicorn[standard]==0.34.2
sqlalchemy[asyncio]==2.0.41
asyncpg==0.31.0
alembic==1.15.2
psycopg2-binary==2.9.10
pydantic[email]==2.11.3
pydantic-settings==2.9.1
python-jose[cryptography]==3.4.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.20
celery[redis]==5.5.2
redis==5.3.0
opencv-python-headless==4.11.0.86
Pillow==11.2.1
httpx==0.28.1
pytest==8.4.0
pytest-asyncio==0.26.0
aiosqlite==0.21.0
```

- [ ] **Step 4: Create backend/app/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Image Pipeline"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/image_pipeline"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@postgres:5432/image_pipeline"
    REDIS_URL: str = "redis://redis:6379/0"

    JWT_ACCESS_SECRET: str = "change-me"
    JWT_REFRESH_SECRET: str = "change-me"
    JWT_ACCESS_EXPIRATION_MINUTES: int = 15
    JWT_REFRESH_EXPIRATION_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"
    STORAGE_PATH: str = "./storage"

    MAX_UPLOAD_SIZE_MB: int = 10
    MAX_PIPELINE_OPERATIONS: int = 20
    JOB_TIMEOUT_SECONDS: int = 300

    BCRYPT_ROUNDS: int = 12

    ACCOUNT_LOCKOUT_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15

    EMAIL_VERIFICATION_EXPIRY_MINUTES: int = 15
    PASSWORD_RESET_EXPIRY_MINUTES: int = 15

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@imagepipeline.local"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
```

- [ ] **Step 5: Create backend/app/main.py**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    os.makedirs(f"{settings.STORAGE_PATH}/uploads", exist_ok=True)
    os.makedirs(f"{settings.STORAGE_PATH}/results", exist_ok=True)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Create backend/app/__init__.py**

```python
```

- [ ] **Step 7: Create backend/Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 8: Create docker-compose.yml**

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend-storage:/app/storage
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  worker:
    build: ./backend
    command: celery -A app.workers.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
      - backend-storage:/app/storage
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: image_pipeline
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres-data:
  backend-storage:
```

- [ ] **Step 9: Copy .env.example to .env and start services**

```bash
cp .env.example .env
docker compose up -d postgres redis
docker compose up -d backend
```

- [ ] **Step 10: Verify health endpoint**

```bash
curl http://localhost:8000/api/v1/health
```

Expected: `{"status":"ok"}`

- [ ] **Step 11: Commit**

```bash
git add .
git commit -m "feat: project skeleton with Docker Compose, FastAPI, PostgreSQL, Redis"
```

---

### Task 2: Database Setup (SQLAlchemy + Alembic)

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/refresh_token.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`

- [ ] **Step 1: Create backend/app/database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

- [ ] **Step 2: Create backend/app/models/user.py**

```python
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verification_token: Mapped[str | None] = mapped_column(String(6), nullable=True)
    email_verification_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    password_reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    pipelines = relationship("Pipeline", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
```

- [ ] **Step 3: Create backend/app/models/refresh_token.py**

```python
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="refresh_tokens")
```

- [ ] **Step 4: Create backend/app/models/__init__.py**

```python
from app.database import Base
from app.models.user import User
from app.models.refresh_token import RefreshToken

__all__ = ["Base", "User", "RefreshToken"]
```

- [ ] **Step 5: Initialize Alembic**

Run inside the backend container:

```bash
docker compose exec backend bash -c "cd /app && alembic init alembic"
```

- [ ] **Step 6: Edit backend/alembic.ini — set sqlalchemy.url to empty (will use env.py)**

Replace the `sqlalchemy.url` line:

```ini
sqlalchemy.url =
```

- [ ] **Step 7: Replace backend/alembic/env.py**

```python
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import settings
from app.models import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 8: Create first migration**

```bash
docker compose exec backend alembic revision --autogenerate -m "add users and refresh_tokens tables"
```

- [ ] **Step 9: Run migration**

```bash
docker compose exec backend alembic upgrade head
```

- [ ] **Step 10: Commit**

```bash
git add .
git commit -m "feat: database setup with SQLAlchemy, Alembic, User and RefreshToken models"
```

---

## Phase 2: Authentication

### Task 3: Security Utilities (JWT + Password Hashing)

**Files:**
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/security.py`
- Create: `backend/app/core/exceptions.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_engine/__init__.py`
- Create: `backend/tests/test_services/__init__.py`
- Create: `backend/tests/test_api/__init__.py`
- Create: `backend/tests/test_core/__init__.py`
- Create: `backend/tests/test_core/test_security.py`

- [ ] **Step 1: Create backend/app/core/__init__.py**

```python
```

- [ ] **Step 2: Create backend/app/core/exceptions.py**

```python
from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")


class AccountLockedException(HTTPException):
    def __init__(self, locked_until: str):
        super().__init__(status_code=status.HTTP_423_LOCKED, detail=f"Account locked until {locked_until}")


class EmailNotVerifiedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")


class TokenInvalidException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


class EmailAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")


class NotFoundException(HTTPException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


class ForbiddenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
```

- [ ] **Step 3: Write failing tests for security utilities**

Create `backend/tests/__init__.py`, `backend/tests/test_core/__init__.py`, `backend/tests/test_engine/__init__.py`, `backend/tests/test_services/__init__.py`, `backend/tests/test_api/__init__.py` (all empty `__init__.py`).

Create `backend/tests/test_core/test_security.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they fail**

```bash
docker compose exec backend pytest tests/test_core/test_security.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'app.core.security'`

- [ ] **Step 5: Implement security utilities**

Create `backend/app/core/security.py`:

```python
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_EXPIRATION_MINUTES)
    payload = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.JWT_ACCESS_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, token_type: str) -> dict:
    secret = settings.JWT_ACCESS_SECRET if token_type == "access" else settings.JWT_REFRESH_SECRET
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")
    if payload.get("type") != token_type:
        raise ValueError(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
    return payload
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
docker compose exec backend pytest tests/test_core/test_security.py -v
```

Expected: all 7 tests PASS

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "feat: security utilities — JWT tokens and password hashing with tests"
```

---

### Task 4: Auth Schemas + Dependencies

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/core/dependencies.py`

- [ ] **Step 1: Create backend/app/schemas/__init__.py**

```python
```

- [ ] **Step 2: Create backend/app/schemas/auth.py**

```python
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    pass  # refresh token comes from cookie


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    email: EmailStr
    new_password: str = Field(min_length=8, max_length=128)


class VerifyEmailRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    email_verified: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
```

- [ ] **Step 3: Create backend/app/core/dependencies.py**

```python
import uuid

from fastapi import Cookie, Depends, Request
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import TokenExpiredException, TokenInvalidException
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User


async def get_current_user(
    request: Request,
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = access_token
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise TokenInvalidException()

    try:
        payload = decode_token(token, token_type="access")
    except ValueError:
        raise TokenInvalidException()

    user_id = payload.get("sub")
    if not user_id:
        raise TokenInvalidException()

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise TokenInvalidException()

    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise TokenInvalidException()
    return user
```

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: auth schemas and dependency injection for current user"
```

---

### Task 5: Auth Service

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/services/token_service.py`

- [ ] **Step 1: Create backend/app/services/__init__.py**

```python
```

- [ ] **Step 2: Create backend/app/services/token_service.py**

```python
import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models.refresh_token import RefreshToken


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def create_token_pair(
    db: AsyncSession,
    user_id: uuid.UUID,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[str, str]:
    access_token = create_access_token(subject=str(user_id))
    refresh_token = create_refresh_token(subject=str(user_id))

    db_token = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(refresh_token),
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
    )
    db.add(db_token)
    await db.flush()

    return access_token, refresh_token


async def revoke_refresh_token(db: AsyncSession, token_hash: str) -> None:
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.token_hash == token_hash, RefreshToken.is_revoked == False)
        .values(is_revoked=True, revoked_at=datetime.now(timezone.utc))
    )


async def revoke_all_user_tokens(db: AsyncSession, user_id: uuid.UUID) -> None:
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)
        .values(is_revoked=True, revoked_at=datetime.now(timezone.utc))
    )


async def find_valid_refresh_token(db: AsyncSession, token_hash: str) -> RefreshToken | None:
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()
```

- [ ] **Step 3: Create backend/app/services/auth_service.py**

```python
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import (
    AccountLockedException,
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    TokenInvalidException,
)
from app.core.security import decode_token, hash_password, verify_password
from app.models.user import User
from app.services.token_service import (
    create_token_pair,
    find_valid_refresh_token,
    hash_token,
    revoke_all_user_tokens,
    revoke_refresh_token,
)


async def register(db: AsyncSession, name: str, email: str, password: str) -> tuple[User, str, str]:
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise EmailAlreadyExistsException()

    verification_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])

    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        email_verification_token=verification_code,
        email_verification_expires=datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRY_MINUTES),
    )
    db.add(user)
    await db.flush()

    access_token, refresh_token = await create_token_pair(db, user.id)
    return user, access_token, refresh_token


async def login(
    db: AsyncSession,
    email: str,
    password: str,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[User, str, str]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise InvalidCredentialsException()

    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise AccountLockedException(locked_until=user.locked_until.isoformat())

    if not verify_password(password, user.password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.ACCOUNT_LOCKOUT_ATTEMPTS:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
        await db.flush()
        raise InvalidCredentialsException()

    user.failed_login_attempts = 0
    user.locked_until = None
    await db.flush()

    access_token, refresh_token = await create_token_pair(db, user.id, user_agent, ip_address)
    return user, access_token, refresh_token


async def refresh(db: AsyncSession, raw_refresh_token: str, user_agent: str | None = None, ip_address: str | None = None) -> tuple[str, str]:
    try:
        payload = decode_token(raw_refresh_token, token_type="refresh")
    except ValueError:
        raise TokenInvalidException()

    token_hash = hash_token(raw_refresh_token)
    db_token = await find_valid_refresh_token(db, token_hash)
    if not db_token:
        raise TokenInvalidException()

    await revoke_refresh_token(db, token_hash)

    user_id = payload["sub"]
    access_token, new_refresh_token = await create_token_pair(db, user_id, user_agent, ip_address)
    return access_token, new_refresh_token


async def logout(db: AsyncSession, raw_refresh_token: str) -> None:
    token_hash = hash_token(raw_refresh_token)
    await revoke_refresh_token(db, token_hash)


async def logout_all(db: AsyncSession, user_id) -> None:
    await revoke_all_user_tokens(db, user_id)


async def verify_email(db: AsyncSession, user: User, code: str) -> None:
    if user.email_verified:
        return
    if user.email_verification_token != code:
        raise TokenInvalidException()
    if user.email_verification_expires and user.email_verification_expires < datetime.now(timezone.utc):
        raise TokenInvalidException()
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_expires = None
    await db.flush()


async def resend_verification(db: AsyncSession, user: User) -> str:
    code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    user.email_verification_token = code
    user.email_verification_expires = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_EXPIRY_MINUTES)
    await db.flush()
    return code


async def forgot_password(db: AsyncSession, email: str) -> str | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None  # don't reveal if email exists

    token = secrets.token_urlsafe(32)
    user.password_reset_token = token
    user.password_reset_expires = datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_EXPIRY_MINUTES)
    await db.flush()
    return token


async def reset_password(db: AsyncSession, email: str, token: str, new_password: str) -> None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or user.password_reset_token != token:
        raise TokenInvalidException()
    if user.password_reset_expires and user.password_reset_expires < datetime.now(timezone.utc):
        raise TokenInvalidException()

    user.password = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.flush()

    await revoke_all_user_tokens(db, user.id)
```

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: auth service and token service — register, login, refresh, logout, password reset"
```

---

### Task 6: Auth API Endpoints

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/v1/__init__.py`
- Create: `backend/app/api/v1/auth.py`
- Create: `backend/app/api/v1/router.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Create empty __init__.py files**

Create `backend/app/api/__init__.py` and `backend/app/api/v1/__init__.py` (both empty).

- [ ] **Step 2: Create backend/app/api/v1/auth.py**

```python
from fastapi import APIRouter, Cookie, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # True in production
        samesite="lax",
        max_age=settings.JWT_ACCESS_EXPIRATION_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.JWT_REFRESH_EXPIRATION_DAYS * 86400,
        path="/api/v1/auth",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/api/v1/auth")


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(body: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user, access_token, refresh_token = await auth_service.register(db, body.name, body.email, body.password)
    _set_auth_cookies(response, access_token, refresh_token)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    user, access_token, refresh_token = await auth_service.login(
        db, body.email, body.password,
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.client.host if request.client else None,
    )
    _set_auth_cookies(response, access_token, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if not refresh_token:
        from app.core.exceptions import TokenInvalidException
        raise TokenInvalidException()
    access_token, new_refresh_token = await auth_service.refresh(
        db, refresh_token,
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.client.host if request.client else None,
    )
    _set_auth_cookies(response, access_token, new_refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if refresh_token:
        await auth_service.logout(db, refresh_token)
    _clear_auth_cookies(response)
    return MessageResponse(message="Logged out successfully")


@router.post("/logout-all", response_model=MessageResponse)
async def logout_all(
    response: Response,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.logout_all(db, user.id)
    _clear_auth_cookies(response)
    return MessageResponse(message="All sessions revoked")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    body: VerifyEmailRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.verify_email(db, user, body.code)
    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.resend_verification(db, user)
    return MessageResponse(message="Verification code sent")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.forgot_password(db, body.email)
    return MessageResponse(message="If that email exists, a reset link has been sent")


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.reset_password(db, body.email, body.token, body.new_password)
    return MessageResponse(message="Password reset successfully")


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user
```

- [ ] **Step 3: Create backend/app/api/v1/router.py**

```python
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
```

- [ ] **Step 4: Update backend/app/main.py to include router**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    os.makedirs(f"{settings.STORAGE_PATH}/uploads", exist_ok=True)
    os.makedirs(f"{settings.STORAGE_PATH}/results", exist_ok=True)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


app = create_app()


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Verify auth endpoints appear in Swagger**

```bash
docker compose restart backend
curl http://localhost:8000/docs
```

Open `http://localhost:8000/docs` — all auth routes should be listed.

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "feat: auth API endpoints — register, login, refresh, logout, email verify, password reset"
```

---

### Task 7: Auth API Integration Tests

**Files:**
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_api/test_auth.py`

- [ ] **Step 1: Create backend/tests/conftest.py**

```python
import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import create_app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionFactory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    await client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword123",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "securepassword123",
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

- [ ] **Step 2: Create backend/tests/test_api/test_auth.py**

```python
import pytest
import pytest_asyncio
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
        assert "access_token" in response.cookies or "set-cookie" in response.headers

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
```

- [ ] **Step 3: Run auth tests**

```bash
docker compose exec backend pytest tests/test_api/test_auth.py -v
```

Expected: all tests PASS

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "test: auth API integration tests — register, login, me, verify email"
```

---

## Phase 3: Pipeline Engine

### Task 8: Operation Registry

**Files:**
- Create: `backend/app/engine/__init__.py`
- Create: `backend/app/engine/registry.py`
- Create: `backend/tests/test_engine/test_registry.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_engine/test_registry.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
docker compose exec backend pytest tests/test_engine/test_registry.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement OperationRegistry**

Create `backend/app/engine/__init__.py` (empty).

Create `backend/app/engine/registry.py`:

```python
from collections.abc import Callable
from typing import Any

import numpy as np


class OperationRegistry:
    _operations: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, params_schema: dict):
        def decorator(func: Callable[[np.ndarray, ...], np.ndarray]):
            cls._operations[name] = {
                "func": func,
                "params_schema": params_schema,
            }
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Callable:
        if name not in cls._operations:
            raise KeyError(f"Unknown operation: {name}")
        return cls._operations[name]["func"]

    @classmethod
    def get_schema(cls, name: str) -> dict:
        if name not in cls._operations:
            raise KeyError(f"Unknown operation: {name}")
        return cls._operations[name]["params_schema"]

    @classmethod
    def list_operations(cls) -> list[dict]:
        return [
            {"name": name, "params": data["params_schema"]}
            for name, data in cls._operations.items()
        ]

    @classmethod
    def has(cls, name: str) -> bool:
        return name in cls._operations
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
docker compose exec backend pytest tests/test_engine/test_registry.py -v
```

Expected: all 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: OperationRegistry with register, get, list, and param schema support"
```

---

### Task 9: OpenCV Operations

**Files:**
- Create: `backend/app/engine/operations/__init__.py`
- Create: `backend/app/engine/operations/color.py`
- Create: `backend/app/engine/operations/filter.py`
- Create: `backend/app/engine/operations/edge.py`
- Create: `backend/app/engine/operations/morphology.py`
- Create: `backend/app/engine/operations/transform.py`
- Create: `backend/tests/test_engine/test_operations.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_engine/test_operations.py`:

```python
import cv2
import numpy as np
import pytest


def make_color_image(width=100, height=100) -> np.ndarray:
    return np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)


def make_gray_image(width=100, height=100) -> np.ndarray:
    return np.random.randint(0, 256, (height, width), dtype=np.uint8)


class TestGrayscale:
    def test_converts_bgr_to_gray(self):
        from app.engine.operations.color import grayscale
        img = make_color_image()
        result = grayscale(img)
        assert len(result.shape) == 2  # single channel

    def test_already_gray_returns_same(self):
        from app.engine.operations.color import grayscale
        img = make_gray_image()
        result = grayscale(img)
        assert len(result.shape) == 2


class TestBrightness:
    def test_increase_brightness(self):
        from app.engine.operations.color import brightness
        img = make_color_image()
        result = brightness(img, value=50)
        assert result.shape == img.shape

    def test_decrease_brightness(self):
        from app.engine.operations.color import brightness
        img = np.full((10, 10, 3), 100, dtype=np.uint8)
        result = brightness(img, value=-50)
        assert result.mean() < 100


class TestContrast:
    def test_increase_contrast(self):
        from app.engine.operations.color import contrast
        img = make_color_image()
        result = contrast(img, value=2.0)
        assert result.shape == img.shape


class TestBlur:
    def test_blur_reduces_noise(self):
        from app.engine.operations.filter import blur
        img = make_color_image()
        result = blur(img, kernel=5)
        assert result.shape == img.shape


class TestThreshold:
    def test_binary_threshold(self):
        from app.engine.operations.filter import threshold
        img = make_gray_image()
        result = threshold(img, value=127, type="binary")
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
        img = make_gray_image()
        result = dilate(img, kernel=3, iterations=1)
        assert result.shape == img.shape


class TestErode:
    def test_erode(self):
        from app.engine.operations.morphology import erode
        img = make_gray_image()
        result = erode(img, kernel=3, iterations=1)
        assert result.shape == img.shape


class TestResize:
    def test_resize(self):
        from app.engine.operations.transform import resize
        img = make_color_image(100, 100)
        result = resize(img, width=50, height=50)
        assert result.shape[:2] == (50, 50)


class TestRotate:
    def test_rotate_90(self):
        from app.engine.operations.transform import rotate
        img = make_color_image(100, 200)
        result = rotate(img, angle=90)
        assert result.shape[:2] == (100, 200) or result.shape[:2] == (200, 100)

    def test_rotate_180(self):
        from app.engine.operations.transform import rotate
        img = make_color_image(100, 200)
        result = rotate(img, angle=180)
        assert result.shape == img.shape
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
docker compose exec backend pytest tests/test_engine/test_operations.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement color operations**

Create `backend/app/engine/operations/color.py`:

```python
import cv2
import numpy as np

from app.engine.registry import OperationRegistry


@OperationRegistry.register(
    name="grayscale",
    params_schema={},
)
def grayscale(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


@OperationRegistry.register(
    name="brightness",
    params_schema={
        "value": {"type": "int", "min": -100, "max": 100, "default": 0, "label": "Brightness"},
    },
)
def brightness(image: np.ndarray, value: int = 0) -> np.ndarray:
    return cv2.convertScaleAbs(image, alpha=1.0, beta=value)


@OperationRegistry.register(
    name="contrast",
    params_schema={
        "value": {"type": "float", "min": 0.5, "max": 3.0, "default": 1.0, "step": 0.1, "label": "Contrast"},
    },
)
def contrast(image: np.ndarray, value: float = 1.0) -> np.ndarray:
    return cv2.convertScaleAbs(image, alpha=value, beta=0)
```

- [ ] **Step 4: Implement filter operations**

Create `backend/app/engine/operations/filter.py`:

```python
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
        "kernel": {"type": "int", "min": 1, "max": 31, "default": 5, "step": 2, "label": "Kernel Size"},
    },
)
def blur(image: np.ndarray, kernel: int = 5) -> np.ndarray:
    k = kernel if kernel % 2 == 1 else kernel + 1
    return cv2.GaussianBlur(image, (k, k), 0)


@OperationRegistry.register(
    name="threshold",
    params_schema={
        "value": {"type": "int", "min": 0, "max": 255, "default": 127, "label": "Threshold Value"},
        "type": {"type": "select", "options": ["binary", "binary_inv", "trunc", "tozero", "tozero_inv"], "default": "binary", "label": "Type"},
    },
)
def threshold(image: np.ndarray, value: int = 127, type: str = "binary") -> np.ndarray:
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh_type = THRESHOLD_TYPES.get(type, cv2.THRESH_BINARY)
    _, result = cv2.threshold(image, value, 255, thresh_type)
    return result
```

- [ ] **Step 5: Implement edge operations**

Create `backend/app/engine/operations/edge.py`:

```python
import cv2
import numpy as np

from app.engine.registry import OperationRegistry


@OperationRegistry.register(
    name="canny",
    params_schema={
        "threshold1": {"type": "int", "min": 0, "max": 500, "default": 100, "label": "Threshold 1"},
        "threshold2": {"type": "int", "min": 0, "max": 500, "default": 200, "label": "Threshold 2"},
    },
)
def canny(image: np.ndarray, threshold1: int = 100, threshold2: int = 200) -> np.ndarray:
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(image, threshold1, threshold2)
```

- [ ] **Step 6: Implement morphology operations**

Create `backend/app/engine/operations/morphology.py`:

```python
import cv2
import numpy as np

from app.engine.registry import OperationRegistry


@OperationRegistry.register(
    name="dilate",
    params_schema={
        "kernel": {"type": "int", "min": 1, "max": 21, "default": 3, "step": 2, "label": "Kernel Size"},
        "iterations": {"type": "int", "min": 1, "max": 10, "default": 1, "label": "Iterations"},
    },
)
def dilate(image: np.ndarray, kernel: int = 3, iterations: int = 1) -> np.ndarray:
    k = np.ones((kernel, kernel), np.uint8)
    return cv2.dilate(image, k, iterations=iterations)


@OperationRegistry.register(
    name="erode",
    params_schema={
        "kernel": {"type": "int", "min": 1, "max": 21, "default": 3, "step": 2, "label": "Kernel Size"},
        "iterations": {"type": "int", "min": 1, "max": 10, "default": 1, "label": "Iterations"},
    },
)
def erode(image: np.ndarray, kernel: int = 3, iterations: int = 1) -> np.ndarray:
    k = np.ones((kernel, kernel), np.uint8)
    return cv2.erode(image, k, iterations=iterations)
```

- [ ] **Step 7: Implement transform operations**

Create `backend/app/engine/operations/transform.py`:

```python
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
        "width": {"type": "int", "min": 1, "max": 4096, "default": 640, "label": "Width"},
        "height": {"type": "int", "min": 1, "max": 4096, "default": 480, "label": "Height"},
    },
)
def resize(image: np.ndarray, width: int = 640, height: int = 480) -> np.ndarray:
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


@OperationRegistry.register(
    name="rotate",
    params_schema={
        "angle": {"type": "select", "options": [90, 180, 270], "default": 90, "label": "Angle"},
    },
)
def rotate(image: np.ndarray, angle: int = 90) -> np.ndarray:
    code = ROTATE_CODES.get(angle)
    if code is None:
        return image
    return cv2.rotate(image, code)
```

- [ ] **Step 8: Create __init__.py that auto-imports all operations**

Create `backend/app/engine/operations/__init__.py`:

```python
from app.engine.operations import color, edge, filter, morphology, transform

__all__ = ["color", "edge", "filter", "morphology", "transform"]
```

- [ ] **Step 9: Run tests to verify they pass**

```bash
docker compose exec backend pytest tests/test_engine/test_operations.py -v
```

Expected: all 13 tests PASS

- [ ] **Step 10: Commit**

```bash
git add .
git commit -m "feat: 10 OpenCV operations — grayscale, blur, threshold, canny, dilate, erode, brightness, contrast, resize, rotate"
```

---

### Task 10: Pipeline Executor

**Files:**
- Create: `backend/app/engine/executor.py`
- Create: `backend/tests/test_engine/test_executor.py`

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_engine/test_executor.py`:

```python
import numpy as np
import pytest

from app.engine.executor import PipelineExecutor
import app.engine.operations  # noqa: F401 — triggers registration


def make_color_image(width=100, height=100) -> np.ndarray:
    return np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)


class TestPipelineExecutor:
    def test_execute_single_operation(self):
        executor = PipelineExecutor()
        img = make_color_image()
        operations = [{"type": "grayscale"}]
        results = executor.execute(img, operations)
        assert len(results) == 1
        assert len(results[0].shape) == 2

    def test_execute_multiple_operations(self):
        executor = PipelineExecutor()
        img = make_color_image()
        operations = [
            {"type": "grayscale"},
            {"type": "blur", "params": {"kernel": 5}},
            {"type": "threshold", "params": {"value": 127}},
        ]
        results = executor.execute(img, operations)
        assert len(results) == 3
        # final result should be binary (threshold)
        unique = np.unique(results[2])
        assert all(v in [0, 255] for v in unique)

    def test_execute_empty_pipeline(self):
        executor = PipelineExecutor()
        img = make_color_image()
        results = executor.execute(img, [])
        assert len(results) == 0

    def test_execute_with_callback(self):
        executor = PipelineExecutor()
        img = make_color_image()
        operations = [{"type": "grayscale"}, {"type": "blur", "params": {"kernel": 3}}]
        progress = []

        def on_step(step: int, total: int, operation: str, result: np.ndarray):
            progress.append({"step": step, "total": total, "operation": operation})

        executor.execute(img, operations, on_step=on_step)
        assert len(progress) == 2
        assert progress[0] == {"step": 1, "total": 2, "operation": "grayscale"}
        assert progress[1] == {"step": 2, "total": 2, "operation": "blur"}

    def test_execute_unknown_operation_raises(self):
        executor = PipelineExecutor()
        img = make_color_image()
        operations = [{"type": "nonexistent_op"}]
        with pytest.raises(KeyError, match="Unknown operation"):
            executor.execute(img, operations)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
docker compose exec backend pytest tests/test_engine/test_executor.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement PipelineExecutor**

Create `backend/app/engine/executor.py`:

```python
from collections.abc import Callable
from typing import Any

import numpy as np

from app.engine.registry import OperationRegistry


class PipelineExecutor:
    def execute(
        self,
        image: np.ndarray,
        operations: list[dict[str, Any]],
        on_step: Callable[[int, int, str, np.ndarray], None] | None = None,
    ) -> list[np.ndarray]:
        results: list[np.ndarray] = []
        current = image.copy()
        total = len(operations)

        for i, op in enumerate(operations):
            op_type = op["type"]
            params = op.get("params", {})
            func = OperationRegistry.get(op_type)
            current = func(current, **params)
            results.append(current)

            if on_step:
                on_step(i + 1, total, op_type, current)

        return results
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
docker compose exec backend pytest tests/test_engine/test_executor.py -v
```

Expected: all 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: PipelineExecutor with step callbacks for real-time progress"
```

---

## Phase 4: Async Job System (Celery + WebSocket)

### Task 11: Data Models (Pipeline, Job, JobStep, Image)

**Files:**
- Create: `backend/app/models/pipeline.py`
- Create: `backend/app/models/job.py`
- Create: `backend/app/models/job_step.py`
- Create: `backend/app/models/image.py`
- Modify: `backend/app/models/__init__.py`

- [ ] **Step 1: Create backend/app/models/image.py**

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Image(Base):
    __tablename__ = "images"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(50))
    file_size: Mapped[int] = mapped_column(Integer)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 2: Create backend/app/models/pipeline.py**

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    operations: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="pipelines")
    jobs = relationship("Job", back_populates="pipeline", cascade="all, delete-orphan")
```

- [ ] **Step 3: Create backend/app/models/job.py**

```python
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    pipeline_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pipelines.id", ondelete="SET NULL"), nullable=True)
    image_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING)
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    total_steps: Mapped[int] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="jobs")
    pipeline = relationship("Pipeline", back_populates="jobs")
    steps = relationship("JobStep", back_populates="job", cascade="all, delete-orphan", order_by="JobStep.step_number")
```

- [ ] **Step 4: Create backend/app/models/job_step.py**

```python
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StepStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStep(Base):
    __tablename__ = "job_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"))
    step_number: Mapped[int] = mapped_column(Integer)
    operation_type: Mapped[str] = mapped_column(String(50))
    operation_params: Mapped[dict] = mapped_column(JSON, default=dict)
    result_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[StepStatus] = mapped_column(Enum(StepStatus), default=StepStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="steps")
```

- [ ] **Step 5: Update backend/app/models/__init__.py**

```python
from app.database import Base
from app.models.image import Image
from app.models.job import Job, JobStatus
from app.models.job_step import JobStep, StepStatus
from app.models.pipeline import Pipeline
from app.models.refresh_token import RefreshToken
from app.models.user import User

__all__ = ["Base", "User", "RefreshToken", "Pipeline", "Job", "JobStatus", "JobStep", "StepStatus", "Image"]
```

- [ ] **Step 6: Generate and run migration**

```bash
docker compose exec backend alembic revision --autogenerate -m "add images, pipelines, jobs, job_steps tables"
docker compose exec backend alembic upgrade head
```

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "feat: data models — Image, Pipeline, Job, JobStep with migrations"
```

---

### Task 12: Storage + Image Upload Service

**Files:**
- Create: `backend/app/services/storage_service.py`
- Create: `backend/app/services/image_service.py`
- Create: `backend/app/schemas/image.py`

- [ ] **Step 1: Create backend/app/services/storage_service.py**

```python
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
```

- [ ] **Step 2: Create backend/app/schemas/image.py**

```python
import uuid
from datetime import datetime

from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    original_filename: str
    mime_type: str
    file_size: int
    width: int
    height: int
    created_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: Create backend/app/services/image_service.py**

```python
import uuid

import cv2
import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.image import Image
from app.services.storage_service import save_upload

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/bmp", "image/tiff"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


async def upload_image(
    db: AsyncSession,
    user_id: uuid.UUID,
    filename: str,
    content_type: str,
    content: bytes,
) -> Image:
    import os
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file format: {ext}")

    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise ValueError(f"File too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB")

    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = save_upload(user_id, unique_filename, content)

    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image file")
    height, width = img.shape[:2]

    image = Image(
        user_id=user_id,
        filename=unique_filename,
        original_filename=filename,
        file_path=file_path,
        mime_type=content_type or "image/png",
        file_size=len(content),
        width=width,
        height=height,
    )
    db.add(image)
    await db.flush()
    return image


async def get_image(db: AsyncSession, image_id: uuid.UUID, user_id: uuid.UUID) -> Image:
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise NotFoundException("Image")
    if image.user_id != user_id:
        raise ForbiddenException()
    return image


async def delete_image(db: AsyncSession, image_id: uuid.UUID, user_id: uuid.UUID) -> None:
    image = await get_image(db, image_id, user_id)
    from app.services.storage_service import delete_file
    delete_file(image.file_path)
    await db.delete(image)
```

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: storage service and image upload with validation"
```

---

### Task 13: Celery Worker + Pipeline Task

**Files:**
- Create: `backend/app/workers/__init__.py`
- Create: `backend/app/workers/celery_app.py`
- Create: `backend/app/workers/tasks.py`

- [ ] **Step 1: Create backend/app/workers/__init__.py**

```python
```

- [ ] **Step 2: Create backend/app/workers/celery_app.py**

```python
from celery import Celery

from app.config import settings

celery_app = Celery(
    "image_pipeline",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_soft_time_limit=settings.JOB_TIMEOUT_SECONDS,
    task_time_limit=settings.JOB_TIMEOUT_SECONDS + 30,
)

celery_app.autodiscover_tasks(["app.workers"])
```

- [ ] **Step 3: Create backend/app/workers/tasks.py**

```python
import json
import time
import uuid
from datetime import datetime, timezone

import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.engine.executor import PipelineExecutor
from app.models.job import Job, JobStatus
from app.models.job_step import JobStep, StepStatus
from app.services.storage_service import load_image, save_step_result
from app.workers.celery_app import celery_app

import app.engine.operations  # noqa: F401 — trigger registration

sync_engine = create_engine(settings.DATABASE_URL_SYNC)
SyncSession = sessionmaker(sync_engine, class_=Session)

redis_client = redis.from_url(settings.REDIS_URL)


def publish_progress(job_id: str, step: int, total: int, operation: str, result_path: str):
    message = json.dumps({
        "job_id": job_id,
        "step": step,
        "total": total,
        "operation": operation,
        "result_path": result_path,
        "status": "processing",
    })
    redis_client.publish(f"job:{job_id}:progress", message)


@celery_app.task(name="execute_pipeline", bind=True)
def execute_pipeline(self, job_id: str):
    with SyncSession() as db:
        job = db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
        if not job:
            return {"error": "Job not found"}

        job.status = JobStatus.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        try:
            image_record = db.query(
                __import__("app.models.image", fromlist=["Image"]).Image
            ).filter_by(id=job.image_id).first()

            if not image_record:
                raise FileNotFoundError("Image record not found")

            image = load_image(image_record.file_path)
            steps = db.query(JobStep).filter(JobStep.job_id == job.id).order_by(JobStep.step_number).all()
            executor = PipelineExecutor()

            operations = [
                {"type": step.operation_type, "params": step.operation_params or {}}
                for step in steps
            ]

            def on_step(step_num, total, operation, result_image):
                step_record = steps[step_num - 1]
                start_time = time.time()

                result_path = save_step_result(job.id, step_num, operation, result_image)

                step_record.result_image_path = result_path
                step_record.status = StepStatus.COMPLETED
                step_record.processing_time_ms = int((time.time() - start_time) * 1000)
                job.current_step = step_num
                db.commit()

                publish_progress(job_id, step_num, total, operation, result_path)

            executor.execute(image, operations, on_step=on_step)

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            db.commit()

            redis_client.publish(f"job:{job_id}:progress", json.dumps({
                "job_id": job_id,
                "status": "completed",
            }))

            return {"status": "completed", "job_id": job_id}

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()

            redis_client.publish(f"job:{job_id}:progress", json.dumps({
                "job_id": job_id,
                "status": "failed",
                "error": str(e),
            }))

            return {"status": "failed", "error": str(e)}
```

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: Celery worker with execute_pipeline task and Redis progress publishing"
```

---

### Task 14: Job Service + Schemas

**Files:**
- Create: `backend/app/services/job_service.py`
- Create: `backend/app/schemas/job.py`
- Create: `backend/app/schemas/operation.py`

- [ ] **Step 1: Create backend/app/schemas/operation.py**

```python
from pydantic import BaseModel


class OperationSchema(BaseModel):
    name: str
    params: dict


class OperationListResponse(BaseModel):
    operations: list[OperationSchema]
```

- [ ] **Step 2: Create backend/app/schemas/job.py**

```python
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class OperationInput(BaseModel):
    type: str
    params: dict = Field(default_factory=dict)


class ExecuteJobRequest(BaseModel):
    image_id: uuid.UUID
    pipeline_id: uuid.UUID | None = None
    operations: list[OperationInput] = Field(min_length=1, max_length=20)


class JobStepResponse(BaseModel):
    id: uuid.UUID
    step_number: int
    operation_type: str
    operation_params: dict
    result_image_path: str | None
    processing_time_ms: int | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class JobResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    pipeline_id: uuid.UUID | None
    image_id: uuid.UUID
    status: str
    current_step: int
    total_steps: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobDetailResponse(JobResponse):
    steps: list[JobStepResponse] = []


class ExecuteJobResponse(BaseModel):
    job_id: uuid.UUID
    status: str = "pending"
```

- [ ] **Step 3: Create backend/app/services/job_service.py**

```python
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.exceptions import ForbiddenException, NotFoundException
from app.engine.registry import OperationRegistry
from app.models.job import Job, JobStatus
from app.models.job_step import JobStep
from app.workers.tasks import execute_pipeline

import app.engine.operations  # noqa: F401


async def create_and_execute_job(
    db: AsyncSession,
    user_id: uuid.UUID,
    image_id: uuid.UUID,
    operations: list[dict],
    pipeline_id: uuid.UUID | None = None,
) -> Job:
    for op in operations:
        if not OperationRegistry.has(op["type"]):
            raise ValueError(f"Unknown operation: {op['type']}")

    if len(operations) > settings.MAX_PIPELINE_OPERATIONS:
        raise ValueError(f"Max {settings.MAX_PIPELINE_OPERATIONS} operations allowed")

    job = Job(
        user_id=user_id,
        image_id=image_id,
        pipeline_id=pipeline_id,
        total_steps=len(operations),
        status=JobStatus.PENDING,
    )
    db.add(job)
    await db.flush()

    for i, op in enumerate(operations):
        step = JobStep(
            job_id=job.id,
            step_number=i + 1,
            operation_type=op["type"],
            operation_params=op.get("params", {}),
        )
        db.add(step)

    await db.flush()

    execute_pipeline.delay(str(job.id))

    return job


async def get_job(db: AsyncSession, job_id: uuid.UUID, user_id: uuid.UUID) -> Job:
    result = await db.execute(
        select(Job).options(selectinload(Job.steps)).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise NotFoundException("Job")
    if job.user_id != user_id:
        raise ForbiddenException()
    return job


async def list_jobs(db: AsyncSession, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[Job]:
    result = await db.execute(
        select(Job)
        .where(Job.user_id == user_id)
        .order_by(Job.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def delete_job(db: AsyncSession, job_id: uuid.UUID, user_id: uuid.UUID) -> None:
    job = await get_job(db, job_id, user_id)
    from app.services.storage_service import delete_directory, get_results_dir
    delete_directory(get_results_dir(job.id))
    await db.delete(job)
```

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: job service with create, execute, list, delete and operation validation"
```

---

### Task 15: Pipeline Service + Schemas

**Files:**
- Create: `backend/app/services/pipeline_service.py`
- Create: `backend/app/schemas/pipeline.py`

- [ ] **Step 1: Create backend/app/schemas/pipeline.py**

```python
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PipelineOperationInput(BaseModel):
    type: str
    params: dict = Field(default_factory=dict)


class CreatePipelineRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    operations: list[PipelineOperationInput] = Field(min_length=1, max_length=20)


class UpdatePipelineRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    operations: list[PipelineOperationInput] | None = None


class PipelineResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: str | None
    operations: list
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Create backend/app/services/pipeline_service.py**

```python
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.pipeline import Pipeline


async def create_pipeline(
    db: AsyncSession,
    user_id: uuid.UUID,
    name: str,
    operations: list[dict],
    description: str | None = None,
) -> Pipeline:
    pipeline = Pipeline(
        user_id=user_id,
        name=name,
        description=description,
        operations=operations,
    )
    db.add(pipeline)
    await db.flush()
    return pipeline


async def get_pipeline(db: AsyncSession, pipeline_id: uuid.UUID, user_id: uuid.UUID) -> Pipeline:
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalar_one_or_none()
    if not pipeline:
        raise NotFoundException("Pipeline")
    if pipeline.user_id != user_id:
        raise ForbiddenException()
    return pipeline


async def list_pipelines(db: AsyncSession, user_id: uuid.UUID) -> list[Pipeline]:
    result = await db.execute(
        select(Pipeline).where(Pipeline.user_id == user_id).order_by(Pipeline.updated_at.desc())
    )
    return list(result.scalars().all())


async def update_pipeline(
    db: AsyncSession,
    pipeline_id: uuid.UUID,
    user_id: uuid.UUID,
    name: str | None = None,
    description: str | None = None,
    operations: list[dict] | None = None,
) -> Pipeline:
    pipeline = await get_pipeline(db, pipeline_id, user_id)
    if name is not None:
        pipeline.name = name
    if description is not None:
        pipeline.description = description
    if operations is not None:
        pipeline.operations = operations
    await db.flush()
    return pipeline


async def delete_pipeline(db: AsyncSession, pipeline_id: uuid.UUID, user_id: uuid.UUID) -> None:
    pipeline = await get_pipeline(db, pipeline_id, user_id)
    await db.delete(pipeline)
```

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: pipeline service with CRUD operations"
```

---

### Task 16: API Endpoints (Images, Pipelines, Jobs, Operations)

**Files:**
- Create: `backend/app/api/v1/images.py`
- Create: `backend/app/api/v1/pipelines.py`
- Create: `backend/app/api/v1/jobs.py`
- Create: `backend/app/api/v1/operations.py`
- Modify: `backend/app/api/v1/router.py`

- [ ] **Step 1: Create backend/app/api/v1/images.py**

```python
import uuid

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.image import ImageUploadResponse
from app.services import image_service

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload", response_model=ImageUploadResponse, status_code=201)
async def upload_image(
    file: UploadFile,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    image = await image_service.upload_image(
        db, user.id, file.filename or "image.png", file.content_type, content,
    )
    return image


@router.get("/{image_id}", response_model=ImageUploadResponse)
async def get_image(
    image_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await image_service.get_image(db, image_id, user.id)


@router.delete("/{image_id}", status_code=204)
async def delete_image(
    image_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await image_service.delete_image(db, image_id, user.id)


@router.get("/file/{image_id}")
async def serve_image(
    image_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    image = await image_service.get_image(db, image_id, user.id)
    return FileResponse(image.file_path, media_type=image.mime_type)
```

- [ ] **Step 2: Create backend/app/api/v1/pipelines.py**

```python
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.pipeline import CreatePipelineRequest, PipelineResponse, UpdatePipelineRequest
from app.services import pipeline_service

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("", response_model=list[PipelineResponse])
async def list_pipelines(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await pipeline_service.list_pipelines(db, user.id)


@router.post("", response_model=PipelineResponse, status_code=201)
async def create_pipeline(
    body: CreatePipelineRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ops = [op.model_dump() for op in body.operations]
    return await pipeline_service.create_pipeline(db, user.id, body.name, ops, body.description)


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await pipeline_service.get_pipeline(db, pipeline_id, user.id)


@router.put("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: uuid.UUID,
    body: UpdatePipelineRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ops = [op.model_dump() for op in body.operations] if body.operations else None
    return await pipeline_service.update_pipeline(db, pipeline_id, user.id, body.name, body.description, ops)


@router.delete("/{pipeline_id}", status_code=204)
async def delete_pipeline(
    pipeline_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await pipeline_service.delete_pipeline(db, pipeline_id, user.id)
```

- [ ] **Step 3: Create backend/app/api/v1/jobs.py**

```python
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.job import ExecuteJobRequest, ExecuteJobResponse, JobDetailResponse, JobResponse
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/execute", response_model=ExecuteJobResponse, status_code=202)
async def execute_job(
    body: ExecuteJobRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    operations = [op.model_dump() for op in body.operations]
    job = await job_service.create_and_execute_job(
        db, user.id, body.image_id, operations, body.pipeline_id,
    )
    return ExecuteJobResponse(job_id=job.id)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await job_service.list_jobs(db, user.id, limit, offset)


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await job_service.get_job(db, job_id, user.id)


@router.get("/{job_id}/steps/{step_number}/image")
async def get_step_image(
    job_id: uuid.UUID,
    step_number: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await job_service.get_job(db, job_id, user.id)
    for step in job.steps:
        if step.step_number == step_number and step.result_image_path:
            return FileResponse(step.result_image_path, media_type="image/png")
    from app.core.exceptions import NotFoundException
    raise NotFoundException("Step image")


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await job_service.delete_job(db, job_id, user.id)
```

- [ ] **Step 4: Create backend/app/api/v1/operations.py**

```python
from fastapi import APIRouter

from app.engine.registry import OperationRegistry
from app.schemas.operation import OperationListResponse

import app.engine.operations  # noqa: F401

router = APIRouter(prefix="/operations", tags=["operations"])


@router.get("", response_model=OperationListResponse)
async def list_operations():
    ops = OperationRegistry.list_operations()
    return OperationListResponse(operations=ops)
```

- [ ] **Step 5: Update backend/app/api/v1/router.py**

```python
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.images import router as images_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.operations import router as operations_router
from app.api.v1.pipelines import router as pipelines_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(images_router)
api_router.include_router(pipelines_router)
api_router.include_router(jobs_router)
api_router.include_router(operations_router)
```

- [ ] **Step 6: Verify all endpoints in Swagger**

```bash
docker compose restart backend
```

Open `http://localhost:8000/docs` — all routes should appear.

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "feat: API endpoints — images, pipelines, jobs, operations"
```

---

### Task 17: WebSocket for Job Progress

**Files:**
- Create: `backend/app/api/v1/websocket.py`
- Modify: `backend/app/api/v1/router.py`

- [ ] **Step 1: Create backend/app/api/v1/websocket.py**

```python
import asyncio
import json

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/jobs/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: str):
    await websocket.accept()

    r = aioredis.from_url(settings.REDIS_URL)
    pubsub = r.pubsub()
    channel = f"job:{job_id}:progress"

    try:
        await pubsub.subscribe(channel)

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)

                if data.get("status") in ("completed", "failed"):
                    break

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await r.aclose()
```

- [ ] **Step 2: Update backend/app/api/v1/router.py to include websocket**

```python
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.images import router as images_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.operations import router as operations_router
from app.api.v1.pipelines import router as pipelines_router
from app.api.v1.websocket import router as websocket_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(images_router)
api_router.include_router(pipelines_router)
api_router.include_router(jobs_router)
api_router.include_router(operations_router)
api_router.include_router(websocket_router)
```

- [ ] **Step 3: Add redis.asyncio to requirements.txt**

Add `redis[hiredis]` is already covered by `redis==5.3.0`. Just need to verify async support is included.

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: WebSocket endpoint for real-time job progress via Redis pub/sub"
```

---

## Phase 5: Frontend

### Task 18: React Project Setup

**Files:**
- Create: `frontend/` (via Vite CLI)
- Create: `frontend/Dockerfile`

- [ ] **Step 1: Create React app with Vite**

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

- [ ] **Step 2: Install dependencies**

```bash
cd frontend
npm install tailwindcss @tailwindcss/vite
npm install framer-motion zustand axios react-router-dom
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
npm install lucide-react clsx tailwind-merge
npm install -D @types/react-router-dom
```

- [ ] **Step 3: Configure Tailwind**

Update `frontend/src/index.css`:

```css
@import "tailwindcss";
```

Update `frontend/vite.config.ts`:

```typescript
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },
});
```

- [ ] **Step 4: Install shadcn/ui**

```bash
cd frontend
npx shadcn@latest init -d
npx shadcn@latest add button card input label toast sonner dialog dropdown-menu separator badge scroll-area slider select tabs avatar
```

- [ ] **Step 5: Create frontend/src/lib/utils.ts**

```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

- [ ] **Step 6: Create frontend/Dockerfile**

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
```

- [ ] **Step 7: Add frontend service to docker-compose.yml**

Add to docker-compose.yml services:

```yaml
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
```

- [ ] **Step 8: Verify frontend runs**

```bash
docker compose up -d frontend
```

Open `http://localhost:5173` — should show Vite React page.

- [ ] **Step 9: Commit**

```bash
git add .
git commit -m "feat: React frontend setup with Vite, Tailwind, shadcn/ui, Framer Motion"
```

---

### Task 19: Frontend Types + API Service Layer

**Files:**
- Create: `frontend/src/types/auth.ts`
- Create: `frontend/src/types/pipeline.ts`
- Create: `frontend/src/types/job.ts`
- Create: `frontend/src/types/operation.ts`
- Create: `frontend/src/services/api.ts`
- Create: `frontend/src/services/auth.ts`
- Create: `frontend/src/services/pipelines.ts`
- Create: `frontend/src/services/jobs.ts`
- Create: `frontend/src/services/images.ts`
- Create: `frontend/src/services/operations.ts`

- [ ] **Step 1: Create type definitions**

Create `frontend/src/types/auth.ts`:

```typescript
export interface User {
  id: string;
  name: string;
  email: string;
  email_verified: boolean;
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface MessageResponse {
  message: string;
}
```

Create `frontend/src/types/operation.ts`:

```typescript
export interface OperationParamSchema {
  type: string;
  min?: number;
  max?: number;
  default?: number | string;
  step?: number;
  label?: string;
  options?: (string | number)[];
}

export interface OperationDefinition {
  name: string;
  params: Record<string, OperationParamSchema>;
}

export interface PipelineOperation {
  id: string; // client-side unique ID for drag-and-drop
  type: string;
  params: Record<string, number | string>;
}
```

Create `frontend/src/types/pipeline.ts`:

```typescript
export interface Pipeline {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  operations: { type: string; params: Record<string, unknown> }[];
  created_at: string;
  updated_at: string;
}

export interface CreatePipelineRequest {
  name: string;
  description?: string;
  operations: { type: string; params: Record<string, unknown> }[];
}
```

Create `frontend/src/types/job.ts`:

```typescript
export interface JobStep {
  id: string;
  step_number: number;
  operation_type: string;
  operation_params: Record<string, unknown>;
  result_image_path: string | null;
  processing_time_ms: number | null;
  status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
}

export interface Job {
  id: string;
  user_id: string;
  pipeline_id: string | null;
  image_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  current_step: number;
  total_steps: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  steps?: JobStep[];
}

export interface JobProgress {
  job_id: string;
  step?: number;
  total?: number;
  operation?: string;
  result_path?: string;
  status: "processing" | "completed" | "failed";
  error?: string;
}
```

- [ ] **Step 2: Create API service layer**

Create `frontend/src/services/api.ts`:

```typescript
import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        await axios.post("/api/v1/auth/refresh", {}, { withCredentials: true });
        return api(originalRequest);
      } catch {
        window.location.href = "/login";
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

Create `frontend/src/services/auth.ts`:

```typescript
import type { LoginRequest, MessageResponse, RegisterRequest, TokenResponse, User } from "@/types/auth";
import api from "./api";

export const authService = {
  register: (data: RegisterRequest) => api.post<User>("/auth/register", data).then((r) => r.data),
  login: (data: LoginRequest) => api.post<TokenResponse>("/auth/login", data).then((r) => r.data),
  refresh: () => api.post<TokenResponse>("/auth/refresh").then((r) => r.data),
  logout: () => api.post<MessageResponse>("/auth/logout").then((r) => r.data),
  logoutAll: () => api.post<MessageResponse>("/auth/logout-all").then((r) => r.data),
  me: () => api.get<User>("/auth/me").then((r) => r.data),
  verifyEmail: (code: string) => api.post<MessageResponse>("/auth/verify-email", { code }).then((r) => r.data),
  resendVerification: () => api.post<MessageResponse>("/auth/resend-verification").then((r) => r.data),
  forgotPassword: (email: string) => api.post<MessageResponse>("/auth/forgot-password", { email }).then((r) => r.data),
  resetPassword: (data: { email: string; token: string; new_password: string }) =>
    api.post<MessageResponse>("/auth/reset-password", data).then((r) => r.data),
};
```

Create `frontend/src/services/images.ts`:

```typescript
import api from "./api";

export interface UploadedImage {
  id: string;
  filename: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  width: number;
  height: number;
  created_at: string;
}

export const imageService = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<UploadedImage>("/images/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },
  getImageUrl: (imageId: string) => `/api/v1/images/file/${imageId}`,
  getStepImageUrl: (jobId: string, stepNumber: number) => `/api/v1/jobs/${jobId}/steps/${stepNumber}/image`,
  delete: (imageId: string) => api.delete(`/images/${imageId}`),
};
```

Create `frontend/src/services/pipelines.ts`:

```typescript
import type { CreatePipelineRequest, Pipeline } from "@/types/pipeline";
import api from "./api";

export const pipelineService = {
  list: () => api.get<Pipeline[]>("/pipelines").then((r) => r.data),
  get: (id: string) => api.get<Pipeline>(`/pipelines/${id}`).then((r) => r.data),
  create: (data: CreatePipelineRequest) => api.post<Pipeline>("/pipelines", data).then((r) => r.data),
  update: (id: string, data: Partial<CreatePipelineRequest>) => api.put<Pipeline>(`/pipelines/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/pipelines/${id}`),
};
```

Create `frontend/src/services/jobs.ts`:

```typescript
import type { Job } from "@/types/job";
import api from "./api";

export interface ExecuteJobRequest {
  image_id: string;
  pipeline_id?: string;
  operations: { type: string; params: Record<string, unknown> }[];
}

export const jobService = {
  execute: (data: ExecuteJobRequest) => api.post<{ job_id: string }>("/jobs/execute", data).then((r) => r.data),
  list: (limit = 50, offset = 0) => api.get<Job[]>(`/jobs?limit=${limit}&offset=${offset}`).then((r) => r.data),
  get: (id: string) => api.get<Job>(`/jobs/${id}`).then((r) => r.data),
  delete: (id: string) => api.delete(`/jobs/${id}`),
};
```

Create `frontend/src/services/operations.ts`:

```typescript
import type { OperationDefinition } from "@/types/operation";
import api from "./api";

export const operationService = {
  list: () => api.get<{ operations: OperationDefinition[] }>("/operations").then((r) => r.data.operations),
};
```

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: frontend types and API service layer for auth, images, pipelines, jobs, operations"
```

---

### Task 20: Zustand Stores

**Files:**
- Create: `frontend/src/stores/authStore.ts`
- Create: `frontend/src/stores/editorStore.ts`
- Create: `frontend/src/stores/themeStore.ts`

- [ ] **Step 1: Create auth store**

Create `frontend/src/stores/authStore.ts`:

```typescript
import type { User } from "@/types/auth";
import { authService } from "@/services/auth";
import { create } from "zustand";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (email, password) => {
    await authService.login({ email, password });
    const user = await authService.me();
    set({ user, isAuthenticated: true });
  },

  register: async (name, email, password) => {
    await authService.register({ name, email, password });
    const user = await authService.me();
    set({ user, isAuthenticated: true });
  },

  logout: async () => {
    await authService.logout();
    set({ user: null, isAuthenticated: false });
  },

  fetchUser: async () => {
    try {
      const user = await authService.me();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  setUser: (user) => set({ user, isAuthenticated: !!user }),
}));
```

- [ ] **Step 2: Create editor store**

Create `frontend/src/stores/editorStore.ts`:

```typescript
import type { OperationDefinition, PipelineOperation } from "@/types/operation";
import { create } from "zustand";

interface EditorState {
  operations: PipelineOperation[];
  availableOperations: OperationDefinition[];
  selectedStepId: string | null;
  uploadedImageId: string | null;
  uploadedImageUrl: string | null;
  jobId: string | null;
  isExecuting: boolean;
  stepPreviews: Record<number, string>; // step_number -> image URL

  setAvailableOperations: (ops: OperationDefinition[]) => void;
  addOperation: (type: string, defaults: Record<string, number | string>) => void;
  removeOperation: (id: string) => void;
  reorderOperations: (operations: PipelineOperation[]) => void;
  updateOperationParams: (id: string, params: Record<string, number | string>) => void;
  selectStep: (id: string | null) => void;
  setUploadedImage: (id: string, url: string) => void;
  setJobId: (id: string | null) => void;
  setIsExecuting: (v: boolean) => void;
  setStepPreview: (stepNumber: number, url: string) => void;
  clearStepPreviews: () => void;
  reset: () => void;
}

let nextId = 0;

export const useEditorStore = create<EditorState>((set) => ({
  operations: [],
  availableOperations: [],
  selectedStepId: null,
  uploadedImageId: null,
  uploadedImageUrl: null,
  jobId: null,
  isExecuting: false,
  stepPreviews: {},

  setAvailableOperations: (ops) => set({ availableOperations: ops }),

  addOperation: (type, defaults) =>
    set((state) => ({
      operations: [
        ...state.operations,
        { id: `op-${++nextId}`, type, params: { ...defaults } },
      ],
    })),

  removeOperation: (id) =>
    set((state) => ({
      operations: state.operations.filter((op) => op.id !== id),
      selectedStepId: state.selectedStepId === id ? null : state.selectedStepId,
    })),

  reorderOperations: (operations) => set({ operations }),

  updateOperationParams: (id, params) =>
    set((state) => ({
      operations: state.operations.map((op) =>
        op.id === id ? { ...op, params: { ...op.params, ...params } } : op
      ),
    })),

  selectStep: (id) => set({ selectedStepId: id }),

  setUploadedImage: (id, url) => set({ uploadedImageId: id, uploadedImageUrl: url }),

  setJobId: (id) => set({ jobId: id }),
  setIsExecuting: (v) => set({ isExecuting: v }),

  setStepPreview: (stepNumber, url) =>
    set((state) => ({
      stepPreviews: { ...state.stepPreviews, [stepNumber]: url },
    })),

  clearStepPreviews: () => set({ stepPreviews: {} }),

  reset: () =>
    set({
      operations: [],
      selectedStepId: null,
      uploadedImageId: null,
      uploadedImageUrl: null,
      jobId: null,
      isExecuting: false,
      stepPreviews: {},
    }),
}));
```

- [ ] **Step 3: Create theme store**

Create `frontend/src/stores/themeStore.ts`:

```typescript
import { create } from "zustand";
import { persist } from "zustand/middleware";

type Theme = "dark" | "light";

interface ThemeState {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "dark",
      toggleTheme: () =>
        set((state) => {
          const newTheme = state.theme === "dark" ? "light" : "dark";
          document.documentElement.classList.toggle("dark", newTheme === "dark");
          return { theme: newTheme };
        }),
      setTheme: (theme) => {
        document.documentElement.classList.toggle("dark", theme === "dark");
        set({ theme });
      },
    }),
    { name: "theme-storage" }
  )
);
```

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: Zustand stores — auth, editor, theme with persistence"
```

---

### Task 21: WebSocket Hook

**Files:**
- Create: `frontend/src/hooks/useWebSocket.ts`

- [ ] **Step 1: Create useWebSocket hook**

Create `frontend/src/hooks/useWebSocket.ts`:

```typescript
import type { JobProgress } from "@/types/job";
import { useCallback, useEffect, useRef } from "react";

interface UseWebSocketOptions {
  jobId: string | null;
  onProgress: (data: JobProgress) => void;
  onComplete: (data: JobProgress) => void;
  onError: (data: JobProgress) => void;
}

export function useWebSocket({ jobId, onProgress, onComplete, onError }: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!jobId) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/ws/jobs/${jobId}`);

    ws.onmessage = (event) => {
      const data: JobProgress = JSON.parse(event.data);

      if (data.status === "completed") {
        onComplete(data);
        ws.close();
      } else if (data.status === "failed") {
        onError(data);
        ws.close();
      } else {
        onProgress(data);
      }
    };

    ws.onerror = () => {
      onError({ job_id: jobId, status: "failed", error: "WebSocket connection failed" });
    };

    wsRef.current = ws;
  }, [jobId, onProgress, onComplete, onError]);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  useEffect(() => {
    connect();
    return disconnect;
  }, [connect, disconnect]);

  return { disconnect };
}
```

- [ ] **Step 2: Commit**

```bash
git add .
git commit -m "feat: useWebSocket hook for real-time job progress"
```

---

### Task 22: Layout + Auth Pages

**Files:**
- Create: `frontend/src/components/layout/AppLayout.tsx`
- Create: `frontend/src/components/layout/Header.tsx`
- Create: `frontend/src/components/layout/ThemeToggle.tsx`
- Create: `frontend/src/components/layout/ProtectedRoute.tsx`
- Create: `frontend/src/pages/LoginPage.tsx`
- Create: `frontend/src/pages/RegisterPage.tsx`
- Create: `frontend/src/App.tsx`

- [ ] **Step 1: Create ThemeToggle**

Create `frontend/src/components/layout/ThemeToggle.tsx`:

```tsx
import { Button } from "@/components/ui/button";
import { useThemeStore } from "@/stores/themeStore";
import { Moon, Sun } from "lucide-react";

export function ThemeToggle() {
  const { theme, toggleTheme } = useThemeStore();

  return (
    <Button variant="ghost" size="icon" onClick={toggleTheme}>
      {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </Button>
  );
}
```

- [ ] **Step 2: Create Header**

Create `frontend/src/components/layout/Header.tsx`:

```tsx
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { useAuthStore } from "@/stores/authStore";
import { ImageIcon, LogOut } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

export function Header() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <ImageIcon className="h-5 w-5 text-primary" />
          <span>Image Pipeline</span>
        </Link>

        <nav className="flex items-center gap-4">
          <Link to="/editor">
            <Button variant="ghost" size="sm">Editor</Button>
          </Link>
          <Link to="/jobs">
            <Button variant="ghost" size="sm">History</Button>
          </Link>
          <ThemeToggle />
          {user && (
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          )}
        </nav>
      </div>
    </header>
  );
}
```

- [ ] **Step 3: Create ProtectedRoute**

Create `frontend/src/components/layout/ProtectedRoute.tsx`:

```tsx
import { useAuthStore } from "@/stores/authStore";
import { Navigate } from "react-router-dom";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
```

- [ ] **Step 4: Create AppLayout**

Create `frontend/src/components/layout/AppLayout.tsx`:

```tsx
import { Header } from "@/components/layout/Header";
import { Outlet } from "react-router-dom";

export function AppLayout() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main>
        <Outlet />
      </main>
    </div>
  );
}
```

- [ ] **Step 5: Create LoginPage**

Create `frontend/src/pages/LoginPage.tsx`:

```tsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/stores/authStore";
import { motion } from "framer-motion";
import { ImageIcon, Loader2 } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <Card className="w-[400px]">
          <CardHeader className="text-center">
            <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <ImageIcon className="h-6 w-6 text-primary" />
            </div>
            <CardTitle className="text-2xl">Welcome back</CardTitle>
            <CardDescription>Sign in to your account</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                  {error}
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Sign in"}
              </Button>
              <div className="text-center text-sm text-muted-foreground">
                Don't have an account?{" "}
                <Link to="/register" className="text-primary hover:underline">
                  Sign up
                </Link>
              </div>
              <div className="text-center">
                <Link to="/forgot-password" className="text-sm text-muted-foreground hover:underline">
                  Forgot password?
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 6: Create RegisterPage**

Create `frontend/src/pages/RegisterPage.tsx`:

```tsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/stores/authStore";
import { motion } from "framer-motion";
import { ImageIcon, Loader2 } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(name, email, password);
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <Card className="w-[400px]">
          <CardHeader className="text-center">
            <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <ImageIcon className="h-6 w-6 text-primary" />
            </div>
            <CardTitle className="text-2xl">Create account</CardTitle>
            <CardDescription>Get started with Image Pipeline</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                  {error}
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  minLength={8}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Create account"}
              </Button>
              <div className="text-center text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link to="/login" className="text-primary hover:underline">
                  Sign in
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 7: Create App.tsx with routing**

Create `frontend/src/App.tsx`:

```tsx
import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { useAuthStore } from "@/stores/authStore";
import { useThemeStore } from "@/stores/themeStore";
import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";

function DashboardPage() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Dashboard</h1><p className="text-muted-foreground mt-2">Coming soon...</p></div>;
}

function EditorPage() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Pipeline Editor</h1><p className="text-muted-foreground mt-2">Coming soon...</p></div>;
}

function JobHistoryPage() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Job History</h1><p className="text-muted-foreground mt-2">Coming soon...</p></div>;
}

export default function App() {
  const { fetchUser } = useAuthStore();
  const { theme } = useThemeStore();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    fetchUser();
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/editor" element={<EditorPage />} />
          <Route path="/jobs" element={<JobHistoryPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

- [ ] **Step 8: Update frontend/src/main.tsx**

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 9: Verify login and register pages render**

```bash
docker compose restart frontend
```

Open `http://localhost:5173/login` — should see login card with animation.
Open `http://localhost:5173/register` — should see register card.

- [ ] **Step 10: Commit**

```bash
git add .
git commit -m "feat: layout, auth pages (login, register), routing with protected routes"
```

---

### Task 23: Pipeline Editor — Sidebar

**Files:**
- Create: `frontend/src/components/editor/Sidebar.tsx`
- Create: `frontend/src/components/editor/OperationCard.tsx`

- [ ] **Step 1: Create OperationCard (draggable from sidebar)**

Create `frontend/src/components/editor/OperationCard.tsx`:

```tsx
import { Card } from "@/components/ui/card";
import type { OperationDefinition } from "@/types/operation";
import { motion } from "framer-motion";
import {
  Contrast,
  Crop,
  Eye,
  Maximize,
  RotateCw,
  ScanLine,
  Shrink,
  Sparkles,
  Sun,
  Waves,
} from "lucide-react";

const OPERATION_ICONS: Record<string, React.ReactNode> = {
  grayscale: <Contrast className="h-4 w-4" />,
  blur: <Waves className="h-4 w-4" />,
  threshold: <ScanLine className="h-4 w-4" />,
  canny: <Eye className="h-4 w-4" />,
  dilate: <Maximize className="h-4 w-4" />,
  erode: <Shrink className="h-4 w-4" />,
  brightness: <Sun className="h-4 w-4" />,
  contrast: <Sparkles className="h-4 w-4" />,
  resize: <Crop className="h-4 w-4" />,
  rotate: <RotateCw className="h-4 w-4" />,
};

interface OperationCardProps {
  operation: OperationDefinition;
  onAdd: () => void;
}

export function OperationCard({ operation, onAdd }: OperationCardProps) {
  return (
    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
      <Card
        className="cursor-pointer p-3 transition-colors hover:bg-accent"
        onClick={onAdd}
      >
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            {OPERATION_ICONS[operation.name] || <Sparkles className="h-4 w-4" />}
          </div>
          <div>
            <p className="text-sm font-medium capitalize">{operation.name}</p>
            <p className="text-xs text-muted-foreground">
              {Object.keys(operation.params).length} params
            </p>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
```

- [ ] **Step 2: Create Sidebar**

Create `frontend/src/components/editor/Sidebar.tsx`:

```tsx
import { OperationCard } from "@/components/editor/OperationCard";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useEditorStore } from "@/stores/editorStore";

export function Sidebar() {
  const { availableOperations, addOperation } = useEditorStore();

  const handleAdd = (op: (typeof availableOperations)[0]) => {
    const defaults: Record<string, number | string> = {};
    for (const [key, schema] of Object.entries(op.params)) {
      if (schema.default !== undefined) {
        defaults[key] = schema.default;
      }
    }
    addOperation(op.name, defaults);
  };

  return (
    <div className="flex h-full w-64 flex-col border-r border-border bg-background">
      <div className="border-b border-border p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Operations
        </h2>
      </div>
      <ScrollArea className="flex-1 p-3">
        <div className="space-y-2">
          {availableOperations.map((op) => (
            <OperationCard key={op.name} operation={op} onAdd={() => handleAdd(op)} />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: editor sidebar with operation cards and click-to-add"
```

---

### Task 24: Pipeline Editor — Canvas (Drag & Drop)

**Files:**
- Create: `frontend/src/components/editor/StepCard.tsx`
- Create: `frontend/src/components/editor/Canvas.tsx`

- [ ] **Step 1: Create StepCard**

Create `frontend/src/components/editor/StepCard.tsx`:

```tsx
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useEditorStore } from "@/stores/editorStore";
import type { PipelineOperation } from "@/types/operation";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { motion } from "framer-motion";
import { GripVertical, Trash2 } from "lucide-react";

interface StepCardProps {
  operation: PipelineOperation;
  index: number;
}

export function StepCard({ operation, index }: StepCardProps) {
  const { selectedStepId, selectStep, removeOperation, stepPreviews, isExecuting } = useEditorStore();
  const isSelected = selectedStepId === operation.id;

  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: operation.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const hasPreview = stepPreviews[index + 1] !== undefined;

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className={`flex items-center gap-3 p-3 cursor-pointer transition-all ${
          isSelected ? "ring-2 ring-primary border-primary" : "hover:border-primary/50"
        }`}
        onClick={() => selectStep(operation.id)}
      >
        <button
          className="cursor-grab text-muted-foreground hover:text-foreground"
          {...attributes}
          {...listeners}
        >
          <GripVertical className="h-4 w-4" />
        </button>

        <Badge variant="outline" className="font-mono text-xs">
          {index + 1}
        </Badge>

        <span className="flex-1 text-sm font-medium capitalize">{operation.type}</span>

        {hasPreview && (
          <div className="h-2 w-2 rounded-full bg-green-500" />
        )}

        {isExecuting && !hasPreview && (
          <div className="h-2 w-2 animate-pulse rounded-full bg-yellow-500" />
        )}

        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={(e) => {
            e.stopPropagation();
            removeOperation(operation.id);
          }}
        >
          <Trash2 className="h-3 w-3" />
        </Button>
      </Card>
    </motion.div>
  );
}
```

- [ ] **Step 2: Create Canvas**

Create `frontend/src/components/editor/Canvas.tsx`:

```tsx
import { StepCard } from "@/components/editor/StepCard";
import { Button } from "@/components/ui/button";
import { useEditorStore } from "@/stores/editorStore";
import { imageService } from "@/services/images";
import { jobService } from "@/services/jobs";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  arrayMove,
} from "@dnd-kit/sortable";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, Play, Save, Upload } from "lucide-react";
import { useCallback, useRef } from "react";

interface CanvasProps {
  onExecute: (jobId: string) => void;
}

export function Canvas({ onExecute }: CanvasProps) {
  const {
    operations,
    reorderOperations,
    uploadedImageId,
    uploadedImageUrl,
    setUploadedImage,
    isExecuting,
    setIsExecuting,
    clearStepPreviews,
  } = useEditorStore();

  const fileInputRef = useRef<HTMLInputElement>(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = operations.findIndex((op) => op.id === active.id);
      const newIndex = operations.findIndex((op) => op.id === over.id);
      reorderOperations(arrayMove(operations, oldIndex, newIndex));
    }
  };

  const handleUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const image = await imageService.upload(file);
      setUploadedImage(image.id, imageService.getImageUrl(image.id));
    } catch (err) {
      console.error("Upload failed:", err);
    }
  }, [setUploadedImage]);

  const handleExecute = async () => {
    if (!uploadedImageId || operations.length === 0) return;

    setIsExecuting(true);
    clearStepPreviews();

    try {
      const { job_id } = await jobService.execute({
        image_id: uploadedImageId,
        operations: operations.map((op) => ({ type: op.type, params: op.params })),
      });
      onExecute(job_id);
    } catch (err) {
      console.error("Execute failed:", err);
      setIsExecuting(false);
    }
  };

  return (
    <div className="flex flex-1 flex-col">
      <div className="flex items-center justify-between border-b border-border p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Pipeline
        </h2>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleExecute} disabled={isExecuting || !uploadedImageId || operations.length === 0}>
            {isExecuting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
            Execute
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {/* Upload area */}
        <motion.div
          className={`mb-4 rounded-lg border-2 border-dashed p-4 text-center transition-colors ${
            uploadedImageUrl ? "border-primary/30 bg-primary/5" : "border-border hover:border-primary/50"
          }`}
          whileHover={{ scale: uploadedImageUrl ? 1 : 1.01 }}
        >
          {uploadedImageUrl ? (
            <div className="flex items-center gap-3">
              <img
                src={uploadedImageUrl}
                alt="Uploaded"
                className="h-16 w-16 rounded-md object-cover"
              />
              <div className="flex-1 text-left">
                <p className="text-sm font-medium">Image uploaded</p>
                <Button
                  variant="link"
                  size="sm"
                  className="h-auto p-0"
                  onClick={() => fileInputRef.current?.click()}
                >
                  Change image
                </Button>
              </div>
            </div>
          ) : (
            <button
              className="flex w-full flex-col items-center gap-2 py-4"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="h-8 w-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Click to upload an image</p>
            </button>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/bmp,image/tiff"
            className="hidden"
            onChange={handleUpload}
          />
        </motion.div>

        {/* Pipeline steps */}
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={operations.map((op) => op.id)} strategy={verticalListSortingStrategy}>
            <div className="space-y-2">
              <AnimatePresence>
                {operations.map((op, index) => (
                  <StepCard key={op.id} operation={op} index={index} />
                ))}
              </AnimatePresence>
            </div>
          </SortableContext>
        </DndContext>

        {operations.length === 0 && (
          <p className="mt-8 text-center text-sm text-muted-foreground">
            Click operations on the sidebar to add them to your pipeline
          </p>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: editor canvas with drag-and-drop reordering, image upload, and execute"
```

---

### Task 25: Pipeline Editor — Preview Panel + Parameter Controls

**Files:**
- Create: `frontend/src/components/editor/ParameterControls.tsx`
- Create: `frontend/src/components/editor/Preview.tsx`
- Create: `frontend/src/components/editor/ProgressOverlay.tsx`

- [ ] **Step 1: Create ParameterControls**

Create `frontend/src/components/editor/ParameterControls.tsx`:

```tsx
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useEditorStore } from "@/stores/editorStore";
import type { OperationParamSchema, PipelineOperation } from "@/types/operation";

interface ParameterControlsProps {
  operation: PipelineOperation;
}

export function ParameterControls({ operation }: ParameterControlsProps) {
  const { availableOperations, updateOperationParams } = useEditorStore();
  const opDef = availableOperations.find((o) => o.name === operation.type);

  if (!opDef || Object.keys(opDef.params).length === 0) {
    return <p className="text-sm text-muted-foreground">No parameters</p>;
  }

  const handleChange = (key: string, value: number | string) => {
    updateOperationParams(operation.id, { [key]: value });
  };

  return (
    <div className="space-y-4">
      {Object.entries(opDef.params).map(([key, schema]) => (
        <ParameterField
          key={key}
          name={key}
          schema={schema}
          value={operation.params[key]}
          onChange={(v) => handleChange(key, v)}
        />
      ))}
    </div>
  );
}

interface ParameterFieldProps {
  name: string;
  schema: OperationParamSchema;
  value: number | string | undefined;
  onChange: (value: number | string) => void;
}

function ParameterField({ name, schema, value, onChange }: ParameterFieldProps) {
  const label = schema.label || name;

  if (schema.type === "select" && schema.options) {
    return (
      <div className="space-y-2">
        <Label className="text-xs">{label}</Label>
        <Select value={String(value ?? schema.default)} onValueChange={(v) => onChange(isNaN(Number(v)) ? v : Number(v))}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {schema.options.map((opt) => (
              <SelectItem key={String(opt)} value={String(opt)}>
                {String(opt)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    );
  }

  if ((schema.type === "int" || schema.type === "float") && schema.min !== undefined && schema.max !== undefined) {
    const numValue = Number(value ?? schema.default ?? schema.min);
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label className="text-xs">{label}</Label>
          <span className="text-xs text-muted-foreground">{numValue}</span>
        </div>
        <Slider
          min={schema.min}
          max={schema.max}
          step={schema.step || (schema.type === "float" ? 0.1 : 1)}
          value={[numValue]}
          onValueChange={([v]) => onChange(v)}
        />
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <Label className="text-xs">{label}</Label>
      <Input
        type="number"
        value={value ?? schema.default ?? ""}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </div>
  );
}
```

- [ ] **Step 2: Create ProgressOverlay**

Create `frontend/src/components/editor/ProgressOverlay.tsx`:

```tsx
import { useEditorStore } from "@/stores/editorStore";
import { motion } from "framer-motion";

export function ProgressOverlay() {
  const { isExecuting, operations, stepPreviews } = useEditorStore();

  if (!isExecuting) return null;

  const completedSteps = Object.keys(stepPreviews).length;
  const totalSteps = operations.length;
  const progress = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  return (
    <div className="absolute inset-x-0 bottom-0 border-t border-border bg-background/95 p-4 backdrop-blur">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">
          Processing step {completedSteps}/{totalSteps}
        </span>
        <span className="font-mono text-xs">{Math.round(progress)}%</span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-secondary">
        <motion.div
          className="h-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create Preview**

Create `frontend/src/components/editor/Preview.tsx`:

```tsx
import { ParameterControls } from "@/components/editor/ParameterControls";
import { Separator } from "@/components/ui/separator";
import { useEditorStore } from "@/stores/editorStore";
import { motion, AnimatePresence } from "framer-motion";

export function Preview() {
  const { operations, selectedStepId, stepPreviews, uploadedImageUrl } = useEditorStore();

  const selectedOp = operations.find((op) => op.id === selectedStepId);
  const selectedIndex = operations.findIndex((op) => op.id === selectedStepId);
  const previewUrl = selectedIndex >= 0 ? stepPreviews[selectedIndex + 1] : null;
  const imageToShow = previewUrl || uploadedImageUrl;

  return (
    <div className="flex h-full w-80 flex-col border-l border-border bg-background">
      <div className="border-b border-border p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Preview
        </h2>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {/* Image preview */}
        <div className="mb-4 overflow-hidden rounded-lg border border-border bg-muted/30">
          <AnimatePresence mode="wait">
            {imageToShow ? (
              <motion.img
                key={imageToShow}
                src={imageToShow}
                alt="Preview"
                className="w-full object-contain"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              />
            ) : (
              <motion.div
                className="flex h-48 items-center justify-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <p className="text-sm text-muted-foreground">No preview available</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Parameters */}
        {selectedOp && (
          <>
            <Separator className="my-4" />
            <div>
              <h3 className="mb-3 text-sm font-medium capitalize">{selectedOp.type} Parameters</h3>
              <ParameterControls operation={selectedOp} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: preview panel with parameter controls, sliders, and progress overlay"
```

---

### Task 26: Pipeline Editor Page (Assemble Everything)

**Files:**
- Create: `frontend/src/pages/EditorPage.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Create EditorPage**

Create `frontend/src/pages/EditorPage.tsx`:

```tsx
import { Canvas } from "@/components/editor/Canvas";
import { Preview } from "@/components/editor/Preview";
import { ProgressOverlay } from "@/components/editor/ProgressOverlay";
import { Sidebar } from "@/components/editor/Sidebar";
import { useEditorStore } from "@/stores/editorStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { operationService } from "@/services/operations";
import { imageService } from "@/services/images";
import type { JobProgress } from "@/types/job";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

export function EditorPage() {
  const {
    setAvailableOperations,
    setJobId,
    setIsExecuting,
    setStepPreview,
    jobId,
  } = useEditorStore();

  useEffect(() => {
    operationService.list().then(setAvailableOperations);
  }, [setAvailableOperations]);

  const handleProgress = useCallback(
    (data: JobProgress) => {
      if (data.step && data.result_path) {
        const url = imageService.getStepImageUrl(data.job_id, data.step);
        setStepPreview(data.step, url);
      }
    },
    [setStepPreview]
  );

  const handleComplete = useCallback(
    (_data: JobProgress) => {
      setIsExecuting(false);
      toast.success("Pipeline executed successfully!");
    },
    [setIsExecuting]
  );

  const handleError = useCallback(
    (data: JobProgress) => {
      setIsExecuting(false);
      toast.error(data.error || "Pipeline execution failed");
    },
    [setIsExecuting]
  );

  useWebSocket({
    jobId,
    onProgress: handleProgress,
    onComplete: handleComplete,
    onError: handleError,
  });

  const handleExecute = (newJobId: string) => {
    setJobId(newJobId);
  };

  return (
    <div className="relative flex h-[calc(100vh-3.5rem)]">
      <Sidebar />
      <Canvas onExecute={handleExecute} />
      <Preview />
      <ProgressOverlay />
    </div>
  );
}
```

- [ ] **Step 2: Update App.tsx — replace placeholder EditorPage**

In `frontend/src/App.tsx`, replace the placeholder `EditorPage` function and import the real one:

```tsx
import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { useAuthStore } from "@/stores/authStore";
import { useThemeStore } from "@/stores/themeStore";
import { Toaster } from "sonner";
import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { EditorPage } from "@/pages/EditorPage";

function DashboardPage() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Dashboard</h1><p className="text-muted-foreground mt-2">Coming soon...</p></div>;
}

function JobHistoryPage() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Job History</h1><p className="text-muted-foreground mt-2">Coming soon...</p></div>;
}

export default function App() {
  const { fetchUser } = useAuthStore();
  const { theme } = useThemeStore();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    fetchUser();
  }, []);

  return (
    <BrowserRouter>
      <Toaster position="bottom-right" theme="system" />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/editor" element={<EditorPage />} />
          <Route path="/jobs" element={<JobHistoryPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

- [ ] **Step 3: Verify the full editor flow**

```bash
docker compose up -d
```

1. Open `http://localhost:5173/register` — create an account
2. Navigate to `/editor`
3. Sidebar should list all 10 operations
4. Click operations to add to canvas
5. Drag to reorder
6. Upload an image
7. Click Execute
8. Watch WebSocket progress update previews in real time

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "feat: pipeline editor page — full integration of sidebar, canvas, preview, WebSocket progress"
```

---

### Task 27: Dashboard + Job History Pages

**Files:**
- Create: `frontend/src/pages/DashboardPage.tsx`
- Create: `frontend/src/pages/JobHistoryPage.tsx`
- Create: `frontend/src/pages/JobDetailPage.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Create DashboardPage**

Create `frontend/src/pages/DashboardPage.tsx`:

```tsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { pipelineService } from "@/services/pipelines";
import { jobService } from "@/services/jobs";
import type { Pipeline } from "@/types/pipeline";
import type { Job } from "@/types/job";
import { motion } from "framer-motion";
import { ArrowRight, ImageIcon, Layers, Zap } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export function DashboardPage() {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);

  useEffect(() => {
    pipelineService.list().then(setPipelines).catch(() => {});
    jobService.list(5).then(setJobs).catch(() => {});
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Link to="/editor">
          <Button>
            <Zap className="mr-2 h-4 w-4" /> New Pipeline
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Saved Pipelines</CardTitle>
              <Layers className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">{pipelines.length}</div></CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Jobs</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">{jobs.length}</div></CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Completed</CardTitle>
              <ImageIcon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent><div className="text-2xl font-bold">{jobs.filter((j) => j.status === "completed").length}</div></CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Jobs */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Recent Jobs</h2>
          <Link to="/jobs"><Button variant="ghost" size="sm">View all <ArrowRight className="ml-1 h-3 w-3" /></Button></Link>
        </div>
        <div className="space-y-2">
          {jobs.map((job) => (
            <Link key={job.id} to={`/jobs/${job.id}`}>
              <Card className="p-3 hover:bg-accent transition-colors cursor-pointer">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`h-2 w-2 rounded-full ${
                      job.status === "completed" ? "bg-green-500" :
                      job.status === "failed" ? "bg-red-500" :
                      job.status === "processing" ? "bg-yellow-500" : "bg-gray-500"
                    }`} />
                    <span className="text-sm font-mono">{job.id.slice(0, 8)}...</span>
                    <span className="text-sm text-muted-foreground">{job.total_steps} steps</span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(job.created_at).toLocaleDateString()}
                  </span>
                </div>
              </Card>
            </Link>
          ))}
          {jobs.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-8">No jobs yet. Start by creating a pipeline!</p>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create JobHistoryPage**

Create `frontend/src/pages/JobHistoryPage.tsx`:

```tsx
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { jobService } from "@/services/jobs";
import type { Job } from "@/types/job";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const STATUS_COLORS: Record<string, string> = {
  completed: "bg-green-500/10 text-green-500",
  failed: "bg-red-500/10 text-red-500",
  processing: "bg-yellow-500/10 text-yellow-500",
  pending: "bg-gray-500/10 text-gray-500",
};

export function JobHistoryPage() {
  const [jobs, setJobs] = useState<Job[]>([]);

  useEffect(() => {
    jobService.list().then(setJobs).catch(() => {});
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Job History</h1>
      <div className="space-y-2">
        {jobs.map((job, i) => (
          <motion.div
            key={job.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Link to={`/jobs/${job.id}`}>
              <Card className="p-4 hover:bg-accent transition-colors cursor-pointer">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-sm">{job.id.slice(0, 8)}</span>
                    <Badge variant="outline" className={STATUS_COLORS[job.status]}>
                      {job.status}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {job.current_step}/{job.total_steps} steps
                    </span>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {new Date(job.created_at).toLocaleString()}
                  </span>
                </div>
              </Card>
            </Link>
          </motion.div>
        ))}
        {jobs.length === 0 && (
          <p className="text-center text-muted-foreground py-12">No jobs yet</p>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create JobDetailPage**

Create `frontend/src/pages/JobDetailPage.tsx`:

```tsx
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { jobService } from "@/services/jobs";
import { imageService } from "@/services/images";
import type { Job } from "@/types/job";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";

export function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);

  useEffect(() => {
    if (id) jobService.get(id).then(setJob).catch(() => {});
  }, [id]);

  if (!job) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center gap-4">
        <Link to="/jobs">
          <Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button>
        </Link>
        <h1 className="text-2xl font-bold">Job {job.id.slice(0, 8)}</h1>
        <Badge variant="outline">{job.status}</Badge>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-4">
        {job.steps?.map((step, i) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="overflow-hidden">
              <div className="aspect-square bg-muted">
                {step.result_image_path ? (
                  <img
                    src={imageService.getStepImageUrl(job.id, step.step_number)}
                    alt={`Step ${step.step_number}`}
                    className="h-full w-full object-contain"
                  />
                ) : (
                  <div className="flex h-full items-center justify-center text-muted-foreground text-sm">
                    No result
                  </div>
                )}
              </div>
              <div className="p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium capitalize">
                    {step.step_number}. {step.operation_type}
                  </span>
                  {step.processing_time_ms !== null && (
                    <span className="text-xs text-muted-foreground">{step.processing_time_ms}ms</span>
                  )}
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Update App.tsx with real pages and job detail route**

```tsx
import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { useAuthStore } from "@/stores/authStore";
import { useThemeStore } from "@/stores/themeStore";
import { Toaster } from "sonner";
import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { EditorPage } from "@/pages/EditorPage";
import { JobHistoryPage } from "@/pages/JobHistoryPage";
import { JobDetailPage } from "@/pages/JobDetailPage";

export default function App() {
  const { fetchUser } = useAuthStore();
  const { theme } = useThemeStore();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    fetchUser();
  }, []);

  return (
    <BrowserRouter>
      <Toaster position="bottom-right" theme="system" />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/editor" element={<EditorPage />} />
          <Route path="/jobs" element={<JobHistoryPage />} />
          <Route path="/jobs/:id" element={<JobDetailPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: dashboard, job history, and job detail pages with animations"
```

---

## Phase 6: Final Integration

### Task 28: End-to-End Smoke Test

- [ ] **Step 1: Start all services**

```bash
docker compose up -d --build
```

- [ ] **Step 2: Run backend tests**

```bash
docker compose exec backend pytest -v
```

Expected: all tests PASS

- [ ] **Step 3: Manual E2E test**

1. Open `http://localhost:5173/register` — create account
2. Navigate to `/editor`
3. Upload a test image
4. Add operations: grayscale → blur (kernel 5) → canny (100, 200)
5. Click Execute
6. Observe WebSocket progress + intermediate previews
7. Navigate to `/jobs` — see the completed job
8. Click job — see all step results in grid

- [ ] **Step 4: Commit any fixes**

```bash
git add .
git commit -m "fix: integration fixes from e2e smoke test"
```

- [ ] **Step 5: Final commit**

```bash
git add .
git commit -m "feat: image pipeline processing system — MVP complete"
```
