# Graph RAG Backend Architecture

This document provides a detailed overview of the backend architecture for the Graph RAG platform, including the data processing workflow, the agentic retrieval framework, and the roles of the various services.

## 1. Technology Stack

The backend is built on a modern Python stack designed for performance and scalability:

- **Web Framework**: FastAPI for building high-performance, asynchronous APIs.
- **Graph Database**: Neo4j for storing and querying the knowledge graph.
- **Data Validation**: Pydantic for robust data validation and settings management.
- **LLM Integration**: Direct integration with providers like Ollama and Groq via REST APIs.
- **Vector Embeddings**: Sentence-Transformers for creating dense vector representations of text.
- **Containerization**: Docker and Docker Compose for creating a reproducible and isolated environment.

## 2. Core Architecture

The backend is designed with a modular, service-oriented architecture that separates concerns into distinct layers:

```
┌───────────────────┐
│    FastAPI API    │  (main.py)
└─────────┬─────────┘
          │ (HTTP Requests)
┌─────────▼─────────┐
│   Service Layer   │  (services/*.py)
└─────────┬─────────┘
          │ (Data Operations)
┌─────────▼─────────┐
│    Data Layer     │  (Neo4j, Vector Store)
└───────────────────┘
```

- **API Layer (`main.py`)**: This is the entry point for all external requests. It defines the API endpoints, handles request validation using Pydantic models, and calls the appropriate services from the service layer.
- **Service Layer (`services/`)**: This is the core of the application, containing the business logic. Each service has a specific responsibility, such as processing documents or handling queries.
- **Data Layer**: This consists of the Neo4j database for the knowledge graph and a simple vector store for semantic search.

## 3. Data Ingestion Workflow

When a document is uploaded via the `/api/documents/upload` endpoint, it goes through a multi-stage pipeline orchestrated primarily by the `DocumentProcessor`.

1.  **Text Extraction (`DocumentProcessor`)**: The raw file content is processed to extract plain text. It supports PDF, DOCX, and TXT files.

2.  **Text Chunking (`DocumentProcessor`)**: The extracted text is split into smaller, semantically meaningful chunks. This is crucial for generating focused embeddings.

3.  **Ontology Extraction (`DocumentProcessor` -> LLM)**: A sample of the text is sent to a Large Language Model (LLM) with a specific prompt asking it to identify key **entities** (e.g., people, organizations, locations) and the **relationships** between them. The LLM returns this information in a structured JSON format.

4.  **Embedding Generation (`DocumentProcessor`)**: The `sentence-transformers` library is used to convert the text chunks and extracted entity names into numerical vector embeddings.

5.  **Graph Construction (`GraphConstructor`)**: This service takes the extracted entities and relationships and populates the Neo4j database. It creates nodes for entities and edges for relationships, linking them together to form the knowledge graph.

6.  **Entity Resolution (`EntityResolver`)**: After the graph is constructed, this service runs to find and merge duplicate entities. It uses string similarity algorithms to identify nodes that likely refer to the same entity, ensuring the graph remains clean.

## 4. Agentic Retrieval Framework

When a query is submitted to the `/api/query` endpoint, the `AgenticRetrieval` service manages a team of specialized agents to find the best possible answer. This framework is designed to be more robust than a single retrieval method.

Here are the key agents and their roles:

1.  **Coordinator Agent**: This is the "manager" of the team. It first analyzes the user's query to understand its intent and complexity. Based on this analysis, it decides which other agents to call upon to gather evidence.

2.  **Vector Search Agent**: This agent is responsible for semantic search. It takes the user's query, converts it into a vector embedding, and searches the vector store for text chunks that are most semantically similar.

3.  **Graph Traversal Agent**: This agent explores the knowledge graph. It looks for entities mentioned in the query and traverses the graph to find related nodes and paths, uncovering connections that a simple text search would miss.

4.  **Filter Agent**: This agent applies structured filters based on metadata. For example, if the query is "Who works in the Delhi office?", this agent can filter for nodes with a `location` property of "Delhi".

5.  **Synthesis Agent**: After the other agents have gathered evidence, the Synthesis Agent collects all the pieces of information. It then uses an LLM to analyze this combined context and generate a single, coherent, human-readable answer. It is also responsible for calculating a final confidence score.

This multi-agent approach allows the system to tackle complex queries by combining the strengths of semantic search (for finding relevant concepts) and graph traversal (for understanding explicit relationships).

## 5. Service Layer Deep Dive

- **`document_processor.py`**: Orchestrates the entire data ingestion pipeline as described above.
- **`graph_constructor.py`**: Responsible for translating the extracted ontology into graph structures in Neo4j.
- **`graph_service.py`**: Provides a unified, abstract interface for all database interactions. It contains a `Neo4jAdapter` and an `InMemoryGraphDB` adapter, making it easy to switch between databases.
- **`agentic_retrieval.py`**: Contains the logic for the agentic framework, including the implementation of all the agents.
- **`entity_resolver.py`**: Handles the logic for finding and merging duplicate entities to maintain graph quality.
- **`ontology_manager.py`**: Manages the schema of the graph and can use an LLM to suggest improvements.
- **`metrics_collector.py`**: A simple service for tracking application performance and usage statistics.
- **`cypher_generator.py`**: A service designed to translate natural language queries directly into Neo4j Cypher queries (Note: this is part of the design but may not be fully integrated into the primary query flow).
