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
import pandas as pd
import logging
from decimal import Decimal
from sklearn.model_selection import train_test_split

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# asyncpg requiere el esquema postgresql:// (no postgres://)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypass@db:5432/mydb")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejar startup y shutdown de la aplicación"""
    try:
        # Conectar a la base de datos
        app.state.db = await asyncpg.create_pool(DATABASE_URL)

        # Entrenar modelos automáticamente al inicio
        try:
            logger.info("Iniciando entrenamiento automático de modelos...")
            await entrenar_modelos_automaticamente(app.state.db)
            logger.info("Modelos entrenados exitosamente")
        except Exception as e:
            logger.warning(f"No se pudieron entrenar los modelos automáticamente: {e}")

    except Exception as e:
        logger.error(f"Error al conectarse a la base de datos: {e}")
        raise e

    yield

    # Cleanup
    if hasattr(app.state, "db"):
        await app.state.db.close()


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

    query += f" LIMIT {limit}"

    async with app.state.db.acquire() as connection:
        rows = await connection.fetch(query, *params)
        cars = []
        for row in rows:
            row_dict = dict(row)
            car_data = {k: convert_value(k, v) for k, v in row_dict.items()}
            cars.append(Car(**car_data))
        return cars


@app.post("/predict", response_model=CarPredictionResponse)
async def predict_car_price(request: CarPredictionRequest):
    """Predice el precio de un automóvil basado en sus características"""
    try:
        datos_entrada = {
            "engine_capacity_in_cc_log": request.engine_capacity_in_cc_log,
            "horsepower_in_hp_log": request.horsepower_in_hp_log,
            "horsepower_in_hp_2_log": request.horsepower_in_hp_2_log,
            "max_speed_in_km_h_boxcox": request.max_speed_in_km_h_boxcox,
            "time_to_100kmph_sec_reciprocal": request.time_to_100kmph_sec_reciprocal,
            "seats_yeojohnson": request.seats_yeojohnson,
            "torque_in_nm_log": request.torque_in_nm_log,
            "torque_in_nm_2_log": request.torque_in_nm_2_log,
        }

        resultado = car_service.predecir_auto(datos_entrada)
        return CarPredictionResponse(**resultado)

    except Exception as e:
        logger.error(f"Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


@app.post("/train")
async def train_models():
    """Entrena los modelos de ML con los datos de la base de datos."""
    try:
        async with app.state.db.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM cars_data")
            data = [dict(row) for row in rows]
            df = pd.DataFrame(data)

            if df.empty:
                return {"success": False, "message": "No hay datos en la base de datos"}

        logger.info(f"Columnas del DataFrame: {list(df.columns)}")

        X, y_reg, y_clf = car_service.preparar_datos(df)

        # Split único y consistente
        X_train, X_test, y_train_reg, y_test_reg = train_test_split(
            X, y_reg, test_size=0.2, random_state=42
        )
        y_train_clf, y_test_clf = (
            y_clf.loc[X_train.index],
            y_clf.loc[X_test.index],
        )

        success = car_service.entrenar_modelos(
            X_train, y_train_reg, X_test, y_test_reg, y_train_clf, y_test_clf
        )

        if success:
            car_service.guardar_modelos()
            return {
                "success": True,
                "message": "Modelos entrenados y guardados exitosamente",
            }
        else:
            return {"success": False, "message": "Error al entrenar los modelos"}

    except Exception as e:
        logger.error(f"Error al entrenar modelos: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error al entrenar modelos: {str(e)}"
        )


@app.get("/cars/stats")
async def get_cars_stats():
    """Devuelve estadísticas de los datos de automóviles"""
    try:
        async with app.state.db.acquire() as connection:
            stats_query = """
            SELECT
                COUNT(*) as total_registros,
                AVG(price_max_log) as precio_promedio_log,
                MIN(price_max_log) as precio_min_log,
                MAX(price_max_log) as precio_max_log,
                AVG(engine_capacity_in_cc_log) as motor_promedio,
                AVG(horsepower_in_hp_log) as potencia_promedio,
                COUNT(DISTINCT precio_categoria) as categorias_unicas,
                COUNT(DISTINCT seats_cat) as tipos_asientos
            FROM cars_data
            """
            stats_result = await connection.fetchrow(stats_query)

            category_query = """
            SELECT precio_categoria, COUNT(*) as cantidad
            FROM cars_data
            GROUP BY precio_categoria
            ORDER BY cantidad DESC
            """
            category_result = await connection.fetch(category_query)

            return {
                "estadisticas": {
                    "total_registros": stats_result["total_registros"],
                    "precio_promedio_log": float(stats_result["precio_promedio_log"]),
                    "precio_min_log": float(stats_result["precio_min_log"]),
                    "precio_max_log": float(stats_result["precio_max_log"]),
                    "motor_promedio": float(stats_result["motor_promedio"]),
                    "potencia_promedio": float(stats_result["potencia_promedio"]),
                    "categorias_unicas": stats_result["categorias_unicas"],
                    "tipos_asientos": stats_result["tipos_asientos"],
                },
                "distribucion_categorias": [
                    {"categoria": row["precio_categoria"], "cantidad": row["cantidad"]}
                    for row in category_result
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
                "engine_capacity_in_cc_log": car.engine_capacity_in_cc_log,
                "horsepower_in_hp_log": car.horsepower_in_hp_log,
                "horsepower_in_hp_2_log": car.horsepower_in_hp_2_log,
                "max_speed_in_km_h_boxcox": car.max_speed_in_km_h_boxcox,
                "time_to_100kmph_sec_reciprocal": car.time_to_100kmph_sec_reciprocal,
                "seats_yeojohnson": car.seats_yeojohnson,
                "torque_in_nm_log": car.torque_in_nm_log,
                "torque_in_nm_2_log": car.torque_in_nm_2_log,
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
        "engine_capacity_in_cc_log": float,
        "horsepower_in_hp_log": float,
        "horsepower_in_hp_2_log": float,
        "max_speed_in_km_h_boxcox": float,
        "time_to_100kmph_sec_reciprocal": float,
        "price_max_log": float,
        "seats_yeojohnson": float,
        "torque_in_nm_log": float,
        "torque_in_nm_2_log": float,
        "precio_alto": int,
        "precio_categoria": str,
        "seats_cat": str,
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
