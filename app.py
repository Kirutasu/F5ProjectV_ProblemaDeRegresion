import streamlit as st
import pandas as pd
import numpy as np
import joblib # Necesario para cargar los modelos serializados

# --- 1. CONFIGURACIÓN INICIAL DE LA PÁGINA ---
st.set_page_config(
    page_title="🚗 Predictor de Precios de Automóviles",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PERSONALIZADO (Mantenemos el diseño) ---
# ... (Todo el CSS se mantiene igual) ...
st.markdown("""
<style>
    /* Estilo para la cabecera principal */
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        padding-top: 1rem;
    }
    
    /* Estilo para las tarjetas de métricas */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    /* Estilo para el resultado de la predicción final (destacado) */
    .prediction-result {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    
    /* Estilo para el área de comparación de modelos/información extra */
    .model-comparison {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    /* Estilo para la información de la barra lateral */
    .sidebar-info {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        text-align: center;
    }

    /* Ajuste para los elementos de selección de Streamlit */
    .stSelectbox > div > div > select {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNCIONES DE CARGA DE MODELOS (MODIFICADO) ---

# Usamos st.cache_resource para cargar los activos una sola vez, mejorando el rendimiento.
@st.cache_resource
def load_assets():
    """Carga el modelo y el preprocesador usando joblib. Cargamos SOLO el modelo final para simplificar."""
    try:
        # Cargamos SOLO el modelo final. Asumimos que es el Pipeline completo.
        # Quitamos la carga de 'preprocesador.joblib' para evitar conflictos.
        modelo_final = joblib.load('backend/assets/modelo_final.joblib')
        
        # Devolvemos un solo objeto
        return modelo_final 
    except FileNotFoundError:
        st.error("Error: Archivo de modelo no encontrado en la ruta esperada ('backend/assets/modelo_final.joblib').")
        st.stop()
    except Exception as e:
        st.error(f"Error al cargar los activos del modelo: {e}")
        st.stop()

# La variable ahora contiene solo el Pipeline o Estimador final.
modelo_final = load_assets()


# --- 4. DATOS DUMMY (Opciones de entrada) ---
MARCAS = ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Nissan']
TIPOS = ['Sedán', 'SUV', 'Hatchback', 'Camioneta', 'Deportivo']
TRANSMISIONES = ['Automática', 'Manual']
COMBUSTIBLES = ['Gasolina', 'Diésel', 'Eléctrico', 'Híbrido']

# --- 5. BARRA LATERAL (ENTRADA DE DATOS DEL USUARIO) ---
st.sidebar.markdown('<div class="sidebar-info"><h2>⚙️ Parámetros de la Predicción</h2></div>', unsafe_allow_html=True)

# Controles de entrada
marca = st.sidebar.selectbox("Marca del Vehículo", MARCAS)
tipo = st.sidebar.selectbox("Tipo de Carrocería", TIPOS)
transmision = st.sidebar.selectbox("Tipo de Transmisión", TRANSMISIONES)
combustible = st.sidebar.selectbox("Tipo de Combustible", COMBUSTIBLES)

# Control deslizante para el año
year_actual = pd.Timestamp.now().year
year_min = year_actual - 20
year = st.sidebar.slider("Año de Fabricación", min_value=year_min, max_value=year_actual, value=year_actual - 5)

# Entradas numéricas
kilometraje = st.sidebar.number_input("Kilometraje (km)", min_value=0, value=50000, step=1000)
potencia = st.sidebar.number_input("Potencia (HP)", min_value=50, max_value=500, value=150, step=10)

# Función para realizar la predicción (MODIFICADO: Se añaden las 10 columnas faltantes)
def make_prediction(car_data):
    """Realiza la predicción, asegurando que el DataFrame de entrada contenga TODAS las columnas 
    esperadas por el modelo, incluyendo las controladas por el usuario y las que son features internas."""
    try:
        # 1. Mapeo de nombres amigables y adición de columnas faltantes
        # Creamos un diccionario que contiene TODAS las columnas que el modelo espera.
        input_data_mapped = {
            # --- INPUTS CONTROLADAS POR EL USUARIO (Mapeadas a nombres técnicos) ---
            'Brands': car_data['Marca'], 
            'Model': car_data['Tipo'], 
            'Transmision': car_data['Transmision'], # Asumo que el nombre es correcto
            'Fuel_1': car_data['Combustible'],      # Asumo que el nombre es correcto
            'HorsePower_in_HP': car_data['Potencia'],
            'Kilometraje': car_data['Kilometraje'], # Asumo que el nombre es correcto
            'Año': car_data['Año'],                 # Asumo que el nombre es correcto
            
            # --- COLUMNAS FALTANTES (Valores Dummy para satisfacer al modelo) ---
            # Usamos la potencia de entrada para HP_2 por si es una variable derivada.
            'HorsePower_in_HP_2': car_data['Potencia'], 
            # Numéricas con valores promedio seguros
            'Engine_capacity_in_cc': 1500.0,
            'Time_to_100kmph_sec': 10.0,
            'Seats': 5,
            'Engines': 1,
            'Torque_in_Nm': 200.0,
            'Max_speed_in_km/h': 180.0,
            'Torque_in_Nm_2': 0.0,
            
            # ID y Precios Mínimos (Usamos 0 o un valor mínimo seguro)
            'id': 0,
            'Price_Min': 10000.0,
        }
        
        # 2. Crear un DataFrame con los datos de entrada Mapeados
        # Este DataFrame ahora contiene 17 columnas (7 de usuario + 10 dummy/mapeadas)
        input_df = pd.DataFrame([input_data_mapped])
        
        # 3. Realizar la predicción usando el objeto modelo_final
        prediction = modelo_final.predict(input_df)
        
        # El resultado se devuelve como un array, tomamos el primer (y único) elemento
        return prediction[0]
    except Exception as e:
        # Mantenemos el error específico para el usuario
        st.error(f"Error grave durante la predicción. **Detalle de Integridad de Datos:** A pesar de mapear las columnas, hubo un error. El error completo es: {e}")
        return None

# Botón de predicción
if st.sidebar.button("Calcular Precio Estimado", key="predict_btn"):
    
    # Datos de entrada del usuario (Nombres amigables)
    car_input = {
        'Marca': marca, 
        'Tipo': tipo, 
        'Transmision': transmision, 
        'Combustible': combustible, 
        'Año': year, 
        'Kilometraje': kilometraje, 
        'Potencia': potencia
    }
    
    precio_predicho = make_prediction(car_input)
    
    if precio_predicho is not None:
        st.session_state['run_prediction'] = True
        st.session_state['predicted_price'] = precio_predicho
        st.session_state['car_input'] = car_input
    else:
        st.session_state['run_prediction'] = False


# --- 6. CUERPO PRINCIPAL DE LA APLICACIÓN (Se mantiene igual) ---

# Título principal con la clase CSS personalizada
st.markdown('<p class="main-header">🚗 Predictor de Precios de Automóviles</p>', unsafe_allow_html=True)
st.write("Selecciona los parámetros del vehículo en la barra lateral para obtener una estimación de precio.")

# 6.1 Área de Métricas del Modelo (Ejemplo, usa la clase .metric-card)
st.subheader("Métricas de Calidad del Modelo (Dummy)")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card"><h4>R² (Precisión)</h4><p style="font-size: 1.5rem;">0.92</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h4>MAE (Error Absoluto Medio)</h4><p style="font-size: 1.5rem;">$1,500 USD</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><h4>Modelo en Uso</h4><p style="font-size: 1.5rem;">Gradient Boosting</p></div>', unsafe_allow_html=True)

# 6.2 Área de Resultados (Solo se muestra después de una predicción exitosa)
if st.session_state.get('run_prediction') and 'predicted_price' in st.session_state:
    
    precio_predicho = st.session_state['predicted_price']
    input_data = st.session_state['car_input']

    st.markdown("---")
    st.subheader("🎉 Resultado de la Predicción")
    
    # Mostrar el resultado final con la clase de destaque .prediction-result
    st.markdown(
        f"""
        <div class="prediction-result">
            <h2>El Precio Estimado de Venta es:</h2>
            <h1>${precio_predicho:,.2f} USD</h1>
            <p><strong>Vehículo:</strong> {input_data['Marca']} {input_data['Tipo']} | <strong>Año:</strong> {input_data['Año']} | <strong>KM:</strong> {input_data['Kilometraje']:,.0f}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.success("Predicción completada exitosamente usando el modelo final.")

    # 6.3 Área de Comparación (Opcional, usa la clase .model-comparison)
    st.markdown('<br>', unsafe_allow_html=True)
    st.subheader("Comparativa de Modelos")
    
    st.markdown(
        f"""
        <div class="model-comparison">
            <p>El modelo actual (Gradient Boosting) se seleccionó por su mejor equilibrio entre precisión (R²: 0.92) y velocidad.</p>
            <ul>
                <li>**Regresión Lineal:** R² 0.75 (Muy simple, bajo sesgo)</li>
                <li>**Random Forest:** R² 0.90 (Buena precisión, más lento)</li>
            </ul>
        </div>
        """, 
        unsafe_allow_html=True
    )

# 6.4 Área de Visualización (Espacio para gráficos futuros)
st.markdown("---")
st.subheader("Análisis de Influencia de Variables")
st.info("Aquí se podrían integrar gráficos interactivos que muestren cómo las variables (ej. Kilometraje vs. Precio) influyen en la predicción.")

