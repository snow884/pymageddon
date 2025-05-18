set -e

echo "building image..."
docker build --platform=linux/amd64 -t pymageddon-redis-server .

