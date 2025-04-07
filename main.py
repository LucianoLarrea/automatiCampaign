import logging
from db_connection import connect_db
from price_updaters import update_insumo_prices, update_competitor_prices
from snapshot_creator import create_financial_snapshot

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, filename='snapshot_job.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Flujo Principal del Script ---
if __name__ == "__main__":
    logging.info("===== Iniciando Job de Actualización y Snapshot =====")
    connection = connect_db()

    if connection and connection.is_connected():
        # Ejecutar actualizaciones primero
        insumos_ok = update_insumo_prices(connection)
        competencia_ok = update_competitor_prices(connection)

        # Si las actualizaciones fueron bien (o si decides continuar aunque fallen)
        if insumos_ok and competencia_ok:
            snapshot_ok = create_financial_snapshot(connection)
        else:
            logging.warning("Saltando snapshot debido a errores en la actualización de precios.")

        # Cerrar conexión
        connection.close()
        logging.info("Conexión a MySQL cerrada.")
    else:
        logging.error("No se pudo establecer conexión con la base de datos. Abortando.")

    logging.info("===== Job de Actualización y Snapshot Finalizado =====")