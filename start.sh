#!/bin/bash
set -e

echo "========================================"
echo " Lector Doc Extractor - Iniciar app"
echo "========================================"

# Check .env exists
if [ ! -f ".env" ]; then
  echo "[ERROR] Falta el archivo .env"
  echo "Copia .env.example a .env y agrega tu GOOGLE_API_KEY"
  exit 1
fi

echo "[1/2] Iniciando backend FastAPI en http://localhost:8000 ..."
uvicorn api.main:app --reload --port 8000 &
BACKEND_PID=$!

sleep 2

echo "[2/2] Iniciando frontend React en http://localhost:5173 ..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "Dashboard disponible en: http://localhost:5173"
echo "Backend API en: http://localhost:8000"
echo ""
echo "Presiona Ctrl+C para detener ambos servicios."

# Graceful shutdown
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait
