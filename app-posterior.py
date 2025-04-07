import streamlit as st
import pandas as pd
import mysql.connector
import os
import plotly.express as px
from db_connection import connect_db # Tu módulo de conexión
from campaign_analyzer import get_campaign_simulation_data, generate_campaign_brief # Importa funciones clave
from datetime import datetime
import io
from price_updaters import update_insumo_prices, update_competitor_prices
from snapshot_creator import create_financial_snapshot
from db_connection import connect_db

# --- Configuración de Página ---
st.set_page_config(page_title="Análisis Financiero Platos", layout="wide")
st.title("📈 Análisis Financiero y Campañas")

# --- Conexión a BD (Cacheada para eficiencia) ---
@st.cache_resource # Cachea el recurso de conexión
def init_connection():
    conn = connect_db()
    if conn and conn.is_connected():
        return conn
    st.error("No se pudo conectar a la base de datos.")
    return None

conn = init_connection()

# --- Barra Lateral de Navegación ---
st.sidebar.title("Navegación")
app_mode = st.sidebar.selectbox(
    "Elige la sección:",
    ["Inicio", "Análisis de Campañas", "Historial Financiero"] # Añade otras secciones que tengas
)

# --- Lógica de la Página/Sección ---

if app_mode == "Inicio":
    st.header("Dashboard Principal")
    st.write("Bienvenido. Usa la barra lateral para navegar.")
    # Aquí podrías mostrar KPIs generales o un resumen

elif app_mode == "Historial Financiero":
    st.header("📊 Historial Financiero")
    if conn:
        # Aquí iría la lógica para mostrar datos de PLATOS_FINANCIALS_HISTORY
        # Ejemplo:
        # history_df = get_history_data(conn) # Necesitarías esta función
        # if not history_df.empty:
        #     st.dataframe(history_df)
        # else:
        #     st.warning("No hay datos históricos disponibles.")
        st.write("Funcionalidad de historial pendiente de implementar.") # Placeholder
    else:
        st.error("Conexión a BD no disponible.")


# --- SECCIÓN ANÁLISIS DE CAMPAÑAS ---
elif app_mode == "Análisis de Campañas":
    st.header("📢 Simulación y Análisis de Campañas")

    if not conn:
        st.error("Conexión a BD no disponible.")
        st.stop() # Detener si no hay conexión

    # --- Cargar Datos de Simulación (Cacheado) ---
    @st.cache_data(ttl=600) # Cachea los datos por 10 minutos
    def load_simulation_data():
        # Usamos '_conn' porque st.cache_data no puede hashear el objeto de conexión directamente
        _conn = init_connection() # Obtener conexión fresca dentro de la función cacheada si es necesario
        if _conn:
             df = get_campaign_simulation_data(_conn)
             #_conn.close() # Cerrar la conexión específica si se abrió aquí
             return df
        return pd.DataFrame()

    sim_df = load_simulation_data()

    if sim_df.empty:
        st.warning("No se pudieron cargar los datos de simulación o no hay campañas/platos elegibles.")
        st.stop() # Detener si no hay datos

    # --- Filtros Interactivos en la Barra Lateral ---
    st.sidebar.header("Filtros de Simulación")

    # Filtrar por Plataforma
    platforms = ['Todas'] + sorted(sim_df['PlatformName'].unique())
    selected_platform = st.sidebar.selectbox("Plataforma", platforms)

    # Filtrar por Campaña (depende de la plataforma seleccionada)
    available_campaigns = ['Todas']
    if selected_platform != 'Todas':
        available_campaigns += sorted(sim_df[sim_df['PlatformName'] == selected_platform]['CampaignName'].unique())
    else:
        available_campaigns += sorted(sim_df['CampaignName'].unique())
    selected_campaign = st.sidebar.selectbox("Campaña", available_campaigns)

    # Filtrar por Categoría de Plato
    categories = ['Todas'] + sorted(sim_df['Categoria_Plato'].unique())
    selected_category = st.sidebar.selectbox("Categoría Plato", categories)

    # Filtrar por Rentabilidad Mínima (%)
    min_margin_pct = st.sidebar.slider(
        "Margen Bruto Mínimo (%)",
        min_value=float(sim_df['Pct_Margen_Bruto_Campaign'].min()*100) if not sim_df.empty else -50.0,
        max_value=float(sim_df['Pct_Margen_Bruto_Campaign'].max()*100) if not sim_df.empty else 100.0,
        value=0.0, # Por defecto mostrar solo rentables
        step=1.0
    )

    # Checkbox para mostrar/ocultar conflictos de exclusividad
    # Asume que 'Exclusivity_Conflict' es una columna booleana añadida en analyze_campaigns
    # Si no la añadiste, puedes calcularla aquí o ignorar este filtro
    # show_conflicts = st.sidebar.checkbox("Mostrar Conflictos de Exclusividad", value=True)

    # --- Aplicar Filtros al DataFrame ---
    filtered_df = sim_df.copy()
    if selected_platform != 'Todas':
        filtered_df = filtered_df[filtered_df['PlatformName'] == selected_platform]
    if selected_campaign != 'Todas':
        filtered_df = filtered_df[filtered_df['CampaignName'] == selected_campaign]
    if selected_category != 'Todas':
        filtered_df = filtered_df[filtered_df['Categoria_Plato'] == selected_category]

    # Convertir slider % a decimal para comparar
    filtered_df = filtered_df[filtered_df['Pct_Margen_Bruto_Campaign'] >= (min_margin_pct / 100.0)]

    # if not show_conflicts and 'Exclusivity_Conflict' in filtered_df.columns:
    #     filtered_df = filtered_df[filtered_df['Exclusivity_Conflict'] == False]


    # --- Mostrar Tabla Filtrada ---
    st.subheader("Resultados de Simulación Filtrados")
    st.write(f"Mostrando {len(filtered_df)} combinaciones Plato-Campaña.")
    st.dataframe(filtered_df.sort_values(by='Pct_Margen_Bruto_Campaign', ascending=False))


    # --- Selección para el Brief ---
    st.subheader("Selección para el Brief")

    if not filtered_df.empty:
        # Crear identificadores únicos para la selección
        filtered_df['SelectionID'] = filtered_df['CampaignID'] + ' | ' + filtered_df['ID_Plato'] + ' (' + filtered_df['Nombre_Plato'] + ')'
        options = filtered_df['SelectionID'].tolist()

        selected_options = st.multiselect(
            "Selecciona las combinaciones Plato-Campaña para incluir en el brief:",
            options=options
        )

        # --- Generar Brief ---
        if st.button("Generar Brief"):
            if selected_options:
                # Obtener las filas completas correspondientes a las opciones seleccionadas
                final_selection_df = filtered_df[filtered_df['SelectionID'].isin(selected_options)]

                # Llamar a la función para generar el archivo (ej: CSV)
                output_filename = f"campaign_brief_{datetime.date.today()}.csv"
                try:
                    # Usar una función que devuelva los datos del archivo en lugar de guardarlo directamente
                    # o guardar y luego leer para el botón de descarga.
                    # Aquí asumimos que generate_campaign_brief puede guardar el archivo
                    generate_campaign_brief(final_selection_df, output_filename)

                    # Ofrecer descarga del archivo generado
                    with open(output_filename, "rb") as fp:
                         btn = st.download_button(
                             label="Descargar Brief Generado (CSV)",
                             data=fp,
                             file_name=output_filename,
                             mime="text/csv"
                         )
                    st.success(f"Brief generado como '{output_filename}'")

                except Exception as e:
                     st.error(f"Error al generar el brief: {e}")

            else:
                st.warning("Por favor, selecciona al menos una combinación para generar el brief.")
    else:
        st.info("No hay datos filtrados disponibles para seleccionar.")


# --- Cerrar Conexión (Opcional, depende de cómo manejes la conexión) ---
# if conn and conn.is_connected():
#    conn.close()
#    st.sidebar.info("Conexión cerrada.")