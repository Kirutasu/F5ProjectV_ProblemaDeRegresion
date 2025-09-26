# -*- coding: utf-8 -*-
"""
Definitivo Factorizado Modelo Grupo 6 - Machine Learning

Entrena y evalúa modelos de regresión y clasificación
para predecir precios de automóviles usando la tabla cars_data.
"""

# ----------------------------
# Importación de librerías optimizadas
# ----------------------------
import numpy as np
import pandas as pd

# Visualización
import matplotlib.pyplot as plt
import seaborn as sns

# Preprocesamiento y modelado
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Modelos
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

# Evaluación de modelos
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error,
    r2_score,
    accuracy_score,
    classification_report,
    confusion_matrix,
)

# Producción
import joblib

# Configuración global
RANDOM_STATE = 42
TEST_SIZE = 0.2


class AutomovilesModelEnhanced:
    def __init__(self, ruta_dataset: str):
        self.ruta_dataset = ruta_dataset
        self.df = None
        self.modelo_regresion = None
        self.modelo_clasificacion = None
        self.preprocesador = None

    def cargar_datos(self):
        """Carga y muestra información básica del dataset"""
        self.df = pd.read_csv(self.ruta_dataset)
        print(
            f"✅ Dataset cargado: {self.df.shape[0]} filas × {self.df.shape[1]} columnas"
        )
        return self.df

    def preparar_datos(self):
        """Prepara los datos para modelado creando variables objetivo"""
        df = self.df.copy()

        # Normalizamos nombres de columnas a minúsculas
        df.columns = df.columns.str.lower()

        # Verificación de columna de precio
        if "price_max_log" not in df.columns:
            raise ValueError(
                "❌ La columna 'price_max_log' no se encontró en la tabla."
            )

        # Crear variable de clasificación si no existe
        if "precio_alto" not in df.columns:
            precio_mediano = df["price_max_log"].median()
            df["precio_alto"] = (df["price_max_log"] > precio_mediano).astype(int)
            print(f"✅ Variable 'precio_alto' creada (umbral: {precio_mediano:.2f})")

        # Separar características y objetivos
        columnas_objetivo = ["price_max_log", "precio_alto", "precio_categoria"]
        caracteristicas = df.drop(columnas_objetivo, axis=1, errors="ignore")
        objetivo_reg = df["price_max_log"]
        objetivo_clf = df["precio_alto"]

        # Identificar tipos de columnas
        columnas_numericas = caracteristicas.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()
        columnas_categoricas = caracteristicas.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        print(
            f"✅ Características: {len(columnas_numericas)} numéricas, {len(columnas_categoricas)} categóricas"
        )
        return (
            caracteristicas,
            objetivo_reg,
            objetivo_clf,
            columnas_numericas,
            columnas_categoricas,
        )

    def crear_pipeline_preprocesamiento(self, columnas_numericas, columnas_categoricas):
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
            if columnas_categoricas
            else "passthrough"
        )

        self.preprocesador = ColumnTransformer(
            transformers=[
                ("numerico", transformador_numerico, columnas_numericas),
                ("categorico", transformador_categorico, columnas_categoricas),
            ]
        )
        print("✅ Pipeline de preprocesamiento creado")
        return self.preprocesador

    def entrenar_modelos(self, X, y_reg, y_clf):
        """Entrena modelos de regresión y clasificación"""
        X_train, X_test, y_train_reg, y_test_reg = train_test_split(
            X, y_reg, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )
        _, _, y_train_clf, y_test_clf = train_test_split(
            X, y_clf, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )

        # Modelos
        self.modelo_regresion = Pipeline(
            steps=[
                ("preprocesador", self.preprocesador),
                (
                    "modelo",
                    RandomForestRegressor(
                        n_estimators=200, max_depth=10, random_state=RANDOM_STATE
                    ),
                ),
            ]
        )

        self.modelo_clasificacion = Pipeline(
            steps=[
                ("preprocesador", self.preprocesador),
                ("modelo", LogisticRegression(random_state=RANDOM_STATE)),
            ]
        )

        # Entrenamiento
        print("⏳ Entrenando modelo de regresión...")
        self.modelo_regresion.fit(X_train, y_train_reg)

        print("⏳ Entrenando modelo de clasificación...")
        self.modelo_clasificacion.fit(X_train, y_train_clf)

        # Evaluación
        y_pred_reg = self.modelo_regresion.predict(X_test)
        y_pred_clf = self.modelo_clasificacion.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
        r2 = r2_score(y_test_reg, y_pred_reg)
        accuracy = accuracy_score(y_test_clf, y_pred_clf)

        print(f"📊 Resultados Regresión -> RMSE: {rmse:.4f}, R²: {r2:.4f}")
        print(f"📊 Resultados Clasificación -> Accuracy: {accuracy:.4f}")
        print(
            "\nReporte de clasificación:\n",
            classification_report(y_test_clf, y_pred_clf),
        )
        print("Matriz de confusión:\n", confusion_matrix(y_test_clf, y_pred_clf))

        return True

    def guardar_modelos(self, ruta_base="models"):
        """Guarda los modelos entrenados"""
        import os

        os.makedirs(ruta_base, exist_ok=True)
        joblib.dump(self.modelo_regresion, f"{ruta_base}/modelo_regresion.pkl")
        joblib.dump(self.modelo_clasificacion, f"{ruta_base}/modelo_clasificacion.pkl")
        joblib.dump(self.preprocesador, f"{ruta_base}/preprocesador.pkl")
        print(f"💾 Modelos guardados en {ruta_base}/")

    def cargar_modelos(self, ruta_base="models"):
        """Carga modelos previamente guardados"""
        self.modelo_regresion = joblib.load(f"{ruta_base}/modelo_regresion.pkl")
        self.modelo_clasificacion = joblib.load(f"{ruta_base}/modelo_clasificacion.pkl")
        self.preprocesador = joblib.load(f"{ruta_base}/preprocesador.pkl")
        print("✅ Modelos cargados correctamente")


# Ejemplo de uso
if __name__ == "__main__":
    ruta = "cars_data.csv"  # Exporta tu tabla a CSV o conéctala vía SQL
    modelo = AutomovilesModelEnhanced(ruta)

    df = modelo.cargar_datos()
    X, y_reg, y_clf, cols_num, cols_cat = modelo.preparar_datos()
    modelo.crear_pipeline_preprocesamiento(cols_num, cols_cat)
    modelo.entrenar_modelos(X, y_reg, y_clf)
    modelo.guardar_modelos()
