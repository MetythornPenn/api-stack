# FastAPI Boilerplate

A production-ready FastAPI boilerplate with PostgreSQL, Redis, MinIO, and more.

## Setup

1. Create a virtual environment:
   ```bash
   uv venv --python 3.10 .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   uv pip install -e .
   ```

3. Start the database services:
   ```bash
   docker-compose -f docker-compose.db.yml up -d
   ```

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the application:
   ```bash
   python -m app.main
   ```

## Documentation

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
