# models.py
from pydantic import BaseModel
from typing import Optional

class Car(BaseModel):
    id: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    engine_capacity: Optional[float] = None
    horsepower: Optional[float] = None
    max_speed: Optional[float] = None
    time_to_100: Optional[float] = None
    price_max: Optional[float] = None
    seats: Optional[int] = None
    torque: Optional[float] = None
    fuel_type: Optional[str] = None
    precio_categoria: Optional[str] = None
    precio_alto: Optional[int] = None

class CarPredictionRequest(BaseModel):
    brand: str
    model: str
    engine_capacity: float
    horsepower: float
    max_speed: float
    time_to_100: float
    seats: int
    torque: float
    fuel_type: str

class CarPredictionResponse(BaseModel):
    precio_predicho: float
    categoria_predicha: str
    probabilidad_alta: float
    modelo_usado_regresion: str
    modelo_usado_clasificacion: str