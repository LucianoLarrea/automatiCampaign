import os

class Config:
    """Clase centralizada para la configuración de la aplicación."""
    
    # Configuración de la base de datos
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_NAME = os.getenv('DB_NAME', 'atomick')
    
    # Rutas de archivos
    INSUMOS_PRICES_FILE = '4-Brief/Gemini/nuevos_precios_insumos.csv'
    COMPETITOR_PRICES_FILE = '4-Brief/Gemini/precios_competencia.xlsx'
    
    # Configuración de logging
    LOG_FILE = 'snapshot_job.log'
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'