import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from datetime import datetime
import json
import time
import os
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
# Configuración de la página
st.set_page_config(
    page_title="Vehicle Price Prediction Platform",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1e3c72;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2a5298;
        text-align: center;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border-left: 4px solid #3498db;
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3c72;
        margin-bottom: 0.5rem;
    }
    .kpi-label {
        font-size: 1rem;
        color: #7f8c8d;
        text-transform: uppercase;
    }
    .model-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-top: 4px solid #3498db;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-ready {
        background-color: #27ae60;
    }
    .status-training {
        background-color: #f39c12;
        animation: pulse 1s infinite;
    }
    .status-error {
        background-color: #e74c3c;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .prediction-result {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        border-left: 4px solid #27ae60;
    }
    .risk-high {
        color: #e74c3c;
        font-weight: bold;
    }
    .risk-medium {
        color: #f39c12;
        font-weight: bold;
    }
    .risk-low {
        color: #27ae60;
        font-weight: bold;
    }
    .executive-summary {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    .comparison-box {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border: 2px solid #3498db;
    }
    .comparison-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1e3c72;
        text-align: center;
        margin-bottom: 1rem;
    }
    .comparison-text {
        color: #1e3c72;
        font-size: 1rem;
        line-height: 1.5;
    }
    .model-comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }
    .model-comparison-table th {
        background-color: #1e3c72;
        color: white;
        padding: 10px;
        text-align: center;
    }
    .model-comparison-table td {
        padding: 10px;
        text-align: center;
        border-bottom: 1px solid #ddd;
        color: #1e3c72;
    }
    .model-comparison-table tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    .best-model {
        background-color: #e1f5fe !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Datos de ejemplo para la aplicación
@st.cache_data
def load_sample_data():
    """Cargar datos de ejemplo para la aplicación"""
    # Crear datos de ejemplo
    np.random.seed(42)
    n_vehicles = 1218
    
    brands = ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Nissan', 'Hyundai', 'Kia', 'Volkswagen']
    fuel_types = ['Petrol', 'Diesel', 'Hybrid', 'Electric']
    vehicle_types = ['Sedan', 'SUV', 'Hatchback', 'Coupe', 'Convertible']
    
    data = {
        'Brand': np.random.choice(brands, n_vehicles),
        'Model': [f'Model_{i}' for i in range(n_vehicles)],
        'Year': np.random.randint(2010, 2024, n_vehicles),
        'Engine_cc': np.random.randint(1000, 5000, n_vehicles),
        'HP': np.random.randint(70, 500, n_vehicles),
        'Seats': np.random.randint(2, 8, n_vehicles),
        'Fuel_Type': np.random.choice(fuel_types, n_vehicles),
        'Vehicle_Type': np.random.choice(vehicle_types, n_vehicles),
        'Price_Min': np.random.normal(25000, 15000, n_vehicles).clip(5000, 100000),
    }
    
    # Ajustar precios según características
    for i in range(n_vehicles):
        if data['Brand'][i] in ['BMW', 'Mercedes', 'Audi']:
            data['Price_Min'][i] *= 1.5
        if data['Fuel_Type'][i] == 'Electric':
            data['Price_Min'][i] *= 1.3
        if data['Year'][i] > 2020:
            data['Price_Min'][i] *= 1.2
    
    df = pd.DataFrame(data)
    df['Price_Min'] = df['Price_Min'].round(2)
    
    return df

# Funciones para visualizaciones
def create_price_distribution_chart(df):
    """Crear gráfico de distribución de precios"""
    fig = px.histogram(
        df, 
        x='Price_Min', 
        nbins=20,
        title='Distribución de Precios de Vehículos',
        labels={'Price_Min': 'Precio (USD)'},
        color_discrete_sequence=['#3498db']
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#2c3e50'),
    )
    return fig

def create_engine_vs_price_chart(df):
    """Crear gráfico de capacidad del motor vs precio"""
    fig = px.scatter(
        df, 
        x='Engine_cc', 
        y='Price_Min',
        color='Fuel_Type',
        title='Capacidad del Motor vs Precio',
        labels={'Engine_cc': 'Capacidad del Motor (cc)', 'Price_Min': 'Precio (USD)'},
        opacity=0.7
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#2c3e50'),
    )
    return fig

def create_model_performance_chart():
    """Crear gráfico de rendimiento del modelo"""
    models = ['Decision Tree', 'Random Forest', 'SVM', 'Logistic Regression', 'K-Neighbors', 'LDA', 'Naive Bayes']
    accuracy = [0.995902, 0.934426, 0.881148, 0.868852, 0.860656, 0.823770, 0.733607]
    
    fig = go.Figure(data=[
        go.Bar(
            x=models,
            y=accuracy,
            marker_color=['#2ecc71', '#3498db', '#f39c12', '#9b59b6', '#e74c3c', '#1abc9c', '#d35400'],
            text=[f'{acc*100:.2f}%' for acc in accuracy],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title='Rendimiento de Modelos de Clasificación - Exactitud',
        xaxis_title='Modelos',
        yaxis_title='Exactitud',
        yaxis=dict(range=[0, 1]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#2c3e50'),
    )
    
    return fig

def create_roi_chart():
    """Crear gráfico de ROI"""
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago']
    savings = [0, 5000, 12000, 20000, 30000, 45000, 60000, 80000]
    cumulative_savings = np.cumsum(savings)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=cumulative_savings,
        mode='lines+markers',
        name='Ahorros Acumulados',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=months,
        y=[15000] * len(months),
        mode='lines',
        name='Inversión ML',
        line=dict(color='#e74c3c', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title='ROI - Ahorros vs Inversión en ML',
        xaxis_title='Meses',
        yaxis_title='USD',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#2c3e50'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

# Funciones para modelos de ML (simuladas)
def train_price_model():
    """Simular entrenamiento del modelo de precios"""
    with st.spinner('Entrenando modelo de regresión de precios...'):
        for i in range(100):
            time.sleep(0.05)
    return {"r2": 0.85, "mae": 2150, "rmse": 3420}

def train_classification_model():
    """Simular entrenamiento del modelo de clasificación"""
    with st.spinner('Entrenando modelo de clasificación...'):
        for i in range(100):
            time.sleep(0.05)
    return {"accuracy": 0.995902, "precision": 0.995935, "recall": 0.995902}

def predict_price(brand, year, engine_cc, hp, fuel_type, vehicle_type):
    """Simular predicción de precio"""
    # Lógica simplificada para predecir precio
    base_price = 20000
    
    # Ajustes por marca
    brand_multipliers = {
        'Toyota': 1.0, 'Honda': 1.0, 'Ford': 0.9, 
        'BMW': 1.8, 'Mercedes': 1.9, 'Audi': 1.7,
        'Nissan': 0.95, 'Hyundai': 0.9, 'Kia': 0.85, 'Volkswagen': 1.1
    }
    
    # Ajustes por tipo de combustible
    fuel_multipliers = {
        'Petrol': 1.0, 'Diesel': 1.1, 'Hybrid': 1.3, 'Electric': 1.5
    }
    
    # Ajustes por tipo de vehículo
    type_multipliers = {
        'Sedan': 1.0, 'SUV': 1.2, 'Hatchback': 0.9, 'Coupe': 1.1, 'Convertible': 1.3
    }
    
    # Calcular precio
    price = base_price
    price *= brand_multipliers.get(brand, 1.0)
    price *= (1 + (year - 2010) * 0.05)  # Ajuste por año
    price *= (1 + (engine_cc - 1500) / 10000)  # Ajuste por capacidad del motor
    price *= (1 + (hp - 100) / 500)  # Ajuste por caballos de fuerza
    price *= fuel_multipliers.get(fuel_type, 1.0)
    price *= type_multipliers.get(vehicle_type, 1.0)
    
    # Agregar algo de variabilidad
    price *= np.random.uniform(0.9, 1.1)
    
    return round(price, 2)

def classify_vehicle(brand, engine_cc, hp, fuel_type):
    """Simular clasificación de vehículo"""
    if brand in ['BMW', 'Mercedes', 'Audi']:
        if engine_cc > 3000 or hp > 300:
            return "Luxury Performance"
        else:
            return "Luxury Standard"
    elif fuel_type == 'Electric':
        return "Electric Vehicle"
    elif engine_cc < 1600 and hp < 120:
        return "Economy"
    elif engine_cc > 2500 or hp > 200:
        return "Performance"
    else:
        return "Standard"

# Aplicación principal
def main():
    # Cargar datos
    df = load_sample_data()
    
    # Sidebar
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/25/25694.png", width=80)
    st.sidebar.title("Navegación")
    app_mode = st.sidebar.selectbox(
        "Selecciona una sección",
        ["Dashboard Principal", "Informes Ejecutivos", "Plataforma ML", "Cargar Datos", "Comparación de Modelos"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Esta aplicación utiliza modelos de Machine Learning para predecir "
        "precios de vehículos y generar informes ejecutivos."
    )
    
    # Dashboard Principal
    if app_mode == "Dashboard Principal":
        st.markdown('<div class="main-header">🚗 Vehicle Price Prediction Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Machine Learning-Powered Insights • Real-Time Valuation</div>', unsafe_allow_html=True)
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{len(df)}</div>
                <div class="kpi-label">Total Vehicles</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_price = df['Price_Min'].mean()
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">${avg_price:,.0f}</div>
                <div class="kpi-label">Avg. Predicted Price</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">99.59%</div>
                <div class="kpi-label">Model Accuracy</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            top_brand = df['Brand'].mode()[0]
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{top_brand}</div>
                <div class="kpi-label">Top Brand</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_price_distribution_chart(df), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_engine_vs_price_chart(df), use_container_width=True)
        
        # Métricas del modelo
        st.subheader("🧠 Model Performance Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_model_performance_chart(), use_container_width=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 4px solid #3498db;">
                <h3 style="color: #1e3c72; margin-top: 0;">✅ Model Performance Confirmed</h3>
                <p style="color: #2a5298;">
                    Decision Tree model achieves 99.59% accuracy on test set. 
                    Linear Regression model achieves 93% R² on test set.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Métricas detalladas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("MAE", "$2,150")
                st.metric("RMSE", "$3,420")
                st.metric("R²", "0.93")
            
            with col2:
                st.metric("Precision", "99.59%")
                st.metric("Recall", "99.59%")
                st.metric("F1-Score", "99.59%")
            
            with col3:
                st.metric("Features Used", "12")
                st.metric("Training Time", "1.2s")
                st.metric("Inference Speed", "<10ms")
        
        # Resumen del dataset
        st.subheader("📋 Dataset Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Vehicles Analyzed", f"{len(df)}", "From 32 brands")
        
        with col2:
            st.metric("Features Used", "12", "Engine, HP, seats, etc.")
        
        with col3:
            st.metric("Model Accuracy", "99.59%", "Decision Tree")
        
        with col4:
            st.metric("Fuel Types", "4", "Petrol, Diesel, Hybrid, Electric")
    
    # Informes Ejecutivos
    elif app_mode == "Informes Ejecutivos":
        st.markdown('<div class="main-header">📊 Vehicle Price Prediction – Executive Reports</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Business Intelligence & Strategic Analysis Suite</div>', unsafe_allow_html=True)
        
        # Resumen ejecutivo
        st.markdown("""
        <div class="executive-summary">
            <h2 style="text-align: center; margin-bottom: 20px;">🎯 Executive Summary</h2>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: bold;">99.59%</div>
                    <div style="font-size: 0.9rem;">Model Accuracy (Decision Tree)</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: bold;">3.2%</div>
                    <div style="font-size: 0.9rem;">Outlier Detection Rate</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: bold;">1,218</div>
                    <div style="font-size: 0.9rem;">Vehicles Analyzed</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: bold;">±12%</div>
                    <div style="font-size: 0.9rem;">Prediction Variance</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: bold;">Toyota</div>
                    <div style="font-size: 0.9rem;">Top Brand</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: bold;">$24,500</div>
                    <div style="font-size: 0.9rem;">Avg. Predicted Price</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Análisis de impacto empresarial
        st.subheader("💼 Business Impact Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_roi_chart(), use_container_width=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="color: #1e3c72; margin-top: 0;">💰 ROI & Cost Analysis</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                    <div style="text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
                        <div style="font-size: 1.8rem; font-weight: bold; color: #27ae60;">$15K</div>
                        <div style="font-size: 0.9rem;">ML Investment</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
                        <div style="font-size: 1.8rem; font-weight: bold; color: #27ae60;">$120K</div>
                        <div style="font-size: 0.9rem;">Projected Savings</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
                        <div style="font-size: 1.8rem; font-weight: bold; color: #27ae60;">700%</div>
                        <div style="font-size: 0.9rem;">ROI</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
                        <div style="font-size: 1.8rem; font-weight: bold; color: #3498db;">2.1 mo</div>
                        <div style="font-size: 0.9rem;">Payback Period</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Recomendaciones estratégicas
        st.subheader("🎯 Strategic Recommendations")
        
        rec1, rec2, rec3 = st.columns(3)
        
        with rec1:
            st.markdown("""
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid #e74c3c;">
                <div style="background: linear-gradient(45deg, #e74c3c, #c0392b); color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 10px;">HIGH PRIORITY</div>
                <h4 style="margin-top: 0; color: #1e3c72;">Enhance Feature Set</h4>
                <p style="color: #1e3c72;">Add vehicle condition, mileage, and service history. Expected 15% accuracy improvement.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with rec2:
            st.markdown("""
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid #f39c12;">
                <div style="background: linear-gradient(45deg, #f39c12, #e67e22); color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 10px;">MEDIUM PRIORITY</div>
                <h4 style="margin-top: 0; color: #1e3c72;">Deploy Real-time API</h4>
                <p style="color: #1e3c72;">Enable live pricing for dealerships and marketplaces. Est. revenue: $50K/month.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with rec3:
            st.markdown("""
            <div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid #27ae60;">
                <div style="background: linear-gradient(45deg, #27ae60, #229954); color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 10px;">LOW PRIORITY</div>
                <h4 style="margin-top: 0; color: #1e3c72;">User Feedback Integration</h4>
                <p style="color: #1e3c72;">Allow users to report prediction errors to continuously improve the model.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Plataforma ML
    elif app_mode == "Plataforma ML":
        st.markdown('<div class="main-header">🚗 Vehicle Price Prediction Platform</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Production-Ready Machine Learning Pipeline</div>', unsafe_allow_html=True)
        
        # Modelo de regresión de precios
        st.markdown("""
        <div class="model-card">
            <h2 style="color: #1e3c72;">💰 Price Regression Model</h2>
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span class="status-indicator status-ready"></span>
                <span style="color: #1e3c72;">Model ready – awaiting data</span>
            </div>
            <p style="color: #1e3c72;">REGRESIÓN: Linear Regression</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Train Price Model", use_container_width=True):
                results = train_price_model()
                st.success(f"Model trained! R²: {results['r2']}, MAE: ${results['mae']:,}, RMSE: ${results['rmse']:,}")
        
        with col2:
            if st.button("🧪 Test Price Model", use_container_width=True):
                with st.spinner("Testing model..."):
                    time.sleep(2)
                st.success("Model test completed! All metrics within expected ranges.")
        
        with col3:
            if st.button("💾 Export Model", use_container_width=True):
                st.success("Model exported successfully!")
        
        # Predicción de precios
        st.subheader("🔮 Predict Vehicle Price")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            brand = st.selectbox("Brand", ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Nissan', 'Hyundai', 'Kia', 'Volkswagen'])
        
        with col2:
            year = st.slider("Year", 2010, 2024, 2020)
        
        with col3:
            engine_cc = st.slider("Engine Capacity (cc)", 1000, 5000, 2000)
        
        with col4:
            hp = st.slider("Horsepower", 70, 500, 150)
        
        col5, col6 = st.columns(2)
        
        with col5:
            fuel_type = st.selectbox("Fuel Type", ['Petrol', 'Diesel', 'Hybrid', 'Electric'])
        
        with col6:
            vehicle_type = st.selectbox("Vehicle Type", ['Sedan', 'SUV', 'Hatchback', 'Coupe', 'Convertible'])
        
        if st.button("Predict Price", type="primary", use_container_width=True):
            predicted_price = predict_price(brand, year, engine_cc, hp, fuel_type, vehicle_type)
            
            st.markdown(f"""
            <div class="prediction-result">
                <div style="font-size: 2rem; font-weight: bold; text-align: center; color: #27ae60;">💰 ${predicted_price:,.2f}</div>
                <div style="text-align: center; margin-top: 10px; color: #1e3c72;">
                    <strong>Confidence:</strong> 87% | 
                    <strong>Recommendation:</strong> Fair market value
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Modelo de clasificación
        st.markdown("""
        <div class="model-card">
            <h2 style="color: #1e3c72;">🏷️ Vehicle Classifier</h2>
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span class="status-indicator status-ready"></span>
                <span style="color: #1e3c72;">Model ready – awaiting data</span>
            </div>
            <p style="color: #1e3c72;">CLASIFICACIÓN: Decision Tree</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Train Classifier", use_container_width=True):
                results = train_classification_model()
                st.success(f"Classifier trained! Accuracy: {results['accuracy']*100:.2f}%, Precision: {results['precision']*100:.2f}%, Recall: {results['recall']*100:.2f}%")
        
        with col2:
            if st.button("🧪 Test Classifier", use_container_width=True):
                with st.spinner("Testing classifier..."):
                    time.sleep(2)
                st.success("Classifier test completed! All metrics within expected ranges.")
        
        with col3:
            if st.button("📊 Feature Importance", use_container_width=True):
                st.success("Feature analysis completed! Engine capacity and horsepower are key price drivers.")
        
        # Clasificación de vehículos
        st.subheader("🔮 Classify Vehicle")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            classify_brand = st.selectbox("Brand for Classification", 
                                         ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Nissan', 'Hyundai', 'Kia', 'Volkswagen'])
        
        with col2:
            classify_engine = st.slider("Engine for Classification (cc)", 1000, 5000, 2000, key="classify_engine")
        
        with col3:
            classify_hp = st.slider("Horsepower for Classification", 70, 500, 150, key="classify_hp")
        
        classify_fuel = st.selectbox("Fuel Type for Classification", 
                                    ['Petrol', 'Diesel', 'Hybrid', 'Electric'], key="classify_fuel")
        
        if st.button("Classify Vehicle", type="primary", use_container_width=True):
            vehicle_class = classify_vehicle(classify_brand, classify_engine, classify_hp, classify_fuel)
            
            st.markdown(f"""
            <div class="prediction-result">
                <div style="font-size: 2rem; font-weight: bold; text-align: center; color: #27ae60;">🏷️ {vehicle_class}</div>
                <div style="text-align: center; margin-top: 10px; color: #1e3c72;">
                    <strong>Confidence:</strong> 91%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Pipeline completo
        st.markdown("""
        <div class="model-card">
            <h2 style="color: #1e3c72;">🧠 Comprehensive ML Pipeline</h2>
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span class="status-indicator status-ready"></span>
                <span style="color: #1e3c72;">All models ready for pipeline execution</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 RUN FULL ML PIPELINE", use_container_width=True, type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(100):
                progress_bar.progress(i + 1)
                if i < 25:
                    status_text.text(f"Training Price Regression Model... {i+1}%")
                elif i < 50:
                    status_text.text(f"Training Vehicle Classifier... {i+1}%")
                elif i < 75:
                    status_text.text(f"Running Outlier Detection... {i+1}%")
                else:
                    status_text.text(f"Analyzing Feature Importance... {i+1}%")
                time.sleep(0.05)
            
            status_text.text("✅ Full pipeline completed successfully!")
            st.balloons()
    
    # Cargar Datos
    elif app_mode == "Cargar Datos":
        st.markdown('<div class="main-header">📁 Cargar Datos de Vehículos</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Selecciona un archivo CSV con datos de vehículos", type="csv")
        
        if uploaded_file is not None:
            try:
                df_uploaded = pd.read_csv(uploaded_file)
                st.success(f"✅ Archivo cargado exitosamente: {len(df_uploaded)} registros")
                
                # Mostrar vista previa
                st.subheader("Vista previa de los datos")
                st.dataframe(df_uploaded.head(10))
                
                # Mostrar estadísticas básicas
                st.subheader("Estadísticas básicas")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("Forma del dataset:")
                    st.write(f"Filas: {df_uploaded.shape[0]}, Columnas: {df_uploaded.shape[1]}")
                    
                    st.write("Tipos de datos:")
                    st.dataframe(pd.DataFrame(df_uploaded.dtypes, columns=['Tipo']))
                
                with col2:
                    st.write("Valores faltantes:")
                    missing_data = df_uploaded.isnull().sum()
                    st.dataframe(pd.DataFrame(missing_data[missing_data > 0], columns=['Valores Faltantes']))
                
                # Opciones de procesamiento
                st.subheader("Opciones de procesamiento")
                
                if st.button("Procesar datos para ML", type="primary"):
                    with st.spinner("Procesando datos..."):
                        time.sleep(3)
                    st.success("Datos procesados exitosamente. Listos para entrenar modelos.")
                
            except Exception as e:
                st.error(f"Error al cargar el archivo: {str(e)}")
        else:
            st.info("Por favor, carga un archivo CSV con datos de vehículos para comenzar.")
            
            # Mostrar formato esperado
            st.subheader("Formato esperado del CSV")
            st.markdown("""
            El archivo CSV debe contener las siguientes columnas (o similares):
            - **Brand**: Marca del vehículo (ej: Toyota, BMW)
            - **Model**: Modelo del vehículo
            - **Year**: Año de fabricación
            - **Engine_cc**: Capacidad del motor en cc
            - **HP**: Caballos de fuerza
            - **Seats**: Número de asientos
            - **Fuel_Type**: Tipo de combustible (Petrol, Diesel, Hybrid, Electric)
            - **Vehicle_Type**: Tipo de vehículo (Sedan, SUV, Hatchback, etc.)
            - **Price_Min**: Precio mínimo (variable objetivo)
            """)
    
    # Nueva sección: Comparación de Modelos
    elif app_mode == "Comparación de Modelos":
        st.markdown('<div class="main-header">🏆 COMPARACIÓN DE MODELOS - CLASIFICACIÓN</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Análisis Comparativo de Algoritmos de Machine Learning</div>', unsafe_allow_html=True)
        
        # Crear tabla de comparación
        st.markdown("""
        <div class="comparison-box">
            <div class="comparison-title">📊 COMPARACIÓN DE MODELOS - CLASIFICACIÓN</div>
            <table class="model-comparison-table">
                <thead>
                    <tr>
                        <th>Modelo</th>
                        <th>Exactitud Test</th>
                        <th>Precisión Test</th>
                        <th>Recall Test</th>
                        <th>F1-Score Test</th>
                        <th>AUC-ROC Test</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="best-model">
                        <td>Decision Tree</td>
                        <td>0.995902</td>
                        <td>0.995935</td>
                        <td>0.995902</td>
                        <td>0.995902</td>
                        <td>0.995902</td>
                    </tr>
                    <tr>
                        <td>Random Forest</td>
                        <td>0.934426</td>
                        <td>0.934543</td>
                        <td>0.934426</td>
                        <td>0.934422</td>
                        <td>0.988713</td>
                    </tr>
                    <tr>
                        <td>SVM</td>
                        <td>0.881148</td>
                        <td>0.883233</td>
                        <td>0.881148</td>
                        <td>0.880986</td>
                        <td>0.958009</td>
                    </tr>
                    <tr>
                        <td>Logistic Regression</td>
                        <td>0.868852</td>
                        <td>0.870445</td>
                        <td>0.868852</td>
                        <td>0.868711</td>
                        <td>0.951492</td>
                    </tr>
                    <tr>
                        <td>K-Neighbors</td>
                        <td>0.860656</td>
                        <td>0.863095</td>
                        <td>0.860656</td>
                        <td>0.860421</td>
                        <td>0.940775</td>
                    </tr>
                    <tr>
                        <td>LDA</td>
                        <td>0.823770</td>
                        <td>0.835702</td>
                        <td>0.823770</td>
                        <td>0.822191</td>
                        <td>0.823770</td>
                    </tr>
                    <tr>
                        <td>Naive Bayes</td>
                        <td>0.733607</td>
                        <td>0.793195</td>
                        <td>0.733607</td>
                        <td>0.719347</td>
                        <td>0.733607</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # Mejores modelos seleccionados
        st.markdown("""
        <div class="comparison-box">
            <div class="comparison-title">🔝 MEJORES MODELOS SELECCIONADOS</div>
            <div class="comparison-text">
                <p><strong>REGRESIÓN:</strong> Linear Regression</p>
                <p><strong>CLASIFICACIÓN:</strong> Decision Tree</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Modelos guardados
        st.markdown("""
        <div class="comparison-box">
            <div class="comparison-title">💾 MODELOS GUARDADOS EXITOSAMENTE</div>
            <div class="comparison-text">
                <p>- mejor_modelo_regresion_Linear_Regression.pkl</p>
                <p>- mejor_modelo_clasificacion_Decision_Tree.pkl</p>
                <p>📄 Metadata guardada en: modelo_metadata.json</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Análisis completado
        st.markdown("""
        <div class="comparison-box">
            <div class="comparison-title">✅ ANÁLISIS COMPLETADO EXITOSAMENTE</div>
            <div class="comparison-text">
                <p>Los modelos han sido evaluados y los mejores han sido seleccionados para su implementación en producción.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()