#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# .env vars (SECRET_KEY, DATABASE_URL vb.) otomatik yüklenir.
ENV_FILE="${PROJECT_ROOT}/.env"
if [[ -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

UVICORN_BIN="${UVICORN_BIN:-uvicorn}"
APP_MODULE="${APP_MODULE:-app.main:app}"
APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8000}"
APP_RELOAD="${APP_RELOAD:-true}"

EXTRA_ARGS=()
if [[ "${APP_RELOAD}" == "true" ]]; then
  EXTRA_ARGS+=("--reload")
fi

exec "${UVICORN_BIN}" "${APP_MODULE}" --host "${APP_HOST}" --port "${APP_PORT}" "${EXTRA_ARGS[@]}"
