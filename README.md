# Graph RAG Platform

This repository contains a production-ready **Graph RAG (Retrieval-Augmented Generation)** platform. It features a modern React frontend and a powerful FastAPI backend, designed to combine knowledge graphs, vector embeddings, and agentic reasoning for intelligent information retrieval.

## 🌟 Core Features

- **Automatic Knowledge Graph Construction**: Ingests documents (PDF, DOCX, TXT) and uses an LLM to automatically extract entities and relationships, building a comprehensive knowledge graph.
- **Multi-Modal Retrieval**: Leverages a combination of vector similarity search, graph traversal, and metadata filtering to find the most relevant information.
- **Agentic Reasoning**: Employs a multi-agent system to analyze user queries, plan retrieval strategies, and synthesize clear, accurate answers from the retrieved data.
- **Modern Tech Stack**: Built with FastAPI and React, containerized with Docker, and orchestrated with Docker Compose.
- **Interactive UI**: A user-friendly interface to upload documents, explore the knowledge graph, and perform intelligent queries.

## 🛠️ Frameworks & Technologies

- **Backend**: Python, FastAPI
- **Frontend**: JavaScript, React, Tailwind CSS
- **Graph Database**: Neo4j (Community Edition)
- **LLM Integration**: Ollama (for local LLMs like Llama 2)
- **Vector Embeddings**: Sentence Transformers
- **Containerization**: Docker, Docker Compose
- **Development**: Makefile for streamlined commands

## 🚀 Getting Started

Choose one of the following methods to get the platform running.

### Option 1: With Docker & Make (Recommended)

This is the easiest and most reliable way to start the entire application stack.

**Prerequisites:**
- Docker and Docker Compose
- `make` command
- Git

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd graph-rag
    ```

2.  **Start all services:**
    This single command builds the Docker images, starts all containers (backend, frontend, Neo4j, Ollama), and pulls the required LLM model.
    ```bash
    make docker-up
    ```

3.  **Access the platform:**
    - **Frontend**: [http://localhost:3000](http://localhost:3000)
    - **Backend API**: [http://localhost:8000](http://localhost:8000)
    - **Neo4j Browser**: [http://localhost:7474](http://localhost:7474)

### Option 2: Local Development with Make (No Docker)

Use this method if you have `make` but prefer to run the services directly on your machine.

**Prerequisites:**
- Python 3.8+ and Node.js 16+
- `make` command

**Steps:**

1.  **Install all dependencies:**
    This command installs all backend (pip) and frontend (npm) dependencies.
    ```bash
    make setup
    ```

2.  **Start development servers:**
    This starts both the backend and frontend servers concurrently.
    ```bash
    make dev
    ```

### Option 3: Manual Local Development (No Docker, No Make)

Use this method if you do not have `make` installed.

**Prerequisites:**
- Python 3.8+ and Node.js 16+

**Steps:**

1.  **Install backend dependencies:**
    ```bash
    cd graph-rag-backend
    pip install -r requirements.txt
    cd ..
    ```

2.  **Install frontend dependencies:**
    ```bash
    cd graph-rag-frontend
    npm install
    cd ..
    ```

3.  **Run the backend server:**
    In a new terminal window, run:
    ```bash
    cd graph-rag-backend
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ```

4.  **Run the frontend server:**
    In a separate terminal window, run:
    ```bash
    cd graph-rag-frontend
    npm start
    ```

## ⚙️ Available Commands

A `Makefile` in the root directory provides several useful commands for managing the project:

- `make docker-up`: Start the complete application stack using Docker.
- `make docker-down`: Stop all running Docker containers.
- `make setup`: Install all project dependencies.
- `make dev`: Start the frontend and backend for local development.
- `make test`: Run the test suite for the backend.
- `make lint`: Run the linter to check code quality.
- `make format`: Format the code according to project standards.

## 📁 Project Structure

```
graph-rag/
│
├── graph-rag-backend/      # FastAPI Backend
│   ├── services/           # Core logic for RAG pipeline
│   ├── src/                # Main application source
│   ├── tests/              # Backend test suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── graph-rag-frontend/     # React Frontend
│   ├── src/                # Main application source
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.full.yml # Docker Compose for the full stack
├── Makefile                # Convenient development commands
└── README.md               # This file
```