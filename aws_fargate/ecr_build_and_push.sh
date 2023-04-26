#! /bin/bash

# set aws profile
export AWS_PROFILE=gdi

# build docker image and tag with repository url
docker build --platform linux/amd64 -t 385559909061.dkr.ecr.ap-southeast-2.amazonaws.com/gdi-seminar .

# push image to ECR
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 385559909061.dkr.ecr.ap-southeast-2.amazonaws.com/gdi-seminar

docker push 385559909061.dkr.ecr.ap-southeast-2.amazonaws.com/gdi-seminar

# create task definition
aws ecs register-task-definition --cli-input-json file://task_definition.json

# create the ecs cluster
aws ecs create-cluster --cluster-name gdi-seminar-cluster

# create service
aws ecs create-service --cli-input-json file://service_definition.json --desired-count 1