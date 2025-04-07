from mysql.connector import Error
import logging
import datetime

def create_financial_snapshot(conn):
    """Consulta la vista V_PLATOS_FINANCIALS y guarda el snapshot en HISTORY."""
    logging.info("Creando snapshot financiero...")
    try:
        cursor = conn.cursor(dictionary=True)

        # --- PASO 3: Leer parámetros actuales usados por la vista ---
        cursor.execute("SELECT market_discount, iva_rate, commission_rate FROM FINANCIAL_PARAMS WHERE param_id = 1;")
        params = cursor.fetchone()
        if not params:
            logging.error("No se encontraron parámetros financieros en FINANCIAL_PARAMS.")
            return False

        # --- PASO 4: Consultar la vista con los cálculos actuales ---
        select_cursor = conn.cursor(dictionary=True)
        query_vista = """
            SELECT
                vpc.*,
                p.Precio_Competencia
            FROM
                V_PLATOS_FINANCIALS vpc
            JOIN
                 PLATOS p ON vpc.ID_Plato = p.ID_Plato
            WHERE p.Precio_Competencia IS NOT NULL AND p.Precio_Competencia > 0;
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
            history_data.append((
                snapshot_timestamp,
                row['ID_Plato'],
                row.get('Costo_Plato'),
                row.get('Precio_Competencia'),
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
            insert_cursor = conn.cursor()
            insert_cursor.executemany(insert_sql, history_data)
            conn.commit()
            logging.info(f"Insertadas {insert_cursor.rowcount} filas en PLATOS_FINANCIALS_HISTORY.")
            insert_cursor.close()
        else:
            logging.info("No hay datos procesados para insertar en el historial.")
             
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