import json
import time

import boto3
import redis
from singleton import realm


def backup_to_s3():

    if not realm.REDIS_CONNECTION:
        realm.REDIS_CONNECTION = redis.Redis(
            host="pymageddon-redis-server", port=6379, db=0
        )

    # Get all keys
    all_keys = realm.REDIS_CONNECTION.keys()

    dict_to_dump = {}

    # Print the keys
    for key in all_keys:
        dict_to_dump[key.decode()] = (realm.REDIS_CONNECTION.get(key)).hex()

    dict_to_dump_str = json.dumps(dict_to_dump)

    timestamp = int(time.time())

    object_name = str(timestamp) + ".rds"

    bucket_name = "pymageddon-redis-backup"

    s3_client = boto3.client("s3")

    s3_client.put_object(
        Bucket=bucket_name, Key="prod_backup/" + object_name, Body=dict_to_dump_str
    )
    print(f"String data uploaded to s3://{bucket_name}/{object_name}")


def restore_from_s3():

    if not realm.REDIS_CONNECTION:
        realm.REDIS_CONNECTION = redis.Redis(
            host="pymageddon-redis-server", port=6379, db=0
        )

    client = boto3.client("s3")
    bucket_name = "pymageddon-redis-backup"

    result = client.list_objects(
        Bucket=bucket_name, Prefix="prod_backup/", Delimiter="/"
    )

    max_timestamp = 0
    max_prefix = ""

    for o in result.get("Contents"):
        new_timestamp = int((o.get("Key").split("/")[1]).split(".")[0])

        if new_timestamp > max_timestamp:
            max_timestamp = new_timestamp
            max_prefix = o.get("Key").split(".")[0]

    print(max_prefix)

    response = client.get_object(Bucket=bucket_name, Key=max_prefix + ".rds")
    file_content = response["Body"].read()

    dict_from_dump = json.loads(file_content)

    for key, val in dict_from_dump.items():
        realm.REDIS_CONNECTION.set(key, bytes.fromhex(val))
