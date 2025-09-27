from sklearn.ensemble import BaggingRegressor
from sklearn.compose import ColumnTransformer
import os
import joblib
import pandas as pd
from typing import Optional
import numpy as np 
from backend.models import CarPredictionRequest


# Variables globales para almacenar el modelo y el preprocesador
modelo_ml: Optional[BaggingRegressor] = None
preprocesador: Optional[ColumnTransformer] = None

# Definición de las constantes 
MODELO_FILENAME = 'modelo_final.joblib' 
PREPROCESADOR_FILENAME = 'preprocesador.joblib' 

# Ruta al directorio donde deben estar los archivos del modelo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'assets', MODELO_FILENAME)
PREPROCESSOR_PATH = os.path.join(BASE_DIR, 'assets', PREPROCESADOR_FILENAME)


def cargar_modelos() -> bool:
    """Carga los modelos de ML y el preprocesador desde archivos."""
    global modelo_ml
    global preprocesador

    try:
        # 1. Cargar el preprocesador
        preprocesador = joblib.load(PREPROCESSOR_PATH)
        # 2. Cargar el modelo
        modelo_ml = joblib.load(MODEL_PATH)
        
        print(f"   [ML] Preprocesador cargado desde: {PREPROCESSOR_PATH}")
        print(f"   [ML] Modelo cargado desde: {MODEL_PATH}")
        return True 
        
    except FileNotFoundError:
        print(f"   [ML] ERROR: Archivo del modelo no encontrado en la ruta: {MODEL_PATH} o el preprocesador en {PREPROCESSOR_PATH}")
        return False 
    except Exception as e:
        print(f"   [ML] ERROR al cargar modelos: {e}")
        return False 


class CarPredictionService:
    """Clase de servicio que encapsula la lógica de predicción."""

    def __init__(self):
        """Inicializa el servicio y comprueba que el modelo esté cargado."""
        
        self.modelo_cargado = modelo_ml is not None and preprocesador is not None

        if not self.modelo_cargado:
            raise Exception("El modelo de ML no ha sido cargado. Ejecuta cargar_modelos() primero.")

    def predecir_precio(self, request: CarPredictionRequest) -> float:
        global modelo_ml
        """Realiza la predicción usando el modelo cargado."""

        # *** LÍNEA DE DEPURACIÓN (la mantendremos) ***
        print(f"--- Solicitud Pydantic recibida (DEBUG) ---\n{request}\n---------------------------------------------")
        
        # 1. Convertir la solicitud (Pydantic) a un diccionario
        # Usamos exclude_none=False para forzar la inclusión de todos los 7 campos.
        data_dict = request.model_dump(exclude_none=False) 
        
        # Mapeo de los 7 campos de Pydantic a los 7 campos que el modelo espera (inglés/específicos)
        # CORRECCIÓN CLAVE: Aseguramos que solo las variables categóricas se mapeen a columnas que aceptan 'str'
        # o que puedan ser tratadas como categóricas/binarias por el modelo.
        mapeo_columnas_input = {
            'Manufacturer': ('Brands', str),
            'Model': ('Model', str),
            # Mapeos forzados de numéricos (deben ser float):
            'Year': ('Price_Min', float),           
            'Mileage': ('HorsePower_in_HP_2', float), 
            'EngineSize': ('Engine_capacity_in_cc', float), 
            # Mapeos forzados de categóricos (deben ser str) a columnas categóricas del modelo:
            'Transmission': ('Engines', str), # Mapeamos a 'Engines' que es categórica en el modelo original
            'FuelType': ('Fuel_1', str),
        }
        
        # 2. Renombrar y convertir tipos de datos
        mapped_data = {}
        for es_key, (en_key, data_type) in mapeo_columnas_input.items():
            if es_key in data_dict:
                value = data_dict[es_key]
                
                # CORRECCIÓN CLAVE: Lógica estricta para asegurar el tipo de dato
                try:
                    if data_type == float:
                        # Si se espera un float, forzamos la conversión
                        mapped_data[en_key] = float(value) if value is not None else np.nan
                    elif data_type == str:
                        # Si se espera un str, aseguramos que sea una cadena no vacía
                        mapped_data[en_key] = str(value) if value is not None and str(value).strip() else np.nan
                    else:
                        mapped_data[en_key] = value

                except (TypeError, ValueError):
                    # Si la conversión de un numérico falla, asignamos NaN
                    mapped_data[en_key] = np.nan
            
        # 3. Listado completo de 14 columnas que el modelo CIENTÍFICAMENTE requiere 
        columnas_requeridas = [
            'Model', 'Price_Min', 'HorsePower_in_HP_2', 'Fuel_1', 'Engines', 
            'Seats', 'Brands', 'Engine_capacity_in_cc', 'Torque_in_Nm_2', 
            'Time_to_100kmph_sec', 'id', 'Torque_in_Nm', 'HorsePower_in_HP', 
            'Max_speed_in_km/h'
        ]
        
        # 4. Crear el DataFrame y usar reindex para asegurar las 14 columnas
        try:
            # Crear el DataFrame a partir de los datos mapeados
            data_in = pd.DataFrame([mapped_data])
            
            # Reindexar: Rellenar las columnas faltantes con np.nan (que es lo que el modelo espera para las no provistas)
            # CRÍTICO: Las columnas no mapeadas (como 'Seats') deben ser de tipo float para no romper el SimpleImputer.
            # Pandas hace esto automáticamente si fill_value=np.nan.
            data_in = data_in.reindex(columns=columnas_requeridas, fill_value=np.nan)
            
            # IMPRIMIR LAS COLUMNAS PARA DEPURACIÓN:
            print("--- DataFrame Final para Predicción ---")
            print(data_in.head())
            print("---------------------------------------")

        except Exception as e:
             raise ValueError(f"Error al procesar los datos de entrada a DataFrame: {e}")

        # 5. Aplicar la predicción directamente
        # Envolvemos la llamada al preprocesador y al modelo en un try/except para capturar errores más específicos
        try:
            prediccion = modelo_ml.predict(data_in)[0]
        except Exception as e:
            # Propagamos el error al cliente FastAPI con más contexto
            raise ValueError(f"Error durante la predicción del modelo: {e}")


        # 6. Devolver el resultado
        return round(float(prediccion), 2)
