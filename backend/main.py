# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncpg
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from models import Car, CarPredictionRequest, CarPredictionResponse
from typing import List, Optional
from ml_service_final import car_service_final as car_service
from ml_service_final import CarPredictionServiceFinal, car_service_final 
import pandas as pd
import logging
from decimal import Decimal
from sklearn.model_selection import train_test_split
from contextlib import asynccontextmanager


# Importa el servicio ML
from ml_service_final import CarMLService 
# Asegúrase de que el nombre del archivo y la clase sean correctos

# Instancia el servicio ML
car_service = CarMLService()

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# asyncpg requiere el esquema postgresql:// (no postgres://)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypass@db:5432/mydb")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # *** AJUSTE CLAVE: SOLO CARGAR MODELOS AL INICIO ***
    logger.info("Iniciando ciclo de vida: Cargando modelos...")
    
    # Llama a la función de carga con la ruta donde tienes tus .pkl
    success = car_service_final.cargar_modelos(ruta_base="models") 
    
    if not success:
        logger.error("No se pudieron cargar los modelos. La API de predicción no estará disponible.")
    else:
        logger.info("Modelos cargados. Aplicación lista.")
        
    yield # Aquí la aplicación comienza a recibir peticiones

app = FastAPI(
    title="API de Predicción de Precios de Automóviles",
    description="API para predicción de precios de automóviles usando modelos de ML",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Verificar estado de la API"""
    return {"status": "healthy", "models_trained": car_service.is_trained}

@app.get("/cars", response_model=List[Car])
async def get_cars(limit: int = 100):
    """Devuelve hasta 'limit' filas de la tabla cars_data."""
    async with app.state.db.acquire() as connection:
        rows = await connection.fetch(f"SELECT * FROM cars_data LIMIT {limit};")
        cars = []
        for row in rows:
            row_dict = dict(row)
            car_data = {k: convert_value(k, v) for k, v in row_dict.items()}
            cars.append(Car(**car_data))
        return cars

@app.get("/cars/filter", response_model=List[Car])
async def get_cars_filtered(
    limit: int = 300,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    precio_alto: Optional[int] = None,
    brand: Optional[str] = None,
    fuel_type: Optional[str] = None,
):
    """Devuelve autos filtrados por criterios"""
    query = "SELECT * FROM cars_data WHERE 1=1"
    params = []

    if min_price is not None:
        query += f" AND price_max_log >= ${len(params) + 1}"
        params.append(min_price)

    if max_price is not None:
        query += f" AND price_max_log <= ${len(params) + 1}"
        params.append(max_price)

    if precio_alto is not None:
        query += f" AND precio_alto = ${len(params) + 1}"
        params.append(precio_alto)

    if brand is not None:
        query += f" AND brand = ${len(params) + 1}"
        params.append(brand)

    if fuel_type is not None:
        query += f" AND fuel_type = ${len(params) + 1}"
        params.append(fuel_type)

    query += f" LIMIT {limit}"

    async with app.state.db.acquire() as connection:
        rows = await connection.fetch(query, *params)
        cars = []
        for row in rows:
            row_dict = dict(row)
            car_data = {k: convert_value(k, v) for k, v in row_dict.items()}
            cars.append(Car(**car_data))
        return cars


# 3. Verificación del Endpoint /predict
@app.post("/predict", response_model=CarPredictionResponse)
async def predict_car_price(request: CarPredictionRequest):
    if not car_service_final.is_trained:
        raise HTTPException(status_code=503, detail="Modelos no cargados. Servicio no disponible.")
    
    try:
        # Pasa los datos de la petición (que coinciden con tu modelo Pydantic)
        datos_entrada = request.model_dump() # o .dict() si usas Pydantic v1
        
        # Llama a la predicción
        resultado = car_service_final.predecir_auto(datos_entrada)
        
        # Mapea la respuesta del servicio al modelo de respuesta (CarPredictionResponse)
        return CarPredictionResponse(
            predicted_price=resultado["precio_predicho"],
            category=resultado["categoria_predicha"],
            # Incluye los otros campos que devuelve el servicio y que espera el modelo de respuesta
        )
        
    except Exception as e:
        logger.error(f"Error en el endpoint /predict: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

@app.post("/train")
async def train_models():
    """Endpoint informativo - Los modelos ya están pre-entrenados"""
    return {
        "success": True,
        "message": "Los modelos ya están pre-entrenados. No se requiere entrenamiento adicional.",
        "modelo_regresion": "Linear Regression (Pre-entrenado)",
        "modelo_clasificacion": "Decision Tree (Pre-entrenado)"
    }

@app.get("/cars/stats")
async def get_cars_stats():
    """Devuelve estadísticas de los datos de automóviles"""
    try:
        async with app.state.db.acquire() as connection:
            stats_query = """
            SELECT
                COUNT(*) as total_registros,
                AVG(price_max) as precio_promedio,
                MIN(price_max) as precio_min,
                MAX(price_max) as precio_max,
                AVG(engine_capacity) as motor_promedio,
                AVG(horsepower) as potencia_promedio,
                COUNT(DISTINCT brand) as marcas_unicas,
                COUNT(DISTINCT fuel_type) as tipos_combustible
            FROM cars_data
            """
            stats_result = await connection.fetchrow(stats_query)

            brand_query = """
            SELECT brand, COUNT(*) as cantidad
            FROM cars_data
            GROUP BY brand
            ORDER BY cantidad DESC
            LIMIT 10
            """
            brand_result = await connection.fetch(brand_query)

            fuel_query = """
            SELECT fuel_type, COUNT(*) as cantidad
            FROM cars_data
            GROUP BY fuel_type
            ORDER BY cantidad DESC
            """
            fuel_result = await connection.fetch(fuel_query)

            return {
                "estadisticas": {
                    "total_registros": stats_result["total_registros"],
                    "precio_promedio": float(stats_result["precio_promedio"]),
                    "precio_min": float(stats_result["precio_min"]),
                    "precio_max": float(stats_result["precio_max"]),
                    "motor_promedio": float(stats_result["motor_promedio"]),
                    "potencia_promedio": float(stats_result["potencia_promedio"]),
                    "marcas_unicas": stats_result["marcas_unicas"],
                    "tipos_combustible": stats_result["tipos_combustible"],
                },
                "marcas_populares": [
                    {"marca": row["brand"], "cantidad": row["cantidad"]}
                    for row in brand_result
                ],
                "distribucion_combustible": [
                    {"combustible": row["fuel_type"], "cantidad": row["cantidad"]}
                    for row in fuel_result
                ],
            }

    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al obtener estadísticas: {str(e)}"
        )

@app.post("/predict/batch")
async def predict_batch(cars: List[CarPredictionRequest]):
    """Realiza predicciones para múltiples automóviles"""
    try:
        resultados = []
        for car in cars:
            datos_entrada = {
                "brand": car.brand,
                "model": car.model,
                "engine_capacity": car.engine_capacity,
                "horsepower": car.horsepower,
                "max_speed": car.max_speed,
                "time_to_100": car.time_to_100,
                "seats": car.seats,
                "torque": car.torque,
                "fuel_type": car.fuel_type,
            }
            resultado = car_service.predecir_auto(datos_entrada)
            resultados.append(resultado)

        return {"predicciones": resultados, "total": len(resultados)}

    except Exception as e:
        logger.error(f"Error en predicción por lotes: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error en predicción por lotes: {str(e)}"
        )

@app.get("/model/info")
async def get_model_info():
    """Devuelve información sobre los modelos entrenados"""
    if not car_service.is_trained:
        return {"trained": False, "message": "Modelos no entrenados"}

    return {
        "trained": True,
        "columnas_numericas": car_service.columnas_numericas,
        "columnas_categoricas": car_service.columnas_categoricas,
        "modelo_regresion": "Random Forest",
        "modelo_clasificacion": "Logistic Regression",
        "total_datos_entrenamiento": (
            len(car_service.datos_entrenamiento)
            if car_service.datos_entrenamiento is not None
            else 0
        ),
    }

@app.post("/model/load")
async def load_trained_models():
    """Carga modelos pre-entrenados desde archivos"""
    try:
        success = car_service.cargar_modelos()
        if success:
            return {"message": "Modelos cargados exitosamente", "trained": True}
        else:
            raise HTTPException(
                status_code=500, detail="No se pudieron cargar los modelos"
            )
    except Exception as e:
        logger.error(f"Error al cargar modelos: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al cargar modelos: {str(e)}"
        )

def convert_value(key, value):
    """Convierte el valor según el tipo esperado"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        value = float(value)

    type_map = {
        "id": int,
        "brand": str,
        "model": str,
        "engine_capacity": float,
        "horsepower": float,
        "max_speed": float,
        "time_to_100": float,
        "price_max": float,
        "seats": int,
        "torque": float,
        "fuel_type": str,
        "precio_alto": int,
        "precio_categoria": str,
    }

    try:
        return type_map.get(key, str)(value)
    except Exception:
        return value

async def entrenar_modelos_automaticamente(db_pool):
    """Entrena modelos automáticamente al inicio"""
    try:
        async with db_pool.acquire() as connection:
            rows = await connection.fetch("SELECT * FROM cars_data")
            data = [dict(row) for row in rows]
            df = pd.DataFrame(data)

            if df.empty:
                logger.warning("No hay datos en la base de datos")
                return

            X, y_reg, y_clf = car_service.preparar_datos(df)

            # Split único y consistente
            X_train, X_test, y_train_reg, y_test_reg = train_test_split(
                X, y_reg, test_size=0.2, random_state=42
            )
            y_train_clf, y_test_clf = (
                y_clf.loc[X_train.index],
                y_clf.loc[X_test.index],
            )

            car_service.entrenar_modelos(
                X_train, y_train_reg, X_test, y_test_reg, y_train_clf, y_test_clf
            )

            car_service.guardar_modelos()

    except Exception as e:
        logger.error(f"Error en entrenamiento automático: {e}")
        raise