# backend/api/schemas.py
from pydantic import BaseModel
from typing import Any, Optional

class BaseResponse(BaseModel):
    """Esquema base para todas las respuestas de la API."""
    status: str
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None

class HealthResponse(BaseResponse):
    """Respuesta específica para el endpoint de health check."""
    service_status: str
    modelos_status: str
    timestamp: float

class PredictionRequest(BaseModel):
    """Solicitud de predicción (alias para mantener compatibilidad)."""
    Manufacturer: str
    Model: str
    Year: int
    Transmission: str
    Mileage: int
    FuelType: str
    EngineSize: float

class PredictionResponse(BaseResponse):
    """Respuesta de predicción."""
    predicted_price: Optional[float] = None

# Aliases para mantener compatibilidad
CarPredictionRequest = PredictionRequest
CarPredictionResponse = PredictionResponse