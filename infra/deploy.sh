#!/usr/bin/env bash
# Rebuild source into the image; startup runs migrations and collectstatic.
# Old portfolio-web images and dangling build layers are pruned automatically.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

# ── Capture the current image ID before the build so we can remove it later ──
OLD_IMAGE_ID=$(docker images --format "{{.ID}}" portfolio-web:latest 2>/dev/null | head -1 || true)

echo "Building portfolio web image..."
compose build web

# ── Remove the previous image (it is now untagged / replaced by :latest) ─────
if [[ -n "${OLD_IMAGE_ID}" ]]; then
    NEW_IMAGE_ID=$(docker images --format "{{.ID}}" portfolio-web:latest | head -1)
    if [[ "${OLD_IMAGE_ID}" != "${NEW_IMAGE_ID}" ]]; then
        echo "Removing old image ${OLD_IMAGE_ID}..."
        docker rmi "${OLD_IMAGE_ID}" 2>/dev/null || echo "  (image already gone or still in use — skipping)"
    fi
fi

# ── Prune dangling layers left by the build (build cache is kept) ─────────────
echo "Pruning dangling image layers..."
docker image prune -f

echo "Recreating portfolio web service..."
compose up -d --no-deps --force-recreate web
for attempt in {1..30}; do
    if bash "${INFRA_DIR}/health.sh" >/dev/null 2>&1; then
        echo "Deployment verified: homepage and referenced stylesheets return HTTP 200."
        exit 0
    fi
    sleep 2
done
echo "Deployment failed its HTTP/static asset checks." >&2
compose logs --tail 60 web
exit 1
