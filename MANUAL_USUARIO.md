# 📖 Manual de Usuario - CarPredict

## Sistema de Predicción de Precios de Automóviles

---

## ▶️ Cómo ejecutar la app

### Opción A: Docker Compose (recomendado)

1. Desde la raíz del proyecto:
```bash
docker compose up --build -d
```
2. Accede a:
- UI: http://localhost:8501
- API: http://localhost:8000 (documentación en /docs)

3. Probar predicción (opcional):
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

### Opción B: Ejecución local (sin Docker)

1. Crear entorno e instalar dependencias (raíz):
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```
2. Backend (terminal 1):
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
3. Frontend (terminal 2):
```bash
cd frontend
streamlit run streamlit_car_prediction_app.py --server.port 8501
```

### Variables de entorno

- **BACKEND_URL** (para que el frontend apunte al backend):
  - En Docker Compose ya se define como `BACKEND_URL=http://backend:8000`.
  - En ejecución local, si es necesario, exporta/define:
    - Windows (PowerShell):
      ```powershell
      $env:BACKEND_URL = "http://localhost:8000"
      ```
    - Windows (CMD):
      ```bat
      set BACKEND_URL=http://localhost:8000
      ```
    - macOS/Linux:
      ```bash
      export BACKEND_URL=http://localhost:8000
      ```

### Comprobación rápida

- **Acceder a la UI**: `http://localhost:8501`
- **Docs API**: `http://localhost:8000/docs`
- **Health**: `http://localhost:8000/health`
- **Probar predicción (curl)**:
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

### Detener servicios

- **Docker Compose**:
  ```bash
  docker compose down
  ```
- **Ejecución local**:
  - Detén con `Ctrl + C` las terminales donde corrían `uvicorn` y `streamlit`.

---

## 🚀 Introducción

**CarPredict** es un sistema inteligente que utiliza Machine Learning para predecir precios de automóviles basándose en sus especificaciones técnicas. El sistema combina modelos avanzados de regresión y clasificación para proporcionar estimaciones precisas y categorizaciones de precios.

---

## 🌐 Acceso al Sistema

### URL de Acceso
- **Frontend**: http://localhost:8501
- **API Backend**: http://localhost:8000

### Requisitos del Sistema
- Navegador web moderno (Chrome, Firefox, Safari, Edge)
- Conexión a internet estable
- JavaScript habilitado

---

## 🏠 Página de Inicio

### Características Principales

Al acceder al sistema, encontrarás:

1. **Hero Section**: Presentación del sistema con botones de acceso rápido
2. **Estado del Sistema**: Monitoreo en tiempo real de:
   - ✅ API Backend (Activo/Inactivo)
   - 🤖 Modelos ML (Entrenados/No listos)
   - 📊 Base de Datos (Conectada/Error)

3. **Funcionalidades Disponibles**:
   - 🔮 **Predicción Inteligente**: Estimar precios con IA
   - 📊 **Explorar Datos**: Navegar por la base de datos
   - 📈 **Análisis Estadístico**: Ver tendencias y patrones

4. **Proceso del Sistema**:
   - **Paso 1**: Ingresa los datos técnicos
   - **Paso 2**: Procesamiento con IA
   - **Paso 3**: Obtén resultados detallados

---

## 🔮 Predictor de Precios

### Cómo Usar el Predictor

#### Paso 1: Información del Motor ⚙️
Ingresa las especificaciones del motor:

- **Capacidad del Motor (log)**: Logaritmo de la capacidad en CC
  - *Ejemplo*: 8.5 (equivale a ~5000cc)
  - *Rango típico*: 6.5 - 9.5

- **Potencia (log)**: Logaritmo de la potencia en HP
  - *Ejemplo*: 6.8 (equivale a ~900hp)
  - *Rango típico*: 4.0 - 7.5

- **Torque (log)**: Logaritmo del torque en Nm
  - *Ejemplo*: 6.7 (equivale a ~800Nm)
  - *Rango típico*: 4.0 - 7.5

#### Paso 2: Rendimiento 🏎️
Especifica el rendimiento del vehículo:

- **Velocidad Máxima (transformada)**: Transformación Box-Cox
  - *Ejemplo*: 1.5
  - *Rango típico*: -2.0 - 3.0

- **Aceleración 0-100 km/h (recíproca)**: Inverso del tiempo
  - *Ejemplo*: 0.3 (equivale a 3.3 segundos)
  - *Rango típico*: 0.05 - 0.5

#### Paso 3: Configuración 🪑
Características adicionales:

- **Número de Asientos (transformado)**: Transformación Yeo-Johnson
  - *Ejemplo*: -0.5 (equivale a 2 asientos deportivos)
  - *Rango típico*: -2.0 - 1.0

### Funciones Auxiliares

- **📋 Cargar Datos de Ejemplo**: Llena automáticamente con valores de prueba
- **🔄 Limpiar Formulario**: Reinicia todos los campos
- **← Anterior / Siguiente →**: Navega entre pasos
- **🔮 Predecir Precio**: Ejecuta la predicción

### Interpretación de Resultados

El sistema proporciona:

1. **Precio Predicho**: Estimación en formato monetario
2. **Categoría**:
   - 🔴 **Precio Alto**: Vehículos premium/deportivos
   - 🟡 **Precio Medio**: Vehículos de gama media
   - 🟢 **Precio Bajo**: Vehículos económicos

3. **Probabilidad**: Confianza del modelo (0-100%)
4. **Modelos Utilizados**:
   - Random Forest (Regresión)
   - Logistic Regression (Clasificación)

---

## 📊 Explorador de Datos

### Filtros de Búsqueda

#### Filtros Disponibles:
- **Precio Mínimo/Máximo (log)**: Rango de precios
- **Categoría de Precio**: Alto, Medio, Bajo, o Todas
- **Límite de Resultados**: Máximo 500 registros

#### Cómo Filtrar:
1. Ajusta los filtros según tus necesidades
2. Haz clic en **🔍 Aplicar Filtros**
3. Usa **🔄 Limpiar Filtros** para resetear

### Visualización de Datos

#### Vista Desktop:
- Tabla completa con todas las columnas
- Información organizada en columnas fijas

#### Vista Mobile:
- Tarjetas individuales por automóvil
- Información condensada y fácil de leer

#### Información Mostrada:
- **ID**: Identificador único
- **Motor**: Capacidad del motor (log)
- **Potencia**: Potencia del motor (log)
- **Velocidad Máxima**: Velocidad transformada
- **Precio**: Precio en escala logarítmica
- **Categoría**: Badge con color según precio
- **Asientos**: Tipo de configuración
- **Torque**: Torque del motor (log)

### Badges de Categorías

- 🔴 **Precio Alto**: Vehículos premium
- 🟡 **Precio Medio**: Gama media
- 🟢 **Precio Bajo**: Económicos

- 🟣 **Deportivo (1-2)**: Vehículos deportivos
- 🔵 **Compacto (3-4)**: Vehículos compactos
- 🟢 **Familiar (5-10)**: Vehículos familiares
- 🟡 **Comercial (11+)**: Vehículos comerciales

---

## 📈 Estadísticas del Sistema

### Resumen General

#### Tarjetas de Información:
- 🚗 **Total de Automóviles**: Cantidad en base de datos
- 💰 **Precio Promedio**: Precio medio en escala log
- 🏷️ **Categorías de Precio**: Número de categorías
- 🪑 **Tipos de Asientos**: Variedad de configuraciones

### Gráficos Disponibles

#### 1. Distribución por Categorías (Gráfico de Pastel)
- Muestra el porcentaje de cada categoría de precio
- Colores diferenciados por categoría
- Tooltips con información detallada

#### 2. Distribución de Precios (Gráfico de Barras)
- Histograma de precios en rangos
- Eje X: Rangos de precios (log)
- Eje Y: Cantidad de vehículos

#### 3. Distribución por Asientos (Barras Horizontales)
- Cantidad de vehículos por tipo de asiento
- Fácil comparación visual

#### 4. Relación Motor vs Precio (Línea)
- Correlación entre capacidad del motor y precio
- Muestra tendencias generales

### Estadísticas Detalladas

#### Sección de Precios:
- Precio mínimo, máximo y promedio
- Todos en escala logarítmica

#### Motor y Potencia:
- Promedios de capacidad del motor
- Promedios de potencia

#### Distribución por Categorías:
- Cantidad exacta por categoría
- Badges con colores identificativos

### Rendimiento de Modelos

#### Modelo de Regresión (Random Forest):
- **RMSE**: 0.4092 (Error cuadrático medio)
- **R²**: 0.8413 (Coeficiente de determinación)

#### Modelo de Clasificación (Logistic Regression):
- **Accuracy**: 90.96% (Precisión general)
- **Datos**: Total de registros procesados

---

## 🔧 Solución de Problemas

### Problemas Comunes

#### 1. La página no carga
- **Causa**: Servicios no iniciados
- **Solución**: Verificar que Docker esté ejecutándose
- **Comando**: `docker-compose ps`

#### 2. Error de conexión con el backend
- **Causa**: Backend no disponible
- **Solución**: Verificar estado en la página de inicio
- **URL de prueba**: http://localhost:8000/health

#### 3. Predicciones no funcionan
- **Causa**: Modelos no entrenados
- **Solución**: Esperar a que se entrenen automáticamente
- **Indicador**: Estado del sistema en página de inicio

#### 4. Datos no se cargan
- **Causa**: Base de datos desconectada
- **Solución**: Reiniciar servicios
- **Comando**: `docker-compose restart`

### Códigos de Estado

- ✅ **Verde**: Todo funcionando correctamente
- 🟡 **Amarillo**: Advertencia o carga en progreso
- 🔴 **Rojo**: Error que requiere atención

---

## 📱 Compatibilidad

### Navegadores Soportados
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### Dispositivos
- 💻 **Desktop**: Experiencia completa
- 📱 **Mobile**: Interfaz adaptativa
- 📟 **Tablet**: Diseño responsivo

### Resoluciones
- Mínima: 320px (móviles)
- Óptima: 1200px+ (desktop)
- Máxima: Sin límite

---

## 🎯 Consejos de Uso

### Para Mejores Resultados

1. **Usa Datos de Ejemplo**: Comienza con los valores precargados
2. **Verifica Rangos**: Mantén los valores dentro de los rangos sugeridos
3. **Interpreta Contexto**: Los valores están transformados matemáticamente
4. **Compara Resultados**: Usa el explorador para validar predicciones

### Interpretación de Transformaciones

- **Log**: Valores originales elevados a escala logarítmica
- **Box-Cox**: Transformación para normalizar distribuciones
- **Yeo-Johnson**: Similar a Box-Cox pero acepta valores negativos
- **Recíproca**: Inverso del valor original (1/x)

### Valores de Referencia

| Transformación | Valor Ejemplo | Equivalencia Aproximada |
|----------------|---------------|-------------------------|
| Motor (log) | 8.5 | ~5000cc |
| Potencia (log) | 6.8 | ~900hp |
| Torque (log) | 6.7 | ~800Nm |
| Velocidad (Box-Cox) | 1.5 | ~250km/h |
| Aceleración (1/x) | 0.3 | ~3.3s |
| Asientos (YJ) | -0.5 | ~2 asientos |

---

## 📞 Soporte Técnico

### Información del Sistema
- **Versión**: 2.0.0
- **Tecnologías**: Streamlit + FastAPI + SQLite/PostgreSQL
- **Modelos**: Random Forest + Logistic Regression
- **Base de Datos**: 827+ automóviles
---

**¡Gracias por usar CarPredict! 🚗✨**

*Sistema desarrollado con ❤️ usando las mejores prácticas de Machine Learning y desarrollo web moderno.*
