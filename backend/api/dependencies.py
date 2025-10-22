# backend/api/dependencies.py
from fastapi import Request, HTTPException, status
from backend.ml.service import CarPredictionService
from backend.core.logger import logger

def get_car_prediction_service(request: Request) -> CarPredictionService:
    """Dependency para obtener el servicio de predicción."""
    service = request.app.state.car_service
    if service is None:
        logger.error("Servicio de predicción no disponible")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de predicción no disponible. Los modelos no se cargaron correctamente."
        )
    return service

class PredictionError(Exception):
    """Excepción personalizada para errores de predicción."""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)