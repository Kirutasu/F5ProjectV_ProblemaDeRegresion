# backend/Dockerfile.standalone
# Usando imagen base de Python sin necesidad de descargar imágenes externas

FROM python:3.11-slim

# Actualizar sistema y instalar dependencias básicas
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar requirements del backend
COPY backend/requirements.txt /app/backend/requirements.txt

# Crear requirements simplificado para evitar dependencias problemáticas
RUN echo "fastapi==0.117.1" > /app/requirements_simple.txt && \
    echo "uvicorn[standard]==0.36.0" >> /app/requirements_simple.txt && \
    echo "python-dotenv==1.1.1" >> /app/requirements_simple.txt && \
    echo "pydantic==2.11.7" >> /app/requirements_simple.txt && \
    echo "pydantic-settings==2.8.1" >> /app/requirements_simple.txt && \
    echo "numpy==1.26.4" >> /app/requirements_simple.txt && \
    echo "pandas==2.3.2" >> /app/requirements_simple.txt && \
    echo "scikit-learn==1.5.2" >> /app/requirements_simple.txt && \
    echo "joblib==1.4.2" >> /app/requirements_simple.txt && \
    echo "requests==2.32.4" >> /app/requirements_simple.txt && \
    echo "python-multipart==0.0.9" >> /app/requirements_simple.txt && \
    echo "aiofiles==23.2.1" >> /app/requirements_simple.txt

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements_simple.txt

# Copiar código del backend
COPY backend/ /app/backend/
COPY notebook/ /app/notebook/

# Crear directorios necesarios
RUN mkdir -p /app/backend/logs
RUN mkdir -p /app/backend/assets
RUN mkdir -p /app/data

# Configurar variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Exponer puerto
EXPOSE 8000

# Comando de inicio con configuración más robusta
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]