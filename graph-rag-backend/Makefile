.PHONY: help install dev test run docker-up docker-down clean lint format

help:
	@echo "Graph RAG Platform - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Install dev dependencies"
	@echo ""
	@echo "Running:"
	@echo "  make run          - Run the API server"
	@echo "  make demo         - Run demo script"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    - Start all services with Docker"
	@echo "  make docker-down  - Stop all Docker services"
	@echo "  make docker-logs  - View Docker logs"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - Run linting"
	@echo "  make format       - Format code"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Clean temporary files"
	@echo "  make reset-db     - Reset graph database"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

dev:
	@echo "Installing dev dependencies..."
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov black flake8 mypy
	@echo "✓ Dev dependencies installed"

run:
	@echo "Starting Graph RAG API server..."
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

demo:
	@echo "Running demo script..."
	python demo.py

docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d
	@echo "Waiting for services to start..."
	sleep 10
	@echo "Pulling Ollama model..."
	docker exec -it graphrag-ollama ollama pull llama2 || true
	@echo "✓ Services started"
	@echo ""
	@echo "Access points:"
	@echo "  API:         http://localhost:8000"
	@echo "  API Docs:    http://localhost:8000/docs"
	@echo "  Neo4j:       http://localhost:7474"

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down
	@echo "✓ Services stopped"

docker-logs:
	docker-compose logs -f

test:
	@echo "Running tests..."
	pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=services --cov-report=html --cov-report=term
	@echo "✓ Coverage report generated in htmlcov/"

lint:
	@echo "Running linting..."
	flake8 . --max-line-length=100 --exclude=venv,__pycache__
	@echo "✓ Linting complete"

format:
	@echo "Formatting code..."
	black . --exclude=venv
	@echo "✓ Code formatted"

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage
	@echo "✓ Cleaned"

reset-db:
	@echo "Resetting graph database..."
	curl -X POST http://localhost:8000/api/admin/reset
	@echo "✓ Database reset"

setup: install
	@echo "Running setup script..."
	chmod +x setup.sh
	./setup.sh

# Quick commands
up: docker-up
down: docker-down
logs: docker-logs