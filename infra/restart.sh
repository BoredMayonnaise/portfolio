#!/usr/bin/env bash
# Recreate using the existing image to pick up .env changes. Deploy for code changes.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
compose up -d --no-deps --force-recreate web
for attempt in {1..30}; do
    if bash "${INFRA_DIR}/health.sh" >/dev/null 2>&1; then
        echo "Portfolio restarted; HTTP and stylesheet checks passed."
        exit 0
    fi
    sleep 2
done
compose logs --tail 60 web
exit 1
