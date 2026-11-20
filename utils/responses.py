import json


def json_responses(status_code: int, body: dict) -> dict:
    """
    Create a JSON response for AWS Lambda.

    Args:
        status_code (int): The HTTP status code for the response.
        body (dict): The body of the response, which will be converted to JSON.

    Returns:
        dict: A dictionary representing the HTTP response.
    """
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }