# Algorithmic Trading Application

A real-time algorithmic trading application that implements SMA crossover strategy for cryptocurrency trading.

## Features

- Real-time orderbook data ingestion from Binance
- SMA crossover strategy implementation
- MongoDB for data persistence
- Redis for caching and messaging
- Prometheus metrics integration
- Docker containerization
- Health monitoring endpoints

## Prerequisites

- Docker and Docker Compose

## Setup

1. Clone the repository
2. Build and start the application:
```bash
docker-compose up --build
```

## Architecture

The application follows a modular architecture:

- `app/core/`: Core configuration and settings
- `app/models/`: Data models
- `app/services/`: Business logic services
- `app/api/`: API endpoints

## Monitoring

The application exposes several monitoring endpoints:

- Health check: `GET /health`
- Trading metrics: `GET /metrics/trading`
- System metrics: `GET /metrics/system`
- Prometheus metrics: `http://localhost:9090`

## Scalability and Fault Tolerance

The application is designed with the following features:

- Automatic WebSocket reconnection with exponential backoff
- Database connection pooling
- Containerization for easy scaling
- Health checks for Kubernetes readiness/liveness

## Security Considerations

- API credentials stored in environment variables
- No sensitive data logged
- Connection encryption for external APIs
- Input validation and sanitization

## Testing

Run the tests using:
```bash
docker-compose run app pytest
```