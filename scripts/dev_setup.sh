#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  echo "[dev-setup] Installing dependencies with uv"
  uv pip install -e .[dev,backend]
else
  echo "[dev-setup] uv not found; falling back to pip"
  python -m pip install --upgrade pip
  python -m pip install -e .[dev,backend]
fi

if [ -f .env.example ] && [ ! -f .env ]; then
  cp .env.example .env
  echo "[dev-setup] Created .env from template. Update keyring-backed secrets with 'python -m sync_service.secrets'."
fi

echo "[dev-setup] Done. Run 'uvicorn sync_service.main:app --reload' to start the API."
