#!/usr/bin/env bash
# Usage: printf '%s' "$GHCR_TOKEN" | bash deploy.sh <image_tag> <ghcr_user> <image_prefix>
set -euo pipefail

TAG="${1:?image tag is required}"
GHCR_USER="${2:?ghcr user is required}"
IMAGE_PREFIX="${3:?image prefix is required}"

cd "$(dirname "$0")"
COMPOSE="docker compose -f docker-compose.prod.yml"
STATE_FILE=".last_good_tag"
HEALTH_TIMEOUT=600

export IMAGE_PREFIX

# Token arrives on stdin.
docker login ghcr.io -u "$GHCR_USER" --password-stdin

PREVIOUS=""
if [ -f "$STATE_FILE" ]; then
  PREVIOUS="$(cat "$STATE_FILE")"
fi

wait_healthy() {
  local deadline=$((SECONDS + HEALTH_TIMEOUT))
  while [ "$SECONDS" -lt "$deadline" ]; do
    local all_ok=1
    for name in unsdg-backend unsdg-frontend; do
      local status
      status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$name" 2>/dev/null || echo missing)"
      if [ "$status" != "healthy" ]; then
        all_ok=0
      fi
    done
    if [ "$all_ok" -eq 1 ]; then
      return 0
    fi
    sleep 5
  done
  return 1
}

deploy_tag() {
  export IMAGE_TAG="$1"
  echo "Deploying tag $IMAGE_TAG"
  $COMPOSE pull
  $COMPOSE up -d --remove-orphans
}

deploy_tag "$TAG"

if wait_healthy; then
  echo "$TAG" > "$STATE_FILE"
  # Keep a week of images so a manual rollback stays fast.
  docker image prune -af --filter "until=168h" > /dev/null
  echo "Deploy succeeded: $TAG"
  exit 0
fi

echo "Deploy failed health checks for $TAG" >&2
$COMPOSE logs --tail=100 >&2 || true

if [ -n "$PREVIOUS" ] && [ "$PREVIOUS" != "$TAG" ]; then
  echo "Rolling back to $PREVIOUS" >&2
  deploy_tag "$PREVIOUS"
  if wait_healthy; then
    echo "Rollback succeeded: $PREVIOUS" >&2
  else
    echo "Rollback also failed. Manual intervention required." >&2
  fi
else
  echo "No previous good tag recorded, nothing to roll back to." >&2
fi

exit 1