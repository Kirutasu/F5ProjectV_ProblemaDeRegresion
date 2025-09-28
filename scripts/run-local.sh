#!/bin/bash

# run-local.sh - Ejecutar aplicación sin Docker

echo "Iniciando Vehicle Price Prediction Platform localmente..."

# Verificar Python
if ! command -v python &> /dev/null; then
    echo "Error: Python no está instalado"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python -m venv venv
fi

# Activar entorno virtual
if [[ "$OSTYPE" == "msys" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Instalar dependencias básicas
echo "Instalando dependencias..."
pip install --upgrade pip

# Instalar dependencias del backend
pip install fastapi uvicorn python-dotenv pydantic pydantic-settings
pip install numpy pandas scikit-learn joblib requests python-multipart aiofiles

# Instalar dependencias del frontend  
pip install streamlit plotly

# Crear directorios necesarios
mkdir -p backend/logs
mkdir -p data

# Configurar variables de entorno
export PYTHONPATH="$(pwd)"
export DATABASE_URL="sqlite:///$(pwd)/data/vehicles.db"
export BACKEND_URL="http://localhost:8000"

# Función para limpiar procesos al salir
cleanup() {
    echo "Deteniendo servicios..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}
trap cleanup SIGINT SIGTERM

# Iniciar backend
echo "Iniciando backend en puerto 8000..."
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Esperar a que el backend esté listo
echo "Esperando backend..."
sleep 5

# Verificar que el backend esté funcionando
if curl -s http://localhost:8000/health > /dev/null; then
    echo "Backend iniciado correctamente"
else
    echo "Advertencia: Backend podría no estar completamente listo"
fi

# Iniciar frontend
echo "Iniciando frontend en puerto 8501..."
cd frontend
streamlit run streamlit_car_prediction_app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!
cd ..

echo ""
echo "Aplicación iniciada!"
echo ""
echo "URLs de acceso:"
echo "- Frontend: http://localhost:8501"
echo "- Backend: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener todos los servicios"
echo ""

# Mantener el script corriendo
wait