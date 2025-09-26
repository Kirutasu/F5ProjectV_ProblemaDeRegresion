#!/bin/bash

# Script para ejecutar el ETL manualmente
echo "🚗 Iniciando Pipeline ETL de Vehículos..."
echo "=========================================="

# Navegar al directorio correcto
cd "$(dirname "$0")/.."  # Ir a la raíz del proyecto

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Verificar que el archivo kaggle.json existe
if [ ! -f "kaggle.json" ]; then
    echo "❌ No se encuentra kaggle.json en la raíz del proyecto"
    echo "💡 Crea un archivo kaggle.json con tus credenciales de Kaggle"
    exit 1
fi

# Verificar que el directorio src/simulator existe
if [ ! -d "src/simulator" ]; then
    echo "❌ No se encuentra el directorio src/simulator/"
    echo "💡 Asegúrate de que core_simulator.py esté en src/simulator/"
    exit 1
fi

# Ejecutar el ETL
echo "📊 Ejecutando core_simulator.py..."
python3 src/simulator/core_simulator.py

# Verificar si fue exitoso
if [ $? -eq 0 ]; then
    echo "✅ ETL completado exitosamente!"
    echo "📁 Datos procesados en: data/processed/dataset_modelado_optimizado.csv"
else
    echo "❌ Error en el ETL"
    exit 1
fi