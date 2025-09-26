# backend/models.py
from pydantic import BaseModel
from typing import Optional

class Car(BaseModel):
    id: Optional[int] = None
    engine_capacity_in_cc_log: Optional[float] = None
    horsepower_in_hp_log: Optional[float] = None
    horsepower_in_hp_2_log: Optional[float] = None
    max_speed_in_km_h_boxcox: Optional[float] = None
    time_to_100kmph_sec_reciprocal: Optional[float] = None
    price_max_log: Optional[float] = None
    seats_yeojohnson: Optional[float] = None
    torque_in_nm_log: Optional[float] = None
    torque_in_nm_2_log: Optional[float] = None
    precio_categoria: Optional[str] = None
    precio_alto: Optional[int] = None
    seats_cat: Optional[str] = None

class CarPredictionRequest(BaseModel):
    engine_capacity_in_cc_log: float
    horsepower_in_hp_log: float
    horsepower_in_hp_2_log: float
    max_speed_in_km_h_boxcox: float
    time_to_100kmph_sec_reciprocal: float
    seats_yeojohnson: float
    torque_in_nm_log: float
    torque_in_nm_2_log: float

class CarPredictionResponse(BaseModel):
    precio_predicho: float
    categoria_predicha: str
    probabilidad_alta: float
    modelo_usado_regresion: str
    modelo_usado_clasificacion: str
