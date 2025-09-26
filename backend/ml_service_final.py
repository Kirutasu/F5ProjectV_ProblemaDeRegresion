import joblib
import os
import pandas as pd
from models import CarPredictionRequest

# Variables globales para almacenar el modelo y el preprocesador cargados
model = None
preprocessor = None
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')


def cargar_modelos():
    """
    Función encargada de cargar los archivos .joblib (modelo y preprocesador) 
    desde la carpeta 'backend/assets/' al inicio de la aplicación.
    """
    global model, preprocessor
    
    # Rutas de los archivos (ajusta los nombres si son diferentes)
    MODEL_PATH = os.path.join(ASSETS_DIR, 'modelo_final.joblib')
    PREPROCESSOR_PATH = os.path.join(ASSETS_DIR, 'preprocesador.joblib')

    if not os.path.exists(MODEL_PATH) or not os.path.exists(PREPROCESSOR_PATH):
        print(f"ERROR: No se encontraron los archivos del modelo en {ASSETS_DIR}")
        print("Asegúrate de que 'modelo_final.joblib' y 'preprocesador.joblib' existen.")
        return False

    try:
        model = joblib.load(MODEL_PATH)
        preprocessor = joblib.load(PREPROCESSOR_PATH)
        print("✅ Modelos de ML cargados exitosamente.")
        return True
    except Exception as e:
        print(f"❌ Error al cargar los modelos: {e}")
        return False


class CarPredictionService:
    """Clase para encapsular la lógica de predicción."""

    def __init__(self):
        # Asegura que el servicio solo se inicialice si los modelos están cargados
        if model is None or preprocessor is None:
            raise RuntimeError("El modelo de ML no ha sido cargado. Ejecuta cargar_modelos() primero.")

    def predict(self, data: CarPredictionRequest) -> float:
        """Realiza la predicción del precio del coche."""

        # 1. Convertir el objeto Pydantic (el 'request') a un DataFrame de pandas
        input_data_dict = data.dict()
        input_df = pd.DataFrame([input_data_dict])
        
        # Opcional: Asegúrate de que las columnas del DF están en el orden correcto 
        # que tu preprocesador espera.
        
        # 2. Preprocesar los datos (One-Hot Encoding, escalado, etc.)
        # Tu preprocesador (ej. ColumnTransformer) debe transformar el DF.
        processed_data = preprocessor.transform(input_df)

        # 3. Realizar la predicción
        prediction = model.predict(processed_data)[0]

        # 4. Devolver el resultado como float
        # Si tu modelo predice un logaritmo, recuerda hacer np.exp() aquí.
        return float(prediction)