FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema mínimas (opcional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements específicos del frontend si existen
COPY frontend/requirements.txt /app/frontend/requirements.txt

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r /app/frontend/requirements.txt || \
    pip install --no-cache-dir streamlit pandas numpy plotly requests

# Copiar código del frontend
COPY frontend/ /app/frontend/

EXPOSE 8501

ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

CMD ["streamlit", "run", "frontend/streamlit_car_prediction_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]