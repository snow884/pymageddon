# exit when any command fails
set -e

# Set DOCKER_PLATFORM (e.g. linux/amd64) to cross-build for a different
# architecture. Left unset, docker builds natively for the host arch, which
# is far faster than emulating amd64 on Apple Silicon.
PLATFORM_ARG=""
if [ -n "$DOCKER_PLATFORM" ]; then
    PLATFORM_ARG="--platform=$DOCKER_PLATFORM"
fi

echo "building image..."
DOCKER_BUILDKIT=1 docker build $PLATFORM_ARG -f Dockerfile -t pymageddon-server ../..
