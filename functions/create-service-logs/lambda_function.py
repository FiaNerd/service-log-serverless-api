from datetime import datetime, timezone
import json
import os
import uuid
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("TABLE_NAME", "service-logs-db")
table = dynamodb.Table(TABLE_NAME)


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    try:
        raw_body = event.get("body") or "{}"
        data = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON in request body"})

    if not isinstance(data, dict):
        return _response(400, {"error": "Request body must be a JSON object"})

    name = (data.get("name") or "").strip()
    if not name:
        return _response(400, {"error": "Missing or empty 'name' field"})

    priority = (data.get("priority") or "medium").strip().lower()
    if priority not in ["low", "medium", "high"]:
        return _response(
            400,
            {"error": "Invalid 'priority' field. Must be 'low', 'medium', or 'high'"},
        )

    status = (data.get("status") or "OPEN").strip().upper()
    now = datetime.now(timezone.utc).isoformat()
    item_id = str(uuid.uuid4())

    item = {
        "pk": f"SERVICE#{name.lower()}",
        "sk": f"ITEM#{item_id}",
        "itemId": item_id,
        "name": name,
        "status": status,
        "priority": priority,
        "description": data.get("description") or "",
        "createdAt": now,
        "updatedAt": now,
    }

    table.put_item(Item=item)

    return _response(201, {"message": "The service is saved", "item": item})
