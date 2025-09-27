from pydantic import BaseModel
from typing import Optional

# --- Solicitud de Predicción ---
class CarPredictionRequest(BaseModel):
    """
    Define los campos que el frontend debe enviar al endpoint /predict.
    Los nombres de los campos deben coincidir EXACTAMENTE con las columnas 
    que tu modelo ML y preprocesador esperan, incluyendo mayúsculas/minúsculas.
    """
    Manufacturer: str
    Model: str
    Year: int
    Transmission: str
    Mileage: int  # Asumiendo que es un número entero
    FuelType: str
    EngineSize: float # Asumiendo que es un número decimal

    # Ejemplo de un campo opcional, si lo necesitaras:
    # Color: Optional[str] = "Unknown"


# --- Respuesta de Predicción ---
class CarPredictionResponse(BaseModel):
    """
    Define la estructura de la respuesta que el backend enviará al frontend.
    """
    predicted_price: float
    # Puedes añadir un mensaje o más detalles si fuera necesario
    # message: str = "Predicción exitosa"