# Frontend (React + Vite)

Este directorio contiene la definición de Docker y la aplicación React con Vite ubicada en `frontend/regresiones_frontend/`.

## Desarrollo local (sin Docker)

1. Entra a `frontend/regresiones_frontend/`:

```bash
cd regresiones_frontend
npm install
# Ajusta la URL del backend si es necesario
cp .env .env.local  # opcional
npm run dev
```

2. Abre `http://localhost:3000` en tu navegador.

La variable de entorno que usa Vite para la URL del backend es `VITE_BACKEND_URL` (por defecto `http://localhost:8000`).

## Ejecución con Docker Compose

El servicio `frontend` se define en la raíz en `docker-compose.yml` y expone el puerto `8005` para acceder desde el host.

```bash
docker-compose up -d --build
```

- Frontend: http://localhost:8005
- Backend: http://localhost:8000

La URL al backend dentro del contenedor es `http://backend:8000` y se inyecta con la variable `VITE_BACKEND_URL`.
