#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"

# Allow cross-building by exporting DOCKER_PLATFORM, e.g.:
#   DOCKER_PLATFORM=linux/amd64 ./docker_images/build_all.sh
PLATFORM_ARGS=()
if [ -n "${DOCKER_PLATFORM:-}" ]; then
    PLATFORM_ARGS=(--platform="$DOCKER_PLATFORM")
fi

build_image() {
    local name="$1"
    local dockerfile="$2"
    local tag="$3"
    local -a cmd=(docker build --pull)

    if [ ${#PLATFORM_ARGS[@]} -gt 0 ]; then
        cmd+=("${PLATFORM_ARGS[@]}")
    fi

    cmd+=(-f "$dockerfile" -t "$tag" "$REPO_ROOT")

    echo "=== Building $name ($tag) with $dockerfile ==="
    "${cmd[@]}"
    echo "=== Finished $name ($tag) ==="
}

# Keep tags aligned with the compose file and existing image names.
build_image "game-node" "$SCRIPT_DIR/game-node/Dockerfile" "pymageddon-game-node" &
build_image "redis-server" "$SCRIPT_DIR/redis-server/Dockerfile" "pymageddon-redis-server" &
build_image "server" "$SCRIPT_DIR/server/Dockerfile" "pymageddon-server" &

wait
