import pandas as pd
from db_connection import connect_db # Asumiendo que tienes esta función en db_connection.py
import logging

def get_campaign_simulation_data(conn):
    """Obtiene los datos de simulación de la vista V_CAMPAIGN_SIMULATION."""
    logging.info("Obteniendo datos de simulación de campañas...")
    try:
        # Usar pandas para leer directamente la query en un DataFrame
        query = "SELECT * FROM V_CAMPAIGN_SIMULATION;"
        df = pd.read_sql_query(query, conn)
        logging.info(f"Se obtuvieron {len(df)} filas de la simulación.")
        return df
    except Exception as e:
        logging.error(f"Error al obtener datos de simulación: {e}")
        return pd.DataFrame() # Devolver DataFrame vacío en caso de error

def analyze_campaigns(simulation_df):
    """Analiza el DataFrame de simulación para ayudar a la decisión."""
    if simulation_df.empty:
        logging.warning("DataFrame de simulación vacío, no se puede analizar.")
        return pd.DataFrame()

    logging.info("Analizando rentabilidad de campañas...")

    # 1. Filtrar márgenes negativos (opcional, podrías querer verlos)
    profitable_df = simulation_df[simulation_df['Margen_Bruto_Campaign'] > 0].copy()
    logging.info(f"{len(profitable_df)} opciones rentables encontradas.")

    # 2. Ordenar por rentabilidad (ej: % Margen)
    profitable_df = profitable_df.sort_values(by='Pct_Margen_Bruto_Campaign', ascending=False)

    # 3. Manejo de Exclusividad (Ejemplo simple: Marcar conflictos)
    # Encuentra platos que están en campañas exclusivas Y otras campañas
    exclusive_options = profitable_df[profitable_df['IsExclusive'] == True]
    non_exclusive_options = profitable_df[profitable_df['IsExclusive'] == False]

    conflicting_platos = pd.merge(
        exclusive_options[['ID_Plato']].drop_duplicates(),
        non_exclusive_options[['ID_Plato']].drop_duplicates(),
        on='ID_Plato'
    )['ID_Plato'].unique()

    profitable_df['Exclusivity_Conflict'] = profitable_df['ID_Plato'].isin(conflicting_platos)
    if len(conflicting_platos) > 0:
         logging.warning(f"Platos con conflictos de exclusividad detectados: {list(conflicting_platos)}")
         # Aquí podrías decidir eliminar las opciones no exclusivas para esos platos,
         # o simplemente dejar la marca 'Exclusivity_Conflict' para revisión manual.
         # Ejemplo: Priorizar la exclusiva (eliminar no exclusivas para platos en conflicto)
         # profitable_df = profitable_df[~(profitable_df['ID_Plato'].isin(conflicting_platos) & (profitable_df['IsExclusive'] == False))]


    # Podrías añadir más lógica aquí (ej: top N por plataforma, etc.)

    logging.info("Análisis de campañas completado.")
    return profitable_df # Devolver el DF analizado

def analyze_campaigns_simplified(simulation_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analiza el DataFrame de simulación para añadir una marca de conflicto
    si un plato está en una campaña exclusiva y también en otras.

    Args:
        simulation_df: DataFrame con los datos de V_CAMPAIGN_SIMULATION.
                       Debe contener 'ID_Plato' y 'IsExclusive'.

    Returns:
        El mismo DataFrame con una columna adicional 'Exclusivity_Conflict' (boolean).
    """
    if simulation_df.empty:
        logging.warning("DataFrame de simulación vacío en analyze_campaigns_simplified.")
        # Añadir columna vacía para consistencia si no existe
        if 'Exclusivity_Conflict' not in simulation_df.columns:
            simulation_df['Exclusivity_Conflict'] = False
        return simulation_df

    # Asegurarse de que las columnas necesarias existen
    if 'ID_Plato' not in simulation_df.columns or 'IsExclusive' not in simulation_df.columns:
        logging.error("Faltan las columnas 'ID_Plato' o 'IsExclusive' en el DataFrame.")
        # Añadir columna vacía para consistencia si no existe
        if 'Exclusivity_Conflict' not in simulation_df.columns:
            simulation_df['Exclusivity_Conflict'] = False
        return simulation_df

    logging.info("Identificando conflictos de exclusividad...")
    analyzed_df = simulation_df.copy() # Trabajar sobre una copia

    # Platos que están en al menos una campaña exclusiva
    exclusive_platos = set(analyzed_df.loc[analyzed_df['IsExclusive'] == True, 'ID_Plato'].unique())

    # Platos que están en al menos una campaña NO exclusiva
    non_exclusive_platos = set(analyzed_df.loc[analyzed_df['IsExclusive'] == False, 'ID_Plato'].unique())

    # Platos que están en AMBOS grupos (el conflicto)
    conflicting_platos = exclusive_platos.intersection(non_exclusive_platos)

    # Marcar TODAS las filas correspondientes a platos en conflicto
    analyzed_df['Exclusivity_Conflict'] = analyzed_df['ID_Plato'].isin(conflicting_platos)

    if conflicting_platos:
        logging.warning(f"Detectados {len(conflicting_platos)} platos con conflicto de exclusividad.")
    else:
        logging.info("No se detectaron conflictos de exclusividad.")

    return analyzed_df

# --- Ejemplo de cómo la usarías en app.py ---
# import campaign_analyzer
# ... obtener connection ...
# sim_data_raw = campaign_analyzer.get_campaign_simulation_data(connection)
# sim_data_analyzed = campaign_analyzer.analyze_campaigns_simplified(sim_data_raw)
# ... ahora usa sim_data_analyzed en Streamlit para filtrar, ordenar y mostrar ...
# ... la columna 'Exclusivity_Conflict' te sirve para destacar filas o filtrar ...

def generate_campaign_brief(selected_df, output_file='campaign_brief.csv'):
    """Genera un archivo CSV con el brief de campaña."""
    if selected_df.empty:
        logging.warning("No hay campañas seleccionadas para generar el brief.")
        return

    logging.info(f"Generando brief de campaña en {output_file}...")
    try:
        brief_columns = [
            'PlatformName', 'CampaignName', 'ID_Plato', 'Nombre_Plato',
            'Precio_Bruto_Campaign' # Precio final a publicar
            # Puedes añadir más columnas si son útiles para el brief
        ]
        brief_df = selected_df[brief_columns].copy()
        brief_df.rename(columns={'Precio_Bruto_Campaign': 'Precio_Final_Publicar'}, inplace=True)
        brief_df.to_csv(output_file, index=False)
        logging.info("Brief de campaña generado exitosamente.")
    except Exception as e:
        logging.error(f"Error al generar el brief de campaña: {e}")

# --- Ejemplo de cómo usarlo en run_campaign_analysis.py ---
# if __name__ == "__main__":
#     connection = connect_db()
#     if connection and connection.is_connected():
#         sim_data = get_campaign_simulation_data(connection)
#         analyzed_data = analyze_campaigns(sim_data)
#
#         # Aquí, en un escenario real, podrías presentar 'analyzed_data' al usuario
#         # o aplicar reglas automáticas para obtener 'final_selection_df'
#         # Por ahora, asumimos que todo lo analizado y rentable es la selección final
#         final_selection_df = analyzed_data[analyzed_data['Exclusivity_Conflict'] == False] # Ejemplo simple
#
#         generate_campaign_brief(final_selection_df)
#
#         connection.close()