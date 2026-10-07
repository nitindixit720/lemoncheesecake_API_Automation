import os
import sys

import boto3

BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
HOST = os.environ.get("S3_HOST", "s3.ap-south-1.amazonaws.com")
PREFIX = os.environ.get("S3_PREFIX")

# AWS credentials are read from the standard boto3 credential chain
# (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY env vars, shared config, or an
# instance/task role) -- never hardcode credentials here.
_client = boto3.client("s3", endpoint_url="https://{}".format(HOST))


def upload_files(filename):
    _client.upload_file(filename, BUCKET_NAME, "{}/{}".format(PREFIX, filename))


def get_file_from_s3(filename):
    _client.download_file(BUCKET_NAME, "{}{}".format(PREFIX, filename), filename)


def list_backup_in_s3():
    response = _client.list_objects_v2(Bucket=BUCKET_NAME)
    for i, obj in enumerate(response.get("Contents", [])):
        print("[%s] %s" % (i, obj["Key"]))


def delete_all_backups():
    response = _client.list_objects_v2(Bucket=BUCKET_NAME)
    for i, obj in enumerate(response.get("Contents", [])):
        print("deleting %s" % (obj["Key"]))
        _client.delete_object(Bucket=BUCKET_NAME, Key=obj["Key"])


if __name__ == '__main__':
    upload_files(sys.argv[1])
