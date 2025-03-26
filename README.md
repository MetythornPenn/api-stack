# FastAPI Production Boilerplate

A production-ready FastAPI application boilerplate with PostgreSQL, pgvector, Oracle support, Redis caching, MinIO storage, and Kubernetes deployment.

## Features

- **Python 3.10+** with UV for package management
- **FastAPI** for API development with async support
- **PostgreSQL** with pgvector extension for vector database capabilities
- **Oracle** database support with easy switching between databases
- **SQLAlchemy** for ORM with async support
- **Alembic** for database migrations
- **Redis** for caching and rate limiting
- **MinIO** for object storage (images, videos, files)
- **Caddy** for reverse proxy and automatic SSL
- **Docker** and **Docker Compose** for containerization
- **Kubernetes** configurations for production deployment
- **Modular architecture** with each feature in a dedicated folder
- **Rate limiting** for API endpoints
- **Locust** for performance testing
- **Configurable environments** with .env files

## Project Structure

The project follows a modular architecture where each feature is stored in a single folder:

```
.
├── alembic/                      # Database migrations
├── app/                          # Main application
│   ├── api/                      # API endpoints
│   ├── core/                     # Core modules
│   ├── db/                       # Database related
│   ├── models/                   # SQLAlchemy models
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic
│   ├── utils/                    # Utility functions
│   └── main.py                   # FastAPI application creation
├── deployment/                   # Kubernetes deployment
├── performance/                  # Performance testing
├── scripts/                      # Utility scripts
├── tests/                        # Test suite
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- UV package manager (`pip install uv`)

### Setup Development Environment

1. Clone the repository:

```bash
git clone https://github.com/yourusername/fastapi-boilerplate.git
cd fastapi-boilerplate
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
uv pip install -e ".[dev]"
```

3. Start the development database services:

```bash
docker-compose -f docker-compose.db.yml up -d
```

4. Run database migrations:

```bash
alembic upgrade head
```

5. Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)  
API documentation at [http://localhost:8000/docs](http://localhost:8000/docs)

### Using Docker Compose

To run the entire application stack using Docker Compose:

```bash
# Build and run all services
docker-compose up -d --build
```

### Environment Configuration

The application uses environment-specific configuration files:

- `.env.local` - Local development settings
- `.env.prod` - Production settings

To switch between environments, set the `APP_ENV` variable:

```bash
# For local development (default)
export APP_ENV=local

# For production
export APP_ENV=prod
```

## Database

### PostgreSQL with pgvector

The boilerplate is configured to use PostgreSQL with the pgvector extension for vector operations. The extension is automatically enabled in the Docker setup.

### Switching to Oracle

To use Oracle instead of PostgreSQL:

1. Update the `DATABASE_TYPE` setting in your environment file:

```
DATABASE_TYPE=oracle
```

2. Configure Oracle connection details in the same file.

### Running Migrations

```bash
# Generate a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## API Documentation

When running in development mode, API documentation is available at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

In production mode, documentation is disabled by default.

## File Storage with MinIO

The boilerplate integrates MinIO for object storage:

- Files are stored in the configured MinIO bucket
- The `ItemService` includes methods to upload and manage images
- Presigned URLs can be generated for secure file access

## Caching with Redis

Redis caching is implemented using `fastapi-cache2`:

- Cached endpoints are decorated with `@cache()`
- Cache keys are automatically generated based on endpoint parameters
- Cache expiration is configurable in settings

## Performance Testing

Locust is included for load testing:

```bash
# Start the Locust web interface
cd performance
locust
```

Then open [http://localhost:8089](http://localhost:8089) to configure and run tests.

## Deployment

### Docker Deployment

```bash
# Build the Docker image
docker build -t yourregistry/api:latest .

# Push to your registry
docker push yourregistry/api:latest
```

### Kubernetes Deployment

Kubernetes configuration files are provided in the `deployment/` directory:

```bash
# Deploy to Kubernetes
kubectl apply -f deployment/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.