# market-watch-api

Backend-first Market Watch & Alerts API for personal watchlists and finance research workflows.

## Current status

This repo is currently at **Step 2: repo + development skeleton**.

In place now:

- FastAPI application entrypoint
- env-based configuration
- SQLAlchemy database scaffold
- `GET /health` endpoint
- pytest setup
- Ruff lint/format setup
- local PostgreSQL via Docker Compose

## V1 boundaries

Locked in `PROJECT_SCOPE.md`:

- assets: stocks and ETFs only
- alert types:
  - `price_above`
  - `price_below`
  - `pct_move_up_1d`
  - `pct_move_down_1d`
- market data cadence: every 15 minutes during US market hours on trading days
- deployment target: Render

## Quickstart

### 1. Create your local env file

```bash
cp .env.example .env