# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Real estate rental platform for Changsha (长沙租房). Three-tier architecture:
- **Backend** — Flask app (Python), MySQL 8.0, JWT auth
- **Frontend** — Vue 3 + Vite + Element Plus + Pinia
- **AI Engine** — FastAPI-based RAG/LLM service (aliyun DashScope + LangChain)

Deployed via Docker Compose (backend + MySQL). Frontend runs locally during development.

## Architecture

### Backend (`backend/`) — Flask App Factory

```
backend/app/
├── factory.py          # create_app() — app factory, blueprint registration
├── main.py             # Entry point
├── core/               # Config, database, security, exceptions, response helpers
├── common/             # BaseModel, BaseRepository, pagination, dependencies (auth), file_upload, enums
├── container/          # Singleton DI wiring: repositories.py, services.py
└── modules/            # Feature modules (20 modules)
```

Each module follows: **router.py** (routes + Pydantic validation) → **service.py** (business logic) → **repository.py** (SQLAlchemy queries). Each module also has `model.py` (ORM) and `schema.py` (Pydantic).

**Modules:** user, auth, house, house_image, favorite, appointment, conversation, contract, bill, payment, repair, complaint, notification, news, operation_log, statistics, admin, ai, user_avatar

Key patterns:
- **Auth**: JWT (HS256), extracted via `get_required_current_user_id()` / `get_optional_current_user_id()` in `common/dependencies.py`
- **Response**: Unified `{code, message, data}`, helpers in `core/response.py`
- **Error handling**: `AppException` subclasses with numeric error codes in `core/exceptions.py`
- **DB session**: Per-request via `g.db`, managed in `core/database.py` (before_request / teardown_request)
- **DI**: Singleton pattern — services/repositories are module-level singletons wired in `container/services.py` and `container/repositories.py`
- **Config**: Environment-driven, classes in `core/config.py`, selected by `APP_ENV` env var

### Frontend (`frontend/`) — Vue 3 + Vite

- **Router**: Lazy-loaded routes in `src/router/index.js`, `createWebHistory`
- **State**: Pinia store in `src/stores/user.js` (auth state, login/register forms, countdowns)
- **API layer**: `src/utils/request.js` — Axios instance with token interceptor (reads from localStorage) and 401 handling
- **Proxy**: Vite dev server proxies `/api` → `http://127.0.0.1:8000` and `/uploads` → same
- **Mock**: Static mock data in `src/mock/` for dev without backend
- **Components**: Shared components in `src/components/` (Header, NavBar, HouseCard, LoginModal, ChatPopup, etc.)
- **Views**: Per-feature pages in `src/views/` (Home, HouseList, HouseDetail, Contracts, Bills, Repair, Admin, etc.)

### AI Engine (`ai-engine/`) — Separate FastAPI Service

RAG/LLM/OCR service using LangChain + aliyun DashScope (通义千问). Provides:
- Rental chat with RAG (house knowledge base)
- Session history management
- OCR for document processing
- Connected to backend via HTTP (`AI_ENGINE_BASE_URL` env var, default `http://ai-engine:9000`)

### Deployment (`deploy/`)

Docker Compose with two services:
- **mysql**: MySQL 8.0, port 3307, persistent volume `mysql_data`
- **backend**: Flask + gunicorn (4 workers, `--reload`), port 8000, bind-mounts `../backend:/app/backend` for hot reload

Shared bridge network `rental_ai_net` connects with ai-engine's compose.

## Key Commands

```bash
# Backend — start with Docker
docker compose -f deploy/docker-compose.yml up -d

# Backend — start directly (requires MySQL)
cd backend && pip install -r requirements.txt
cd backend && flask run --port 8000

# Backend — integration tests (require running API)
cd backend && pytest tests/ -v
cd backend && pytest tests/api/test_house_filter_flow.py -v

# Frontend — dev server (proxies /api to backend)
cd frontend && npm install && npm run dev

# DB migration
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "description"
```

## Test Approach

**Backend tests** are integration flow tests in `tests/api/` that hit a live backend via `requests`. Fixtures (`api_request`, `auth_headers`, `unique_suffix`) in `tests/api/conftest.py`. Response format verified: `{code: 0, message: "...", data: ...}`. Service-level unit tests also exist in `tests/service/`.

**Frontend** uses mock data in `src/mock/` — no frontend test framework is configured.

## Dependencies

- **Backend**: Flask 3.1, SQLAlchemy 2.0, PyJWT, PyMySQL, gunicorn, alembic, pydantic, pytest
- **Frontend**: Vue 3.5, Vue Router 5, Pinia 3, Element Plus 2.13, Axios, ECharts 6, Vite 8
- **AI Engine**: FastAPI, LangChain, ChatTongyi (DashScope), OCR libraries
