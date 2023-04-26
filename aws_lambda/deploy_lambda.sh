#! /bin/bash
# set aws profile
export AWS_PROFILE=gdi

# zip package
zip dep-package.zip main.py

# copy package to s3
aws s3 cp dep-package.zip s3://gdi-seminar/lambda/dep-package.zip

# # delete existing lambda function
aws lambda delete-function --function-name gdi-demo-lambda

# create lambda function
aws lambda --profile gdi create-function --function-name gdi-demo-lambda --runtime python3.8 --handler main.trigger --code S3Bucket=gdi-seminar,S3Key=lambda/dep-package.zip --role arn:aws:iam::385559909061:role/basic-lambda-role

# add permission to access s3
aws lambda add-permission --function-name gdi-demo-lambda --statement-id s3-permission --action "lambda:InvokeFunction" --principal s3.amazonaws.com --source-arn arn:aws:s3:::gdi-seminar --source-account 385559909061

# add s3 event trigger
aws s3api put-bucket-notification-configuration --bucket gdi-seminar --notification-configuration '{
  "LambdaFunctionConfigurations": [
    {
      "LambdaFunctionArn": "arn:aws:lambda:ap-southeast-2:385559909061:function:gdi-demo-lambda",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "suffix",
              "Value": ".csv"
            }
          ]
        }
      }
    }
  ]
}'
