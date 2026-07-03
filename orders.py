import json
import uuid
import os
import logging
import boto3

from datetime import datetime

from responses import response
from constants import VALID_STATUS, ALLOWED_TRANSITIONS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)


def create_order(event):
    try:
        body = json.loads(event.get("body", "{}"))

        customer_name = body.get("customer_name")
        items = body.get("items")

        if not customer_name or not items:
            return response(
                400,
                {"error": "customer_name e items sono obbligatori"}
            )

        order_id = str(uuid.uuid4())

        logger.info(f"Creazione ordine {order_id}")

        order = {
            "order_id": order_id,
            "customer_name": customer_name,
            "items": items,
            "status": "RECEIVED",
            "created_at": datetime.utcnow().isoformat()
        }

        table.put_item(Item=order)

        logger.info(f"Ordine {order_id} creato con successo")

        return response(201, order)

    except Exception as e:
        logger.exception("Errore durante la creazione dell'ordine")
        return response(500, {"error": str(e)})


def get_order(event):
    try:
        order_id = event.get("pathParameters", {}).get("id")

        if not order_id:
            return response(
                400,
                {"error": "order_id mancante"}
            )

        result = table.get_item(
            Key={"order_id": order_id}
        )

        if "Item" not in result:
            return response(
                404,
                {"error": "Ordine non trovato"}
            )

        return response(200, result["Item"])

    except Exception as e:
        logger.exception("Errore durante il recupero dell'ordine")
        return response(500, {"error": str(e)})


def list_orders(event):
    try:
        logger.info("Recupero di tutti gli ordini")

        result = table.scan()

        return response(
            200,
            result.get("Items", [])
        )

    except Exception as e:
        logger.exception("Errore durante il recupero degli ordini")
        return response(500, {"error": str(e)})


def update_order(event):
    try:
        order_id = event.get("pathParameters", {}).get("id")

        if not order_id:
            return response(
                400,
                {"error": "order_id mancante"}
            )

        body = json.loads(event.get("body", "{}"))
        status = body.get("status")

        if status:
            status = status.strip().upper()

        if not status:
            return response(
                400,
                {"error": "status obbligatorio"}
            )

        if status not in VALID_STATUS:
            return response(
                400,
                {"error": "Stato non valido"}
            )

        result = table.get_item(
            Key={"order_id": order_id}
        )

        if "Item" not in result:
            return response(
                404,
                {"error": "Ordine non trovato"}
            )

        current_status = result["Item"]["status"]

        allowed = ALLOWED_TRANSITIONS.get(current_status, [])

        if status != current_status and status not in allowed:
            return response(
                400,
                {
                    "error": f"Transizione non valida da {current_status} a {status}"
                }
            )

        result = table.update_item(
            Key={"order_id": order_id},
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={
                "#s": "status"
            },
            ExpressionAttributeValues={
                ":status": status
            },
            ReturnValues="ALL_NEW"
        )

        logger.info(f"Ordine {order_id} aggiornato a {status}")

        return response(200, result["Attributes"])

    except Exception as e:
        logger.exception("Errore durante l'aggiornamento dell'ordine")
        return response(500, {"error": str(e)})