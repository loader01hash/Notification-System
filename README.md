# Django Notification System

A scalable, microservice-based notification system built with Django, Redis, Celery, and multiple notification channels.

## Architecture Overview

This system is designed with a microservice architecture to ensure scalability, fault tolerance, and maintainability:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   API Gateway   │    │  Notification   │
│    (Nginx)      │◄──►│   (Django)      │◄──►│    Service      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis Cache   │    │ Celery Workers  │
                       │   & Queue       │    │   (Background)  │
                       └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ SQLite Database │    │  Notification   │
                       │  (Development)  │    │   Channels      │
                       └─────────────────┘    │ (Telegram/Email)│
                                              └─────────────────┘
```

## Key Features

### Core Functionality
- **Multi-channel Notifications**: Telegram, Email
- **Customer-specific Data**: Order updates, status changes, personalized messages
- **Real-time Processing**: Asynchronous task processing with Celery
- **Caching Layer**: Redis for performance optimization
- **Queue Management**: Reliable message queuing for notification delivery

### Design Patterns
- **Factory Pattern**: Notification channel creation
- **Strategy Pattern**: Different notification delivery strategies
- **Observer Pattern**: Event-driven notification triggers
- **Repository Pattern**: Data access abstraction
- **Circuit Breaker**: Fault tolerance for external services

### Scalability & Reliability
- **Microservice Architecture**: Independent, scalable services
- **Load Balancing**: Nginx for distributing requests
- **Fault Tolerance**: Circuit breakers, retries, graceful degradation
- **Health Monitoring**: Service health checks and metrics
- **Rate Limiting**: Prevent API abuse and ensure fair usage

## Technology Stack

- **Backend**: Django 4.2+ with Django REST Framework
- **Cache & Queue**: Redis 7.0+
- **Task Queue**: Celery with Redis broker
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Load Balancer**: Nginx
- **Containerization**: Docker & Docker Compose
- **Notification APIs**: Telegram Bot API, SMTP for email

## Project Structure

```
notification_system/
├── apps/
│   ├── api_gateway/          # Main API gateway service
│   ├── notifications/        # Core notification service
│   ├── customers/           # Customer management
│   └── orders/              # Order management
├── core/
│   ├── patterns/            # Design pattern implementations
│   ├── middleware/          # Custom middleware
│   └── utils/               # Utility functions
├── config/
│   ├── settings/            # Environment-specific settings
│   └── celery.py           # Celery configuration
├── docker/                  # Docker configurations
├── nginx/                   # Nginx configuration
├── tests/                   # Comprehensive test suite
└── requirements/            # Environment-specific requirements
```

## Installation & Setup

### Prerequisites
- Python 3.9+
- Redis Server
- Docker & Docker Compose (optional)

### Local Development Setup

1. **Clone and navigate to project**
```bash
cd c:\Users\10710485\Desktop\python\notification
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements\development.txt
```

4. **Configure environment variables**
```bash
copy .env.example .env
# Edit .env with your configurations
```

5. **Run database migrations**
```bash
python manage.py migrate
```

6. **Start Redis server**
```bash
redis-server
```

7. **Start Celery worker**
```bash
celery -A config worker -l info
```

8. **Start Django server**
```bash
python manage.py runserver
```

### Docker Setup

```bash
docker-compose up --build
```

## API Endpoints

### Notification API
- `POST /api/v1/notifications/send/` - Send notification
- `GET /api/v1/notifications/status/{id}/` - Check notification status
- `GET /api/v1/notifications/history/` - Notification history

### Customer API
- `POST /api/v1/customers/` - Create customer
- `GET /api/v1/customers/{id}/` - Get customer details
- `PUT /api/v1/customers/{id}/` - Update customer

### Order API
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/{id}/` - Get order details
- `PUT /api/v1/orders/{id}/status/` - Update order status

## Configuration

### Environment Variables
```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Redis
REDIS_URL=redis://localhost:6379/0

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Testing

Run the comprehensive test suite:
```bash
python manage.py test
```

Run with coverage:
```bash
coverage run --source='.' manage.py test
coverage report
```

## Monitoring & Health Checks

- **Health Endpoint**: `/health/`
- **Metrics Endpoint**: `/metrics/`
- **Redis Health**: `/health/redis/`
- **Celery Health**: `/health/celery/`

## Deployment Considerations

### Production Checklist
- [ ] Switch to PostgreSQL database
- [ ] Configure proper Redis clustering
- [ ] Set up proper logging (ELK stack)
- [ ] Implement proper secret management
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure backup strategies

### Scaling Strategies
- **Horizontal Scaling**: Multiple Django instances behind load balancer
- **Database Scaling**: Read replicas, connection pooling
- **Cache Scaling**: Redis clustering, multiple cache layers
- **Queue Scaling**: Multiple Celery workers, queue partitioning

## System Workflow

### Notification Flow
1. **Order Created**: Customer places an order
2. **Event Triggered**: Order creation event published
3. **Notification Queued**: Celery task created for notification
4. **Channel Selection**: Factory pattern selects appropriate channels
5. **Message Personalization**: Customer-specific message generated
6. **Delivery Attempt**: Notification sent via selected channels
7. **Status Tracking**: Delivery status recorded and monitored
8. **Retry Logic**: Failed deliveries automatically retried

## Fault Tolerance & Error Handling

### Handled Scenarios
- **Rate Limiting**: Prevents spam and API abuse
- **Network Failures**: Retry mechanisms with exponential backoff
- **Service Unavailability**: Circuit breaker pattern
- **Message Deduplication**: Prevent duplicate notifications
- **Load Spikes**: Queue management and worker scaling
- **Data Consistency**: Atomic operations and transaction management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
