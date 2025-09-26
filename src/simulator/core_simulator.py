#!/usr/bin/env python3
"""
🚗 Vehicle Price Prediction Data ETL Pipeline
Descarga, limpia y transforma el dataset real de Kaggle para ML
"""
import os
import json
import polars as pl
from pathlib import Path
import time
from kaggle.api.kaggle_api_extended import KaggleApi


class VehicleDataETL:
    """
    Pipeline ETL para el dataset de vehículos de Kaggle
    Realiza las mismas transformaciones que el notebook de limpieza
    """
    def __init__(self, kaggle_dataset="abdulmalik1518/cars-datasets-2025"):
        self.kaggle_dataset = kaggle_dataset
        self.project_root = Path(__file__).parent.parent  # FSPROJECTV_PROBLEMADEREGRESION/
        self.data_dir = self.project_root / "data"
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.models_dir = self.project_root / "models"
        self.api = None

    def authenticate_kaggle(self):
        """Autentica con Kaggle usando credenciales del archivo kaggle.json en la raíz"""
        print("🔐 Autenticando con Kaggle...")
        try:
            # Busca el archivo kaggle.json en la raíz del proyecto
            kaggle_json_path = self.project_root / "kaggle.json"
            if not kaggle_json_path.exists():
                raise FileNotFoundError(f"No se encontró {kaggle_json_path}")

            with open(kaggle_json_path, "r") as f:
                credentials = json.load(f)

            os.environ['KAGGLE_USERNAME'] = credentials['USUARIO']
            os.environ['KAGGLE_KEY'] = credentials['CLAVE']

            self.api = KaggleApi()
            self.api.authenticate()
            print("   ✅ Autenticación exitosa")
        except Exception as e:
            print(f"   ❌ Error de autenticación: {e}")
            raise

    def download_dataset(self):
        """Descarga el dataset de Kaggle"""
        print(f"📥 Descargando dataset: {self.kaggle_dataset}")
        try:
            self.api.dataset_download_files(
                self.kaggle_dataset,
                path=str(self.raw_dir),
                unzip=True,
                force=True
            )
            print("   ✅ Dataset descargado y descomprimido")
        except Exception as e:
            print(f"   ❌ Error al descargar: {e}")
            raise

    def find_csv_file(self):
        """Encuentra el archivo CSV en la carpeta raw"""
        csv_files = list(self.raw_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError("No se encontró ningún archivo CSV en la carpeta raw/")
        csv_file = csv_files[0]
        print(f"   📄 Archivo CSV encontrado: {csv_file.name}")
        return csv_file

    def load_and_clean_data(self, csv_file):
        """Carga y limpia los datos siguiendo exactamente el notebook"""
        print(f"🧹 Cargando y limpiando datos desde {csv_file}...")
        
        # Leer CSV
        df = pl.read_csv(csv_file, encoding="latin1")
        print(f"   📊 Datos originales: {df.shape}")
        
        # 1. Renombrar columnas
        df = df.rename({
            "Company Names": "Brands",
            "Cars Names": "Model",
            "CC/Battery Capacity": "Engine_capacity_in_cc",
            "HorsePower": "HorsePower_in_HP",
            "Total Speed": "Max_speed_in_km/h",
            "Performance(0 - 100 )KM/H": "Time_to_100kmph_sec",
            "Cars Prices": "Price_$",
            "Fuel Types": "Fuel",
            "Torque": "Torque_in_Nm"
        })
        
        # 2. Crear columna ID
        df = df.with_columns(pl.arange(0, pl.len()).alias("id"))
        
        # 3. Seleccionar y reordenar columnas necesarias
        df = df.select([
            "id", "Brands", "Model", "Engines", "Engine_capacity_in_cc",
            "HorsePower_in_HP", "Max_speed_in_km/h", "Time_to_100kmph_sec",
            "Price_$", "Fuel", "Seats", "Torque_in_Nm"
        ])
        
        # 4. Limpieza de Brands
        df = df.with_columns(
            (pl.col("Brands").str.slice(0, 1).str.to_uppercase() +
             pl.col("Brands").str.slice(1).str.to_lowercase()).alias("Brands")
        )
        
        # 5. Limpieza de Engine_capacity_in_cc
        df = df.with_columns(
            pl.col("Engine_capacity_in_cc")
            .cast(pl.Utf8)
            .str.replace_all(r"[Cc]{1,2}", "")
            .str.replace_all(r",", "")
            .str.replace_all(r"\s*\+.*", "")
            .str.strip_chars()
            .cast(pl.Int32, strict=False)
            .fill_null(0)
            .alias("Engine_capacity_in_cc")
        )
        
        # 6. Limpieza de HorsePower_in_HP
        df = df.with_columns([
            pl.col("HorsePower_in_HP")
            .str.extract_groups(r"(?P<first>\d+)\s*(?:-\s*(?P<second>\d+))?\s*hp")
            .struct.rename_fields(["HorsePower_in_HP", "HorsePower_in_HP_2"])
            .alias("temp")
        ])
        df = df.with_columns([
            pl.col("temp").struct.field("HorsePower_in_HP").cast(pl.Int32),
            pl.col("temp").struct.field("HorsePower_in_HP_2").cast(pl.Int32)
        ]).drop("temp")
        df = df.with_columns(
            pl.coalesce(pl.col("HorsePower_in_HP_2"), pl.col("HorsePower_in_HP")).alias("HorsePower_in_HP_2")
        )
        
        # 7. Limpieza de Price_$
        df = df.with_columns([
            pl.col("Price_$")
            .str.strip_chars()
            .str.replace_all(r"[\\$,]", "", literal=False)
            .str.extract(r"(\d+)")
            .cast(pl.Float32)
            .alias("Price_Min"),
            pl.col("Price_$")
            .str.strip_chars()
            .str.replace_all(r"[\\$,]", "", literal=False)
            .str.extract(r"\d+\s*-\s*(\d+)")
            .cast(pl.Float32)
            .alias("Price_Max")
        ])
        df = df.with_columns(
            pl.when(pl.col("Price_Max").is_null())
            .then(pl.col("Price_Min"))
            .otherwise(pl.col("Price_Max"))
            .alias("Price_Max")
        )
        df = df.drop("Price_$")
        
        # 8. Limpieza de Max_speed_in_km/h
        df = df.with_columns([
            pl.col("Max_speed_in_km/h")
            .str.extract(r"(\d+)")
            .cast(pl.Float32, strict=False)
            .alias("Max_speed_in_km/h")
        ])
        
        # 9. Limpieza de Time_to_100kmph_sec
        df = df.with_columns([
            pl.col("Time_to_100kmph_sec")
            .str.extract(r"(\d+(?:\.\d+)?)")
            .cast(pl.Float32, strict=False)
            .alias("Time_to_100kmph_sec")
        ])
        
        # 10. Limpieza de Seats
        df = df.with_columns([
            pl.col("Seats")
            .str.extract(r"(\d+(?:\.\\d+)?)")
            .cast(pl.Int32, strict=False)
            .alias("Seats")
        ])
        
        # 11. Limpieza de Torque_in_Nm
        df = df.with_columns([
            pl.col("Torque_in_Nm")
            .str.extract(r"(\d+)")
            .cast(pl.Int32)
            .alias("Torque_in_Nm"),
            pl.col("Torque_in_Nm")
            .str.extract(r"\d+\s*-\s*(\d+)")
            .cast(pl.Int32)
            .alias("Torque_in_Nm_2_temp")
        ])
        df = df.with_columns(
            pl.when(pl.col("Torque_in_Nm_2_temp").is_null())
            .then(pl.col("Torque_in_Nm"))
            .otherwise(pl.col("Torque_in_Nm_2_temp"))
            .alias("Torque_in_Nm_2")
        )
        df = df.drop("Torque_in_Nm_2_temp")
        
        # 12. Limpieza de Fuel
        df = df.with_columns([
            pl.col("Fuel")
            .str.replace_all(r"[()/,+\-]", " ")
            .str.replace_all(r"\s+", " ")
            .str.strip_chars()
            .str.split(" ")
            .alias("Fuel_list")
        ])
        max_len = df.select(pl.col("Fuel_list").list.len().max()).to_numpy()[0][0]
        df = df.with_columns(
            pl.col("Fuel_list").list.to_struct(upper_bound=max_len).alias("Fuel_struct")
        )
        df = df.unnest("Fuel_struct")
        fuel_cols = {f"field_{i}": f"Fuel_{i+1}" for i in range(max_len)}
        df = df.rename(fuel_cols)
        df = df.drop(["Fuel", "Fuel_list", "Fuel_2", "Fuel_3"])
        
        print(f"   ✅ Datos limpios: {df.shape}")
        return df

    def save_clean_data(self, df):
        """Guarda los datos limpios en CSV"""
        self.processed_dir.mkdir(exist_ok=True)
        output_path = self.processed_dir / "dataset_modelado_optimizado.csv"
        df.write_csv(output_path)
        print(f"💾 Datos guardados en: {output_path}")
        return output_path

    def run_etl_pipeline(self):
        """Ejecuta el pipeline ETL completo"""
        print("🏭 VEHICLE DATA ETL PIPELINE")
        print("=" * 50)
        print(f"🎯 Dataset: {self.kaggle_dataset}")
        print(f"📁 Directorio: {self.data_dir}")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            # Paso 1: Autenticar
            self.authenticate_kaggle()
            
            # Paso 2: Descargar
            self.download_dataset()
            
            # Paso 3: Encontrar CSV
            csv_file = self.find_csv_file()
            
            # Paso 4: Limpiar datos
            clean_df = self.load_and_clean_data(csv_file)
            
            # Paso 5: Guardar
            output_path = self.save_clean_data(clean_df)
            
            total_time = time.time() - start_time
            print(f"\n🎉 ETL COMPLETADO!")
            print(f"⏱️  Tiempo total: {total_time:.1f} segundos")
            print(f"📊 Registros procesados: {len(clean_df):,}")
            print(f"📁 Archivo final: {output_path}")
            
            return clean_df, output_path
            
        except Exception as e:
            print(f"\n❌ Error en el pipeline ETL: {e}")
            raise


def main():
    """Función principal para ejecutar el ETL"""
    etl = VehicleDataETL()
    etl.run_etl_pipeline()


if __name__ == "__main__":
    main()