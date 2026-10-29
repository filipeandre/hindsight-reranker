@echo off
rem Starts the reranker service. Paths are relative to this file, so the folder can live anywhere.
rem Optional overrides: RERANKER_PORT (default 8787), RERANKER_MODEL, RERANKER_THREADS, RERANKER_BATCH.
set "HERE=%~dp0"
if "%RERANKER_PORT%"=="" set RERANKER_PORT=8787
set "HF_HOME=%HERE%hf"
rem Offline after the first model download, so boot does not depend on the network.
if exist "%HERE%hf\hub" (set HF_HUB_OFFLINE=1& set TRANSFORMERS_OFFLINE=1)
cd /d "%HERE%"
"%HERE%.venv\Scripts\python.exe" -m uvicorn server:app --host 0.0.0.0 --port %RERANKER_PORT% >> service.log 2>&1
