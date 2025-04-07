import mysql.connector
from mysql.connector import Error
import logging
import os

# --- Configuración de Base de Datos (Leer desde variables de entorno o archivo config) ---
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'atomick')

def connect_db():
    """Establece conexión con la base de datos."""
    conn = None
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        logging.info("Conexión a MySQL establecida.")
        return conn
    except Error as e:
        logging.error(f"Error conectando a MySQL: {e}")
        return None