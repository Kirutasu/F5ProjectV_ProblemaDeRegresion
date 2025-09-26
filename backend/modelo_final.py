# modelo_final.py
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report, confusion_matrix
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class AutomovilesModelEnhanced:
    def __init__(self):
        self.modelo_regresion = None
        self.modelo_clasificacion = None
        self.is_trained = False
        self.columnas_esperadas = None
        
        # Cargar modelos al inicializar
        self.cargar_modelos_preentrenados()

    def cargar_modelos_preentrenados(self):
        """Carga los modelos pre-entrenados desde los archivos .pkl"""
        try:
            # Cargar modelo de regresión
            self.modelo_regresion = joblib.load('clean/mejor_modelo_regresion_Linear_Regression.pkl')
            logger.info("✅ Modelo de regresión (Linear Regression) cargado correctamente")
            
            # Cargar modelo de clasificación
            self.modelo_clasificacion = joblib.load('clean/mejor_modelo_clasificacion_Decision_Tree.pkl')
            logger.info("✅ Modelo de clasificación (Decision Tree) cargado correctamente")
            
            # Establecer como entrenado
            self.is_trained = True
            
            # Obtener las columnas esperadas del preprocesador
            self._obtener_columnas_esperadas()
            
        except FileNotFoundError as e:
            logger.error(f"❌ Error al cargar modelos: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error inesperado al cargar modelos: {e}")
            raise

    def _obtener_columnas_esperadas(self):
        """Obtiene las columnas esperadas por el preprocesador del modelo"""
        try:
            if hasattr(self.modelo_regresion, 'named_steps'):
                preprocesador = self.modelo_regresion.named_steps.get('preprocesador')
                if hasattr(preprocesador, 'feature_names_in_'):
                    self.columnas_esperadas = list(preprocesador.feature_names_in_)
                    logger.info(f"✅ Columnas esperadas: {self.columnas_esperadas}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron obtener las columnas esperadas: {e}")

    def preparar_datos(self, df):
        """Prepara los datos para compatibilidad con los modelos"""
        # Hacer una copia para no modificar el original
        df_preparado = df.copy()
        
        # Normalizar nombres de columnas a minúsculas
        df_preparado.columns = df_preparado.columns.str.lower()
        
        # Verificar columnas de precio
        columnas_precio = [col for col in df_preparado.columns if 'price' in col]
        if not columnas_precio:
            raise ValueError("❌ No se encontraron columnas de precio en el dataset")
        
        # Usar la primera columna de precio encontrada
        columna_precio = columnas_precio[0]
        logger.info(f"✅ Usando columna de precio: {columna_precio}")
        
        # Crear variable de clasificación si no existe
        if 'precio_alto' not in df_preparado.columns:
            precio_mediano = df_preparado[columna_precio].median()
            df_preparado['precio_alto'] = (df_preparado[columna_precio] > precio_mediano).astype(int)
            logger.info(f"✅ Variable 'precio_alto' creada (umbral: {precio_mediano:.2f})")
        
        # Separar características y objetivos
        columnas_excluir = [columna_precio, 'precio_alto', 'precio_categoria']
        caracteristicas = df_preparado.drop([col for col in columnas_excluir if col in df_preparado.columns], 
                                          axis=1, errors='ignore')
        objetivo_reg = df_preparado[columna_precio]
        objetivo_clf = df_preparado['precio_alto']
        
        logger.info(f"✅ Datos preparados - Características: {caracteristicas.shape}")
        return caracteristicas, objetivo_reg, objetivo_clf

    def predecir_auto(self, datos_entrada):
        """Realiza predicciones para un automóvil"""
        try:
            if not self.is_trained:
                raise ValueError("❌ Los modelos no están cargados correctamente")
            
            # Convertir datos de entrada a DataFrame
            datos_df = pd.DataFrame([datos_entrada])
            
            # Asegurar que las columnas estén en minúsculas
            datos_df.columns = datos_df.columns.str.lower()
            
            logger.info(f"🔮 Realizando predicción para: {datos_entrada.get('brand', 'Unknown')} {datos_entrada.get('model', 'Unknown')}")
            
            # Realizar predicciones
            precio_predicho = self.modelo_regresion.predict(datos_df)[0]
            categoria_predicha = self.modelo_clasificacion.predict(datos_df)[0]
            probabilidades = self.modelo_clasificacion.predict_proba(datos_df)[0]
            
            # Preparar respuesta
            resultado = {
                'precio_predicho': float(precio_predicho),
                'precio_alto_predicho': int(categoria_predicha),
                'probabilidad_precio_alto': float(probabilidades[1]),
                'categoria_predicha': 'Alto' if categoria_predicha == 1 else 'Bajo',
                'modelo_utilizado': 'Linear Regression + Decision Tree (Pre-entrenado)',
                'estado': 'success'
            }
            
            logger.info(f"✅ Predicción exitosa: {resultado['categoria_predicha']} (${resultado['precio_predicho']:.2f})")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error en predicción: {e}")
            return {
                'precio_predicho': 0.0,
                'precio_alto_predicho': 0,
                'probabilidad_precio_alto': 0.0,
                'categoria_predicha': 'Error',
                'modelo_utilizado': 'N/A',
                'estado': 'error',
                'error': str(e)
            }

    def evaluar_modelos(self, X_test, y_test_reg, y_test_clf):
        """Evalúa los modelos con datos de prueba"""
        try:
            if not self.is_trained:
                raise ValueError("❌ Los modelos no están cargados correctamente")
            
            # Predicciones de regresión
            y_pred_reg = self.modelo_regresion.predict(X_test)
            rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
            r2 = r2_score(y_test_reg, y_pred_reg)
            
            # Predicciones de clasificación
            y_pred_clf = self.modelo_clasificacion.predict(X_test)
            accuracy = accuracy_score(y_test_clf, y_pred_clf)
            
            resultados = {
                'regression': {
                    'RMSE': float(rmse),
                    'R2': float(r2),
                    'MAE': float(np.mean(np.abs(y_test_reg - y_pred_reg)))
                },
                'classification': {
                    'Accuracy': float(accuracy),
                    'Report': classification_report(y_test_clf, y_pred_clf, output_dict=True)
                }
            }
            
            logger.info(f"📊 Evaluación completada - RMSE: {rmse:.4f}, Accuracy: {accuracy:.4f}")
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Error en evaluación: {e}")
            raise

# Instancia global para usar en la API
car_service_final = AutomovilesModelEnhanced()

# Funciones de compatibilidad con el main.py existente
def predecir_auto(datos_entrada):
    """Función de compatibilidad para la API"""
    return car_service_final.predecir_auto(datos_entrada)

def preparar_datos(df):
    """Función de compatibilidad para la API"""
    return car_service_final.preparar_datos(df)

def entrenar_modelos(X_train, y_train_reg, X_test, y_test_reg, y_train_clf, y_test_clf):
    """Función de compatibilidad - No necesaria para modelos pre-entrenados"""
    logger.info("⚠️ Los modelos ya están pre-entrenados, no se requiere entrenamiento adicional")
    return True

def guardar_modelos():
    """Función de compatibilidad - No necesaria para modelos pre-entrenados"""
    logger.info("⚠️ Los modelos ya están guardados como archivos .pkl")
    pass

def cargar_modelos():
    """Función de compatibilidad para la API"""
    try:
        car_service_final.cargar_modelos_preentrenados()
        return True
    except Exception as e:
        logger.error(f"❌ Error al cargar modelos: {e}")
        return False

# Atributos esperados por main.py
is_trained = car_service_final.is_trained
datos_entrenamiento = None
columnas_numericas = car_service_final.columnas_esperadas or []
columnas_categoricas = []