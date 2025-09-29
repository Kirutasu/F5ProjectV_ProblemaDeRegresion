# Backend – FastAPI (Vehicle Price Prediction API)

API REST para predicción de precios de automóviles y verificación de salud del sistema.

## Endpoints

- POST `/predict`: Predice precio a partir de especificaciones del vehículo.
- GET `/health`: Health check del servicio.
- GET `/model-info`: Metadatos del modelo en uso.

Ejemplo `/predict`:
```json
{
  "Manufacturer": "Toyota",
  "Model": "Camry",
  "Year": 2022,
  "Transmission": "Automatic",
  "Mileage": 15000,
  "FuelType": "Petrol",
  "EngineSize": 2.5
}
```

## Ejecución local (sin Docker)

Requisitos: Python 3.10+

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r ../requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Ejecución con Docker Compose (recomendado)

Desde la raíz del proyecto:
```bash
docker compose up --build -d
```
- El contenedor usa `backend/Dockerfile` definido en `docker-compose.yml`.
- Volúmenes mapean `./notebook` en modo lectura para cargar modelos (`*.pkl`, `*.joblib`).

## Variables de entorno relevantes

Definidas en `backend/core/config.py` y `.env`:
```
API_TITLE="API de Predicción de Precios de Autos"
API_VERSION="1.0.0"
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///app/data/vehicles.db  # por defecto en docker-compose
CORS_ORIGINS=["*"]
```

## Modelos y artefactos

- Artefactos de modelo en `notebook/`: `mejor_modelo*.pkl|joblib` y `modelo_metadata.json`.
- Si faltan artefactos, `/predict` puede fallar y el health degradarse.

## Logs

- Logs estructurados (JSON) en `backend/core/logger.py`.
- Persistencia en `backend/logs/` (mapeado por Docker Compose).

## Notas

- En Docker, el frontend se comunica con `http://backend:8000`.
- En local (sin Docker), usar `http://localhost:8000`.

### Notas de compatibilidad

- `/predict` retorna un objeto envoltorio: `{ "status": "success", "message": "...", "data": { "predicted_price": <float> } }`.
- Pydantic v2: se usa `request.model_dump()` en lugar de `request.dict()`.
- Imports absolutos en ejecución como paquete: `from backend.core...`, `from backend.api...`, `from backend.ml...`.
