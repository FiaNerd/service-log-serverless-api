from datetime import datetime, timezone
import json
from utils.db import get_table
from utils.responses import json_response
from botocore.exceptions import ClientError

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"}


def lambda_handler(event, context):
    path_parameters = event.get("pathParameters") or {}
    service_name = (path_parameters.get("name") or "").strip()
    item_id = (path_parameters.get("itemId") or "").strip()

    if not service_name or not item_id:
        return json_response(
            400, {"error": "Missing 'name' or 'itemId' in path parameters"}
        )

    try:
        raw_body = event.get("body") or "{}"
        data = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except json.JSONDecodeError:
        return json_response(400, {"error": "Invalid JSON in request body"})

    if not isinstance(data, dict):
        return json_response(400, {"error": "Request body must be a JSON object"})

    update_parts = ["#updatedAt = :updatedAt"]
    expr_names = {"#updatedAt": "updatedAt"}
    expr_values = {":updatedAt": datetime.now(timezone.utc).isoformat()}

    if "status" in data and data["status"] is not None:
        status = str(data["status"]).strip().upper()
        if status not in VALID_STATUSES:
            return json_response(
                400,
                {
                    "error": f"Invalid 'status'. Allowed: {', '.join(sorted(VALID_STATUSES))}"
                },
            )
        update_parts.append("#status = :status")
        expr_names["#status"] = "status"
        expr_values[":status"] = status

    if "priority" in data and data["priority"] is not None:
        priority = str(data["priority"]).strip().lower()
        if priority not in VALID_PRIORITIES:
            return json_response(
                400,
                {"error": "Invalid 'priority'. Must be 'low', 'medium', or 'high'"},
            )
        update_parts.append("#priority = :priority")
        expr_names["#priority"] = "priority"
        expr_values[":priority"] = priority

    if "description" in data and data["description"] is not None:
        update_parts.append("#description = :description")
        expr_names["#description"] = "description"
        expr_values[":description"] = str(data["description"])

    if len(update_parts) == 1:
        return json_response(
            400,
            {
                "error": "Provide at least one field to update: 'status', 'priority', or 'description'"
            },
        )

    table = get_table()

    try:
        result = table.update_item(
            Key={
                "pk": f"SERVICE#{service_name.lower()}",
                "sk": f"ITEM#{item_id}",
            },
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)",
            ReturnValues="ALL_NEW",
        )
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return json_response(404, {"error": "Service log item not found"})
        raise

    return json_response(
        200,
        {
            "message": "The service log is updated",
            "item": result.get("Attributes", {}),
        },
    )
