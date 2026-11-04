"""Create the configured bucket in the local S3-compatible Silo service."""
import os
import time

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

client = boto3.client(
    "s3",
    endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
    config=Config(s3={"addressing_style": "path"}),
)

bucket = os.environ["AWS_STORAGE_BUCKET_NAME"]
for attempt in range(60):
    try:
        client.head_bucket(Bucket=bucket)
        print(f"Bucket {bucket!r} already exists.")
        break
    except (BotoCoreError, ClientError):
        try:
            client.create_bucket(Bucket=bucket)
            print(f"Created bucket {bucket!r}.")
            break
        except (BotoCoreError, ClientError):
            if attempt == 59:
                raise
            time.sleep(2)
