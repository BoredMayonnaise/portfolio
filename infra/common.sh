#!/usr/bin/env bash
# Shared Docker Compose context; safe to invoke from any working directory.
set -euo pipefail
INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${INFRA_DIR}/.." && pwd)"
cd "${PROJECT_DIR}"
compose() { docker compose --project-directory "${PROJECT_DIR}" -f "${PROJECT_DIR}/docker-compose.yml" "$@"; }
