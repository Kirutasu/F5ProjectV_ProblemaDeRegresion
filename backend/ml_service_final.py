# ml_service_final.py
import pandas as pd
import numpy as np
import joblib
import os
from typing import Dict, Any, Tuple
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CarPredictionServiceFinal:
    """Servicio de predicción de precios de automóviles"""

    def __init__(self):
        self.modelo_regresion = None
        self.modelo_clasificacion = None
        self.datos_entrenamiento = None
        self.columnas_numericas = None
        self.columnas_categoricas = None
        self.preprocesador = None
        self.is_trained = False

    async def cargar_datos_desde_sql(self, db_connection) -> pd.DataFrame:
        """Carga datos desde la base de datos SQL"""
        try:
            query = "SELECT * FROM cars_data LIMIT 10000"
            rows = await db_connection.fetch(query)
            df = pd.DataFrame([dict(r) for r in rows])
            logger.info(f"Datos cargados: {df.shape[0]} filas × {df.shape[1]} columnas")
            return df
        except Exception as e:
            logger.error(f"Error al cargar datos desde SQL: {e}")
            raise

    def preparar_datos(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """Prepara los datos para modelado creando variables objetivo"""

        # Normalizar nombres de columnas
        df.columns = df.columns.str.lower()

        # Crear variables objetivo si no existen
        if "precio_alto" not in df.columns and "price_max" in df.columns:
            # Crear variable binaria para clasificación
            precio_mediano = df["price_max"].median()
            df["precio_alto"] = (df["price_max"] > precio_mediano).astype(int)
            
            # Crear categorías de precio
            q1 = df["price_max"].quantile(0.33)
            q2 = df["price_max"].quantile(0.66)
            
            def categorizar_precio(precio):
                if precio <= q1:
                    return "Bajo"
                elif precio <= q2:
                    return "Medio"
                else:
                    return "Alto"
            
            df["precio_categoria"] = df["price_max"].apply(categorizar_precio)

        # Confirmar columnas críticas
        if "price_max" not in df.columns or "precio_alto" not in df.columns:
            raise ValueError(
                f"Faltan columnas críticas en DataFrame: {list(df.columns)}"
            )

        # Separar características y objetivos
        caracteristicas = df.drop(
            ["price_max", "precio_alto", "precio_categoria", "id"],
            axis=1,
            errors="ignore",
        )
        objetivo_reg = df["price_max"]
        objetivo_clf = df["precio_alto"]

        # Identificar tipos de columnas
        columnas_numericas = caracteristicas.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()
        columnas_categoricas = caracteristicas.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        logger.info(f"Características: {caracteristicas.shape}")
        logger.info(f"Columnas numéricas: {columnas_numericas}")
        logger.info(f"Columnas categóricas: {columnas_categoricas}")

        self.columnas_numericas = columnas_numericas
        self.columnas_categoricas = columnas_categoricas

        return caracteristicas, objetivo_reg, objetivo_clf

    def crear_preprocesador(self):
        """Crea el pipeline de preprocesamiento"""
        transformador_numerico = Pipeline(
            steps=[
                ("imputador", SimpleImputer(strategy="median")),
                ("escalador", StandardScaler()),
            ]
        )

        transformador_categorico = (
            Pipeline(
                steps=[
                    (
                        "imputador",
                        SimpleImputer(strategy="constant", fill_value="missing"),
                    ),
                    (
                        "onehot",
                        OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    ),
                ]
            )
            if self.columnas_categoricas
            else "passthrough"
        )

        preprocesador = ColumnTransformer(
            transformers=[
                ("numerico", transformador_numerico, self.columnas_numericas),
                ("categorico", transformador_categorico, self.columnas_categoricas),
            ]
        )

        self.preprocesador = preprocesador
        logger.info("Pipeline de preprocesamiento creado")
        return preprocesador

    def crear_modelos(self, preprocesador):
        """Crea los modelos de regresión y clasificación"""
        modelo_regresion = Pipeline(
            [
                ("preprocesador", preprocesador),
                (
                    "modelo",
                    RandomForestRegressor(
                        n_estimators=200, max_depth=10, random_state=42
                    ),
                ),
            ]
        )

        modelo_clasificacion = Pipeline(
            [
                ("preprocesador", preprocesador),
                ("modelo", LogisticRegression(random_state=42, max_iter=200)),
            ]
        )

        return modelo_regresion, modelo_clasificacion

    def entrenar_modelos(
        self, X_train, y_train_reg, X_test, y_test_reg, y_train_clf, y_test_clf
    ):
        """Entrena los modelos"""
        preprocesador = self.crear_preprocesador()
        self.modelo_regresion, self.modelo_clasificacion = self.crear_modelos(
            preprocesador
        )

        logger.info("Entrenando modelo de regresión...")
        self.modelo_regresion.fit(X_train, y_train_reg)

        logger.info("Entrenando modelo de clasificación...")
        self.modelo_clasificacion.fit(X_train, y_train_clf)

        # Evaluación
        y_pred_reg = self.modelo_regresion.predict(X_test)
        y_pred_clf = self.modelo_clasificacion.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
        r2 = r2_score(y_test_reg, y_pred_reg)
        accuracy = accuracy_score(y_test_clf, y_pred_clf)

        logger.info(f"Regresión - RMSE: {rmse:.4f}, R²: {r2:.4f}")
        logger.info(f"Clasificación - Accuracy: {accuracy:.4f}")

        self.is_trained = True
        return True

    def predecir_auto(self, datos_entrada: Dict[str, Any]) -> Dict[str, Any]:
        """Predice el precio y la categoría"""
        if not self.is_trained:
            raise ValueError("Los modelos no han sido entrenados")

        try:
            # Crear DataFrame con los datos de entrada
            df_entrada = pd.DataFrame([datos_entrada])
            
            # Agregar columnas faltantes con valores por defecto
            columnas_esperadas = self.columnas_numericas + self.columnas_categoricas
            
            for col in columnas_esperadas:
                if col not in df_entrada.columns:
                    if col in self.columnas_numericas:
                        df_entrada[col] = 0.0
                    else:
                        df_entrada[col] = 'unknown'
            
            # Reordenar columnas para que coincidan con el entrenamiento
            df_entrada = df_entrada[columnas_esperadas]
            
            precio_predicho = self.modelo_regresion.predict(df_entrada)[0]
            categoria_predicha = self.modelo_clasificacion.predict(df_entrada)[0]

            if hasattr(self.modelo_clasificacion, "predict_proba"):
                proba_alto = self.modelo_clasificacion.predict_proba(df_entrada)[0][1]
            else:
                proba_alto = 1.0 if categoria_predicha == 1 else 0.0

            return {
                "precio_predicho": float(precio_predicho),
                "categoria_predicha": (
                    "Precio Alto" if categoria_predicha == 1 else "Precio Bajo"
                ),
                "probabilidad_alta": float(proba_alto),
                "modelo_usado_regresion": "Random Forest",
                "modelo_usado_clasificacion": "Logistic Regression",
            }

        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            logger.error(f"Columnas esperadas: {self.columnas_numericas + self.columnas_categoricas}")
            logger.error(f"Columnas recibidas: {list(datos_entrada.keys())}")
            raise

    def guardar_modelos(self, ruta_base: str = "models"):
        """Guarda modelos entrenados"""
        if not self.is_trained:
            raise ValueError("Los modelos no han sido entrenados")

        os.makedirs(ruta_base, exist_ok=True)
        joblib.dump(self.modelo_regresion, f"{ruta_base}/modelo_regresion.pkl")
        joblib.dump(self.modelo_clasificacion, f"{ruta_base}/modelo_clasificacion.pkl")
        joblib.dump(self.preprocesador, f"{ruta_base}/preprocesador.pkl")
        logger.info(f"Modelos guardados en {ruta_base}")
        return True

    def cargar_modelos(self, ruta_base: str = "models"):
        """Carga modelos entrenados"""
        try:
            self.modelo_regresion = joblib.load(f"{ruta_base}/modelo_regresion.pkl")
            self.modelo_clasificacion = joblib.load(
                f"{ruta_base}/modelo_clasificacion.pkl"
            )
            self.preprocesador = joblib.load(f"{ruta_base}/preprocesador.pkl")
            self.is_trained = True
            logger.info("Modelos cargados exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error al cargar modelos: {e}")
            return False

# Instancia global del servicio
car_service_final = CarPredictionServiceFinal()