#!/bin/bash

# upload file to s3 to trigger the lambda deployment (needs sleep to run as full script)
aws s3 cp --profile gdi ../data/student_data.csv s3://gdi-seminar/input_data/student_data.csv

## installs dependencies in linux to ensure they are compatible with the lambda runtime (move outside script)
pip install \
    --platform manylinux2014_x86_64 \
    --target=package \
    --implementation cp \
    --python 3.8 \
    --only-binary=:all: --upgrade \
    pandas numpy pyarrow
