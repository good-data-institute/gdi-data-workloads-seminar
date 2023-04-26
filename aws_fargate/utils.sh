#! /bin/bash

# delete existing service
aws ecs --profile gdi delete-service --cluster gdi-seminar-cluster --service gdi-seminar-service --force