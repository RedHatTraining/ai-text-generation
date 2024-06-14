#!/usr/bin/env python3

import os
import boto3
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


def download_s3_folder(
    bucket_name: str,
    s3_dir: str,
    local_dir: Path,
    endpoint: str,
    key_id: str,
    access_key: str,
):
    # Create an S3 client with the provided connection parameters
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=key_id,
        aws_secret_access_key=access_key,
    )

    # Ensure the local directory exists
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    # Get the list of objects in the S3 folder
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_dir)

    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                key = obj["Key"]
                # Remove the folder prefix to get the relative path
                relative_path = os.path.relpath(key, s3_dir)
                local_file_path = os.path.join(local_dir, relative_path)

                # Ensure the local directory exists for the file
                local_dir_path = os.path.dirname(local_file_path)
                if not os.path.exists(local_dir_path):
                    os.makedirs(local_dir_path)

                # Download the file
                s3.download_file(bucket_name, key, local_file_path)
                print(f"Downloaded {key} to {local_file_path}")


if __name__ == "__main__":
    s3_dir_path = os.getenv("S3_MODEL_PATH")
    local_dir_path = Path(os.getenv("LOCAL_MODEL_PATH"))

    s3_endpoint_url = os.environ.get("AWS_S3_ENDPOINT")
    s3_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    s3_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    s3_bucket_name = os.environ.get("AWS_S3_BUCKET")

    if not all([s3_endpoint_url, s3_access_key, s3_secret_key, s3_bucket_name]):
        print(
            "Please set all the required environment variables: "
            "AWS_S3_ENDPOINT, AWS_ACCESS_KEY_ID, "
            "AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET"
        )
    else:
        print(
            f"Downloading {s3_dir_path} dir "
            f"from bucket {s3_bucket_name} "
            f"at {s3_endpoint_url} "
            f"to {local_dir_path}"
        )

        download_s3_folder(
            s3_bucket_name,
            s3_dir_path,
            local_dir_path,
            s3_endpoint_url,
            s3_access_key,
            s3_secret_key,
        )
