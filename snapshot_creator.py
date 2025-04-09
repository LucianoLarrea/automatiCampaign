# snapshot_creator.py (Corregido)

from mysql.connector import Error
import logging
import datetime

def create_financial_snapshot(conn):
    """
    Consulta V_PLATOS_FINANCIALS, obtiene parámetros, y guarda el snapshot en HISTORY.
    Devuelve (bool, str) indicando éxito y un mensaje.
    """
    logging.info("Iniciando creación de snapshot financiero...")
    params_cursor = None
    select_cursor = None
    insert_cursor = None
    message = ""
    success = False

    try:
        # --- PASO 1: Leer parámetros actuales ---
        params_cursor = conn.cursor(dictionary=True)
        params_cursor.execute("SELECT market_discount, iva_rate, commission_rate FROM FINANCIAL_PARAMS WHERE param_id = 1;") # O tu lógica de selección
        params = params_cursor.fetchone()
#        params_cursor.close() # Cerrar cursor de parámetros, eliminado por causer problemas en el testing

        if not params:
            message = "Error: No se encontraron parámetros financieros en FINANCIAL_PARAMS."
            logging.error(message)
            return False, message # Salir si no hay parámetros

        # --- PASO 2: Consultar la vista con los cálculos actuales ---
        select_cursor = conn.cursor(dictionary=True)
        query_vista = """
            SELECT
                vpc.*,
                p.Precio_Competencia,
                p.Nombre_Plato -- Asegurarse de incluir Nombre_Plato si lo quieres usar
            FROM
                V_PLATOS_FINANCIALS vpc
            JOIN
                PLATOS p ON vpc.ID_Plato = p.ID_Plato
            WHERE p.Precio_Competencia IS NOT NULL AND p.Precio_Competencia > 0;
        """
        select_cursor.execute(query_vista)
        results = select_cursor.fetchall()
        # select_cursor.close() # Cerrar cursor de selección. Eliminado por Testing
        logging.info(f"Se obtuvieron {len(results)} filas de V_PLATOS_FINANCIALS.")

        # --- PASO 3: Procesar resultados y preparar inserción ---
        if not results:
            message = "La vista V_PLATOS_FINANCIALS no devolvió resultados. No se insertó snapshot."
            logging.warning(message)
            success = True # Se considera éxito (no hubo error), aunque no se insertó nada.
        else:
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
            # Usar .get(col_name, default_value) por seguridad si una columna de la vista pudiera faltar
            for row in results:
                history_data.append((
                    snapshot_timestamp,
                    row.get('ID_Plato'),
                    row.get('Costo_Plato'),
                    row.get('Precio_Competencia'),
                    params.get('market_discount'),
                    params.get('iva_rate'),
                    params.get('commission_rate'),
                    row.get('PBA'),
                    row.get('PNA'),
                    row.get('COGS_Partner_Actual'),
                    row.get('Costo_Total_CT'),
                    row.get('Margen_Bruto_Actual_MBA'),
                    row.get('Porcentaje_Margen_Bruto_PctMBA')
                ))

            if history_data:
                # Realizar inserción
                insert_cursor = conn.cursor()
                insert_cursor.executemany(insert_sql, history_data)
                conn.commit()
                row_count = insert_cursor.rowcount if insert_cursor.rowcount else len(history_data) # rowcount puede ser -1
                message = f"Insertadas {row_count} filas en PLATOS_FINANCIALS_HISTORY."
                logging.info(message)
                # insert_cursor.close() # Cerrar cursor de inserción. Eliminado por Testing
                success = True
            else:
                # Esto no debería ocurrir si 'results' no estaba vacío, pero por si acaso
                message = "Se obtuvieron resultados de la vista pero no se pudieron procesar para el historial."
                logging.warning(message)
                success = True # Aún se considera éxito del proceso general

    except Error as e:
        logging.error(f"Error de BD creando snapshot financiero: {e}")
        conn.rollback() # Revertir en caso de error de BD
        message = f"Error de BD al crear snapshot: {e}"
        success = False
    except Exception as ex:
        logging.error(f"Error inesperado creando snapshot financiero: {ex}", exc_info=True)
        # No hacer rollback necesariamente aquí, podría ser un error de Python, no de BD
        message = f"Error inesperado al crear snapshot: {ex}"
        success = False
    finally:
        # Asegurarse de cerrar cursores abiertos. Es seguro llamar a close()
        # incluso si ya está cerrado, pero verificamos si la variable existe.
        if params_cursor:
            try:
                params_cursor.close()
            except Error as e: # Manejar posible error si la conexión ya está mal
                 logging.warning(f"Error menor al cerrar params_cursor: {e}")
        if select_cursor:
            try:
                select_cursor.close()
            except Error as e:
                 logging.warning(f"Error menor al cerrar select_cursor: {e}")
        if insert_cursor:
            try:
                insert_cursor.close()
            except Error as e:
                 logging.warning(f"Error menor al cerrar insert_cursor: {e}")

    return success, message # Devolver el estado final y el mensaje