# FastAPI Boilerplate

A production-ready FastAPI boilerplate with PostgreSQL, Redis, MinIO, and more.

## Features

- 🚀 FastAPI with async support
- 🔒 OAuth2 authentication with JWT tokens
- 📊 PostgreSQL with pgvector for vector database capabilities
- 🔄 ORM with SQLAlchemy and Alembic for migrations
- 📦 Redis for caching and rate limiting
- 📁 MinIO for object storage
- 🌐 Caddy for reverse proxy and SSL
- 📋 Fully modular architecture
- 🐳 Docker and Kubernetes ready
- 📈 Performance testing with Locust
- 🔧 Configurable for local development and production

## Quick Start

The project includes a comprehensive Makefile with commands for all development and deployment tasks.

### First-Time Setup

```bash
# Setup the entire development environment (creates venv, installs dependencies, starts DB, and more)
make setup-all

# Start the application with auto-reload
make start-reload
```

### Common Commands

```bash
# See all available commands
make help

# Start database containers
make db-up

# Stop database containers
make db-down

# Run database migrations
make db-migrate

# Create dummy data for testing
make create-dummy-data

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Build Docker image
make docker-build

# Start all Docker containers
make docker-compose-up

# Stop all Docker containers
make docker-compose-down
```

## Development Workflow

1. **Setup environment for first time**: `make setup-all`
2. **Start development server**: `make start-reload`
3. **Format code and check linting**: `make format lint`
4. **Run tests**: `make test`
5. **After changing models, create migration**: `make db-auto-migrate`

## Deployment Options

### Docker Deployment

```bash
# Build and start all containers
make docker-compose-up
```

### Kubernetes Deployment

```bash
# Apply Kubernetes configuration
make k8s-apply
```

## Project Structure

```
fastapi-boilerplate/
├── app/
│   ├── core/           # Core functionality
│   ├── api/            # API endpoints
│   ├── services/       # Business logic services
│   ├── models/         # Database models
│   ├── db/             # Database configuration
│   ├── utils/          # Utilities
│   └── main.py         # Application entry point
├── docker/             # Docker configuration
├── deployment/         # Kubernetes configuration
├── performance/        # Load testing
├── scripts/            # Utility scripts
└── tests/              # Tests
```

## API Documentation

When running in development mode, API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Ensure code quality before committing: `make check-all`
2. Create tests for new features
3. Follow the existing project structure

## License

This project is licensed under the MIT License - see the LICENSE file for details.