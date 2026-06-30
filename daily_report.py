import json
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')
s3 = boto3.client('s3')
ses = boto3.client('ses')

BUCKET_NAME = 'order-reports-gabriele'
SENDER_EMAIL = 'aiellogabri05@gmail.com'
RECIPIENT_EMAIL = 'aiellogabri05@gmail.com'


def lambda_handler(event, context):
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    orders = get_today_orders()
    
    report = build_report(orders, today)
    
    save_report_to_s3(report, today)
    
    send_report_email(report, today)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Report generato e inviato', 'orders_count': len(orders)})
    }


def get_today_orders():
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    response = table.scan()
    all_orders = response.get('Items', [])
    
    today_orders = [
        order for order in all_orders
        if order.get('created_at', '').startswith(today)
    ]
    
    return today_orders


def build_report(orders, date):
    total_orders = len(orders)
    total_items = sum(
        sum(item.get('quantity', 0) for item in order.get('items', []))
        for order in orders
    )
    
    status_breakdown = {}
    for order in orders:
        status = order.get('status', 'UNKNOWN')
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    report = {
        'date': date,
        'total_orders': total_orders,
        'total_items_ordered': total_items,
        'status_breakdown': status_breakdown,
        'orders': [
            {
                'order_id': o.get('order_id'),
                'customer_name': o.get('customer_name'),
                'status': o.get('status')
            }
            for o in orders
        ]
    }
    
    return report


def save_report_to_s3(report, date):
    key = f'reports/{date}.json'
    
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(report, cls=DecimalEncoder, indent=2),
        ContentType='application/json'
    )


def send_report_email(report, date):
    subject = f'Report Ordini - {date}'
    
    body_text = f"""
Report giornaliero ordini - {date}

Totale ordini: {report['total_orders']}
Totale articoli ordinati: {report['total_items_ordered']}

Distribuzione per stato:
{json.dumps(report['status_breakdown'], indent=2)}
    """
    
    ses.send_email(
        Source=SENDER_EMAIL,
        Destination={'ToAddresses': [RECIPIENT_EMAIL]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body_text}}
        }
    )


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)