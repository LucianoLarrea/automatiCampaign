# Usa una imagen base oficial de Python (elige una versión específica)
FROM python:3.11-slim

# Establece variables de entorno útiles
# Para que los logs de Python aparezcan inmediatamente
ENV PYTHONUNBUFFERED=1 
# Directorio donde vivirá la app dentro del contenedor
ENV APP_HOME=/app      

# Establece rutas por defecto DENTRO del contenedor para los archivos de datos
# ESTOS PUEDEN (Y DEBEN) SER SOBRESCRITOS EN TIEMPO DE EJECUCIÓN (ej: en Cloud Run)
ENV INSUMOS_CSV_PATH=${APP_HOME}/data/nuevos_precios_insumos.csv
ENV COMPETENCIA_FILE_PATH=${APP_HOME}/data/precios_competencia.xlsx
# ¡¡NO PONGAS CREDENCIALES DE BD O API KEYS AQUÍ!! Se inyectan al ejecutar.

WORKDIR ${APP_HOME}

# Instalar dependencias del sistema si fueran necesarias (ej: para alguna librería Python)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Copia solo el archivo de requerimientos primero para aprovechar el caché de capas de Docker
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia el código de tu aplicación (los scripts .py) al directorio de trabajo /app
# Asegúrate de copiar todos los .py necesarios para snapshot_job.py
COPY snapshot_job.py .
COPY db_connection.py .
COPY price_updaters.py .
COPY snapshot_creator.py .
COPY config.py .  
# COPY Gemini/llm_integrator.py . # Si ya lo tienes y es necesario para el job

# --- IMPORTANTE: Archivos de Datos ---
# Por defecto, NO copiamos los archivos CSV/XLSX a la imagen.
# Es MEJOR práctica montarlos como volúmenes o proveerlos al contenedor
# en tiempo de ejecución (ej: descargarlos de Cloud Storage, montar GCS FUSE en Cloud Run).
# Las variables de entorno INSUMOS_CSV_PATH y COMPETENCIA_FILE_PATH deben apuntar
# a donde estarán esos archivos disponibles DENTRO del contenedor en ejecución.
#
# Si *realmente* necesitas incluirlos en la imagen (menos flexible):
# WORKDIR ${APP_HOME}/data # Cambia al subdirectorio de datos
# COPY Gemini/nuevos_precios_insumos.csv .
# COPY Gemini/precios_competencia.xlsx .
# WORKDIR ${APP_HOME} # Vuelve al directorio principal

# Comando por defecto que se ejecutará cuando el contenedor inicie
CMD ["python", "snapshot_job.py"]
# Nota: snapshot_job.py ya ejecuta todos los pasos por defecto si no se dan argumentos específicos.