# Usa una imagen base más ligera y específica
FROM python:3.9-slim

# Establece variables de entorno para evitar advertencias
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia solo lo necesario para instalar dependencias (mejor caché)
COPY requirements.txt .

# Instala dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia toda la estructura del proyecto
COPY . .

# Expone el puerto de Streamlit
EXPOSE 8501

# Comando por defecto: ejecuta el dashboard
CMD ["streamlit", "run", "src/dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]