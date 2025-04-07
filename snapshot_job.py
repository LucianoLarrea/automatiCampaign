# snapshot_job.py (Versión Modificada)
from dotenv import load_dotenv
load_dotenv() # Carga variables desde .env al entorno
import argparse
import datetime
import logging
import os
import db_connection
import price_updaters
import snapshot_creator
import sys # Para salir si falla la conexión

# --- Configuración de Logging ---
log_file = 'snapshot_job.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler() # También mostrar en consola
    ]
)

# --- Leer Configuración Externa (Rutas desde Variables de Entorno) ---
# Define rutas por defecto que pueden ser sobrescritas por Env Vars o Argparse
DEFAULT_INSUMOS_CSV = os.getenv('INSUMOS_CSV_PATH', 'nuevos_precios_insumos.csv')
DEFAULT_COMPETENCIA_XLSX = os.getenv('COMPETENCIA_FILE_PATH', 'precios_competencia.xlsx')


def run_job(args):
    """Función principal que ejecuta las tareas."""
    logging.info("===== Iniciando Job de Actualización y Snapshot =====")
    connection = None

    # Determinar rutas de archivo finales
    insumos_file = args.insumos_file if args.insumos_file else DEFAULT_INSUMOS_CSV
    competencia_file = args.competencia_file if args.competencia_file else DEFAULT_COMPETENCIA_XLSX

    try:
        connection = db_connection.connect_db()
        if not (connection and connection.is_connected()):
            logging.critical("FALLO CRÍTICO: No se pudo establecer conexión con la base de datos. Abortando.")
            sys.exit(1) # Salir con código de error

        # --- Ejecutar Pasos Solicitados ---
        tasks_to_run = {
            "insumos": args.run_all or args.update_insumos,
            "competencia": args.run_all or args.update_competencia,
            "snapshot": args.run_all or args.create_snapshot
        }
        results = {}

        if tasks_to_run["insumos"]:
            logging.info(f"--- Iniciando: Actualización precios insumos ({insumos_file}) ---")
            success, msg = price_updaters.update_insumo_prices(connection, file_path=insumos_file)
            results["insumos"] = {"success": success, "message": msg}
            if success: logging.info(f"--- Finalizado: Actualización insumos - {msg} ---")
            else: logging.error(f"--- FALLO: Actualización insumos - {msg} ---")

        if tasks_to_run["competencia"]:
            logging.info(f"--- Iniciando: Actualización precios competencia ({competencia_file}) ---")
            success, msg = price_updaters.update_competitor_prices(connection, file_path=competencia_file)
            results["competencia"] = {"success": success, "message": msg}
            if success: logging.info(f"--- Finalizado: Actualización competencia - {msg} ---")
            else: logging.error(f"--- FALLO: Actualización competencia - {msg} ---")

        if tasks_to_run["snapshot"]:
            logging.info("--- Iniciando: Creación de snapshot financiero ---")
            success, msg = snapshot_creator.create_financial_snapshot(connection)
            results["snapshot"] = {"success": success, "message": msg}
            if success: logging.info(f"--- Finalizado: Creación snapshot - {msg} ---")
            else: logging.error(f"--- FALLO: Creación snapshot - {msg} ---")

        # --- Resumen Final ---
        all_success = all(res["success"] for task, res in results.items() if tasks_to_run[task])
        if all_success:
            logging.info("Todas las tareas solicitadas se completaron exitosamente.")
        else:
            logging.warning("Al menos una tarea falló. Revise los logs.")

    except Exception as e:
        logging.error(f"Error inesperado en la ejecución del job: {e}", exc_info=True)
        # Asegurar que salga con error si hay excepción no manejada
        sys.exit(1)
    finally:
        if connection and connection.is_connected():
            connection.close()
            logging.info("Conexión a MySQL cerrada.")

    logging.info("===== Job de Actualización y Snapshot Finalizado =====")

    # Salir con código 0 si todo OK, 1 si algo falló (útil para schedulers)
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Actualiza precios de insumos/competencia y crea snapshots financieros.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Muestra defaults en ayuda
    )

    # Argumentos para rutas de archivo (sobrescriben Env Vars/Defaults)
    parser.add_argument(
        '--insumos-file',
        type=str,
        default=DEFAULT_INSUMOS_CSV,
        help='Ruta al archivo CSV de precios de insumos.'
    )
    parser.add_argument(
        '--competencia-file',
        type=str,
        default=DEFAULT_COMPETENCIA_XLSX,
        help='Ruta al archivo Excel/CSV de precios de competencia.'
    )

    # Argumentos para controlar qué pasos ejecutar
    parser.add_argument(
        '--update-insumos',
        action='store_true',
        help='Ejecutar solo la actualización de precios de insumos.'
    )
    parser.add_argument(
        '--update-competencia',
        action='store_true',
        help='Ejecutar solo la actualización de precios de competencia.'
    )
    parser.add_argument(
        '--create-snapshot',
        action='store_true',
        help='Ejecutar solo la creación del snapshot.'
    )

    args = parser.parse_args()

    # Determinar si ejecutar todos los pasos (si no se especifica uno concreto)
    args.run_all = not (args.update_insumos or args.update_competencia or args.create_snapshot)

    # Llamar a la función principal
    run_job(args)