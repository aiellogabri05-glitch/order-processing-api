# Order Processing System — Serverless
A complete serverless system for managing e-commerce/logistics orders, built entirely on AWS managed services (no servers to maintain). Includes a public REST API for order management and an automated daily reporting pipeline.

## Architecture
- **API Gateway**: public HTTP endpoint for order operations
- **Lambda (order-processing)**: handles order creation/retrieval business logic
- **DynamoDB**: NoSQL table storing order records (pay-per-request billing)
- **EventBridge**: triggers the daily report Lambda on a cron schedule
- **Lambda (daily-report)**: aggregates today's orders, builds a summary report
- **S3**: stores historical JSON reports, one per day
- **SES**: emails the daily summary report

## API Endpoints

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

## Daily Report Pipeline
Runs automatically every day at 8:00 UTC via an EventBridge scheduled rule. For each run:

1. Scans DynamoDB for orders created that day
2. Aggregates statistics: total orders, total items, status breakdown
3. Saves a JSON report to S3 (`reports/{date}.json`)
4. Sends a summary email via Amazon SES

## Tech stack
- AWS Lambda (Python 3.12) — two functions
- Amazon API Gateway (HTTP API, payload format 2.0)
- Amazon DynamoDB (pay-per-request)
- Amazon EventBridge (scheduled rule)
- Amazon S3 (report archive)
- Amazon SES (email notifications)
- IAM roles with least-privilege-oriented permissions
- AWS CLI for infrastructure provisioning

## Engineering notes / challenges solved
- **Event format mismatch**: HTTP API (v2) sends the HTTP method inside `requestContext.http.method`, not `httpMethod` as in the older REST API format. Adjusted the handler accordingly.
- **Decimal serialization**: DynamoDB returns numeric fields as Python `Decimal`, which isn't natively JSON-serializable. Implemented a custom `json.JSONEncoder` to handle conversion.
- **Explicit routing**: Initially used a catch-all `$default` route; switched to explicit routes (`POST /orders`, `GET /orders/{id}`) to correctly populate `pathParameters` for the GET endpoint.
- **Cross-service IAM permissions**: the report Lambda needs scoped access to DynamoDB (read), S3 (write), and SES (send) — managed via a dedicated IAM role.

## Cost
Runs entirely within AWS Free Tier for development/testing volumes — Lambda, API Gateway, DynamoDB, EventBridge, S3, and SES (sandbox mode) all have generous always-free tiers for this kind of usage.

## Local development
```bash
# Deploy order-processing Lambda
Compress-Archive -Path lambda_function.py -DestinationPath function.zip -Force
aws lambda update-function-code --function-name OrderProcessingFunction --zip-file fileb://function.zip --region eu-north-1

# Deploy daily-report Lambda
Compress-Archive -Path daily_report.py -DestinationPath daily_report.zip -Force
aws lambda update-function-code --function-name DailyReportFunction --zip-file fileb://daily_report.zip --region eu-north-1
```

## Author
Gabriele Aiello