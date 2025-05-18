# exit when any command fails
set -e

cp -r ../../app/ ./app/

echo "building image..."
docker build --platform=linux/amd64 -t pymageddon-server .

rm -r ./app/   
