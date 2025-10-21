.PHONY: help install-backend install-frontend dev test run docker-up docker-down clean lint format setup

help:
	@echo "Graph RAG Platform - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup           - Complete setup (backend + frontend)"
	@echo "  make install-backend - Install backend dependencies"
	@echo "  make install-frontend- Install frontend dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev             - Start both frontend and backend in dev mode"
	@echo "  make run-backend     - Run backend only"
	@echo "  make run-frontend    - Run frontend only"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up       - Start all services with Docker"
	@echo "  make docker-down     - Stop all Docker services"
	@echo "  make docker-logs     - View Docker logs"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run all tests"
	@echo "  make test-backend    - Run backend tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            - Run linting"
	@echo "  make format          - Format code"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           - Clean temporary files"
	@echo "  make reset-db        - Reset graph database"

setup:
	@echo "Setting up Graph RAG Platform..."
	@echo "Installing backend dependencies..."
	cd graph-rag-backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd graph-rag-frontend && npm install
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Start backend: make run-backend"
	@echo "  2. Start frontend: make run-frontend"
	@echo "  3. Or use Docker: make docker-up"

install-backend:
	@echo "Installing backend dependencies..."
	cd graph-rag-backend && pip install -r requirements.txt
	@echo "✓ Backend dependencies installed"

install-frontend:
	@echo "Installing frontend dependencies..."
	cd graph-rag-frontend && npm install
	@echo "✓ Frontend dependencies installed"

dev:
	@echo "Starting development environment..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:3000"
	@echo ""
	@echo "Press Ctrl+C to stop both services"
	@echo ""
	@trap 'kill %1; kill %2' INT; \
	cd graph-rag-backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000 & \
	cd graph-rag-frontend && npm start & \
	wait

run-backend:
	@echo "Starting Graph RAG Backend..."
	cd graph-rag-backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	@echo "Starting Graph RAG Frontend..."
	cd graph-rag-frontend && npm start

docker-up:
	@echo "Starting Docker services..."
	docker-compose -f docker-compose.full.yml up -d
	@echo "Waiting for services to start..."
	sleep 10
	@echo "Pulling Ollama model..."
	docker exec -it graphrag-ollama ollama pull llama2 || true
	@echo "✓ Services started"
	@echo ""
	@echo "Access points:"
	@echo "  Frontend:    http://localhost:3000"
	@echo "  Backend API: http://localhost:8000"
	@echo "  API Docs:    http://localhost:8000/docs"
	@echo "  Neo4j:       http://localhost:7474"

docker-down:
	@echo "Stopping Docker services..."
	docker-compose -f docker-compose.full.yml down
	@echo "✓ Services stopped"

docker-logs:
	docker-compose -f docker-compose.full.yml logs -f

test:
	@echo "Running backend tests..."
	cd graph-rag-backend && pytest tests/ -v
	@echo "Running frontend tests..."
	cd graph-rag-frontend && npm test -- --watchAll=false

test-backend:
	@echo "Running backend tests..."
	cd graph-rag-backend && pytest tests/ -v

lint:
	@echo "Running backend linting..."
	cd graph-rag-backend && flake8 . --max-line-length=100 --exclude=venv,__pycache__
	@echo "Running frontend linting..."
	cd graph-rag-frontend && npm run lint || echo "No lint script found"

format:
	@echo "Formatting backend code..."
	cd graph-rag-backend && black . --exclude=venv
	@echo "Formatting frontend code..."
	cd graph-rag-frontend && npm run format || echo "No format script found"

clean:
	@echo "Cleaning temporary files..."
	@echo "Backend cleanup..."
	cd graph-rag-backend && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	cd graph-rag-backend && find . -type f -name "*.pyc" -delete
	cd graph-rag-backend && find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	cd graph-rag-backend && find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	cd graph-rag-backend && rm -rf htmlcov/ .coverage
	@echo "Frontend cleanup..."
	cd graph-rag-frontend && rm -rf node_modules/ build/ .eslintcache
	@echo "✓ Cleaned"

reset-db:
	@echo "Resetting graph database..."
	curl -X POST http://localhost:8000/api/admin/reset
	@echo "✓ Database reset"

# Quick commands
up: docker-up
down: docker-down
logs: docker-logs
