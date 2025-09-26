import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib  # Importamos joblib para cargar el modelo .pkl
import os

# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="Dashboard de Predicción de Precios de Vehículos",
    page_icon="🚗",
    layout="wide"
)

# --- Inicialización del estado de la sesión ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Título principal y descripción ---
st.title("🚗 Dashboard Interactivo de Vehículos de Segunda Mano")
st.markdown("Bienvenido al dashboard. Aquí puedes explorar los datos de vehículos y obtener una estimación de precios.")

# --- Cargar los datos ---
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("DatosLimpios.csv")
        return data
    except FileNotFoundError:
        st.error("No se encontró el archivo de datos. Asegúrate de que 'DatosLimpios.csv' esté en la misma carpeta.")
        return pd.DataFrame() # Devuelve un DataFrame vacío si el archivo no se encuentra

# Función para cargar el modelo de regresión
@st.cache_resource
def load_model(model_filename):
    try:
        model_path = os.path.join("agents", model_filename)
        model = joblib.load(model_path)
        return model
    except FileNotFoundError:
        st.error(f"No se encontró el modelo '{model_filename}' en la carpeta 'agents'.")
        return None
    
# Cargar todos los datos y modelos al inicio
df = load_data()
reg_model_1 = load_model("modelo_regresion_precios.pkl")
class_model_1 = load_model("modelo_clasificacion_precio_alto.pkl")
reg_model_rf = load_model("mejor_modelo_regresion_Random_forest.pkl")
class_model_rf = load_model("mejor_modelo_clasificacion_random_forest.pkl")

# --- Funciones para cada página ---
def home_page(df, models):
    """Página principal del dashboard con filtros y el formulario."""
    
    # --- Diseño de la barra lateral (Sidebar) ---
    with st.sidebar:
        st.header("Filtros y Controles")
        st.markdown("Usa estos controles para interactuar con los datos.")
        
        selected_brand = st.selectbox(
            "Selecciona una Marca",
            sorted(df['Brands'].unique()),
            key="brand_select"
        )
        
        if st.button("Resetear Filtros"):
            st.session_state.brand_select = None
            st.rerun()
            
        if st.button("Refrescar datos"):
            st.cache_data.clear()
            st.rerun()
            st.success("¡Datos refrescados exitosamente!")

        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')
        
        filtered_df = df[df['Brands'] == selected_brand] if selected_brand else df
        csv = convert_df_to_csv(filtered_df)
        
        st.download_button(
            label="Descargar Datos Filtrados",
            data=csv,
            file_name='datos_filtrados.csv',
            mime='text/csv',
        )
        
    st.subheader("Exploración de Datos")
    filtered_df = df[df['Brands'] == selected_brand] if selected_brand else df
    st.dataframe(filtered_df)

    # --- Sección de Exploración de Datos ---
    st.subheader("Formulario de Simulación")
    st.markdown("Introduce los datos del vehículo para realizar una predicción.")

    # --- Formulario de entrada de datos ---
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            brand = st.selectbox("Marca del vehículo", sorted(df['Brands'].unique()))
            models_for_brand = sorted(df[df['Brands'] == brand]['Model'].unique())
            model_selection = st.selectbox("Modelo del vehículo", models_for_brand)
            year = st.number_input("Año de fabricación", 1950, 2025, 2015)
            engine_capacity = st.number_input("Cilindrada (cc)", 0, value=int(df['Engine_capacity_in_cc'].mean()))

        with col2:
            horsepower = st.number_input("Caballos de fuerza (HP)", 0, value=int(df['HorsePower_in_HP'].mean()))
            seats = st.number_input("Número de asientos", 1, 10, 5)
            fuel_options = sorted(df['Fuel_1'].unique())
            fuel_type = st.selectbox("Tipo de combustible", fuel_options)
            mileage = st.number_input("Kilometraje", 0, value=50000)

        # --- Lógica de envío del formulario ---
        submitted = st.form_submit_button("Realizar Predicciones")

    if submitted:
        # --- CONSTRUCCIÓN MANUAL DEL DATAFRAME DE ENTRADA ---
        
        # 1. Cargar la lista de columnas que el modelo espera
        try:
            model_columns = joblib.load(os.path.join("agents", "model_columns.pkl"))
        except FileNotFoundError:
            st.error("Falta el archivo 'model_columns.pkl' en la carpeta 'agents'. Este archivo es esencial para construir la entrada del modelo. Pídelo a quien entrenó el modelo.")
            st.stop()

        # 2. Crear un DataFrame con todas las columnas del modelo, lleno de ceros
        input_df = pd.DataFrame(columns=model_columns)
        input_df.loc[0] = 0

        # 3. Rellenar los valores que conocemos del formulario
        # Valores numéricos directos
        if 'Year' in input_df.columns: input_df['Year'] = year
        if 'Engine_capacity_in_cc' in input_df.columns: input_df['Engine_capacity_in_cc'] = engine_capacity
        if 'HorsePower_in_HP' in input_df.columns: input_df['HorsePower_in_HP'] = horsepower
        if 'Seats' in input_df.columns: input_df['Seats'] = seats
        if 'Mileage' in input_df.columns: input_df['Mileage'] = mileage

        # Valores categóricos (One-Hot Encoding manual)
        brand_col = f"Brands_{brand}"
        if brand_col in input_df.columns: input_df[brand_col] = 1
        
        model_col = f"Model_{model_selection}"
        if model_col in input_df.columns: input_df[model_col] = 1

        fuel_col = f"Fuel_1_{fuel_type}"
        if fuel_col in input_df.columns: input_df[fuel_col] = 1

        # 4. Rellenar las columnas transformadas y otras que no están en el formulario
        # Para estas, usaremos la media del dataset original como un valor de relleno plausible.
        for col in input_df.columns:
            # Si la columna sigue siendo 0 (no la hemos rellenado) y existe en el df original...
            if input_df[col].iloc[0] == 0 and col in df.columns:
                input_df[col] = df[col].mean()

        # 5. Asegurarse de que el orden de las columnas es el correcto
        input_df = input_df[model_columns]

        st.subheader("Resultados de la Simulación")
        res_col1, res_col2 = st.columns(2)

        # --- Columna de Regresión ---
        with res_col1:
            st.markdown("#### 1. Predicción de Precio (Regresión)")
            if models['reg_rf'] is not None:
                try:
                    prediction_rf = models['reg_rf'].predict(input_df)
                    st.metric(label="Precio Estimado (Random Forest)", value=f"${prediction_rf[0]:,.2f}")
                except Exception as e:
                    st.error(f"Error con modelo Random Forest: {e}")
                    st.write("Debug: Columnas del DataFrame de entrada:")
                    st.write(input_df.columns.tolist())
            else:
                st.warning("Modelo de regresión (RF) no cargado.")

        # --- Columna de Clasificación ---
        with res_col2:
            st.markdown("#### 2. Clasificación de Precio (Alto/Bajo)")
            if models['class_rf'] is not None:
                try:
                    classification_rf = models['class_rf'].predict(input_df)
                    if classification_rf[0] == 1:
                        st.success("Resultado (Random Forest): PRECIO ALTO")
                    else:
                        st.info("Resultado (Random Forest): PRECIO NO ALTO")
                except Exception as e:
                    st.error(f"Error con modelo Random Forest: {e}")
            else:
                st.warning("Modelo de clasificación (RF) no cargado.")
                
def history_page():
    """Página para el historial de búsquedas del usuario."""
    st.header("Historial de Búsquedas")
    st.info("Aquí se mostraría un registro de las búsquedas y predicciones realizadas.")
    st.markdown("Esta es una página de ejemplo. Para implementarla, necesitarías usar una base de datos para guardar el historial de cada usuario.")
    
def profile_page():
    """Página de perfil del usuario."""
    st.header("Mi Perfil")
    st.info("Aquí se mostraría la información del usuario.")
    st.markdown("**Nombre de Usuario:** `usuario_ejemplo`")
    st.markdown("**Correo Electrónico:** `correo@ejemplo.com`")

def login_page():
    """Página de inicio de sesión."""
    st.subheader("Iniciar Sesión")
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            # Lógica de autenticación simple (puedes reemplazarla con una base de datos)
            if username == "admin" and password == "password123":
                st.session_state.logged_in = True
                st.session_state.page = "home"
                st.success("¡Inicio de sesión exitoso!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

# --- Barra de navegación superior ---
def navigation_bar():
    st.markdown("""
        <style>
            .navbar {
                display: flex;
                justify-content: flex-start;
                padding: 10px;
                background-color: #f0f2f6;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .nav-button {
                margin: 0 10px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        cols = st.columns([1, 1, 1, 5])
        with cols[0]:
            if st.button("Inicio", key="nav_home"):
                st.session_state.page = "home"
        with cols[1]:
            if st.button("Historial", key="nav_history"):
                st.session_state.page = "history"
        with cols[2]:
            if st.button("Perfil", key="nav_profile"):
                st.session_state.page = "profile"

# --- Lógica principal de la aplicación ---
if not st.session_state.logged_in:
    login_page()
else:
    navigation_bar()
    with st.sidebar:
        if st.button("Cerrar Sesión"):
            st.session_state.logged_in = False
            st.session_state.page = "home"
            st.warning("Has cerrado sesión.")
            st.rerun()

    if st.session_state.page == "home":
        model_pack = {
            "reg_1": reg_model_1, "class_1": class_model_1,
            "reg_rf": reg_model_rf, "class_rf": class_model_rf
        }
        home_page(df, model_pack)
    elif st.session_state.page == "history":
        history_page()
    elif st.session_state.page == "profile":
        profile_page()
