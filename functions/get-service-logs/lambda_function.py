import json
from utils.db import get_table
from utils.responses import json_response


def lambda_handler(event, context):
    print(json.dumps(event))

    path_parameters = event.get("pathParameters") or {}
    service_name = (path_parameters.get("name") or "").strip()

    if not service_name:
        return json_response(400, {"error": "Missing or empty 'name' path parameter"})

    table = get_table()
    response = table.query(
        KeyConditionExpression="pk = :pk AND begins_with(sk, :sk)",
        ExpressionAttributeValues={
            ":pk": f"SERVICE#{service_name.lower()}",
            ":sk": "ITEM#",
        },
    )

    print(json.dumps(response, default=str))

    return json_response(
        200,
        {
            "success": True,
            "service": service_name,
            "items": response.get("Items", []),
        },
    )
