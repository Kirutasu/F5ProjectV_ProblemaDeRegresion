# Makefile para Vehicle Price Prediction Platform

.PHONY: help build up down restart logs clean setup check health

help: ## Mostrar esta ayuda
	@echo "Vehicle Price Prediction Platform - Docker Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Configuración inicial del proyecto
	@echo "🔧 Configurando proyecto..."
	@mkdir -p backend/logs frontend/.streamlit data scripts
	@cp .env.example .env 2>/dev/null || true
	@if [ ! -f frontend/.streamlit/config.toml ]; then \
		echo '[server]' > frontend/.streamlit/config.toml; \
		echo 'headless = true' >> frontend/.streamlit/config.toml; \
		echo 'port = 8501' >> frontend/.streamlit/config.toml; \
		echo 'address = "0.0.0.0"' >> frontend/.streamlit/config.toml; \
		echo 'enableCORS = false' >> frontend/.streamlit/config.toml; \
	fi
	@if [ ! -f notebook/cars_data.sql ]; then \
		echo "-- Archivo SQL generado automáticamente" > notebook/cars_data.sql; \
	fi
	@chmod +x scripts/start.sh 2>/dev/null || true
	@echo "✅ Configuración completada"

build: setup ## Construir todos los servicios
	@echo "🔨 Construyendo servicios..."
	docker-compose build

up: build ## Iniciar todos los servicios
	@echo "🚀 Iniciando servicios..."
	docker-compose up -d
	@echo "⏳ Esperando inicialización..."
	@sleep 15
	@make check

down: ## Detener todos los servicios
	@echo "⏹️  Deteniendo servicios..."
	docker-compose down

restart: ## Reiniciar todos los servicios
	@echo "🔄 Reiniciando servicios..."
	docker-compose restart

logs: ## Ver logs de todos los servicios
	docker-compose logs -f

logs-backend: ## Ver logs del backend
	docker-compose logs -f backend

logs-frontend: ## Ver logs del frontend
	docker-compose logs -f frontend

logs-db: ## Ver logs de la base de datos
	docker-compose logs -f db

clean: ## Limpiar contenedores, volúmenes e imágenes
	@echo "🧹 Limpiando recursos Docker..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	docker volume prune -f

clean-all: clean ## Limpieza completa (incluye imágenes)
	docker rmi $$(docker images -q) 2>/dev/null || true

check: ## Verificar estado de los servicios
	@echo "📊 Verificando servicios..."
	@echo ""
	@echo "🔍 Estado de contenedores:"
	@docker-compose ps
	@echo ""
	@echo "🔍 Verificando conectividad:"
	@sleep 2
	@curl -s http://localhost:8000/health > /dev/null && echo "✅ Backend: OK (http://localhost:8000)" || echo "❌ Backend: No disponible"
	@curl -s http://localhost:8501 > /dev/null && echo "✅ Frontend: OK (http://localhost:8501)" || echo "❌ Frontend: No disponible"
	@docker-compose exec -T db pg_isready -U myuser -d mydb > /dev/null && echo "✅ Database: OK" || echo "❌ Database: No disponible"

health: ## Health check detallado
	@echo "🏥 Health Check Detallado:"
	@echo ""
	@echo "Backend Health:"
	@curl -s http://localhost:8000/health | python -m json.tool 2>/dev/null || echo "No disponible"
	@echo ""
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "Frontend App: http://localhost:8501"

dev: ## Modo desarrollo (con rebuild automático)
	docker-compose up --build

prod: ## Modo producción
	docker-compose -f docker-compose.yml up -d --build

shell-backend: ## Shell del contenedor backend
	docker-compose exec backend /bin/bash

shell-frontend: ## Shell del contenedor frontend
	docker-compose exec frontend /bin/bash

shell-db: ## Shell de la base de datos
	docker-compose exec db psql -U myuser -d mydb

backup-db: ## Backup de la base de datos
	@echo "💾 Creando backup..."
	@mkdir -p backups
	docker-compose exec -T db pg_dump -U myuser mydb > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup creado en backups/"

restore-db: ## Restaurar base de datos (especificar BACKUP_FILE=archivo)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "❌ Especifica BACKUP_FILE=archivo.sql"; exit 1; fi
	docker-compose exec -T db psql -U myuser -d mydb < $(BACKUP_FILE)

info: ## Mostrar información del proyecto
	@echo "📋 Vehicle Price Prediction Platform"
	@echo ""
	@echo "🌐 URLs:"
	@echo "   Frontend: http://localhost:8501"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"
	@echo "   Health:   http://localhost:8000/health"
	@echo ""
	@echo "🗄️  Base de datos:"
	@echo "   Host:     localhost:5432"
	@echo "   Usuario:  myuser"
	@echo "   Password: mypass"
	@echo "   DB:       mydb"
	@echo ""
	@echo "📁 Estructura:"
	@echo "   Backend:  ./backend/"
	@echo "   Frontend: ./frontend/"
	@echo "   Models:   ./notebook/"
	@echo "   Data:     ./data/"