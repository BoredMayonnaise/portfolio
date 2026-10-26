#!/usr/bin/env bash
# Portfolio commands target the Docker service serving the application.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
COMMAND="${1:-help}"
case "$COMMAND" in
    deploy|docker-up) bash "${INFRA_DIR}/deploy.sh" ;;
    restart|reload) bash "${INFRA_DIR}/restart.sh" ;;
    status) bash "${INFRA_DIR}/status.sh" ;;
    logs) shift; bash "${INFRA_DIR}/logs.sh" "$@" ;;
    start) compose up -d --no-deps web ;;
    stop) compose stop web ;;
    check) compose exec -T web python manage.py check --deploy; bash "${INFRA_DIR}/health.sh" ;;
    docker-logs) compose logs --tail 50 -f "${2:-web}" ;;
    docker-down) compose stop web ;;
    help|--help|-h)
        cat <<'HELP'
Usage: infra/service.sh <command>
  deploy       Build and recreate web; verify HTTP and static assets
  restart      Recreate web with current image and updated environment
  reload       Alias for restart
  status       Docker status and application HTTP check
  logs [-f]    Recent web logs, optionally followed
  start        Start web using its existing image
  stop         Stop web only
  check        Django production checks and HTTP check
  docker-up    Alias for deploy (web only)
  docker-down  Alias for stop (web only)
  docker-logs [service]  Follow Compose logs (default: web)
Code/template changes require deploy. Environment changes require restart.
Other Compose services are managed separately and are left running.
HELP
        ;;
    *) echo "Unknown command: ${COMMAND}. Run $0 help." >&2; exit 2 ;;
esac
