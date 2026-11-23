# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

TiCuida is a web app for online pre-triage and health-unit occupancy (lotação). It is the final project for "Programação Web Avançada – UVV" and has a single author. User-facing text, code identifiers, API error messages and docs are in Portuguese (pt-BR).

Sources of truth (read these before changing behavior):
- `docs/MVP_TiCuida.md`: scope (MoSCoW; F1–F7 are Must), priority rules (§5.4), entities (§8.3), endpoints (§8.4), non-functional requirements (§7).
- `docs/banco/schema.sql`: the physical model. The SQLAlchemy models mirror its tables, CHECK constraints and enum values. If you change a model, update schema.sql and the ER files (`modelo_fisico.*`) and generate a migration.

## Commands

The backend lives at the repo root (virtualenv `.venv`); the frontend lives in `frontend/`.

- Setup: `pip install -e ".[dev,test]"` (or `invoke install`), then `copy .env.example .env`, `flask db upgrade`, `flask seed`.
- Run the API: `flask run --debug` (port 5000; `.flaskenv` sets `FLASK_APP=app.py`).
- Run the frontend: `cd frontend && npm run dev` (port 5173; Vite proxies `/api` to 5000). Vite binds to `localhost`, which is IPv6 on Windows, so test with `localhost:5173`, not `127.0.0.1`.
- Tests: `pytest`. A single test: `pytest tests/test_auth.py::test_login_com_sucesso`. Coverage: `pytest --cov=ticuida`.
- Lint/format: `flake8 ticuida tests`, `black ticuida tests` (line length 100; `migrations/` and `frontend/` are excluded).
- New migration after model changes: `flask db migrate -m "..."`, then `flask db upgrade` (batch mode, so it works on SQLite).
- Frontend build check: `cd frontend && npm run build`.

## Architecture

The app is a modular monolith: a Flask REST API plus a Vue 3 SPA. The layout follows the class TaskFlow project.

- `ticuida/__init__.py` `create_app(config_class)`: config → `ext/*` `init_app` → `ext.db.register_models()` → `errors.init_app` → each domain's `init_app` (registers its blueprint) → CLI commands. Tests pass `TestConfig` (in-memory SQLite, fast password hashing, no log file).
- Each domain package (`auth`, `pacientes`, `triagem`, `unidades`, `encaminhamentos`) has `models.py`, `schemas.py` (Pydantic), `services.py` (business logic + queries; raises `APIError`) and `routes.py` (thin blueprint). `unidades` registers two blueprints: `/api/unidades` and `/api/convenios`. `core` holds `/api/health` and shared utilities.
- **Validation:** routes call `validar(Schema, obter_json())` from `core/validacao.py`. Pydantic errors become a 422 response `{"erro": ..., "campos": {campo: [msgs]}}` with Portuguese messages, and the frontend maps `campos` to form fields. Field validators raise `ValueError("mensagem em pt")`.
- **Errors:** `errors.py` makes every error (APIError, HTTPException, unexpected) return JSON `{"erro": ...}`.
- **Auth:** the JWT identity is `str(usuario.id)`, and the `jwt_auth` user loader exposes `current_user`. Use `@papel_requerido("paciente"|"operador")` from `auth/decorators.py`. An operator sees only their own `unidade_id`; another unit's records return 404, not 403 (LGPD).
- **Priority rules:** `triagem/regras.py` is pure Python (no Flask, no DB) and has its own unit tests. An emergencia triage can never become an encaminhamento.
- **Recommendation order** (`unidades/services.py`): open before closed, then lotação (baixa < media < alta < not informed), then Haversine distance. The current lotação is the latest `RegistroLotacao` row.
- **Status transitions** are defined in `encaminhamentos/models.py` `TRANSICOES`.
- **Timestamps** are stored in UTC. SQLite returns naive datetimes, so serialize them with `core.tempo.iso()`.
- **Logging:** use `logging.getLogger(__name__)` under the `ticuida` logger (console + `logs/ticuida.log`). Log IDs only, never CPF or symptoms.
- **Seed data** (`ticuida/seed.py`) is fictitious, idempotent, and also used by the test fixtures. Tests depend on its names, for example "Pronto Atendimento Praia da Costa" lotação alta, Cobilândia not accepting SaúdeMais, and the demo patient on SaúdeMais.
- **Frontend:** `src/services/api.js` (axios with the token, 401 → logout), `src/stores/sessao.js` (token + user in localStorage), and a router guard driven by `meta.papel` / `meta.visitante`. Views live in `src/views`, and labels and Bulma colors in `src/utils/formatos.js`.

## Grading rubric (delivery 23/11/2026; presentations 23 and 27/11)

Each of the 7 technical criteria is worth 1 point: Application Factory; modularization (blueprints); forms + server-side validation; frontend with a CSS framework and responsiveness; automated tests; ORM persistence and correct modeling; code quality (.env, logging, error handling, git history).

Deliverables: `GrupoX_TiCuida.zip` without `.venv/`, `__pycache__/` or `frontend/node_modules/`, plus a PDF with:
- title and members
- product description
- ER diagram
- code walkthrough
- architecture
- technologies
- how to run
- challenges
