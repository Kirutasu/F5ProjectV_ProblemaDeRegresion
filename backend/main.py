# backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.logger import logger
from ml.service import CarPredictionService
from api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación."""
    logger.info("Iniciando aplicación FastAPI...")
    
    # Inicializar servicio de ML
    try:
        app.state.car_service = CarPredictionService()
        logger.info("Servicio de predicción inicializado correctamente")
    except Exception as e:
        logger.error(f"❌ Error inicializando el servicio de predicción: {e}")
        app.state.car_service = None
    
    yield
    
    # Cleanup
    logger.info("Apagando aplicación FastAPI...")
    app.state.car_service = None

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(router)

# Manejador global de excepciones
@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Error interno del servidor: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Error interno del servidor",
            "error": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )