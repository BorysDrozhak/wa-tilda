import json
import logging

from boto3 import client as boto3_client

lambda_client = boto3_client("lambda", region_name="us-east-1")
log = logging.getLogger(__name__)

INVOKE_FUNCTION_LAMBDA = "kasa_forecasting-wa-telegram-bot-dev-forecast"


def _encode_payload(data):
    return json.dumps(data)


def invoke_lambda(lambda_name, data):
    """Invoke provided lambda with specified data."""
    return lambda_client.invoke(
        FunctionName=lambda_name,
        InvocationType="Event",
        Payload=_encode_payload(data),
    )


def invoke_function_in_lambda(data):
    data = {
        "sales_data": data,
    }

    return invoke_lambda(
        lambda_name=INVOKE_FUNCTION_LAMBDA,
        data=data,
    )
