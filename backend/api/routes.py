# backend/api/routes.py
import asyncio
from fastapi import APIRouter, Depends, Request, HTTPException, status

from backend.core.logger import logger
from backend.api.schemas import (
    BaseResponse, HealthResponse, PredictionResponse, 
    CarPredictionRequest, CarPredictionResponse
)
from backend.api.dependencies import get_car_prediction_service
from backend.ml.service import CarPredictionService

router = APIRouter()

# ✅ Endpoint raíz en "/"
@router.get("/", response_model=BaseResponse)
async def root():
    """Endpoint raíz."""
    return BaseResponse(
        status="success",
        message="API de Predicción de Precios de Autos",
        data={"version": "1.0.0"}
    )

@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check de la aplicación."""
    service_status = "available" if request.app.state.car_service is not None else "unavailable"
    modelos_status = "loaded" if request.app.state.car_service is not None else "not loaded"
    
    return HealthResponse(
        status="healthy" if service_status == "available" else "unhealthy",
        service_status=service_status,
        modelos_status=modelos_status,
        timestamp=asyncio.get_event_loop().time()
    )

@router.post("/predict", response_model=PredictionResponse)
async def predict(
    request: CarPredictionRequest,
    service: CarPredictionService = Depends(get_car_prediction_service)
):
    """Endpoint para predecir precios de automóviles."""
    try:
        logger.info(f"Solicitud de predicción recibida: {request.dict()}")
        predicted_value = service.predecir_precio(request)
        logger.info(f"Predicción realizada: {predicted_value}")
        
        return PredictionResponse(
            status="success",
            message="Predicción realizada correctamente",
            data={"predicted_price": predicted_value}
        )
        
    except ValueError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Datos de entrada inválidos: {e}"
        )
    except Exception as e:
        logger.error(f"Error durante la predicción: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante la predicción."
        )

# ✅ Único endpoint en /model-info
@router.get("/model-info", response_model=BaseResponse)
async def model_info(service: CarPredictionService = Depends(get_car_prediction_service)):
    """Información sobre los modelos cargados."""
    return BaseResponse(
        status="success",
        message="Información del modelo de predicción",
        data={
            "modelo_utilizado": "LinearRegression",
            "preprocesador": "ColumnTransformer (del modelo de clasificación)",
            "status": "loaded"
        }
    )