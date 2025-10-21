@echo off

REM Graph RAG - Start both Backend and Frontend

SETLOCAL ENABLEDELAYEDEXPANSION

REM Start Backend
start "Graph RAG Backend" powershell -NoExit -Command "cd '%CD%\graph-rag-backend'; uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Small delay to let backend start
ping -n 5 127.0.0.1 > nul

REM Start Frontend
start "Graph RAG Frontend" powershell -NoExit -Command "cd '%CD%\graph-rag-frontend'; npm start"

ECHO Both Backend (http://localhost:8000) and Frontend (http://localhost:3000) are starting...
ECHO Close these windows to stop the services.

ENDLOCAL
