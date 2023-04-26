#! /bin/bash

# aws profile
export AWS_PROFILE=gdi

# zip
zip dep-package.zip main.py

# upload zip to s3
aws s3 cp dep-package.zip s3://gdi-seminar/lambda/dep-package.zip

# update lambda
aws lambda \
    update-function-code \
    --function-name gdi-demo-lambda \
    --s3-bucket gdi-seminar \
    --s3-key lambda/dep-package.zip