# 🚗 F5ProjectV - Sistema de Predicción de Precios de Automóviles

Un sistema completo de machine learning para predicción de precios de automóviles utilizando datos transformados y modelos avanzados de regresión y clasificación.

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Uso de la API](#-uso-de-la-api)
- [Estructura de Datos](#-estructura-de-datos)
- [Modelos de Machine Learning](#-modelos-de-machine-learning)
- [Endpoints Disponibles](#-endpoints-disponibles)
- [Testing y Validación](#-testing-y-validación)
- [Contribución](#-contribución)

## ✨ Características Principales

- **Predicción de Precios**: Modelos de regresión avanzados para estimar precios de automóviles
- **Clasificación de Precios**: Sistema binario para categorizar vehículos como "Precio Alto" o "Precio Bajo"
- **API RESTful**: Endpoints FastAPI para integración con aplicaciones frontend
- **Datos Transformados**: Utiliza transformaciones logarítmicas y Box-Cox para mejorar el rendimiento de los modelos
- **Entrenamiento Automático**: Los modelos se entrenan automáticamente al iniciar la aplicación
- **Validación Robusta**: Sistema completo de validación de datos de entrada y salida

## 🏗️ Arquitectura del Sistema

```
F5ProjectV_ProblemaDeRegresion/
├── backend/
│   ├── main.py                 # API FastAPI principal
│   ├── models.py              # Modelos Pydantic
│   ├── ml_service.py          # Servicio de ML
│   ├── validation.py          # Validación de datos
│   ├── modelo_final.py        # Modelo ML avanzado
│   └── requirements.txt       # Dependencias
├── data/
│   └── new_data.csv          # Datos transformados
├── generate_sql.py           # Generador de SQL
├── cars_data.sql            # Base de datos SQL
├── docker-compose.yml       # Docker Compose
└── frontend/                # Aplicación frontend
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- PostgreSQL
- Docker (opcional)

### Instalación con Docker

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd F5ProjectV_ProblemaDeRegresion
   ```

2. **Configurar variables de entorno**:
   ```bash
   cp backend/.env.example backend/.env
   ```

   Editar `backend/.env`:
   ```env
   DATABASE_URL=postgresql://myuser:mypass@db:5432/mydb
   ```

3. **Levantar servicios con Docker**:
   ```bash
   docker-compose up -d
   ```

4. **Instalar dependencias**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Instalación Manual

1. **Configurar PostgreSQL**:
   ```sql
   CREATE DATABASE mydb;
   CREATE USER myuser WITH PASSWORD 'mypass';
   GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
   ```

2. **Cargar datos**:
   ```bash
   psql -h localhost -U myuser -d mydb -f cars_data.sql
   ```

3. **Ejecutar la aplicación**:
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🖼️ Frontend (Vite)

El proyecto incluye una aplicación frontend basada en React + Vite en `frontend/regresiones_frontend/`.

- Puerto de desarrollo (Docker): `http://localhost:8005`
- API Backend (Docker): `http://localhost:8000`
- Variable de entorno para el frontend: `VITE_BACKEND_URL`

Con Docker Compose, esta variable ya se pasa al contenedor del frontend como `VITE_BACKEND_URL=http://backend:8000` (ver `docker-compose.yml`).

Para ejecutar el frontend localmente fuera de Docker:

```bash
cd frontend/regresiones_frontend
cp .env .env.local  # opcional; ajusta VITE_BACKEND_URL si lo necesitas
npm install
npm run dev
```

Abre `http://localhost:3000` y asegúrate de que `VITE_BACKEND_URL` apunte al backend (por defecto `http://localhost:8000`).

## 🔧 Uso de la API

### Verificar Estado del Sistema

```bash
curl http://localhost:8000/health
```

Respuesta:
```json
{
  "status": "healthy",
  "models_trained": true
}
```

### Obtener Información de Modelos

```bash
curl http://localhost:8000/model/info
```

### Obtener Datos de Automóviles

```bash
# Obtener todos los autos (limitado a 100)
curl http://localhost:8000/cars?limit=100

# Filtrar por precio
curl "http://localhost:8000/cars/filter?min_price=10&max_price=15&limit=50"
```

### Realizar Predicción

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "engine_capacity_in_cc_log": 8.5,
    "horsepower_in_hp_log": 6.8,
    "horsepower_in_hp_2_log": 6.8,
    "max_speed_in_km_h_boxcox": 1.5,
    "time_to_100kmph_sec_reciprocal": 0.3,
    "seats_yeojohnson": -0.5,
    "torque_in_nm_log": 6.7,
    "torque_in_nm_2_log": 6.7
  }'
```

Respuesta:
```json
{
  "precio_predicho": 45000.50,
  "categoria_predicha": "Precio Alto",
  "probabilidad_alta": 0.85,
  "modelo_usado_regresion": "Random Forest",
  "modelo_usado_clasificacion": "Logistic Regression"
}
```

### Entrenar Modelos

```bash
curl -X POST http://localhost:8000/train
```

## 📊 Estructura de Datos

### Columnas de Datos Transformados

| Columna | Descripción | Transformación |
|---------|-------------|----------------|
| `engine_capacity_in_cc_log` | Capacidad del motor (log) | Logarítmica |
| `horsepower_in_hp_log` | Potencia (log) | Logarítmica |
| `horsepower_in_hp_2_log` | Potencia secundaria (log) | Logarítmica |
| `max_speed_in_km_h_boxcox` | Velocidad máxima | Box-Cox |
| `time_to_100kmph_sec_reciprocal` | Tiempo a 100km/h | Recíproca |
| `price_max_log` | Precio máximo (log) | Logarítmica |
| `seats_yeojohnson` | Número de asientos | Yeo-Johnson |
| `torque_in_nm_log` | Torque (log) | Logarítmica |
| `torque_in_nm_2_log` | Torque secundario (log) | Logarítmica |
| `precio_categoria` | Categoría de precio | Categórica |
| `precio_alto` | Precio alto (0/1) | Binaria |
| `seats_cat` | Categoría de asientos | Categórica |

## 🤖 Modelos de Machine Learning

### Modelo de Regresión
- **Algoritmo**: Random Forest Regressor
- **Parámetros**:
  - `n_estimators`: 200
  - `max_depth`: 10
  - `random_state`: 42
- **Métricas objetivo**: RMSE, MAE, R²

### Modelo de Clasificación
- **Algoritmo**: Logistic Regression
- **Métricas objetivo**: Accuracy, Precision, Recall, F1-Score, AUC-ROC

## 🔌 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del sistema |
| GET | `/model/info` | Información de modelos |
| GET | `/cars` | Listar automóviles |
| GET | `/cars/filter` | Filtrar automóviles |
| POST | `/predict` | Realizar predicción |
| POST | `/train` | Entrenar modelos |
| GET | `/stats/columns` | Columnas disponibles |
| GET | `/stats/distinct` | Valores distintos |

## 🧪 Testing y Validación

### Testing Automático

El sistema incluye validación automática de:

- **Datos de entrada**: Rangos válidos y tipos correctos
- **Modelos entrenados**: Verificación de rendimiento
- **Respuestas**: Estructura y tipos de datos
- **Conexión a BD**: Disponibilidad y accesibilidad

### Validación Manual

```python
# Ejemplo de testing
import requests

# Test de predicción
response = requests.post("http://localhost:8000/predict", json={
    "engine_capacity_in_cc_log": 8.5,
    "horsepower_in_hp_log": 6.8,
    "horsepower_in_hp_2_log": 6.8,
    "max_speed_in_km_h_boxcox": 1.5,
    "time_to_100kmph_sec_reciprocal": 0.3,
    "seats_yeojohnson": -0.5,
    "torque_in_nm_log": 6.7,
    "torque_in_nm_2_log": 6.7
})

print(response.json())
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```env
DATABASE_URL=postgresql://user:password@host:port/database
LOG_LEVEL=INFO
MODEL_UPDATE_INTERVAL=3600  # segundos
MAX_PREDICTIONS_PER_HOUR=1000
```

### Parámetros de Modelos

Los parámetros de los modelos se pueden configurar en `ml_service.py`:

```python
# Ejemplo de configuración
model_config = {
    "regresion": {
        "n_estimators": 200,
        "max_depth": 10,
        "random_state": 42
    },
    "clasificacion": {
        "random_state": 42
    }
}
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Historial de Versiones

### v2.0.0 (2024)
- ✅ Integración completa con modelo_final.py
- ✅ API FastAPI optimizada
- ✅ Sistema de validación robusto
- ✅ Entrenamiento automático
- ✅ Documentación completa

### v1.0.0 (2023)
- ✅ Modelo básico de regresión
- ✅ API inicial
- ✅ Base de datos PostgreSQL

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

Para soporte técnico, contactar al equipo de desarrollo:

- **Email**: support@f5project.com
- **Issues**: [GitHub Issues](https://github.com/username/F5ProjectV_ProblemaDeRegresion/issues)
- **Documentación**: [Wiki](https://github.com/username/F5ProjectV_ProblemaDeRegresion/wiki)

---

**¡Gracias por usar F5ProjectV! 🚗✨**
