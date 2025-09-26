# Frontend Dockerfile
FROM node:20-slim

WORKDIR /app

# Copiar archivos de configuración
COPY regresiones_frontend/package*.json ./
RUN npm install

# Copiar el resto del código fuente
COPY regresiones_frontend/ ./

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "--port", "3000"]
