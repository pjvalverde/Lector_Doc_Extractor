@echo off
echo ========================================
echo  Lector Doc Extractor - Iniciar app
echo ========================================

REM Check .env exists
if not exist ".env" (
    echo [ERROR] Falta el archivo .env
    echo Copia .env.example a .env y agrega tu GOOGLE_API_KEY
    pause
    exit /b 1
)

echo [1/2] Iniciando backend FastAPI en http://localhost:8000 ...
start "Backend" cmd /k "uvicorn api.main:app --reload --port 8000"

timeout /t 2 /nobreak >nul

echo [2/2] Iniciando frontend React en http://localhost:5173 ...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Dashboard disponible en: http://localhost:5173
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
