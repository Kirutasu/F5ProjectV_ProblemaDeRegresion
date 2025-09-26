from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv # Si usas .env para variables de entorno
from models import CarPredictionRequest, CarPredictionResponse
from ml_service_final import cargar_modelos, CarPredictionService

# Cargar variables de entorno (si aplica)
load_dotenv()

# --- 1. Configuración del Lifespan (Carga de Modelos) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Función que se ejecuta al inicio y al final de la aplicación."""
    print("Iniciando FastAPI: Llamando a cargar_modelos()...")
    # Llama a la función de carga del servicio ML
    if not cargar_modelos():
        print("¡ADVERTENCIA! La aplicación continuará, pero el servicio /predict fallará sin modelos.")
    
    yield # La aplicación permanece activa

    # Al cierre (si necesitas limpiar recursos)
    print("Apagando FastAPI.")


# --- 2. Inicialización de la Aplicación FastAPI ---
app = FastAPI(
    title="Car Price Prediction API",
    version="1.0.0",
    lifespan=lifespan # Asocia el lifespan
)

# --- 3. Configuración de CORS ---
# Crucial para permitir que tu frontend de Streamlit (que corre en otro puerto/servidor) 
# pueda hacer peticiones a este backend.
# Para desarrollo, puedes usar "*". Para producción, usa la URL específica del frontend.
origins = [
    "*", # Permite cualquier origen (MÁS FÁCIL PARA DESARROLLO)
    # "http://localhost:8501", # Si Streamlit corre localmente en el puerto 8501
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (POST, GET, etc.)
    allow_headers=["*"], # Permite todas las cabeceras
)

# --- 4. Inicialización del Servicio ---
# Esto solo ocurrirá después de que el lifespan haya intentado cargar los modelos
try:
    car_service = CarPredictionService()
except RuntimeError as e:
    # Esto es un caso de error extremo donde el servicio no está listo
    print(f"El servicio de predicción no pudo inicializarse: {e}")
    car_service = None # Dejamos la variable a None o manejamos de otra forma

# --- 5. Endpoints ---

@app.get("/")
def read_root():
    """Endpoint de salud (Health check)."""
    return {"message": "✅ Car Price Prediction API is running!"}


@app.post("/predict", response_model=CarPredictionResponse)
async def predict_car_price(request: CarPredictionRequest):
    """
    Endpoint principal para recibir datos JSON y devolver la predicción.
    """
    if car_service is None:
        raise HTTPException(status_code=503, detail="Servicio no disponible. El modelo de ML falló al cargar.")

    try:
        # Llama al servicio de predicción
        predicted_price = car_service.predict(request)

        # Devuelve la respuesta en el formato de CarPredictionResponse
        return CarPredictionResponse(predicted_price=predicted_price)

    except Exception as e:
        # Captura errores en la lógica de predicción/preprocesamiento
        print(f"Error en la predicción/preprocesamiento: {e}")
        # Retorna un 500 (Error Interno del Servidor)
        raise HTTPException(status_code=500, detail="Error interno al procesar la solicitud.")