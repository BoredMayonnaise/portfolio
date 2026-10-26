#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
case "${1:-}" in
    '') compose logs --tail 50 web ;;
    -f|--follow) compose logs --tail 50 -f web ;;
    *) echo "Usage: $0 [-f|--follow]" >&2; exit 2 ;;
esac
