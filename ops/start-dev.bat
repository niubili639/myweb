@echo off
setlocal

rem Resolve repo root (parent of ops)
for %%I in ("%~dp0..") do set ROOT=%%~fI
set API_DIR=%ROOT%\apps\api
set WEB_DIR=%ROOT%\apps\web

echo [+] Starting backend (FastAPI)...
start "myweb-api" cmd /k ^
    "cd /d \"%API_DIR%\" ^
    ^&^& if not exist .venv (python -m venv .venv) ^
    ^&^& call .venv\Scripts\activate ^
    ^&^& if not exist .env (copy .env.example .env) ^
    ^&^& pip install -e . ^
    ^&^& uvicorn app.main:app --reload"

echo [+] Starting frontend (Vite)...
start "myweb-web" cmd /k ^
    "cd /d \"%WEB_DIR%\" ^
    ^&^& if not exist node_modules (npm install) ^
    ^&^& npm run dev -- --host"

echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo Windows one-click dev startup launched in two terminals.

endlocal
