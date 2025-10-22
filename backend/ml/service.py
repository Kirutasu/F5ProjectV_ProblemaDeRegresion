# backend/ml/service.py
import pandas as pd
import numpy as np
from typing import Optional
import joblib

from backend.core.config import settings
from backend.core.logger import logger
from backend.api.schemas import CarPredictionRequest

class CarPredictionService:
    """Servicio encapsulado para predicciones de automóviles."""
    
    def __init__(self):
        self.modelo_ml: Optional[object] = None
        self.preprocesador: Optional[object] = None
        self._cargar_modelos()
    
    def _cargar_modelos(self) -> bool:
        """Carga los modelos desde los archivos configurados."""
        try:
            # CORRECCIÓN: Cargar los modelos que realmente existen
            self.modelo_ml = joblib.load(settings.MODEL_PATHS["regresion"])
            
            # El modelo de clasificación contiene el preprocesador que necesitamos
            modelo_clasificacion = joblib.load(settings.MODEL_PATHS["clasificacion"])
            self.preprocesador = modelo_clasificacion.named_steps['preprocesador']
            
            logger.info("Modelos cargados correctamente")
            return True
            
        except FileNotFoundError as e:
            logger.error(f"Archivos de modelo no encontrados: {e}")
            raise
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            raise
    
    def _mapear_datos_entrada(self, request: CarPredictionRequest) -> dict:
        """Mapea los datos de entrada al formato esperado por el modelo."""
        mapeo_columnas = {
            'Manufacturer': 'Brands',
            'Model': 'Model', 
            'Year': 'Price_Min',
            'Mileage': 'HorsePower_in_HP_2',
            'EngineSize': 'Engine_capacity_in_cc',
            'Transmission': 'Engines',
            'FuelType': 'Fuel_1',
        }
        
        data_dict = request.model_dump(exclude_none=False)
        mapped_data = {}
        
        for es_key, en_key in mapeo_columnas.items():
            if es_key in data_dict:
                value = data_dict[es_key]
                try:
                    # Conversión de tipos básica
                    if isinstance(value, (int, float)):
                        mapped_data[en_key] = float(value)
                    else:
                        mapped_data[en_key] = str(value) if value else np.nan
                except (TypeError, ValueError):
                    mapped_data[en_key] = np.nan
        
        return mapped_data
    
    def predecir_precio(self, request: CarPredictionRequest) -> float:
        """Realiza la predicción del precio del automóvil."""
        try:
            # Mapear datos de entrada
            mapped_data = self._mapear_datos_entrada(request)
            
            # Crear DataFrame con columnas esperadas
            columnas_requeridas = [
                'Model', 'Price_Min', 'HorsePower_in_HP_2', 'Fuel_1', 'Engines', 
                'Seats', 'Brands', 'Engine_capacity_in_cc', 'Torque_in_Nm_2', 
                'Time_to_100kmph_sec', 'id', 'Torque_in_Nm', 'HorsePower_in_HP', 
                'Max_speed_in_km/h'
            ]
            
            # Crear DataFrame y llenar valores faltantes
            data_in = pd.DataFrame([mapped_data])
            
            # Asegurar que tengamos todas las columnas requeridas
            for col in columnas_requeridas:
                if col not in data_in.columns:
                    data_in[col] = np.nan
            
            data_in = data_in[columnas_requeridas]
            
            logger.debug(f"DataFrame para predicción: {data_in.shape}")
            
            # Preprocesar datos
            if self.preprocesador:
                data_preprocessed = self.preprocesador.transform(data_in)
            else:
                data_preprocessed = data_in
            
            # Realizar predicción
            prediccion = self.modelo_ml.predict(data_preprocessed)[0]
            return round(float(prediccion), 2)
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            raise ValueError(f"Error procesando la solicitud: {str(e)}")