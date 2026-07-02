import json
import boto3
import uuid
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)
    
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
VALID_STATUS = [
    "RECEIVED",
    "PROCESSING",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED"
]
ALLOWED_TRANSITIONS = {
    "RECEIVED": ["PROCESSING", "CANCELLED"],
    "PROCESSING": ["SHIPPED", "CANCELLED"],
    "SHIPPED": ["DELIVERED"],
    "DELIVERED": [],
    "CANCELLED": []
}
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    logger.info(f"Evento ricevuto: {event}")

    http_method = event.get("httpMethod")

    if http_method == "POST":
        return create_order(event)

    elif http_method == "GET":

        # GET /orders/{id}
        if event.get("pathParameters"):
            return get_order(event)

        # GET /orders
        else:
            return list_orders(event)
    
    elif http_method == "PUT":
        return update_order(event)

    else:
        return response(400, {"error": "Metodo non supportato"})


def create_order(event):
    try:
        body = json.loads(event.get('body', '{}'))
        
        customer_name = body.get('customer_name')
        items = body.get('items')
        
        if not customer_name or not items:
            return response(400, {'error': 'customer_name e items sono obbligatori'})
        
        order_id = str(uuid.uuid4())

        logger.info(f"Creazione ordine {order_id}")
        
        order = {
            'order_id': order_id,
            'customer_name': customer_name,
            'items': items,
            'status': 'RECEIVED',
            'created_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Salvataggio ordine {order_id}")
        table.put_item(Item=order)
        
        return response(201, order)
    
    except Exception as e:
        return response(500, {'error': str(e)})


def get_order(event):
    try:
        order_id = event.get('pathParameters', {}).get('id')
        
        if not order_id:
            return response(400, {'error': 'order_id mancante'})
        
        result = table.get_item(Key={'order_id': order_id})
        
        if 'Item' not in result:
            return response(404, {'error': 'Ordine non trovato'})
        
        return response(200, result['Item'])
    
    except Exception as e:
        return response(500, {'error': str(e)})
    
def list_orders(event):
    try:
        logger.info("Recupero di tutti gli ordini")

        result = table.scan()

        return response(200, result.get("Items", []))

    except Exception as e:
        logger.error(str(e))
        return response(500, {"error": str(e)})

def update_order(event):
    try:
        order_id = event.get("pathParameters", {}).get("id")

        if not order_id:
            return response(400, {"error": "order_id mancante"})

        body = json.loads(event.get("body", "{}"))
        status = body.get("status")

        if not status:
            return response(400, {"error": "status obbligatorio"})

        if status not in VALID_STATUS:
            return response(400, {"error": "Stato non valido"})

        logger.info(f"Aggiornamento ordine {order_id}")

        result = table.get_item(Key={"order_id": order_id})
        if "Item" not in result:
            return response(404, {"error": "Ordine non trovato"})

        current_status = result["Item"].get("status")
        allowed = ALLOWED_TRANSITIONS.get(current_status, [])
        if status != current_status and status not in allowed:
            return response(400, {"error": f"Transizione non valida da {current_status} a {status}"})

        result = table.update_item(
            Key={"order_id": order_id},
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":status": status},
            ReturnValues="ALL_NEW"
        )

        return response(200, result["Attributes"])

    except Exception as e:
        logger.error(str(e))
        return response(500, {"error": str(e)})


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body, cls=DecimalEncoder)
    }