# Image Pipeline Processing System — Design Spec

## Overview

Sistema fullstack para processamento de imagens via pipeline configuravel. O usuario envia uma imagem, monta uma sequencia de operacoes (pipeline) via interface drag-and-drop, executa de forma assincrona, e visualiza resultados intermediarios em tempo real.

## Stack

- **Frontend:** React + TypeScript + Tailwind CSS + Framer Motion + shadcn/ui
- **Backend:** FastAPI + SQLAlchemy + Alembic
- **Worker:** Celery + Redis (broker + result backend)
- **Database:** PostgreSQL
- **Storage:** Local filesystem (MVP), interface abstraida para S3 futuro
- **Auth:** JWT dual-token (access 15min + refresh 7d), bcrypt, httpOnly cookies
- **Realtime:** WebSocket (FastAPI nativo) + Redis pub/sub

---

## Architecture

```
React SPA
  |
  | REST + WebSocket
  v
FastAPI
  ├── Auth Module (JWT, register, login, logout, verify email, reset password)
  ├── Pipeline API (CRUD pipelines, execute, results)
  ├── WebSocket Server (job progress push)
  ├── Celery Worker
  │     └── Pipeline Engine
  │           └── OperationRegistry (grayscale, blur, threshold, canny, dilate, erode, brightness, contrast, resize, rotate)
  ├── PostgreSQL (users, pipelines, jobs)
  ├── Redis (celery broker, pub/sub progress)
  └── File Storage (uploads, intermediaries, results)
```

---

## Authentication

### Strategy

JWT dual-token com httpOnly cookies, seguindo o padrao do projeto gestao-restaurante adaptado para FastAPI.

### Features (MVP)

- Registro com email + senha
- Login com JWT (access token 15min, refresh token 7d)
- Refresh token rotation (revoga o anterior ao gerar novo)
- Logout (single device + all devices)
- Verificacao de email (codigo 6 digitos, 15min expiry)
- Reset de senha (token, 15min expiry)
- Account lockout (5 tentativas falhas = lock 15min)
- Rate limiting em endpoints sensiveis

### User Model

```
User:
  id: UUID (PK)
  name: string
  email: string (unique)
  password: string (bcrypt hash)
  email_verified: bool (default false)
  email_verification_token: string?
  email_verification_expires: datetime?
  password_reset_token: string?
  password_reset_expires: datetime?
  failed_login_attempts: int (default 0)
  locked_until: datetime?
  is_active: bool (default true)
  created_at: datetime
  updated_at: datetime

RefreshToken:
  id: UUID (PK)
  user_id: UUID (FK -> User)
  token_hash: string (unique, SHA-256)
  user_agent: string?
  ip_address: string?
  expires_at: datetime
  is_revoked: bool (default false)
  revoked_at: datetime?
  created_at: datetime
```

### Auth Routes

```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
POST /api/v1/auth/logout-all
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password
POST /api/v1/auth/verify-email
POST /api/v1/auth/resend-verification
GET  /api/v1/auth/me
```

---

## Pipeline Engine

### Operations (MVP)

| Operation   | Params                          | OpenCV Function                    |
|-------------|----------------------------------|------------------------------------|
| grayscale   | —                                | cv2.cvtColor(BGR2GRAY)             |
| blur        | kernel: int (odd, 1-31)         | cv2.GaussianBlur                   |
| threshold   | value: int (0-255), type: str   | cv2.threshold                      |
| canny       | threshold1: int, threshold2: int| cv2.Canny                          |
| dilate      | kernel: int, iterations: int    | cv2.dilate                         |
| erode       | kernel: int, iterations: int    | cv2.erode                          |
| brightness  | value: int (-100 to 100)        | cv2.convertScaleAbs (beta)         |
| contrast    | value: float (0.5 to 3.0)      | cv2.convertScaleAbs (alpha)        |
| resize      | width: int, height: int         | cv2.resize                         |
| rotate      | angle: int (90, 180, 270)       | cv2.rotate                         |

### Registry Pattern

```python
class OperationRegistry:
    _operations: dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, schema: dict):
        def decorator(func):
            cls._operations[name] = {"func": func, "schema": schema}
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Callable:
        return cls._operations[name]["func"]

    @classmethod
    def list_operations(cls) -> list:
        return [{"name": k, "params": v["schema"]} for k, v in cls._operations.items()]
```

### Pipeline Execution Flow

```
1. POST /api/v1/pipeline/execute {image_id, operations[]}
2. Server valida operacoes e cria Job record (status: pending)
3. Envia task para Celery: execute_pipeline.delay(job_id)
4. Retorna { job_id } ao frontend (202 Accepted)
5. Frontend conecta WebSocket: ws://api/v1/ws/jobs/{job_id}
6. Celery worker:
   a. Carrega imagem do storage
   b. Para cada operacao:
      - Executa via OperationRegistry
      - Salva imagem intermediaria no storage
      - Publica progresso no Redis pub/sub:
        { step: 2, total: 6, operation: "blur", preview_url: "/api/v1/files/xxx" }
   c. Marca Job como completed
7. WebSocket server escuta Redis pub/sub e faz push para o client
8. Frontend atualiza canvas com preview de cada etapa em tempo real
```

---

## Data Models

### Pipeline (saved templates)

```
Pipeline:
  id: UUID (PK)
  user_id: UUID (FK -> User)
  name: string
  description: string?
  operations: JSON  # [{ type, ...params }]
  created_at: datetime
  updated_at: datetime
```

### Job (execution instance)

```
Job:
  id: UUID (PK)
  user_id: UUID (FK -> User)
  pipeline_id: UUID? (FK -> Pipeline, nullable se ad-hoc)
  original_image_path: string
  status: enum (pending, processing, completed, failed)
  current_step: int (default 0)
  total_steps: int
  error_message: string?
  started_at: datetime?
  completed_at: datetime?
  created_at: datetime

JobStep:
  id: UUID (PK)
  job_id: UUID (FK -> Job)
  step_number: int
  operation_type: string
  operation_params: JSON
  result_image_path: string?
  processing_time_ms: int?
  status: enum (pending, processing, completed, failed)
  created_at: datetime
```

---

## File Storage

### Structure

```
storage/
  uploads/
    {user_id}/
      {image_id}.{ext}          # imagem original
  results/
    {job_id}/
      step_0_original.{ext}     # copia da original
      step_1_grayscale.png      # resultado etapa 1
      step_2_blur.png           # resultado etapa 2
      ...
      final.png                 # resultado final
```

### Upload endpoint

```
POST /api/v1/images/upload
  - multipart/form-data
  - max 10MB
  - formatos: jpg, jpeg, png, bmp, tiff
  - retorna { image_id, url, width, height }
```

---

## API Routes

### Images

```
POST   /api/v1/images/upload          # upload imagem
GET    /api/v1/images/{id}            # metadata da imagem
DELETE /api/v1/images/{id}            # deletar imagem
GET    /api/v1/files/{path}           # servir arquivo (imagem)
```

### Pipelines

```
GET    /api/v1/pipelines              # listar pipelines do usuario
POST   /api/v1/pipelines              # criar pipeline template
GET    /api/v1/pipelines/{id}         # detalhe
PUT    /api/v1/pipelines/{id}         # atualizar
DELETE /api/v1/pipelines/{id}         # deletar
```

### Jobs

```
POST   /api/v1/jobs/execute           # executar pipeline (retorna job_id)
GET    /api/v1/jobs                    # listar jobs do usuario
GET    /api/v1/jobs/{id}              # detalhe do job + steps
GET    /api/v1/jobs/{id}/steps        # listar steps com previews
DELETE /api/v1/jobs/{id}              # deletar job e arquivos
```

### Operations

```
GET    /api/v1/operations             # listar operacoes disponiveis + schemas
```

### WebSocket

```
WS     /api/v1/ws/jobs/{job_id}       # stream de progresso do job
```

---

## Frontend

### Pages

| Page               | Route              | Description                                    |
|--------------------|--------------------|------------------------------------------------|
| Login              | /login             | Email + senha                                  |
| Register           | /register          | Nome + email + senha                           |
| Verify Email       | /verify-email      | Input codigo 6 digitos                         |
| Forgot Password    | /forgot-password   | Input email                                    |
| Reset Password     | /reset-password    | Nova senha                                     |
| Dashboard          | /                  | Lista de pipelines salvos + jobs recentes      |
| Pipeline Editor    | /editor            | Sidebar + Canvas + Preview (pagina principal)  |
| Job History        | /jobs              | Lista de execucoes com status                  |
| Job Detail         | /jobs/:id          | Visualizar resultado completo de um job        |

### Pipeline Editor (pagina principal)

Layout em 3 colunas:

```
┌──────────────┬───────────────────────────────┬──────────────┐
│   Sidebar    │         Canvas                │   Preview    │
│              │                               │              │
│  Operacoes   │  [Upload] ──→ [Grayscale]     │  Imagem      │
│  disponiveis │      ──→ [Blur k=5]           │  do step     │
│              │      ──→ [Canny 100,200]      │  selecionado │
│  - Grayscale │      ──→ [Result]             │              │
│  - Blur      │                               │  Params do   │
│  - Threshold │  (drag-and-drop reorder)      │  step        │
│  - Canny     │  (click step = preview)       │  selecionado │
│  - Dilate    │                               │              │
│  - Erode     │                               │              │
│  - Brightness│  [Save Pipeline] [Execute]    │              │
│  - Contrast  │                               │              │
│  - Resize    │                               │              │
│  - Rotate    │                               │              │
└──────────────┴───────────────────────────────┴──────────────┘
```

**Interacao:**
- Drag da sidebar para o canvas adiciona operacao
- Drag entre steps no canvas reordena
- Click em um step mostra preview (imagem intermediaria) e params no painel direito
- Params editaveis em tempo real (sliders, inputs)
- Botao Execute envia para API, WebSocket atualiza previews em tempo real
- Animacoes com Framer Motion: entrada de steps, progresso, transicoes

### Visual Design

- Dark mode como padrao com toggle para light
- Paleta: tons de slate/zinc + accent color (indigo ou violet)
- Componentes shadcn/ui customizados
- Transicoes suaves entre estados (loading, processing, complete)
- Barra de progresso animada durante execucao
- Toast notifications para erros e sucesso

---

## Project Structure

```
backend/
  app/
    main.py                    # FastAPI app, middleware, CORS
    config.py                  # Settings (pydantic-settings)
    database.py                # SQLAlchemy engine + session
    models/
      user.py
      refresh_token.py
      pipeline.py
      job.py
      job_step.py
    schemas/                   # Pydantic DTOs
      auth.py
      pipeline.py
      job.py
      image.py
      operation.py
    api/
      v1/
        router.py              # Include all routers
        auth.py
        pipelines.py
        jobs.py
        images.py
        operations.py
        websocket.py
    services/
      auth_service.py
      token_service.py
      email_service.py
      pipeline_service.py
      job_service.py
      image_service.py
      storage_service.py
    engine/
      registry.py              # OperationRegistry
      executor.py              # PipelineExecutor
      operations/
        __init__.py
        color.py               # grayscale, brightness, contrast
        filter.py              # blur, threshold
        edge.py                # canny
        morphology.py          # dilate, erode
        transform.py           # resize, rotate
    workers/
      celery_app.py            # Celery config
      tasks.py                 # execute_pipeline task
    core/
      security.py              # JWT, bcrypt, password hashing
      dependencies.py          # FastAPI dependencies (get_db, get_current_user)
      exceptions.py            # Custom exceptions
      middleware.py            # Rate limiting, etc
    alembic/
      versions/
    alembic.ini
  requirements.txt
  Dockerfile

frontend/
  src/
    components/
      ui/                      # shadcn/ui components
      auth/                    # Login, Register, etc
      editor/
        Sidebar.tsx            # Lista de operacoes
        Canvas.tsx             # Pipeline visual
        Preview.tsx            # Preview + params
        OperationCard.tsx      # Card draggable
        ProgressBar.tsx        # Progresso do job
      layout/
        Header.tsx
        ThemeToggle.tsx
    pages/
      LoginPage.tsx
      RegisterPage.tsx
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
      api.ts                   # Axios/fetch config
      auth.ts
      pipeline.ts
      jobs.ts
      images.ts
    stores/
      authStore.ts             # Zustand
      pipelineStore.ts
      jobStore.ts
      themeStore.ts
    types/
      auth.ts
      pipeline.ts
      job.ts
      operation.ts
    lib/
      utils.ts
    App.tsx
    main.tsx
  tailwind.config.ts
  package.json
  Dockerfile

docker-compose.yml             # FastAPI + Celery + Redis + PostgreSQL + Frontend
```

---

## Infrastructure (Docker Compose)

```yaml
services:
  backend:     FastAPI (port 8000)
  worker:      Celery worker (same image, different command)
  redis:       Redis 7 (port 6379)
  postgres:    PostgreSQL 16 (port 5432)
  frontend:    React dev server (port 5173) / nginx em prod
```

---

## Non-functional Requirements

- Upload max: 10MB
- Formatos suportados: JPG, JPEG, PNG, BMP, TIFF
- Max operacoes por pipeline: 20
- Job timeout: 5 minutos
- Cleanup: jobs e arquivos > 7 dias deletados automaticamente (futuro)
- Senhas: bcrypt 12 rounds
- CORS: configuravel via env
