import logging

from responses import response

from orders import (
    create_order,
    get_order,
    list_orders,
    update_order
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    logger.info(f"Evento ricevuto: {event}")

    request_context = event.get("requestContext", {})

    http_method = (
        event.get("httpMethod")
        or request_context.get("http", {}).get("method")
    )

    if http_method == "POST":
        return create_order(event)

    elif http_method == "GET":

        if event.get("pathParameters"):
            return get_order(event)

        return list_orders(event)

    elif http_method == "PUT":
        return update_order(event)

    return response(
        400,
        {
            "error": "Metodo non supportato"
        }
    )