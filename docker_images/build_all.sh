#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

# Always rebuild from the repo root so Docker Compose picks up the latest UI and
# backend files. Use DOCKER_PLATFORM=linux/amd64 to cross-build when needed.
cd "$REPO_ROOT"

echo "=== Rebuilding all Docker images from the repository root ==="
docker compose build --no-cache

echo "=== Restarting containers with the rebuilt images ==="
docker compose up -d --force-recreate

printf '\nUpdated images:\n'
docker images --format '{{.Repository}}:{{.Tag}}' | grep '^pymageddon-' || true
