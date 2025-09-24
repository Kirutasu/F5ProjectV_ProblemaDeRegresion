import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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
        st.error("No se encontró el archivo de datos. Asegúrate de que 'Datos Limpios - Datos Limpios (1).csv' esté en la misma carpeta.")
        return pd.DataFrame() # Devuelve un DataFrame vacío si el archivo no se encuentra

# Llama a la función para cargar los datos.
df = load_data()

# --- Funciones para cada página ---
def home_page(df):
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
    
    # --- Sección de Exploración de Datos ---
    st.subheader("Exploración de Datos")
    st.write(f"Mostrando datos para la marca: **{selected_brand if selected_brand else 'Todas las Marcas'}**")
    st.dataframe(filtered_df)

    # --- Sección del Formulario de Predicción de Precios ---
    st.subheader("Formulario de Predicción de Precios")
    st.markdown("Por favor, introduce los datos del vehículo para obtener una estimación de su precio.")

    col1, col2 = st.columns(2)
    with col1:
        brand = st.selectbox("Marca del vehículo", sorted(df['Brands'].unique()))
        models_for_brand = sorted(df[df['Brands'] == brand]['Model'].unique())
        model = st.selectbox("Modelo del vehículo", models_for_brand)
        engine = st.text_input("Motor (Ej. V8)", "V8")
        year = st.number_input("Año de fabricación", min_value=1950, max_value=2025, value=2015, step=1)
        engine_capacity = st.number_input("Cilindrada del motor (en cc)", min_value=0, value=int(df['Engine_capacity_in_cc'].mean()), step=100)

    with col2:
        horsepower = st.number_input("Caballos de fuerza (HP)", min_value=0, value=int(df['HorsePower_in_HP'].mean()), step=10)
        seats = st.number_input("Número de asientos", min_value=1, max_value=10, value=5, step=1)
        fuel_options = sorted(df['Fuel_1'].unique())
        fuel_type = st.selectbox("Tipo de combustible", fuel_options)
        mileage = st.number_input("Kilometraje", min_value=0, value=50000, step=1000)

    predict_button = st.button("Predecir Precio")

    if predict_button:
        st.subheader("Resultados de la Predicción")
        st.info("Nota: La lógica del modelo de predicción debe ser implementada aquí.")
        estimated_price = 460000
        price_min = 450000
        price_max = 470000
        st.metric(label="Precio Estimado", value=f"${estimated_price:,.2f}")
        st.markdown(f"**Rango de precios:** ${price_min:,.2f} - ${price_max:,.2f}")
        st.subheader("Visualizaciones de Apoyo")
        st.write("Gráfico de comparación del precio predicho vs. precio real (simulado).")
        
        comparison_df = pd.DataFrame({'Tipo de Precio': ['Predicho', 'Real (Ejemplo)'], 'Precio': [estimated_price, 455000]})
        fig_comparison = px.bar(comparison_df, x='Tipo de Precio', y='Precio', title='Comparación de Precios', color='Tipo de Precio', labels={'Tipo de Precio': 'Precio', 'Precio': 'Valor en USD'}, template="plotly_white")
        st.plotly_chart(fig_comparison)
        
        st.markdown("---")
        st.write("Importancia de las características en la predicción (simulado).")
        feature_importance_df = pd.DataFrame({'Característica': ['Kilometraje', 'Año', 'Caballos de Fuerza', 'Cilindrada', 'Tipo de Combustible'], 'Importancia': [0.45, 0.30, 0.15, 0.05, 0.05]}).sort_values('Importancia', ascending=True)
        fig_importance = px.bar(feature_importance_df, y='Característica', x='Importancia', orientation='h', title='Importancia de las Características', labels={'Importancia': 'Nivel de Importancia', 'Característica': 'Características'}, template="plotly_white")
        st.plotly_chart(fig_importance)

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
        home_page(df)
    elif st.session_state.page == "history":
        history_page()
    elif st.session_state.page == "profile":
        profile_page()
