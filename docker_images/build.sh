# exit when any command fails
set -e

# export AWS_ACCESS_KEY_ID="ASIAYT7F5KQBR5PZGMUS"
# export AWS_SECRET_ACCESS_KEY="TOQcTKL0aADMa/AC4wTyYfUUngtUsWADygusPxHe"
# export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEPr//////////wEaCXVzLWVhc3QtMSJGMEQCIEmZ1+QvEOuKiaTYVoeFLQrTLVr6nS+2FS1lFltxURguAiAc7WZZf60FhwU2BlmkcJMIFOUtm3YHJ73UEBc4i4nu6iquAwhjEAAaDDU5MjY1MDc4NTc5NSIMbjVVN2s3Jy/nnip2KosD627JSJm6IpEe/9QLfbxlpcOQar9pRDqOdghNn+ZfWHfLf3l461toeZwiFPMsIiN02WcJ3F0salfZ36B51CgRxwO3Lcj05Ujoye4m0322N+HXeBTj4IPitqewSNPKyrYo1Zme5cSw3piQljyCeYSZ2ssY7jxzn5yJm7fm9mkhvWo7/F/Ci5bmRWC/OPhz6YeMk58O1bcZO7flbJTsdOlxJtd6omxz0ioTDwCOteilKU1nZsb3Bn8D86dhHNNtv/o7O553DCZBjxUwVaZ1UCohh2UV1S8cAWssbUFztbUo+P1a/Znx6vox17z/pTtuhGxd7pT9wcOGsskxxHtpFv67TemwSKlPWfSEBUwP4HWZHFWldwet3sQe09p33rSu6h/QEx6vZ4C9GlTRZgMM3eKl5sw6RRDcSiR05V/JqSdv9Oued0sJSW/EFbp9Mux938GHthx22XZ62IwYzvoZx9Dqv9eLwKIbr2gR4Hpg5qoiFEY3abP3sRG/Ng54leNvqrmnYgePz53yrM4QauQw5oDVlwY6pwG8n8S71k8ucszJEcNBmoSumaINXwVbGQYJpzQStae39aPzoBBF11lXjPa3z2XZ6/LpNhrudkHO9A7XFAdYegm98SIrHHSBId5aTySkBwg9IQ5waf6LjXx3wsMNxGi+Ih8C+1EO+ejPTZvRnBf5xppsLyKRQ9KhgYF8wM7xoQh66STyIJ11Fc4WYWkFQjFwIcuYPENNo4nQ49ZgcwIkiOXBgwcmp84dGA=="

export AWS_ACCOUNT_ID=143858405180

#export AWS_ACCOUNT_ID=143858405180
export CLUSTER_NAME=web-app-cluster
export REPOSITORY_NAME=handle_usda
export SERVICE_NAME=other-loads-app-service

export DOCKER_TAG=latest

docker rmi $DOCKER_TAG || echo "no image found, skipping deletion..."
docker rmi $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/$REPOSITORY_NAME\:$DOCKER_TAG || echo "no image found, skipping deletion..."

echo "building image..."
docker build --platform=linux/amd64 -t $DOCKER_TAG .

echo "tagging image..."
docker tag $DOCKER_TAG $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/$REPOSITORY_NAME\:$DOCKER_TAG

echo "logging in..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

echo "create repository..."
aws ecr create-repository --repository-name $REPOSITORY_NAME --region us-east-1 || echo "error, probably exists..."

echo "deleting image..."
aws ecr batch-delete-image --repository-name $REPOSITORY_NAME --image-ids imageTag=latest --region us-east-1

echo "pushing image..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/$REPOSITORY_NAME\:$DOCKER_TAG

echo "Pushed to $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/$REPOSITORY_NAME\:$DOCKER_TAG"

aws ecs update-service --region us-east-1 --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment