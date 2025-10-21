#!/bin/bash

# Graph RAG Backend Setup Script
# This script sets up the entire Graph RAG environment

set -e

echo "======================================"
echo "Graph RAG Backend Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if Python is installed
echo "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
print_status "Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3."
    exit 1
fi
print_status "pip3 found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip
print_status "pip upgraded"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt
print_status "Dependencies installed"

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p vector_store
mkdir -p logs
mkdir -p services
print_status "Directories created"

# Create services __init__.py
touch services/__init__.py

# Copy environment file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    print_status ".env file created"
    print_warning "Please edit .env file with your configuration"
else
    print_warning ".env file already exists. Skipping."
fi

# Check if Docker is available
echo ""
echo "Checking for Docker..."
if command -v docker &> /dev/null; then
    print_status "Docker found: $(docker --version)"
    
    read -p "Do you want to start services with Docker Compose? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting Docker services..."
        docker-compose up -d
        print_status "Docker services started"
        
        echo ""
        echo "Waiting for services to be ready..."
        sleep 10
        
        echo ""
        echo "Pulling Ollama model..."
        docker exec -it graphrag-ollama ollama pull llama2
        print_status "Ollama model ready"
    fi
else
    print_warning "Docker not found. Skipping Docker setup."
    print_warning "You can install Docker from: https://docs.docker.com/get-docker/"
fi

# Check if Neo4j is available
echo ""
echo "Checking for Neo4j..."
if curl -s http://localhost:7474 > /dev/null 2>&1; then
    print_status "Neo4j is running at http://localhost:7474"
else
    print_warning "Neo4j is not running. System will use in-memory graph."
    print_warning "To use Neo4j, either:"
    print_warning "  1. Start with Docker: docker-compose up -d neo4j"
    print_warning "  2. Download from: https://neo4j.com/download/"
fi

# Check if Ollama is available
echo ""
echo "Checking for Ollama..."
if curl -s http://localhost:11434 > /dev/null 2>&1; then
    print_status "Ollama is running at http://localhost:11434"
else
    print_warning "Ollama is not running. LLM features will be limited."
    print_warning "To use Ollama:"
    print_warning "  1. Start with Docker: docker-compose up -d ollama"
    print_warning "  2. Download from: https://ollama.ai/"
fi

# Run tests
echo ""
read -p "Do you want to run tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running tests..."
    pytest tests/ -v
    print_status "Tests completed"
fi

# Final instructions
echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Review and update .env file with your configuration"
echo "2. Start the API server:"
echo "   $ source venv/bin/activate"
echo "   $ uvicorn main:app --reload"
echo ""
echo "3. Access the services:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Neo4j Browser: http://localhost:7474"
echo ""
echo "4. Upload a document:"
echo "   $ curl -X POST http://localhost:8000/api/documents/upload \\"
echo "     -F \"file=@your_document.pdf\""
echo ""
echo "5. Query the knowledge base:"
echo "   $ curl -X POST http://localhost:8000/api/query \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"query\": \"Your question here\"}'"
echo ""
echo "For more information, see README.md"
echo ""