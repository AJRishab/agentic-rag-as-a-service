# Graph RAG Frontend Architecture

This document provides a detailed overview of the frontend architecture for the Graph RAG platform.

## 1. Technology Stack

The frontend is a modern, single-page application (SPA) built with a focus on user experience and maintainability.

- **Framework**: React (v18) for building the user interface.
- **Build Tool**: Create React App (`react-scripts`) for a streamlined development and build process.
- **Styling**: Tailwind CSS for a utility-first styling workflow. The configuration is in `tailwind.config.js`.
- **Icons**: Lucide React for a lightweight and consistent set of SVG icons.
- **API Communication**: Native `fetch` API for making asynchronous requests to the backend.

## 2. Project Structure

The frontend code is organized in a standard Create React App structure:

- **`public/`**: Contains the main `index.html` template, `manifest.json`, and other static assets.
- **`src/`**: Contains all the React application source code.
  - **`App.js`**: The main and currently the only major component, which contains all the UI logic and state management.
  - **`index.js`**: The entry point for the React application, where the `App` component is rendered into the DOM.
  - **`index.css`**: The global stylesheet where Tailwind CSS directives are imported.

## 3. Core Architecture & State Management

The application is currently built around a single, powerful root component: `App.js`. This component is responsible for:

- **UI Rendering**: It contains the JSX for the entire user interface, including the header, navigation tabs, and the content for each tab.
- **State Management**: It uses React Hooks (`useState` and `useEffect`) to manage the application's entire state. Key state variables include:
  - `activeTab`: Tracks which tab the user is currently viewing ('upload', 'graph', or 'query').
  - `documents`: An array holding the list of processed documents.
  - `graphData`: Stores statistics and visualization data for the knowledge graph.
  - `query` & `queryResult`: Manages the user's input query and the final answer from the backend.
  - `processing`: A boolean flag to indicate when an API call (like an upload or query) is in progress, used for showing loading indicators.
  - `agentActivity`: An array that stores the steps of a processing pipeline or reasoning chain to display to the user in real-time.
  - `apiStatus` & `error`: Tracks the connection status of the backend and displays any errors.
- **Side Effects**: The `useEffect` hook is used to perform actions when the component mounts, such as checking the backend API health and loading initial data (documents and graph stats).

## 4. UI/UX Workflow

The user interface is designed to be intuitive and provide real-time feedback.

1.  **Tabbed Navigation**: The user navigates between three main sections:
    - **Document Upload**: Where users can upload files to be processed by the backend.
    - **Knowledge Graph**: Displays statistics and a simplified visualization of the constructed graph.
    - **Agentic Query**: The main interaction point for asking natural language questions.

2.  **Real-time Feedback**: When a user performs an action like uploading a document or submitting a query, the UI provides immediate feedback:
    - A loading indicator shows that a process is running.
    - The `agentActivity` state is used to display the backend's processing steps (e.g., "Document Parser", "Vector Search Agent") as they happen, giving the user visibility into the workflow.

3.  **Styling**: The application uses a dark theme with purple and pink accent colors, defined in `tailwind.config.js`. It employs "glass morphism" effects (blurred, semi-transparent backgrounds) to create a modern look and feel.

## 5. API Integration

The frontend is decoupled from the backend and communicates via a REST API.

- **API Client**: The native `fetch` API is used for all HTTP requests.
- **Backend URL**: The base URL for the backend is defined in a constant `API_BASE_URL` at the top of `App.js`. For development, this is set to `http://localhost:8000`.
- **Key Functions**:
  - `checkApiHealth()`: Pings the backend's `/health` endpoint to ensure it's running.
  - `loadDocuments()` & `loadGraphStats()`: Fetch initial data when the application loads.
  - `handleDocumentUpload()`: Constructs a `FormData` object to send the uploaded file to the `/api/documents/upload` endpoint.
  - `handleQuery()`: Sends the user's question to the `/api/query` endpoint and processes the response.

## 6. Deployment

The frontend is a static application that can be easily deployed.

- **Build Process**: Running `npm run build` creates a production-ready, optimized build in the `build/` directory.
- **Production Server**: The provided `Dockerfile` uses a multi-stage build. It first builds the React app and then copies the static files into a lightweight **Nginx** container. The `nginx.conf` file is configured to serve the application and handle client-side routing correctly.
