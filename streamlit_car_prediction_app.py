import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import os
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVR, SVC
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="🚗 Predictor de Precios de Automóviles",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .prediction-result {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    
    .model-comparison {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .sidebar-info {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }

    .stSelectbox > div > div > select {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitCarPredictionApp:
    def __init__(self):
        self.df = None
        self.models_regression = {}
        self.models_classification = {}
        self.best_model_reg = None
        self.best_model_clf = None
        self.preprocessor = None
        self.feature_names = []
        
    def load_data(self, uploaded_file=None):
        """Carga los datos del dataset"""
        if uploaded_file is not None:
            try:
                self.df = pd.read_csv(uploaded_file)
                return True
            except Exception as e:
                st.error(f"Error al cargar el archivo: {e}")
                return False
        return False
    
    def prepare_data(self):
        """Prepara los datos para el modelado"""
        if self.df is None:
            return False
            
        # Crear variable objetivo binaria
        if 'Precio_Alto' not in self.df.columns:
            precio_mediano = self.df['Price_Max_log'].median()
            self.df['Precio_Alto'] = (self.df['Price_Max_log'] > precio_mediano).astype(int)
        
        # Separar características y objetivos
        features = self.df.drop(['Price_Max_log', 'Precio_Alto'], axis=1, errors='ignore')
        target_reg = self.df['Price_Max_log']
        target_clf = self.df['Precio_Alto']
        
        # Identificar columnas
        numeric_columns = features.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_columns = features.select_dtypes(include=['object', 'category']).columns.tolist()
        
        self.feature_names = features.columns.tolist()
        
        return features, target_reg, target_clf, numeric_columns, categorical_columns
    
    def create_preprocessor(self, numeric_columns, categorical_columns):
        """Crea el pipeline de preprocesamiento"""
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ]) if categorical_columns else 'passthrough'
        
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_columns),
                ('cat', categorical_transformer, categorical_columns)
            ]
        )
        
        return self.preprocessor
    
    def train_models(self, X, y_reg, y_clf):
        """Entrena múltiples modelos"""
        # Dividir datos
        X_train, X_test, y_train_reg, y_test_reg = train_test_split(
            X, y_reg, test_size=0.2, random_state=42, stratify=y_clf
        )
        _, _, y_train_clf, y_test_clf = train_test_split(
            X, y_clf, test_size=0.2, random_state=42, stratify=y_clf
        )
        
        # Modelos de regresión
        regression_models = {
            'Random Forest': Pipeline([
                ('preprocessor', self.preprocessor),
                ('model', RandomForestRegressor(n_estimators=100, random_state=42))
            ]),
            'Linear Regression': Pipeline([
                ('preprocessor', self.preprocessor),
                ('model', LinearRegression())
            ]),
            'SVM': Pipeline([
                ('preprocessor', self.preprocessor),
                ('model', SVR(kernel='rbf'))
            ])
        }
        
        # Modelos de clasificación
        classification_models = {
            'Random Forest': Pipeline([
                ('preprocessor', self.preprocessor),
                ('model', RandomForestClassifier(n_estimators=100, random_state=42))
            ]),
            'Logistic Regression': Pipeline([
                ('preprocessor', self.preprocessor),
                ('model', LogisticRegression(random_state=42))
            ]),
            'SVM': Pipeline([
                ('preprocessor', self.preprocessor),
                ('model', SVC(kernel='rbf', probability=True, random_state=42))
            ])
        }
        
        # Entrenar y evaluar modelos
        regression_results = {}
        classification_results = {}
        
        progress_bar = st.progress(0)
        total_models = len(regression_models) + len(classification_models)
        current_model = 0
        
        # Entrenar modelos de regresión
        for name, model in regression_models.items():
            model.fit(X_train, y_train_reg)
            y_pred = model.predict(X_test)
            
            rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred))
            r2 = r2_score(y_test_reg, y_pred)
            
            regression_results[name] = {
                'model': model,
                'rmse': rmse,
                'r2': r2
            }
            
            current_model += 1
            progress_bar.progress(current_model / total_models)
        
        # Entrenar modelos de clasificación
        for name, model in classification_models.items():
            model.fit(X_train, y_train_clf)
            y_pred = model.predict(X_test)
            
            accuracy = accuracy_score(y_test_clf, y_pred)
            
            classification_results[name] = {
                'model': model,
                'accuracy': accuracy
            }
            
            current_model += 1
            progress_bar.progress(current_model / total_models)
        
        # Seleccionar mejores modelos
        best_reg_name = max(regression_results.keys(), key=lambda x: regression_results[x]['r2'])
        best_clf_name = max(classification_results.keys(), key=lambda x: classification_results[x]['accuracy'])
        
        self.best_model_reg = regression_results[best_reg_name]['model']
        self.best_model_clf = classification_results[best_clf_name]['model']
        self.models_regression = regression_results
        self.models_classification = classification_results
        
        progress_bar.empty()
        
        return best_reg_name, best_clf_name, regression_results, classification_results

def main():
    app = StreamlitCarPredictionApp()
    
    # Header principal
    st.markdown('<h1 class="main-header">🚗 Predictor de Precios de Automóviles</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Utiliza Machine Learning para predecir precios de automóviles con alta precisión</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown('<div class="sidebar-info"><h3>📊 Panel de Control</h3><p>Configura tu análisis desde aquí</p></div>', unsafe_allow_html=True)
    
    # Subir archivo
    uploaded_file = st.sidebar.file_uploader("📁 Subir Dataset CSV", type=['csv'])
    
    if uploaded_file is not None:
        # Cargar datos
        if app.load_data(uploaded_file):
            st.sidebar.success("✅ Datos cargados exitosamente")
            
            # Mostrar información del dataset
            with st.expander("📋 Información del Dataset", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>📊 Filas</h3>
                        <h2>{app.df.shape[0]:,}</h2>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>📈 Columnas</h3>
                        <h2>{app.df.shape[1]}</h2>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>💰 Precio Promedio</h3>
                        <h2>${np.exp(app.df["Price_Max_log"].mean()):,.0f}</h2>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>🔍 Valores Únicos</h3>
                        <h2>{app.df.nunique().sum()}</h2>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # Preparar datos
            data_prep = app.prepare_data()
            if data_prep:
                X, y_reg, y_clf, numeric_cols, categorical_cols = data_prep
                preprocessor = app.create_preprocessor(numeric_cols, categorical_cols)
                
                # Tabs principales
                tab1, tab2, tab3, tab4 = st.tabs(["🎯 Predicción", "📊 Análisis de Modelos", "📈 Visualizaciones", "🔍 Exploración de Datos"])
                
                with tab1:
                    st.markdown("### 🎯 Realizar Predicción")
                    
                    # Entrenar modelos si no están entrenados
                    if app.best_model_reg is None:
                        with st.spinner("🔄 Entrenando modelos... Por favor espera."):
                            best_reg_name, best_clf_name, reg_results, clf_results = app.train_models(X, y_reg, y_clf)
                        
                        st.success(f"✅ Modelos entrenados exitosamente!")
                        st.info(f"🏆 Mejor modelo de regresión: **{best_reg_name}**")
                        st.info(f"🏆 Mejor modelo de clasificación: **{best_clf_name}**")
                    
                    # Formulario de predicción
                    st.markdown("#### 📝 Ingresa las características del automóvil:")
                    
                    col1, col2 = st.columns(2)
                    
                    prediction_data = {}
                    
                    # Variables numéricas
                    with col1:
                        st.markdown("##### 🔢 Variables Numéricas")
                        for col in numeric_cols[:len(numeric_cols)//2]:
                            if col in app.df.columns:
                                col_stats = app.df[col].describe()
                                prediction_data[col] = st.number_input(
                                    f"{col.replace('_', ' ').title()}",
                                    min_value=float(col_stats['min']),
                                    max_value=float(col_stats['max']),
                                    value=float(col_stats['mean']),
                                    help=f"Rango: {col_stats['min']:.2f} - {col_stats['max']:.2f}"
                                )
                    
                    with col2:
                        st.markdown("##### 🔢 Variables Numéricas (cont.)")
                        for col in numeric_cols[len(numeric_cols)//2:]:
                            if col in app.df.columns:
                                col_stats = app.df[col].describe()
                                prediction_data[col] = st.number_input(
                                    f"{col.replace('_', ' ').title()}",
                                    min_value=float(col_stats['min']),
                                    max_value=float(col_stats['max']),
                                    value=float(col_stats['mean']),
                                    help=f"Rango: {col_stats['min']:.2f} - {col_stats['max']:.2f}"
                                )
                    
                    # Variables categóricas
                    if categorical_cols:
                        st.markdown("##### 📋 Variables Categóricas")
                        cols_cat_display = st.columns(min(len(categorical_cols), 3))
                        for i, col in enumerate(categorical_cols):
                            if col in app.df.columns:
                                with cols_cat_display[i % 3]:
                                    unique_values = app.df[col].unique()
                                    prediction_data[col] = st.selectbox(
                                        f"{col.replace('_', ' ').title()}",
                                        options=unique_values,
                                        index=0
                                    )
                    
                    # Botón de predicción
                    if st.button("🚀 Realizar Predicción", type="primary", use_container_width=True):
                        # Crear DataFrame con los datos de entrada
                        new_data = pd.DataFrame([prediction_data])
                        
                        # Realizar predicciones
                        precio_pred_log = app.best_model_reg.predict(new_data)[0]
                        categoria_pred = app.best_model_clf.predict(new_data)[0]
                        
                        # Convertir precio a escala original
                        precio_pred = np.exp(precio_pred_log)
                        
                        # Obtener probabilidades
                        if hasattr(app.best_model_clf, 'predict_proba'):
                            proba = app.best_model_clf.predict_proba(new_data)[0]
                            proba_alto = proba[1] if len(proba) > 1 else 0
                        else:
                            proba_alto = categoria_pred
                        
                        # Mostrar resultados
                        st.markdown(f'''
                        <div class="prediction-result">
                            <h2>🎯 Resultados de la Predicción</h2>
                            <h1>${precio_pred:,.2f}</h1>
                            <h3>Categoría: {"🔴 Precio Alto" if categoria_pred == 1 else "🟢 Precio Bajo"}</h3>
                            <p>Probabilidad de precio alto: {proba_alto:.1%}</p>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Gráfico de confianza
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = proba_alto * 100,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Confianza de Precio Alto (%)"},
                            gauge = {
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, 50], 'color': "lightgray"},
                                    {'range': [50, 100], 'color': "gray"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            }
                        ))
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    st.markdown("### 📊 Comparación de Modelos")
                    
                    if app.models_regression:
                        # Comparación de modelos de regresión
                        st.markdown("#### 📈 Modelos de Regresión")
                        reg_comparison = []
                        for name, results in app.models_regression.items():
                            reg_comparison.append({
                                'Modelo': name,
                                'RMSE': results['rmse'],
                                'R²': results['r2']
                            })
                        
                        df_reg_comp = pd.DataFrame(reg_comparison).sort_values('R²', ascending=False)
                        st.dataframe(df_reg_comp, use_container_width=True)
                        
                        # Gráfico de comparación
                        fig = px.bar(df_reg_comp, x='Modelo', y='R²', 
                                    title='Comparación R² por Modelo',
                                    color='R²', color_continuous_scale='viridis')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    if app.models_classification:
                        # Comparación de modelos de clasificación
                        st.markdown("#### 🎯 Modelos de Clasificación")
                        clf_comparison = []
                        for name, results in app.models_classification.items():
                            clf_comparison.append({
                                'Modelo': name,
                                'Exactitud': results['accuracy']
                            })
                        
                        df_clf_comp = pd.DataFrame(clf_comparison).sort_values('Exactitud', ascending=False)
                        st.dataframe(df_clf_comp, use_container_width=True)
                        
                        # Gráfico de comparación
                        fig = px.bar(df_clf_comp, x='Modelo', y='Exactitud', 
                                    title='Comparación Exactitud por Modelo',
                                    color='Exactitud', color_continuous_scale='plasma')
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    st.markdown("### 📈 Visualizaciones del Dataset")
                    
                    # Distribución de precios
                    fig1 = px.histogram(app.df, x='Price_Max_log', 
                                       title='Distribución de Precios (Log)',
                                       marginal='box')
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Correlación entre variables numéricas
                    if len(numeric_cols) > 1:
                        corr_matrix = app.df[numeric_cols].corr()
                        fig2 = px.imshow(corr_matrix, 
                                        title='Matriz de Correlación',
                                        color_continuous_scale='RdBu')
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    # Distribución de categorías de precio
                    if 'Precio_Alto' in app.df.columns:
                        precio_counts = app.df['Precio_Alto'].value_counts()
                        fig3 = px.pie(values=precio_counts.values, 
                                     names=['Precio Bajo', 'Precio Alto'],
                                     title='Distribución de Categorías de Precio')
                        st.plotly_chart(fig3, use_container_width=True)
                
                with tab4:
                    st.markdown("### 🔍 Exploración de Datos")
                    
                    # Estadísticas descriptivas
                    st.markdown("#### 📊 Estadísticas Descriptivas")
                    st.dataframe(app.df.describe(), use_container_width=True)
                    
                    # Información del dataset
                    st.markdown("#### ℹ️ Información del Dataset")
                    buffer = st.empty()
                    
                    # Mostrar primeras filas
                    st.markdown("#### 👁️ Vista Previa de los Datos")
                    st.dataframe(app.df.head(10), use_container_width=True)
                    
                    # Valores faltantes
                    missing_data = app.df.isnull().sum()
                    if missing_data.sum() > 0:
                        st.markdown("#### ⚠️ Valores Faltantes")
                        missing_df = pd.DataFrame({
                            'Columna': missing_data.index,
                            'Valores Faltantes': missing_data.values,
                            'Porcentaje': (missing_data.values / len(app.df)) * 100
                        })
                        missing_df = missing_df[missing_df['Valores Faltantes'] > 0]
                        st.dataframe(missing_df, use_container_width=True)
                    else:
                        st.success("✅ No hay valores faltantes en el dataset")
    
    else:
        # Página de inicio
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2>🚀 ¡Bienvenido al Predictor de Precios de Automóviles!</h2>
            <p style="font-size: 1.1rem;">Esta aplicación utiliza algoritmos de Machine Learning avanzados para predecir precios de automóviles.</p>
            <br>
            <p>📁 <strong>Para comenzar, sube tu archivo CSV en la barra lateral</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Información sobre el formato esperado
        with st.expander("📋 Formato del Dataset", expanded=True):
            st.markdown("""
            ### Formato Esperado del Dataset:
            
            - **Price_Max_log**: Variable objetivo (precio en escala logarítmica)
            - **Variables numéricas**: Características como kilometraje, año, etc.
            - **Variables categóricas**: Marca, modelo, tipo de combustible, etc.
            
            ### Características de la Aplicación:
            
            ✅ **Múltiples algoritmos de ML**: Random Forest, SVM, Regresión Lineal, etc.  
            ✅ **Predicción dual**: Precio exacto + Categoría (Alto/Bajo)  
            ✅ **Visualizaciones interactivas**: Gráficos y análisis detallados  
            ✅ **Comparación de modelos**: Encuentra el mejor algoritmo para tus datos  
            ✅ **Interfaz intuitiva**: Fácil de usar, sin conocimientos técnicos  
            """)

if __name__ == "__main__":
    main()