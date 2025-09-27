# Backend Dockerfile

# 1️⃣ Imagen base ligera
FROM python:3.13-slim

# 2️⃣ Configuración para evitar problemas con stdout/stderr en logs
ENV PYTHONUNBUFFERED=1

# 3️⃣ Crear directorio de la app
WORKDIR /app

# 4️⃣ Copiar dependencias primero (mejora cacheo)
COPY requirements.txt .

# 5️⃣ Instalar dependencias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6️⃣ Copiar el código de la app
COPY . .

# 7️⃣ Exponer puerto (FastAPI con Uvicorn)
EXPOSE 8000

# 8️⃣ Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
