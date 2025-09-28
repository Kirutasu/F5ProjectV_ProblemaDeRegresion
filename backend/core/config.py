# backend/core/config.py
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración centralizada de la aplicación."""
    
    # Configuración de la API
    API_TITLE: str = "API de Predicción de Precios de Autos"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API para predecir precios de automóviles usando modelos de ML"
    
    # Configuración del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # Base de datos
    DATABASE_URL: str | None = None   # 👈 lee postgres://... de .env
    
    # Configuración de modelos
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    NOTEBOOK_DIR: Path = BASE_DIR / "notebook"
    ASSETS_DIR: Path = BASE_DIR / "backend" / "assets"
    DATA_DIR: Path = BASE_DIR / "data" 

    # CORRECCIÓN: Usar los modelos que realmente existen
    MODEL_PATHS: dict = {
        "clasificacion": NOTEBOOK_DIR / "mejor_modelo_clasificacion_Decision_Tree.pkl",
        "regresion": NOTEBOOK_DIR / "mejor_modelo_regresion_Linear_Regression.pkl",
        # Usar el modelo de regresión lineal como modelo principal
        "bagging": NOTEBOOK_DIR / "mejor_modelo_regresion_Linear_Regression.pkl",
        # Usar el pipeline de clasificación como preprocesador (ya incluye transformaciones)
        "preprocesador": NOTEBOOK_DIR / "mejor_modelo_clasificacion_Decision_Tree.pkl"
    }
    
    # Configuración CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()