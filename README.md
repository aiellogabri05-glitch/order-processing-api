# Order Processing API — Serverless
A serverless REST API for managing e-commerce/logistics orders, built entirely on AWS managed services (no servers to maintain).

## Architecture
- **API Gateway**: public HTTP endpoint, routes requests to Lambda
- **Lambda**: handles business logic, validation, and data persistence
- **DynamoDB**: NoSQL table storing order records (pay-per-request billing)

## Endpoints

### Create an order
Response (201 Created):
```json
{
  "order_id": "uuid-generated",
  "customer_name": "Mario Rossi",
  "items": [{"sku": "ABC123", "quantity": 2}],
  "status": "RECEIVED",
  "created_at": "2026-06-30T11:24:55.506854"
}
```

### Get an order
Response (200 OK): same structure as above. Returns 404 if not found.

## Tech stack
- AWS Lambda (Python 3.12)
- Amazon API Gateway (HTTP API, payload format 2.0)
- Amazon DynamoDB (pay-per-request)
- IAM roles with least-privilege-oriented permissions
- AWS CLI for infrastructure provisioning

## Engineering notes / challenges solved
- **Event format mismatch**: HTTP API (v2) sends the HTTP method inside `requestContext.http.method`, not `httpMethod` as in the older REST API format. Adjusted the handler accordingly.
- **Decimal serialization**: DynamoDB returns numeric fields as Python `Decimal`, which isn't natively JSON-serializable. Implemented a custom `json.JSONEncoder` to handle conversion.
- **Explicit routing**: Initially used a catch-all `$default` route; switched to explicit routes (`POST /orders`, `GET /orders/{id}`) to correctly populate `pathParameters` for the GET endpoint.

## Cost
Runs entirely within AWS Free Tier for development/testing volumes — Lambda, API Gateway, and DynamoDB all have generous always-free tiers for this kind of usage.

## Local development
```bash
# Deploy code changes
Compress-Archive -Path lambda_function.py -DestinationPath function.zip -Force
aws lambda update-function-code --function-name OrderProcessingFunction --zip-file fileb://function.zip --region eu-north-1
```

## Author
Gabriele Aiello