def get_tables():
    global _dynamodb, _table
    if _table is None:
        table_name = os.environ.get("TABLE_NAME", "service-logs-db")
        _dynamodb = boto3.resource("dynamodb")
        _table = _dynamodb.Table(table_name)

    return _table
