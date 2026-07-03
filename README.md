# 🚀 Order Processing API

A serverless REST API built with AWS Lambda, Amazon API Gateway and DynamoDB for managing customer orders.

The project was developed as a hands-on learning journey to understand cloud-native backend development while applying software engineering principles such as modular architecture, RESTful APIs and business rule validation.

# ✨ Features

- ✅ Create orders
- ✅ Retrieve a single order
- ✅ Retrieve all orders
- ✅ Update order status
- ✅ Order workflow validation
- ✅ RESTful API
- ✅ Modular architecture
- ✅ CloudWatch logging

# 🏗️ Architecture

```text
                    Client
                       │
                       ▼
               Amazon API Gateway
                       │
                       ▼
               AWS Lambda (Python)
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
     Request Routing         Business Logic
  (lambda_function.py)        (orders.py)
                       │
                       ▼
               Amazon DynamoDB
```

# 📂 Project Structure

```text
order-processing-api/

├── lambda_function.py
├── orders.py
├── constants.py
├── responses.py
├── README.md
└── function.zip
```

# ⚙️ Technologies

| Technology | Purpose |
|------------|---------|
| Python 3.12 | Backend language |
| AWS Lambda | Serverless compute |
| Amazon API Gateway | REST API |
| Amazon DynamoDB | NoSQL database |
| AWS IAM | Permissions |
| Amazon CloudWatch | Monitoring & Logs |
| Postman | API Testing |

# 🌐 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /orders | Create a new order |
| GET | /orders | Retrieve all orders |
| GET | /orders/{id} | Retrieve a specific order |
| PUT | /orders/{id} | Update the order status |

# 🔄 Order Workflow

Every order follows a predefined workflow.

```text
RECEIVED
     │
     ├────────────► CANCELLED
     │
     ▼
PROCESSING
     │
     ├────────────► CANCELLED
     │
     ▼
SHIPPED
     │
     ▼
DELIVERED
```

Invalid transitions return:

HTTP 400 Bad Request

# 🧠 Software Design

The application follows the **Single Responsibility Principle (SRP)**.

| Module | Responsibility |
|---------|----------------|
| lambda_function.py | Request routing |
| orders.py | Business logic |
| constants.py | Business rules |
| responses.py | HTTP response generation |

The business logic is intentionally separated from the request routing to improve maintainability and scalability.

# 🚧 Roadmap

## Completed

- [x] Create Order
- [x] Get Order
- [x] List Orders
- [x] Update Order
- [x] Status Workflow Validation
- [x] Modular Architecture

## Next Steps

- [ ] Amazon Cognito Authentication
- [ ] JWT Authorization
- [ ] User Management
- [ ] Role-Based Access Control
- [ ] Automated Testing
- [ ] Docker Support
- [ ] CI/CD Pipeline

# 📚 Lessons Learned

During the development of this project I learned:

- How API Gateway routes requests to AWS Lambda.
- How to model REST APIs.
- How DynamoDB performs CRUD operations.
- How to separate routing from business logic.
- Why modular architecture improves maintainability.
- How to implement business rules inside a backend service.

## Development Log

### v0.1
- Created the first Lambda function.
- Connected API Gateway.
- Created the first POST endpoint.

### v0.2
- Added GET endpoints.
- Introduced DynamoDB scan and get_item.

### v0.3
- Added PUT endpoint.
- Implemented business workflow validation.
- Refactored the project into multiple modules.

# 👨‍💻 Author

Gabriele Aiello
Backend project developed for educational purposes with a strong focus on AWS Serverless technologies and software engineering principles.

