# 🚗 Vehicle Price Prediction Platform

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-FF6B6B?style=for-the-badge&logo=tensorflow&logoColor=white)

Una plataforma completa de Machine Learning para predecir precios de vehículos, generar informes ejecutivos y proporcionar insights de negocio mediante modelos de regresión y clasificación.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Secciones de la Aplicación](#-secciones-de-la-aplicación)
- [Modelos de ML](#-modelos-de-ml)
- [Formato de Datos](#-formato-de-datos)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)

## 🌟 Características

### 🎯 Dashboard Principal
- **KPIs en Tiempo Real**: Total de vehículos, precio promedio, precisión del modelo, marca más común
- **Visualizaciones Interactivas**: Distribución de precios, capacidad del motor vs precio
- **Métricas de Modelos**: Rendimiento detallado de algoritmos de ML
- **Resumen del Dataset**: Estadísticas completas de los datos

### 📊 Informes Ejecutivos
- **Análisis de ROI**: Retorno de inversión y período de recuperación
- **Impacto Empresarial**: Métricas de negocio y recomendaciones estratégicas
- **Pronósticos**: Proyecciones a 12 meses de precisión y ahorros
- **Análisis de Riesgos**: Detección de outliers y calidad de datos

### 🤖 Plataforma ML
- **Modelo de Regresión**: Predicción de precios con Linear Regression
- **Clasificador de Vehículos**: Categorización con Decision Tree
- **Detección de Outliers**: Identificación de valores atípicos
- **Análisis de Features**: Importancia de características
- **Pipeline Completo**: Flujo integral de ML

### 📁 Carga de Datos
- **Interfaz Intuitiva**: Subida sencilla de archivos CSV
- **Validación de Datos**: Verificación de formato y calidad
- **Vista Previa**: Exploración rápida de los datos
- **Procesamiento Automático**: Preparación para ML

## 📁 Estructura del Proyecto

```
F5ProjectV_ProblemaDeRegresion/
├── notebook/
│   ├── mejor_modelo_clasificacion_Decision_Tree.pkl
│   ├── mejor_modelo_regresion_Linear_Regression.pkl
│   └── EDA/
│       ├── ExecutiveReports.html
│       ├── MLModels.html
│       └── static_dashboard.html
└── frontend/
    └── streamlit_car_prediction_app.py
```

## 🚀 Instalación

### Prerrequisitos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   # Si tienes el repositorio en GitHub
   git clone <url-del-repositorio>
   cd F5ProjectV_ProblemaDeRegresion/frontend
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install streamlit pandas numpy plotly
   ```

## 💻 Uso

### Ejecutar la aplicación
```bash
streamlit run streamlit_car_prediction_app.py
```

La aplicación se abrirá automáticamente en tu navegador predeterminado en `http://localhost:8501`.

### Navegación
Utiliza la barra lateral para navegar entre las diferentes secciones:
- **Dashboard Principal**: Vista general del sistema
- **Informes Ejecutivos**: Análisis de negocio y ROI
- **Plataforma ML**: Entrenamiento y predicciones
- **Cargar Datos**: Gestión de datasets

## 📊 Secciones de la Aplicación

### 1. Dashboard Principal
- **KPIs Principales**: Métricas clave del sistema
- **Gráficos Interactivos**: Visualizaciones de datos
- **Rendimiento de Modelos**: Métricas de precisión
- **Resumen Técnico**: Detalles de implementación

### 2. Informes Ejecutivos
- **Resumen Ejecutivo**: Puntos clave para la dirección
- **Análisis Financiero**: ROI, ahorros y período de recuperación
- **Recomendaciones Estratégicas**: Acciones priorizadas
- **Pronósticos**: Tendencias futuras

### 3. Plataforma ML
- **Entrenamiento de Modelos**: Interface para entrenar algoritmos
- **Predicciones en Tiempo Real**: Estimación de precios y clasificación
- **Evaluación de Modelos**: Métricas de rendimiento
- **Exportación**: Descarga de modelos entrenados

### 4. Cargar Datos
- **Subida de Archivos**: Interface drag-and-drop
- **Validación**: Verificación automática de formato
- **Vista Previa**: Exploración de datos cargados
- **Procesamiento**: Preparación para análisis

## 🤖 Modelos de ML

### Modelo de Regresión (Precios)
- **Algoritmo**: Linear Regression
- **Precisión**: 85% R² score
- **Métricas**: 
  - MAE: $2,150
  - RMSE: $3,420
  - R²: 0.85

### Modelo de Clasificación (Categorías)
- **Algoritmo**: Decision Tree
- **Precisión**: 92% accuracy
- **Métricas**:
  - Precision: 91%
  - Recall: 89%
  - F1-Score: 90%

### Características Utilizadas
1. Engine_cc (Capacidad del motor)
2. HP (Caballos de fuerza)
3. Seats (Número de asientos)
4. Year (Año de fabricación)
5. Brand (Marca)
6. Fuel_Type (Tipo de combustible)
7. Vehicle_Type (Tipo de vehículo)

## 📝 Formato de Datos

### Estructura del CSV Requerido
```csv
Brand,Model,Year,Engine_cc,HP,Seats,Fuel_Type,Vehicle_Type,Price_Min
Toyota,Corolla,2020,1800,140,5,Petrol,Sedan,22000
BMW,X5,2021,3000,340,5,Petrol,SUV,65000
Tesla,Model 3,2022,0,283,5,Electric,Sedan,45000
```

### Columnas Requeridas
- **Brand**: Marca del vehículo (Texto)
- **Model**: Modelo específico (Texto)
- **Year**: Año de fabricación (Número)
- **Engine_cc**: Capacidad del motor en cc (Número)
- **HP**: Caballos de fuerza (Número)
- **Seats**: Número de asientos (Número)
- **Fuel_Type**: Tipo de combustible (Petrol/Diesel/Hybrid/Electric)
- **Vehicle_Type**: Tipo de vehículo (Sedan/SUV/Hatchback/Coupe/Convertible)
- **Price_Min**: Precio de referencia (Número, variable objetivo)

## 🛠 Tecnologías Utilizadas

### Backend & ML
- **Python 3.x**: Lenguaje principal
- **Streamlit**: Framework para aplicaciones web
- **Pandas**: Manipulación y análisis de datos
- **NumPy**: Cálculos numéricos
- **Scikit-learn**: Algoritmos de Machine Learning

### Frontend & Visualización
- **Plotly**: Gráficos interactivos
- **CSS Personalizado**: Estilos y animaciones
- **HTML5**: Estructura semántica

### Machine Learning
- **Linear Regression**: Predicción de precios
- **Decision Tree**: Clasificación de vehículos
- **Métricas de Evaluación**: R², MAE, RMSE, Accuracy, Precision, Recall

## 📈 Métricas de Rendimiento

### Actuales
- **Precisión de Regresión**: 85% R²
- **Precisión de Clasificación**: 92% Accuracy
- **Detección de Outliers**: 97% Recall
- **Tiempo de Entrenamiento**: 1.2 segundos
- **Velocidad de Inferencia**: <10ms por predicción

### Objetivos
- **Precisión de Regresión**: 90% R²
- **Precisión de Clasificación**: 95% Accuracy
- **Cobertura de Características**: 15/15 features

## 🎯 Casos de Uso

### Para Dealers de Vehículos
- Valoración precisa de inventario
- Clasificación automática de vehículos
- Detección de precios anómalos

### Para Compradores
- Estimación justa de precios
- Comparación entre categorías
- Identificación de mejores ofertas

### Para Analistas de Negocio
- Informes ejecutivos automatizados
- Análisis de tendencias del mercado
- ROI de implementación de ML

## 🔧 Desarrollo Futuro

### Próximas Características
- [ ] Integración con APIs de mercado en tiempo real
- [ ] Modelos especializados por categoría (Luxury, EV, etc.)
- [ ] Sistema de feedback para mejora continua
- [ ] Dashboard móvil responsive
- [ ] Exportación de informes en PDF/Excel

### Mejoras Planeadas
- [ ] Incorporación de imágenes de vehículos
- [ ] Análisis de sentimiento de reviews
- [ ] Predicción de depreciación
- [ ] Integración con sistemas CRM

## 📞 Soporte

Para reportar issues o solicitar características:
1. Revisa la documentación existente
2. Verifica que el formato de datos sea correcto
3. Proporciona ejemplos específicos del problema

## 📄 Licencia

Este proyecto es para fines educativos y demostrativos. Consulte los términos de uso para implementaciones comerciales.

---

**¿Listo para empezar?** Ejecuta `streamlit run streamlit_car_prediction_app.py` y comienza a explorar el poder del Machine Learning para la predicción de precios de vehículos! 🚀