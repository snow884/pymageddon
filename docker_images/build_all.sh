# exit when any command fails
set -e

export AWS_ACCOUNT_ID=143858405180

#export AWS_ACCOUNT_ID=143858405180
export REPOSITORY_NAME=pymageddon-webserver
export SERVICE_NAME=pymageddon-webserver-web-app-service

for folder in game-node redis-server server
do 
    echo "Updating task $folder..."
    cd $folder
    sh build.sh
    cd ..
    echo "Done updating task $folder"
done

echo "updating the service image..."

aws ecs update-service --region us-east-1 --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment