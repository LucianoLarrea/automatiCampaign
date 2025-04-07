import mysql.connector
from mysql.connector import Error
import datetime
import pandas as pd # Ejemplo si cargas desde Excel/CSV
# import requests # Ejemplo si cargas desde API
import logging
import os # Para leer variables de entorno (recomendado para credenciales)

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, filename='snapshot_job.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

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

def update_insumo_prices(conn):
    """Actualiza precios de insumos (Ejemplo: desde un CSV)."""
    logging.info("Iniciando actualización de precios de insumos...")
    try:
        # --- PASO 1: Leer nuevos precios (EJEMPLO desde CSV) ---
        # Cambia esto según tu fuente de datos (CSV, Excel, API, etc.)
        df_precios = pd.read_csv('4-Brief/Gemini/nuevos_precios_insumos.csv') # Asume columnas 'ID_Insumo', 'Nuevo_Costo_Compra', 'Nueva_Unidad_Compra'
        cursor = conn.cursor()

        update_sql = """
            UPDATE INSUMOS
            SET Costo_Compra = %s,
                Unidad_Medida_Compra = %s, -- Opcional si cambia
                Fecha_Ultima_Actualizacion_Costo = NOW()
                -- AQUI DEBES RECALCULAR Costo_Por_Unidad_Uso o tener un Trigger/Función en la BD
                -- Ejemplo simple si la unidad de uso es 'g' y compra es 'kg' o 'g':
                , Costo_Por_Unidad_Uso = CASE
                                            WHEN %s LIKE '%kg' THEN %s / 1000.0
                                            WHEN %s LIKE 'g' THEN %s
                                            ELSE NULL -- Manejar otros casos (Litros a ml, etc)
                                        END
            WHERE ID_Insumo = %s;
        """
        update_data = []
        for index, row in df_precios.iterrows():
             # Asegúrate de que las unidades y costos sean correctos para el cálculo de Costo_Por_Unidad_Uso
            unidad_compra = row['Nueva_Unidad_Compra']
            costo_compra = row['Nuevo_Costo_Compra']
            update_data.append((
                costo_compra,
                unidad_compra,
                unidad_compra, # Para el CASE
                costo_compra,  # Para el CASE
                unidad_compra, # Para el CASE
                costo_compra,  # Para el CASE
                row['ID_Insumo']
            ))

        if update_data:
            cursor.executemany(update_sql, update_data)
            conn.commit()
            logging.info(f"Actualizados precios para {cursor.rowcount} insumos.")
        else:
            logging.info("No hay datos de precios de insumos para actualizar.")

        cursor.close()
        return True

    except FileNotFoundError:
        logging.warning("Archivo nuevos_precios_insumos.csv no encontrado. Saltando actualización.")
        return True # O False si es un error crítico
    except Error as e:
        logging.error(f"Error actualizando precios de insumos: {e}")
        conn.rollback() # Revertir cambios en caso de error
        return False
    except Exception as ex:
        logging.error(f"Error inesperado en update_insumo_prices: {ex}")
        conn.rollback()
        return False


def update_competitor_prices(conn):
    """Actualiza precios de competencia (Ejemplo: desde un Excel)."""
    logging.info("Iniciando actualización de precios de competencia...")
    try:
        # --- PASO 2: Leer nuevos precios (EJEMPLO desde Excel) ---
        df_competencia = pd.read_excel('4-Brief/Gemini/precios_competencia.xlsx') # Asume columnas 'ID_Plato', 'Precio_Competencia_Nuevo'
        cursor = conn.cursor()

        update_sql = """
            UPDATE PLATOS
            SET Precio_Competencia = %s
            WHERE ID_Plato = %s;
        """
        update_data = [(row['Precio_Competencia_Nuevo'], row['ID_Plato']) for index, row in df_competencia.iterrows()]

        if update_data:
            cursor.executemany(update_sql, update_data)
            conn.commit()
            logging.info(f"Actualizados precios de competencia para {cursor.rowcount} platos.")
        else:
            logging.info("No hay datos de precios de competencia para actualizar.")

        cursor.close()
        return True

    except FileNotFoundError:
        logging.warning("Archivo precios_competencia.xlsx no encontrado. Saltando actualización.")
        return True # O False
    except Error as e:
        logging.error(f"Error actualizando precios de competencia: {e}")
        conn.rollback()
        return False
    except Exception as ex:
        logging.error(f"Error inesperado en update_competitor_prices: {ex}")
        conn.rollback()
        return False

def create_financial_snapshot(conn):
    """Consulta la vista V_PLATOS_FINANCIALS y guarda el snapshot en HISTORY."""
    logging.info("Creando snapshot financiero...")
    try:
        cursor = conn.cursor(dictionary=True) # Devuelve filas como diccionarios

        # --- PASO 3: Leer parámetros actuales usados por la vista ---
        # (La vista ya los usa, pero es bueno guardarlos en el historial)
        cursor.execute("SELECT market_discount, iva_rate, commission_rate FROM FINANCIAL_PARAMS WHERE param_id = 1;") # O tu lógica
        params = cursor.fetchone()
        if not params:
            logging.error("No se encontraron parámetros financieros en FINANCIAL_PARAMS.")
            return False

        # --- PASO 4: Consultar la vista con los cálculos actuales ---
        # Crear un nuevo cursor para la consulta SELECT
        select_cursor = conn.cursor(dictionary=True)
        # Asegúrate que tu VISTA incluya las columnas base necesarias (Costo_Plato, Precio_Competencia)
        # Si no las incluye, modifica esta query para hacer JOINs o agregarlas a la VISTA
        query_vista = """
            SELECT
                vpc.*, -- Selecciona todo de la vista
                p.Precio_Competencia -- Asegura que el precio de competencia esté disponible
            FROM
                V_PLATOS_FINANCIALS vpc
            JOIN
                 PLATOS p ON vpc.ID_Plato = p.ID_Plato -- Une para obtener Precio_Competencia si no está en la vista
            WHERE p.Precio_Competencia IS NOT NULL AND p.Precio_Competencia > 0; -- Aplica filtro si es necesario aqui tambien
        """
        select_cursor.execute(query_vista)
        results = select_cursor.fetchall()
        select_cursor.close()
        logging.info(f"Se obtuvieron {len(results)} filas de V_PLATOS_FINANCIALS.")

        if not results:
            logging.warning("La vista V_PLATOS_FINANCIALS no devolvió resultados. No se creará snapshot.")
            return True

        # --- PASO 5: Insertar en la tabla de historial ---
        snapshot_timestamp = datetime.datetime.now()
        insert_sql = """
            INSERT INTO PLATOS_FINANCIALS_HISTORY (
                SnapshotTimestamp, ID_Plato,
                Costo_Plato_Hist, Precio_Competencia_Hist,
                Market_Discount_Used, IVA_Rate_Used, Commission_Rate_Used,
                PBA_Hist, PNA_Hist, COGS_Partner_Actual_Hist,
                Costo_Total_CT_Hist, Margen_Bruto_Actual_MBA_Hist,
                Porcentaje_Margen_Bruto_PctMBA_Hist
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
        """
        history_data = []
        for row in results:
            # Asegúrate que los nombres de columna coincidan con tu VISTA y tabla HISTORY
            history_data.append((
                snapshot_timestamp,
                row['ID_Plato'],
                row.get('Costo_Plato'), # Nombre de la columna en tu vista
                row.get('Precio_Competencia'), # Nombre de la columna (puede venir del JOIN)
                params['market_discount'],
                params['iva_rate'],
                params['commission_rate'],
                row.get('PBA'),
                row.get('PNA'),
                row.get('COGS_Partner_Actual'),
                row.get('Costo_Total_CT'),
                row.get('Margen_Bruto_Actual_MBA'),
                row.get('Porcentaje_Margen_Bruto_PctMBA')
            ))

        if history_data:
            # Crear un nuevo cursor para la inserción
            insert_cursor = conn.cursor()
            insert_cursor.executemany(insert_sql, history_data)
            conn.commit()
            logging.info(f"Insertadas {insert_cursor.rowcount} filas en PLATOS_FINANCIALS_HISTORY.")
            insert_cursor.close()
        else:
             logging.info("No hay datos procesados para insertar en el historial.")
             
        # Cerrar el cursor original
        cursor.close()
        return True

    except Error as e:
        logging.error(f"Error creando snapshot financiero: {e}")
        conn.rollback()
        return False
    except Exception as ex:
        logging.error(f"Error inesperado en create_financial_snapshot: {ex}")
        conn.rollback()
        return False

# --- Flujo Principal del Script ---
if __name__ == "__main__":
    logging.info("===== Iniciando Job de Actualización y Snapshot =====")
    connection = connect_db()

    if connection and connection.is_connected():
        # Ejecutar actualizaciones primero
        insumos_ok = update_insumo_prices(connection)
        competencia_ok = update_competitor_prices(connection)

        # Si las actualizaciones fueron bien (o si decides continuar aunque fallen)
        if insumos_ok and competencia_ok: # O ajusta esta lógica
             snapshot_ok = create_financial_snapshot(connection)
        else:
            logging.warning("Saltando snapshot debido a errores en la actualización de precios.")

        # Cerrar conexión
        connection.close()
        logging.info("Conexión a MySQL cerrada.")
    else:
        logging.error("No se pudo establecer conexión con la base de datos. Abortando.")

    logging.info("===== Job de Actualización y Snapshot Finalizado =====")