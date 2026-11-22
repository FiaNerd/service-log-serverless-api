import json
from botocore.exceptions import ClientError
from utils.db import get_table
from utils.responses import json_response


def lambda_handler(event, context):
    try:
        path_params = event.get("pathParameters") or {}
        raw_name = path_params.get("name")
        item_id = path_params.get("itemId")

        if not raw_name or not str(raw_name).strip():
            return json_response(400, {"error": "Path parameter 'name' is required"})

        if not item_id or not str(item_id).strip():
            return json_response(400, {"error": "Path parameter 'itemId' is required"})

        service_name = str(raw_name).strip().lower()
        pk = f"SERVICE#{service_name}"
        sk = f"ITEM#{str(item_id).strip()}"

        table = get_table()
        response = table.delete_item(
            Key={"pk": pk, "sk": sk},
            ReturnValues="ALL_OLD",
        )

        deleted_item = response.get("Attributes")
        if not deleted_item:
            return json_response(404, {"error": "Service log item not found"})

        return json_response(
            200,
            {
                "message": "The service log is deleted",
                "deletedItem": deleted_item,
            },
        )

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "ClientError")
        print(f"DynamoDB ClientError ({error_code}): {e}")
        return json_response(500, {"error": "Database error occurred"})
    except Exception as e:
        print(f"Unhandled error: {e}")
        return json_response(500, {"error": "Internal server error"})