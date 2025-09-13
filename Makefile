# Cosmic Django Project Makefile
.PHONY: help install dev-install clean test shell migrate runserver check format lint docker-build docker-run

# Default target
help:
	@echo "Cosmic Django Project Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install      - Install production dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  clean        - Clean cache and temporary files"
	@echo ""
	@echo "Development Commands:"
	@echo "  shell        - Open Django shell_plus"
	@echo "  runserver    - Start Django development server"
	@echo "  migrate      - Run Django migrations"
	@echo "  makemigrations - Create new Django migrations"
	@echo "  check        - Run Django system checks"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test         - Run all tests"
	@echo "  test-verbose - Run tests with verbose output"
	@echo "  test-file    - Run specific test file (usage: make test-file FILE=path/to/test.py)"
	@echo "  test-pattern - Run tests matching pattern (usage: make test-pattern PATTERN=test_name)"
	@echo "  format       - Format code with ruff"
	@echo "  lint         - Lint code with ruff"
	@echo "  lint-fix     - Fix linting issues automatically"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo ""

# Environment Variables
export DJANGO_SETTINGS_MODULE ?= cosmic.settings.base
export DJANGO_DEBUG ?= True
export DJANGO_SECRET_KEY ?= django-insecure-zq5&^7efwwa)@zy#n9(w#(pxk&=jpg$$_%o(%5(z1z07f_$$l*(k
export DJANGO_ALLOWED_HOSTS ?= localhost,127.0.0.1,0.0.0.0
export DATABASE_URL ?= sqlite:///db.sqlite3
export PYTHONPATH ?= .

# Project paths
MANAGE_PY = cosmic/manage.py
DJANGO_APP = cosmic

# Setup Commands
install:
	@echo "Installing production dependencies..."
	uv sync --no-dev

dev-install:
	@echo "Installing development dependencies..."
	uv sync

clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Development Commands
shell:
	@echo "Starting Django shell_plus..."
	uv run python $(MANAGE_PY) shell_plus

runserver:
	@echo "Starting Django development server..."
	uv run python $(MANAGE_PY) runserver 0.0.0.0:8000

migrate:
	@echo "Running Django migrations..."
	uv run python $(MANAGE_PY) migrate

makemigrations:
	@echo "Creating Django migrations..."
	uv run python $(MANAGE_PY) makemigrations

check:
	@echo "Running Django system checks..."
	uv run python $(MANAGE_PY) check

# Testing & Quality Commands
test:
	@echo "Running tests..."
	uv run pytest

test-verbose:
	@echo "Running tests with verbose output..."
	uv run pytest -v -s

test-coverage:
	@echo "Running tests with coverage..."
	uv run pytest --cov=allocation --cov=cosmic --cov-report=html --cov-report=term

test-file:
	@echo "Running specific test file: $(FILE)"
	@if [ -z "$(FILE)" ]; then echo "Usage: make test-file FILE=path/to/test_file.py"; exit 1; fi
	uv run pytest $(FILE)

test-pattern:
	@echo "Running tests matching pattern: $(PATTERN)"
	@if [ -z "$(PATTERN)" ]; then echo "Usage: make test-pattern PATTERN=test_name_pattern"; exit 1; fi
	uv run pytest -k $(PATTERN)

format:
	@echo "Formatting code with ruff..."
	uv run ruff format .

lint:
	@echo "Linting code with ruff..."
	uv run ruff check .

lint-fix:
	@echo "Fixing linting issues automatically..."
	uv run ruff check --fix .

# Docker Commands
docker-build:
	@echo "Building Docker image..."
	docker build -t cosmic-django .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 -e DJANGO_DEBUG=True cosmic-django

# Utility Commands
reset-db:
	@echo "Resetting database..."
	rm -f $(DJANGO_APP)/db.sqlite3
	$(MAKE) migrate

superuser:
	@echo "Creating Django superuser..."
	uv run python $(MANAGE_PY) createsuperuser

collectstatic:
	@echo "Collecting static files..."
	uv run python $(MANAGE_PY) collectstatic --noinput

# Development workflow shortcuts
dev-setup: dev-install migrate
	@echo "Development environment setup complete!"

dev-reset: clean reset-db
	@echo "Development environment reset complete!"

# Quality check pipeline
quality: lint format test
	@echo "Quality checks complete!"
