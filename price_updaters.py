from mysql.connector import Error
import pandas as pd
import logging
import os

def update_insumo_prices(conn, file_path): # Eliminado valor por defecto
    if not file_path or not os.path.exists(file_path): # Verificar si existe
        logging.error(f"Archivo de precios de insumos no encontrado o no especificado: {file_path}")
        return False, f"Archivo no encontrado: {file_path}"
    """Actualiza precios de insumos (Ejemplo: desde un CSV)."""
    logging.info("Iniciando actualización de precios de insumos...")
    try:
        # --- PASO 1: Leer nuevos precios (EJEMPLO desde CSV) ---
        # Cambia esto según tu fuente de datos (CSV, Excel, API, etc.)
        df_precios = pd.read_csv(file_path)
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
            message = f"Actualizados precios para {cursor.rowcount} insumos."
            logging.info(message)
            cursor.close()
            return True, message # <--- CORREGIDO
        else:
            message = "No hay datos de precios de insumos para actualizar."
            logging.info(message)
            if cursor: cursor.close() # Asegurar cierre si se abrió
            return True, message # <--- CORREGIDO (Éxito, sin cambios)


    except FileNotFoundError:
        message = f"Archivo {file_path} no encontrado. Saltando actualización."
        logging.warning(message)
        return True, message # <--- CORREGIDO (Considerado éxito, tarea saltada)
        # O podrías devolver False si es crítico: return False, message
    except Error as e:
        message = f"Error actualizando precios de insumos: {e}"
        logging.error(message)
        conn.rollback()
        if cursor: cursor.close()
        return False, message # <--- CORREGIDO
    except Exception as ex:
        message = f"Error inesperado en update_insumo_prices: {ex}"
        logging.error(message, exc_info=True)
        conn.rollback()
        if cursor: cursor.close()
        return False, message # <--- CORREGIDO


def update_competitor_prices(conn, file_path): # Eliminado valor por defecto
    if not file_path or not os.path.exists(file_path): # Verificar si existe
        logging.error(f"Archivo de precios de competencia no encontrado o no especificado: {file_path}")
        return False, f"Archivo no encontrado: {file_path}"
    """Actualiza precios de competencia (Ejemplo: desde un Excel)."""
    logging.info("Iniciando actualización de precios de competencia...")
    try:
        # --- PASO 2: Leer nuevos precios (EJEMPLO desde Excel) ---
        df_competencia = pd.read_excel(file_path)
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
            message = f"Actualizados precios de competencia para {cursor.rowcount} platos."
            logging.info(message)
            cursor.close()
            return True, message # <--- CORREGIDO
        else:
            message = "No hay datos de precios de competencia para actualizar."
            logging.info(message)
            if cursor: cursor.close() # Asegurar cierre si se abrió
            return True, message # <--- CORREGIDO (Éxito, sin cambios)

    except FileNotFoundError:
        message = f"Archivo {file_path} no encontrado. Saltando actualización."
        logging.warning(message)
        return True, message # <--- CORREGIDO (Considerado éxito, tarea saltada)
        # O podrías devolver False si es crítico: return False, message
    except Error as e:
        message = "Error actualizando precios de competencia: {e}"
        logging.error(message)
        conn.rollback()
        if cursor: cursor.close()
        return False, message # <--- CORREGIDO
    except Exception as ex:
        message = "Error inesperado en update_competitor_prices: {ex}"
        logging.error(message)
        conn.rollback()
        if cursor: cursor.close()
        return False, message # <--- CORREGIDO