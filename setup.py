#!/usr/bin/env python3
"""
FastAPI Boilerplate - Project Structure Generator

This script creates the directory structure and empty files
for the FastAPI boilerplate project.
"""

import os
import sys
from pathlib import Path


class TerminalColors:
    """Terminal colors for prettier output."""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'


def print_colored(text, color):
    """Print colored text to the terminal."""
    print(f"{color}{text}{TerminalColors.END}")


def create_directory(path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print_colored(f"Created directory: {path}", TerminalColors.GREEN)
    else:
        print_colored(f"Directory already exists: {path}", TerminalColors.YELLOW)


def create_file(path):
    """Create an empty file if it doesn't exist."""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            pass  # Create an empty file
        print_colored(f"Created file: {path}", TerminalColors.GREEN)
    else:
        print_colored(f"File already exists: {path}", TerminalColors.YELLOW)


def create_file_with_content(path, content):
    """Create a file with content if it doesn't exist."""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(content)
        print_colored(f"Created file with content: {path}", TerminalColors.GREEN)
    else:
        print_colored(f"File already exists: {path}", TerminalColors.YELLOW)


def main():
    """Main function to create the project structure."""
    # Project root directory (current directory)
    root_dir = os.getcwd()
    
    # Confirm before proceeding
    print_colored("This script will create the folder structure and files for the FastAPI boilerplate.", TerminalColors.BLUE)
    print_colored("It will not overwrite existing files.", TerminalColors.YELLOW)
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print_colored("Aborted.", TerminalColors.RED)
        sys.exit(1)
    
    print_colored("\nCreating project structure for: fastapi-boilerplate\n", TerminalColors.BLUE)
    
    # Create directory structure
    directories = [
        # App structure
        "app",
        "app/core",
        "app/api",
        "app/api/v1",
        "app/api/v1/items",
        "app/api/v1/auth",
        "app/services",
        "app/models",
        "app/db",
        "app/db/migrations",
        "app/db/migrations/versions",
        "app/utils",
        
        # Docker files
        "docker",
        "docker/api",
        "docker/caddy",
        
        # Deployment files
        "deployment",
        "deployment/k8s",
        "deployment/helm",
        
        # Other directories
        "performance",
        "scripts",
        "tests",
        "tests/api",
        "tests/core",
        "tests/services",
        "tests/utils",
        "logs",
        "backups",
    ]
    
    # Create directories
    for directory in directories:
        create_directory(os.path.join(root_dir, directory))
    
    # Define files to create
    files = [
        # App core files
        "app/__init__.py",
        "app/main.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/db.py",
        "app/core/exceptions.py",
        "app/core/logging.py",
        "app/core/security.py",
        
        # API structure
        "app/api/__init__.py",
        "app/api/deps.py",
        "app/api/router.py",
        "app/api/v1/__init__.py",
        
        # Items module
        "app/api/v1/items/__init__.py",
        "app/api/v1/items/models.py",
        "app/api/v1/items/router.py",
        "app/api/v1/items/schemas.py",
        "app/api/v1/items/service.py",
        "app/api/v1/items/utils.py",
        
        # Auth module
        "app/api/v1/auth/__init__.py",
        "app/api/v1/auth/models.py",
        "app/api/v1/auth/router.py",
        "app/api/v1/auth/schemas.py",
        "app/api/v1/auth/service.py",
        "app/api/v1/auth/utils.py",
        
        # Services
        "app/services/__init__.py",
        "app/services/cache.py",
        "app/services/minio.py",
        "app/services/ratelimit.py",
        "app/services/redis.py",
        
        # Models
        "app/models/__init__.py",
        "app/models/base.py",
        
        # Database files
        "app/db/__init__.py",
        "app/db/base.py",
        "app/db/factories.py",
        "app/db/migrations/env.py",
        "app/db/migrations/README",
        "app/db/migrations/script.py.mako",
        "app/db/migrations/versions/.gitkeep",
        
        # Utils
        "app/utils/__init__.py",
        "app/utils/common.py",
        
        # Docker files
        "docker/api/Dockerfile",
        "docker/caddy/Caddyfile",
        
        # Deployment files
        "deployment/k8s/api-deployment.yaml",
        "deployment/k8s/api-service.yaml",
        "deployment/k8s/caddy-configmap.yaml",
        "deployment/k8s/caddy-deployment.yaml",
        "deployment/k8s/caddy-pvc.yaml",
        "deployment/k8s/caddy-service.yaml",
        "deployment/k8s/configmap.yaml",
        "deployment/k8s/ingress.yaml",
        "deployment/k8s/minio-deployment.yaml",
        "deployment/k8s/minio-pvc.yaml",
        "deployment/k8s/minio-service.yaml",
        "deployment/k8s/namespace.yaml",
        "deployment/k8s/postgres-deployment.yaml",
        "deployment/k8s/postgres-pvc.yaml",
        "deployment/k8s/postgres-service.yaml",
        "deployment/k8s/redis-deployment.yaml",
        "deployment/k8s/redis-pvc.yaml",
        "deployment/k8s/redis-service.yaml",
        "deployment/k8s/secrets.yaml",
        "deployment/helm/.gitkeep",
        
        # Performance test files
        "performance/locustfile.py",
        
        # Scripts
        "scripts/create_dummy_data.py",
        "scripts/backup_db.py",
        "scripts/generate_models.py",
        
        # Test files
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/api/__init__.py",
        "tests/api/test_items.py",
        "tests/api/test_auth.py",
        "tests/core/__init__.py",
        "tests/core/test_config.py",
        "tests/services/__init__.py",
        "tests/services/test_cache.py",
        "tests/utils/__init__.py",
        
        # Configuration files
        ".env.local",
        ".env.prod",
        "docker-compose.db.yml",
        "docker-compose.yml",
        "pyproject.toml",
        "uvproject.toml",
        "alembic.ini",
        "Makefile",
        ".gitignore",
    ]
    
    # Create empty files
    for file in files:
        create_file(os.path.join(root_dir, file))
    
    # Create files with content
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
coverage.xml
.coverage
htmlcov/

# Virtual Environments
venv/
.venv/
env/
.env/

# Environment variables
.env
.env.local
.env.prod
.env.dev
.env.test

# Logs
logs/
*.log

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Backups
backups/
*.bak
*.dmp
*.dump
*.sql
*.gz

# Docker volumes
.docker-data/

# k8s secrets
*kubeconfig*
*kube-config*
"""
    
    readme_content = """# FastAPI Boilerplate

A production-ready FastAPI boilerplate with PostgreSQL, Redis, MinIO, and more.

## Setup

1. Create a virtual environment:
   ```bash
   uv venv --python 3.10 .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
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
"""
    
    create_file_with_content(os.path.join(root_dir, ".gitignore"), gitignore_content)
    create_file_with_content(os.path.join(root_dir, "README.md"), readme_content)
    
    # Success message and next steps
    print_colored("\nProject structure created successfully!", TerminalColors.GREEN)
    print_colored("\nNext steps:", TerminalColors.BLUE)
    print("1. Copy and paste the code from the provided artifacts into the corresponding files")
    print("2. Create a virtual environment: uv venv --python 3.10 .venv")
    print("3. Activate the virtual environment: source .venv/bin/activate")
    print("4. Install dependencies: uv pip install -e .")
    print("5. Start the database services: docker-compose -f docker-compose.db.yml up -d")
    print("6. Run migrations: alembic upgrade head")
    print("7. Start the application: python -m app.main")
    print("\nFor more commands, see the Makefile: make help")


if __name__ == "__main__":
    main()