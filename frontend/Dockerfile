version: '3.8'

services:
  # Base de datos PostgreSQL
  db:
    image: postgres:15-alpine
    container_name: ml_postgres_db
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypass
      POSTGRES_DB: mydb
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./notebook/cars_data.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
    networks:
      - ml-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myuser -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend FastAPI
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: ml_backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://myuser:mypass@db:5432/mydb
      - PYTHONPATH=/app
      - HOST=0.0.0.0
      - PORT=8000
    volumes:
      - ./backend/logs:/app/backend/logs
      - ./notebook:/app/notebook:ro
      - ./backend:/app/backend
    networks:
      - ml-network
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend Streamlit
  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    container_name: ml_frontend
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://backend:8000
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_ENABLE_CORS=false
      - STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
    volumes:
      - ./frontend:/app/frontend
    networks:
      - ml-network
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local

networks:
  ml-network:
    driver: bridge