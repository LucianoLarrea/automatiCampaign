from mysql.connector import Error
import pandas as pd
import logging

def update_insumo_prices(conn, file_path): # Eliminado valor por defecto
    if not file_path or not os.path.exists(file_path): # Verificar si existe
        logging.error(f"Archivo de precios de insumos no encontrado o no especificado: {file_path}")
        return False, f"Archivo no encontrado: {file_path}"
    """Actualiza precios de insumos (Ejemplo: desde un CSV)."""
    logging.info("Iniciando actualización de precios de insumos...")
    try:
        # --- PASO 1: Leer nuevos precios (EJEMPLO desde CSV) ---
        # Cambia esto según tu fuente de datos (CSV, Excel, API, etc.)
        df_precios = pd.read_csv('4-Brief/Gemini/nuevos_precios_insumos.csv')
        cursor = conn.cursor()

        update_sql = """
            UPDATE INSUMOS
            SET Costo_Compra = %s,
                Unidad_Medida_Compra = %s,
                Fecha_Ultima_Actualizacion_Costo = NOW()
                , Costo_Por_Unidad_Uso = CASE
                                            WHEN %s LIKE '%kg' THEN %s / 1000.0
                                            WHEN %s LIKE 'g' THEN %s
                                            ELSE NULL
                                        END
            WHERE ID_Insumo = %s;
        """
        update_data = []
        for index, row in df_precios.iterrows():
            unidad_compra = row['Nueva_Unidad_Compra']
            costo_compra = row['Nuevo_Costo_Compra']
            update_data.append((
                costo_compra,
                unidad_compra,
                unidad_compra,
                costo_compra,
                unidad_compra,
                costo_compra,
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
        return True
    except Error as e:
        logging.error(f"Error actualizando precios de insumos: {e}")
        conn.rollback()
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
        df_competencia = pd.read_excel('4-Brief/Gemini/precios_competencia.xlsx')
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
        return True
    except Error as e:
        logging.error(f"Error actualizando precios de competencia: {e}")
        conn.rollback()
        return False
    except Exception as ex:
        logging.error(f"Error inesperado en update_competitor_prices: {ex}")
        conn.rollback()
        return False