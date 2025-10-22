#!/bin/bash

# fix-docker.sh - Script para solucionar problemas de conectividad Docker

echo "🔧 Diagnosticando y solucionando problemas de Docker..."

# Verificar conectividad de red
echo "📡 Verificando conectividad de red..."
if ping -c 1 google.com > /dev/null 2>&1; then
    echo "✅ Conectividad a internet OK"
else
    echo "❌ Sin conectividad a internet"
    echo "Por favor verifica tu conexión de red"
fi

# Verificar DNS
echo "🔍 Verificando resolución DNS..."
if nslookup docker.io > /dev/null 2>&1; then
    echo "✅ DNS OK"
else
    echo "❌ Problema con DNS"
    echo "Intentando configurar DNS alternativo..."
fi

# Reiniciar Docker Desktop
echo "🔄 Reiniciando Docker Desktop..."
echo "Por favor reinicia Docker Desktop manualmente si es necesario"

# Limpiar caché de Docker
echo "🧹 Limpiando caché de Docker..."
docker system prune -f 2>/dev/null || true

# Configurar Docker para usar mirrors alternativos
echo "🔧 Configurando mirrors de Docker..."

# Crear configuración daemon.json para Windows
if [[ "$OSTYPE" == "msys" ]]; then
    DOCKER_CONFIG_DIR="/c/Users/$USER/.docker"
    mkdir -p "$DOCKER_CONFIG_DIR"
    
    cat > "$DOCKER_CONFIG_DIR/daemon.json" << EOF
{
  "registry-mirrors": [
    "https://mirror.gcr.io",
    "https://daocloud.io",
    "https://docker.mirrors.ustc.edu.cn"
  ],
  "dns": ["8.8.8.8", "8.8.4.4"],
  "insecure-registries": [],
  "debug": false,
  "experimental": false
}
EOF
    echo "✅ Configuración Docker creada en $DOCKER_CONFIG_DIR/daemon.json"
fi

echo ""
echo "🚀 Soluciones alternativas disponibles:"
echo ""
echo "OPCIÓN 1 - Usar versión sin base de datos externa:"
echo "   docker-compose -f docker-compose-offline.yml up --build"
echo ""
echo "OPCIÓN 2 - Ejecutar solo con Python (sin Docker):"
echo "   cd backend && python -m uvicorn main:app --reload &"
echo "   cd frontend && streamlit run streamlit_car_prediction_app.py &"
echo ""
echo "OPCIÓN 3 - Usar imágenes base más ligeras:"
echo "   Modificar Dockerfiles para usar alpine linux"
echo ""
echo "OPCIÓN 4 - Configurar proxy si estás en una red corporativa:"
echo "   docker --config ~/.docker --log-level debug info"
echo ""

# Verificar si Docker funciona
echo "🧪 Probando Docker básico..."
if docker --version > /dev/null 2>&1; then
    echo "✅ Docker instalado correctamente"
    
    # Intentar ejecutar contenedor de prueba con imagen Python base
    echo "🧪 Probando contenedor básico..."
    if timeout 30 docker run --rm python:3.11-slim python --version > /dev/null 2>&1; then
        echo "✅ Docker funciona correctamente"
    else
        echo "❌ Problemas al ejecutar contenedores"
        echo "Probablemente sea un problema de conectividad de red"
    fi
else
    echo "❌ Docker no está instalado o no funciona"
fi

echo ""
echo "📋 Pasos siguientes recomendados:"
echo "1. Reinicia Docker Desktop"
echo "2. Verifica tu conexión a internet"
echo "3. Si estás en una red corporativa, configura el proxy"
echo "4. Usa la versión offline: docker-compose -f docker-compose-offline.yml up"
echo "5. O ejecuta directamente con Python sin Docker"