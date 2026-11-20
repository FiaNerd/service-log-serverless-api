import os
import boto3

_dynamodb = None
_table = None


def get_table():
    global _dynamodb, _table
    if _table is None:
        table_name = os.environ.get("TABLE_NAME", "service-logs-db")
        _dynamodb = boto3.resource("dynamodb")
        _table = _dynamodb.Table(table_name)
    return _table
