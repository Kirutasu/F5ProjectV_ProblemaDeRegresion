import asyncio
from contextlib import asynccontextmanager
from typing import Optional # ¡CORRECCIÓN CLAVE: Importar Optional!

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from backend.models import CarPredictionRequest, CarPredictionResponse
from backend.ml_service_final import CarPredictionService, cargar_modelos

# Creamos una instancia global del servicio, inicializada como None
car_service: Optional[CarPredictionService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Función de ciclo de vida que se ejecuta al inicio y al final del servidor.
    Se encarga de cargar los modelos.
    """
    print("Iniciando FastAPI: Llamando a cargar_modelos()...")
    if cargar_modelos():
        global car_service
        try:
            # Inicializamos el servicio SOLO después de cargar los modelos
            car_service = CarPredictionService()
            print("✅ Modelos de ML cargados exitosamente.")
        except Exception as e:
            print(f"El servicio de predicción no pudo inicializarse: {e}")
            # Si la inicialización falla, el servicio permanece como None.
            car_service = None
    else:
        print("❌ Fallo al cargar los modelos de ML.")
    
    yield
    print("Apagando FastAPI.")


app = FastAPI(lifespan=lifespan)

# Configuración de CORS para permitir peticiones desde Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_car_prediction_service() -> CarPredictionService:
    """Dependencia para inyectar el servicio de predicción."""
    if car_service is None:
        # Lanza un 503 si el servicio no se pudo inicializar (modelos no cargados)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de predicción no disponible. Los modelos no se cargaron correctamente."
        )
    return car_service

# Endpoint de prueba
@app.get("/")
def read_root():
    return {"message": "API de Predicción de Precios de Autos activa."}

# Endpoint principal de predicción
@app.post("/predict", response_model=CarPredictionResponse)
def predict(
    request: CarPredictionRequest,
    service: CarPredictionService = Depends(get_car_prediction_service)
):
    """Recibe datos de un auto y devuelve el precio predicho."""
    try:
        # Llamada a la lógica de predicción en ml_service_final.py
        predicted_value = service.predecir_precio(request)
        
        # Devolver un diccionario que coincide con CarPredictionResponse
        return CarPredictionResponse(predicted_price=predicted_value)
        
    except ValueError as e:
        # Atrapa errores específicos de manejo de datos
        print(f"Error durante la predicción: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Datos de entrada inválidos: {e}"
        )
    except Exception as e:
        # Atrapa cualquier otro error interno y lo registra
        print(f"Error interno inesperado durante la predicción: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante la predicción."
        )

