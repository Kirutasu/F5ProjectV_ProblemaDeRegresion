# Vehicle Price Prediction Platform

Plataforma de Machine Learning de punta a punta para predecir precios de automóviles. Incluye API (FastAPI), dashboard (Streamlit), artefactos de modelo versionados y orquestación con Docker Compose.


## Características

- **API REST** con FastAPI para predicciones en tiempo real
- **Dashboard interactivo** con Streamlit y visualizaciones avanzadas
- **Modelos ML optimizados**: Decision Tree (99.59% precisión) y Linear Regression
- **Base de datos PostgreSQL** para almacenamiento persistente
- **Arquitectura Docker** para despliegue escalable
- **Informes ejecutivos** con métricas de ROI y análisis de negocio

## Arquitectura del Proyecto

```bash
# Clonar repositorio
git clone <repository-url>
cd F5ProjectV_ProblemaDeRegresion

# Configurar entorno
cp .env.example .env
chmod +x scripts/*.sh

# Iniciar con Docker
docker-compose up --build -d

# O usar Makefile
make up
```

**URLs de acceso:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

### Opción 2: Ejecución Local

```bash
# Configurar entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servicios
./scripts/run-local.sh
```

### Opción 3: Sin Conectividad Docker

Si tienes problemas de conectividad Docker:

```bash
# Usar versión offline
docker-compose -f docker-compose-offline.yml up --build

# O ejecutar diagnóstico
./scripts/fix-docker.sh
```

## Comandos Útiles

```bash
# Ver estado de servicios
make check

# Ver logs
make logs

# Limpiar recursos Docker
make clean

# Backup de base de datos
make backup-db

# Health check detallado
make health

# Ayuda completa
make help
```

## API Endpoints

### Predicción de Precios
```http
POST /predict
Content-Type: application/json

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

### Health Check
```http
GET /health
```

### Información del Modelo
```http
GET /model-info
```

## Modelos de Machine Learning

### Clasificación
- **Algoritmo**: Decision Tree
- **Precisión**: 99.59%
- **Características**: 12 features de entrada
- **Uso**: Clasificación de tipos de vehículos

### Regresión
- **Algoritmo**: Linear Regression
- **R²**: 0.93
- **MAE**: $2,150
- **Uso**: Predicción de precios

## Dashboard Features

### Panel Principal
- KPIs en tiempo real
- Distribución de precios
- Análisis por marca y tipo de combustible
- Métricas de rendimiento del modelo

### Informes Ejecutivos
- ROI y análisis de costos
- Recomendaciones estratégicas
- Proyecciones de ahorro
- Métricas de negocio

### Plataforma ML
- Entrenamiento de modelos
- Predicciones interactivas
- Pipeline completo de ML
- Monitoreo de rendimiento

## Estructura de Datos

### Entrada Requerida
```json
{
  "Manufacturer": "string",
  "Model": "string", 
  "Year": "integer",
  "Transmission": "string",
  "Mileage": "integer",
  "FuelType": "string",
  "EngineSize": "float"
}
```

### Respuesta de Predicción
```json
{
  "status": "success",
  "message": "Predicción realizada correctamente",
  "data": {
    "predicted_price": 25750.50
  }
}
```

## Configuración

### Variables de Entorno
```bash
# API Configuration
API_TITLE="API de Predicción de Precios de Autos"
API_VERSION="1.0.0"

# Database
DATABASE_URL=postgresql://myuser:mypass@db:5432/mydb

# Server
HOST=0.0.0.0
PORT=8000
```

### Base de Datos
- **PostgreSQL 15** para producción
- **SQLite** para desarrollo local
- Migrations automáticos en inicio
- Backup automático disponible

## Desarrollo

### Estructura del Backend
```
backend/
├── api/
│   ├── dependencies.py  # Inyección de dependencias
│   ├── routes.py       # Endpoints REST
│   └── schemas.py      # Modelos Pydantic
├── core/
│   ├── config.py       # Configuración
│   └── logger.py       # Logging
├── ml/
│   └── service.py      # Servicio ML
└── main.py            # Aplicación FastAPI
```

### Estructura del Frontend
```
frontend/
├── streamlit_car_prediction_app.py  # App principal
├── .streamlit/
│   └── config.toml                  # Configuración Streamlit
└── requirements.txt
```

## Monitoreo y Logs

### Health Checks
- **Backend**: `/health` endpoint
- **Database**: Conexión PostgreSQL
- **Models**: Estado de modelos ML

### Logging
- Logs estructurados en JSON
- Rotación automática
- Niveles: INFO, WARNING, ERROR
- Ubicación: `backend/logs/api.log`

## Despliegue en Producción

### Docker Swarm
```bash
docker swarm init
docker stack deploy -c docker-compose.yml ml-platform
```

### Kubernetes
```bash
# Generar manifiestos K8s
kompose convert -f docker-compose.yml
kubectl apply -f .
```

### Variables de Producción
- Deshabilitar `reload` en uvicorn
- Usar base de datos externa
- Configurar reverse proxy (nginx)
- SSL/HTTPS habilitado

## Troubleshooting

### Problemas Comunes

**Docker no puede descargar imágenes:**
```bash
./scripts/fix-docker.sh
docker-compose -f docker-compose-offline.yml up
```

**Modelos no se cargan:**
- Verificar rutas en `backend/core/config.py`
- Confirmar archivos `.pkl` en `notebook/`

**Frontend no conecta al backend:**
- Verificar `BACKEND_URL` en variables de entorno
- Confirmar puertos disponibles (8000, 8501)

### Logs de Debug
```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# Database logs
docker-compose logs -f db
```

## Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

#Cómo Usar

Inicio Rápido (3 pasos)

Clonar y configurar:

bash   git clone <repository-url>
   cd F5ProjectV_ProblemaDeRegresion
   cp .env.example .env

Iniciar aplicación:

bash   # Opción A: Con Docker (recomendado)
   make up
   
   # Opción B: Sin Docker
   ./scripts/run-local.sh
   
   # Opción C: Si hay problemas de conectividad
   docker-compose -f docker-compose-offline.yml up --build

Acceder a la aplicación:

Frontend: http://localhost:8501
API: http://localhost:8000
Documentación: http://localhost:8000/docs



Usar la Predicción de Precios
Desde el Dashboard Web

Ve a http://localhost:8501
Completa el formulario con datos del vehículo
Haz clic en "Predict Price"
Obtén el precio estimado

Desde la API REST
bashcurl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "Manufacturer": "Toyota",
       "Model": "Camry",
       "Year": 2022,
       "Transmission": "Automatic", 
       "Mileage": 15000,
       "FuelType": "Petrol",
       "EngineSize": 2.5
     }'
Desde Python
pythonimport requests

data = {
    "Manufacturer": "Toyota",
    "Model": "Camry", 
    "Year": 2022,
    "Transmission": "Automatic",
    "Mileage": 15000,
    "FuelType": "Petrol",
    "EngineSize": 2.5
}

response = requests.post("http://localhost:8000/predict", json=data)
precio = response.json()["data"]["predicted_price"]
print(f"Precio estimado: ${precio:,.2f}")

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Soporte

Para soporte técnico:
- Revisar documentación en `/docs`
- Verificar issues en GitHub
- Ejecutar `make help` para comandos disponibles

---

**Desarrollado con:** FastAPI • Streamlit • scikit-learn • Docker • PostgreSQL
---

## Quick start

1) Levantar con Docker Compose:
```bash
docker compose up --build -d
```
2) Acceder:
- UI (Streamlit): http://localhost:8501
- API (FastAPI): http://localhost:8000 (docs en /docs)

3) Probar predicción:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Manufacturer": "Toyota",
    "Model": "Camry",
    "Year": 2022,
    "Transmission": "Automatic",
    "Mileage": 15000,
    "FuelType": "Petrol",
    "EngineSize": 2.5
  }'
```

## Enlaces útiles

- README de Backend: `backend/README.md`
- README de Frontend: `frontend/README.md`
