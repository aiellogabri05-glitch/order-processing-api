import json
import boto3
import uuid
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)
    
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

def lambda_handler(event, context):
    http_method = event.get('requestContext', {}).get('http', {}).get('method')
    
    if http_method == 'POST':
        return create_order(event)
    elif http_method == 'GET':
        return get_order(event)
    else:
        return response(400, {'error': 'Metodo non supportato'})


def create_order(event):
    try:
        body = json.loads(event.get('body', '{}'))
        
        customer_name = body.get('customer_name')
        items = body.get('items')
        
        if not customer_name or not items:
            return response(400, {'error': 'customer_name e items sono obbligatori'})
        
        order_id = str(uuid.uuid4())
        
        order = {
            'order_id': order_id,
            'customer_name': customer_name,
            'items': items,
            'status': 'RECEIVED',
            'created_at': datetime.utcnow().isoformat()
        }
        
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


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body, cls=DecimalEncoder)
    }