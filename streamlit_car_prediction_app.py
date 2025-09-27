import streamlit as st
import requests
import json

# --- 1. Configuración de la URL del Backend ---
# ¡IMPORTANTE! Asegúrate que esta URL sea correcta. 
# Si tu backend corre localmente en el puerto 8000:
BACKEND_URL = "http://localhost:8000/predict"
API_URL = "http://127.0.0.1:8000/predict"

# Si has desplegado el backend, usa la URL de despliegue:
# BACKEND_URL = "https://tumi-fastapi-app.herokuapp.com/predict"


st.set_page_config(page_title="Predicción de Precios de Coches", layout="centered")
st.title("🚗 Estimador de Precios de Vehículos")
st.markdown("Introduce los detalles del vehículo y obtén una predicción de precio en tiempo real.")

# --- 2. Formulario de Entrada ---
with st.form("car_prediction_form"):
    st.subheader("Datos del Vehículo")

    # Los widgets deben recoger los datos que coincidan con CarPredictionRequest (models.py)

    manufacturer = st.selectbox("1. Fabricante", ["Audi", "BMW", "Toyota", "Ford", "Otros"])
    model = st.text_input("2. Modelo (ej: Q3, X5)", "A4")
    year = st.number_input("3. Año de Fabricación", min_value=1990, max_value=2024, value=2018, step=1)
    transmission = st.selectbox("4. Tipo de Transmisión", ["Manual", "Automático", "Semi-automático"])
    mileage = st.number_input("5. Kilometraje (unidades)", min_value=0, value=50000)
    fuel_type = st.selectbox("6. Tipo de Combustible", ["Gasolina", "Diésel", "Eléctrico", "Híbrido"])
    engine_size = st.number_input("7. Tamaño del Motor (Litros)", min_value=0.5, max_value=8.0, value=2.0, step=0.1)

    # Botón de envío
    submitted = st.form_submit_button("💰 PREDECIR PRECIO")

    if submitted:
        # 3. Recolectar datos para enviar
        prediction_data = {
            "Manufacturer": manufacturer,
            "Model": model,
            "Year": year,
            "Transmission": transmission,
            "Mileage": int(mileage), # Asegurarse de enviar enteros/float según el modelo
            "FuelType": fuel_type,
            "EngineSize": float(engine_size)
        }

        # 4. Enviar la petición a la API
        try:
            with st.spinner("Conectando con el backend y calculando predicción..."):
                # Usar requests.post con el diccionario 'prediction_data' como JSON
                response = requests.post(BACKEND_URL, json=prediction_data)
            
            # 5. Procesar la respuesta
            if response.status_code == 200:
                # Éxito
                result = response.json()
                predicted_price = result.get("predicted_price")

                st.success("✅ ¡Predicción Exitosa!")
                # Mostrar el precio formateado con separador de miles y dos decimales
                st.metric(label="PRECIO PREDICHO (Estimado)", value=f"${predicted_price:,.2f}")
                st.balloons()
            
            elif response.status_code == 422:
                # Error de validación (Pydantic/FastAPI)
                st.error("❌ Error de Validación de Datos. Por favor, revisa los valores introducidos.")
                st.json(response.json())
            
            else:
                # Otros errores de la API (500, 503, etc.)
                st.error(f"❌ Error al contactar con el backend. Código: {response.status_code}")
                st.markdown(f"**Detalle:** {response.text}")

        except requests.exceptions.ConnectionError:
            # Error de conexión (Backend apagado o URL incorrecta)
            st.error(f"⚠️ **Error de Conexión:** No se pudo conectar al backend en **{BACKEND_URL}**.")
            st.info("💡 **Instrucción:** Asegúrate de que el backend (`main.py`) está corriendo en el puerto y dirección correctos.")
        except Exception as e:
            st.error(f"Ocurrió un error inesperado en el frontend: {e}")