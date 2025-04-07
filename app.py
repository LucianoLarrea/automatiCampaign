import streamlit as st
import pandas as pd
import mysql.connector
import os
import plotly.express as px
from datetime import datetime, date # Asegurar importar date tambien
import io
import logging # Importar logging

# --- Importar módulos del proyecto ---
from price_updaters import update_insumo_prices, update_competitor_prices
from snapshot_creator import create_financial_snapshot
from db_connection import connect_db
# --- Importar módulos de campaña ---
from campaign_analyzer import get_campaign_simulation_data, analyze_campaigns_simplified, generate_campaign_brief

# --- Configuración de Logging (Opcional pero recomendado) ---
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuración de la página ---
st.set_page_config(page_title="Atomick - Finanzas y Campañas", layout="wide")

# --- Título y descripción ---
st.title("📈 Sistema Financiero y de Campañas Atomick")
# st.markdown("Actualiza precios, crea snapshots, visualiza historial y analiza campañas.")

# --- Crear conexión (Cacheada) ---
@st.cache_resource
def get_connection():
    conn = connect_db()
    # No mostrar error aquí, manejarlo donde se usa la conexión
    # if not (conn and conn.is_connected()):
    #    st.error("No se pudo conectar a la base de datos.")
    return conn

# --- Funciones auxiliares (si se necesitan) ---
def show_data_preview(df, title):
    st.subheader(title)
    if not df.empty:
        st.dataframe(df.head(20)) # Mostrar más filas quizás
    else:
        st.info(f"No hay datos para mostrar en '{title}'.")

# --- Barra Lateral de Navegación ---
st.sidebar.title("Navegación")
option = st.sidebar.radio(
    "Selecciona una opción:",
    ("Ver Datos Actuales", "Actualizar Precios", "Crear Snapshot", "Ver Historial", "Análisis de Campañas") # Opción añadida
)

# --- Placeholder para mensajes de estado ---
status_placeholder = st.empty()

# ==============================================================================
# --- SECCIÓN: Ver Datos Actuales ---
# ==============================================================================
if option == "Ver Datos Actuales":
    st.header("Visualización de Datos Actuales")
    conn = get_connection()
    if conn and conn.is_connected():
        try:
            # Selector de tablas/vistas a visualizar
            available_views = [
                "INSUMOS", "PLATOS", "CAMPAIGNS", "FINANCIAL_PARAMS",
                "V_PLATOS_COSTOS", "V_PLATOS_FINANCIALS", "V_CAMPAIGN_SIMULATION"
                # Añade otras tablas/vistas relevantes
            ]
            view_option = st.selectbox(
                "Selecciona una tabla o vista para visualizar:",
                available_views
            )

            if view_option:
                query = f"SELECT * FROM {view_option} LIMIT 500;" # Limitar por rendimiento
                df_view = pd.read_sql_query(query, conn)
                st.dataframe(df_view)
                st.caption(f"Mostrando hasta 500 filas de '{view_option}'.")

        except mysql.connector.Error as err:
            status_placeholder.error(f"Error de base de datos al cargar vista '{view_option}': {err}")
        except Exception as e:
            status_placeholder.error(f"Error inesperado al cargar vista '{view_option}': {e}")
        # finally:
            # Considera si cerrar la conexión aquí o mantenerla viva
            # if conn and conn.is_connected(): conn.close()
    else:
        status_placeholder.error("Error de conexión a la base de datos.")


# ==============================================================================
# --- SECCIÓN: Actualizar Precios ---
# ==============================================================================
elif option == "Actualizar Precios":
    st.header("Actualización de Precios Base")
    conn = get_connection()
    if not (conn and conn.is_connected()):
        status_placeholder.error("Error de conexión a la base de datos. No se pueden actualizar precios.")
    else:
        # --- Actualizar Insumos ---
        st.subheader("1. Actualizar Precios de Insumos desde CSV")
        uploaded_insumos_csv = st.file_uploader("Carga archivo CSV de insumos (nuevos_precios_insumos.csv)", type="csv")
        if uploaded_insumos_csv is not None:
            if st.button("Actualizar Precios de Insumos"):
                try:
                    # Leer el archivo subido directamente con pandas
                    df_insumos = pd.read_csv(uploaded_insumos_csv)
                    # Llamar a la función de actualización (asume que puede tomar un DataFrame)
                    # Necesitarías adaptar update_insumo_prices para aceptar un DataFrame
                    # O guardar el archivo temporalmente y pasar la ruta
                    # --- EJEMPLO: Guardando temporalmente ---
                    with open("temp_insumos.csv", "wb") as f:
                        f.write(uploaded_insumos_csv.getbuffer())
                    success, message = update_insumo_prices(conn, file_path="temp_insumos.csv") # Ajusta la función si es necesario
                    os.remove("temp_insumos.csv") # Limpiar archivo temporal
                    # --- FIN EJEMPLO ---

                    if success:
                        status_placeholder.success(message)
                    else:
                        status_placeholder.error(message)
                except Exception as e:
                    status_placeholder.error(f"Error procesando archivo de insumos: {e}")

        st.divider()

        # --- Actualizar Competencia ---
        st.subheader("2. Actualizar Precios de Competencia desde Excel/CSV")
        uploaded_competencia_xlsx = st.file_uploader("Carga archivo Excel/CSV de competencia (precios_competencia.xlsx)", type=["xlsx", "csv"])
        if uploaded_competencia_xlsx is not None:
             if st.button("Actualizar Precios de Competencia"):
                try:
                    # --- EJEMPLO: Guardando temporalmente ---
                    file_ext = uploaded_competencia_xlsx.name.split('.')[-1]
                    temp_comp_file = f"temp_competencia.{file_ext}"
                    with open(temp_comp_file, "wb") as f:
                        f.write(uploaded_competencia_xlsx.getbuffer())
                    # Asume que update_competitor_prices puede manejar la extensión o adaptar
                    success, message = update_competitor_prices(conn, file_path=temp_comp_file) # Ajusta la función si es necesario
                    os.remove(temp_comp_file) # Limpiar
                    # --- FIN EJEMPLO ---

                    if success:
                        status_placeholder.success(message)
                    else:
                        status_placeholder.error(message)
                except Exception as e:
                    status_placeholder.error(f"Error procesando archivo de competencia: {e}")

# ==============================================================================
# --- SECCIÓN: Crear Snapshot ---
# ==============================================================================
elif option == "Crear Snapshot":
    st.header("Crear Snapshot Financiero")
    st.write("Esto consultará los datos financieros actuales y los guardará en la tabla de historial.")
    conn = get_connection()
    if not (conn and conn.is_connected()):
        status_placeholder.error("Error de conexión a la base de datos. No se puede crear snapshot.")
    else:
        if st.button("Crear Snapshot Ahora"):
            try:
                # Llamar a la función del snapshot_creator
                success, message = create_financial_snapshot(conn)
                if success:
                    status_placeholder.success(message)
                else:
                    status_placeholder.error(message)
            except Exception as e:
                status_placeholder.error(f"Error inesperado al crear snapshot: {e}")

# ==============================================================================
# --- SECCIÓN: Ver Historial ---
# ==============================================================================
elif option == "Ver Historial":
    st.header("📊 Historial Financiero")
    conn = get_connection()
    if not (conn and conn.is_connected()):
        status_placeholder.error("Error de conexión a la base de datos.")
    else:
        try:
            # Cargar datos del historial
            query_history = "SELECT * FROM PLATOS_FINANCIALS_HISTORY ORDER BY SnapshotTimestamp DESC, ID_Plato;"
            df_history = pd.read_sql_query(query_history, conn)

            if df_history.empty:
                st.warning("No hay datos en el historial financiero.")
            else:
                st.write(f"Total de registros en el historial: {len(df_history)}")
                # Convertir timestamp a formato legible si es necesario
                if 'SnapshotTimestamp' in df_history.columns:
                   df_history['SnapshotTimestamp'] = pd.to_datetime(df_history['SnapshotTimestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')

                # --- Filtros para el historial ---
                st.subheader("Filtrar Historial")
                col1, col2 = st.columns(2)
                with col1:
                    platos_hist = ['Todos'] + sorted(df_history['ID_Plato'].unique())
                    selected_plato_hist = st.selectbox("Selecciona un Plato:", platos_hist, key="hist_plato_select")
                with col2:
                     # Asume que SnapshotTimestamp es string ahora
                    fechas_hist = ['Todas'] + sorted(pd.to_datetime(df_history['SnapshotTimestamp']).dt.date.unique(), reverse=True)
                    selected_fecha_hist = st.selectbox("Selecciona una Fecha (Snapshot):", fechas_hist, key="hist_fecha_select")

                # Aplicar filtros al DataFrame del historial
                filtered_history_df = df_history.copy()
                if selected_plato_hist != 'Todos':
                    filtered_history_df = filtered_history_df[filtered_history_df['ID_Plato'] == selected_plato_hist]
                if selected_fecha_hist != 'Todas':
                    # Convertir selected_fecha_hist (que es un objeto date) a string para comparar si es necesario, o comparar fechas
                     filtered_history_df = filtered_history_df[pd.to_datetime(filtered_history_df['SnapshotTimestamp']).dt.date == selected_fecha_hist]


                st.subheader("Datos Históricos Filtrados")
                st.dataframe(filtered_history_df)

                # --- Visualizaciones del Historial ---
                if not filtered_history_df.empty:
                    st.subheader("Visualizaciones (Basadas en datos filtrados)")
                    tab1, tab2 = st.tabs(["Margen Bruto % (Top 10 Último Snapshot)", "Costos vs Precios (Último Snapshot)"])

                    # Usar solo los datos del último snapshot disponible en el set filtrado para gráficos simples
                    last_snapshot_time = filtered_history_df['SnapshotTimestamp'].max()
                    df_last_snap = filtered_history_df[filtered_history_df['SnapshotTimestamp'] == last_snapshot_time]

                    with tab1:
                        if not df_last_snap.empty:
                            # Gráfico de margen bruto por plato
                            fig1 = px.bar(
                                df_last_snap.sort_values('Porcentaje_Margen_Bruto_PctMBA_Hist', ascending=False).head(10),
                                x='ID_Plato', # Usar Nombre_Plato si está disponible
                                y='Porcentaje_Margen_Bruto_PctMBA_Hist',
                                title=f"Top 10 Platos por Margen Bruto (%) - Snapshot {last_snapshot_time}",
                                labels={'Porcentaje_Margen_Bruto_PctMBA_Hist': 'Margen Bruto (%)', 'ID_Plato': 'Plato'},
                                color='Porcentaje_Margen_Bruto_PctMBA_Hist',
                                color_continuous_scale=px.colors.sequential.Blues,
                                text_auto='.1%' # Formato porcentaje
                            )
                            fig1.update_layout(yaxis_tickformat=".0%") # Formato eje Y
                            st.plotly_chart(fig1, use_container_width=True)
                        else:
                            st.info("No hay datos del último snapshot para graficar.")

                    with tab2:
                        if not df_last_snap.empty:
                            # Asegura que los tamaños no sean negativos (reemplaza negativos con 0)
                            df_last_snap['Size_For_Plot'] = df_last_snap['Margen_Bruto_Actual_MBA_Hist'].clip(lower=0)
                           # Gráfico de costos vs precios
                            fig2 = px.scatter(
                                df_last_snap,
                                x='Costo_Plato_Hist', y='Precio_Competencia_Hist',
                                hover_name='ID_Plato', # Usar Nombre_Plato si está disponible
                                size='Size_For_Plot', # Tamaño por margen absoluto
                                color='Porcentaje_Margen_Bruto_PctMBA_Hist', # Color por margen %
                                color_continuous_scale=px.colors.sequential.Viridis,
                                title=f"Relación Costo vs Precio Competencia - Snapshot {last_snapshot_time}",
                                labels={
                                    'Costo_Plato_Hist': 'Costo del Plato ($)',
                                    'Precio_Competencia_Hist': 'Precio de Competencia ($)',
                                    'Size_For_Plot': 'Margen Bruto ($) (Tamaño >= 0)', # Etiqueta actualizada
                                    'Porcentaje_Margen_Bruto_PctMBA_Hist': 'Margen Bruto (%)'
                                }
                            )
                            fig2.update_layout(coloraxis_colorbar_tickformat=".0%") # Formato barra color
                            st.plotly_chart(fig2, use_container_width=True)
                        else:
                            st.info("No hay datos del último snapshot para graficar.")

        except mysql.connector.Error as err:
            status_placeholder.error(f"Error de base de datos al cargar historial: {err}")
        except Exception as e:
            status_placeholder.error(f"Error inesperado al cargar historial: {e}")

# ==============================================================================
# --- SECCIÓN: Análisis de Campañas ---
# ==============================================================================
elif option == "Análisis de Campañas":
    st.header("📢 Simulación y Análisis de Campañas")
    conn = get_connection()
    if not (conn and conn.is_connected()):
        status_placeholder.error("Error de conexión a la base de datos.")
    else:
        # --- Cargar Datos de Simulación (Cacheado) ---
        @st.cache_data(ttl=300) # Cachear por 5 minutos
        def load_simulation_data_cached():
            _conn = get_connection() # Re-obtener conexión dentro de función cacheada
            if _conn:
                df = get_campaign_simulation_data(_conn)
                # Aplicar análisis simplificado para obtener flag de conflicto
                df_analyzed = analyze_campaigns_simplified(df)
                return df_analyzed
            return pd.DataFrame()

        sim_df_analyzed = load_simulation_data_cached()

        if sim_df_analyzed.empty:
            st.warning("No se pudieron cargar los datos de simulación o no hay campañas/platos elegibles.")
        else:
            # --- Filtros Interactivos (en área principal) ---
            with st.expander("Filtros de Simulación", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    platforms = ['Todas'] + sorted(sim_df_analyzed['PlatformName'].unique())
                    selected_platform = st.selectbox("Plataforma", platforms, key="camp_platform")
                with col2:
                    available_campaigns = ['Todas']
                    temp_df = sim_df_analyzed
                    if selected_platform != 'Todas':
                         temp_df = sim_df_analyzed[sim_df_analyzed['PlatformName'] == selected_platform]
                    available_campaigns += sorted(temp_df['CampaignName'].unique())
                    selected_campaign = st.selectbox("Campaña", available_campaigns, key="camp_campaign")
                with col3:
                    categories = ['Todas'] + sorted(sim_df_analyzed['Categoria_Plato'].unique())
                    selected_category = st.selectbox("Categoría Plato", categories, key="camp_category")

                min_margin_pct = st.slider(
                    "Margen Bruto Mínimo Aceptable (%)",
                     min_value=float(sim_df_analyzed['Pct_Margen_Bruto_Campaign'].min()*100) if not sim_df_analyzed.empty else -100.0,
                     max_value=float(sim_df_analyzed['Pct_Margen_Bruto_Campaign'].max()*100) if not sim_df_analyzed.empty else 100.0,
                     value=0.0, # Por defecto mostrar solo rentables >= 0%
                     step=1.0,
                     key="camp_margin_slider"
                )
                show_conflicts_filter = st.checkbox("Mostrar Solo Conflictos de Exclusividad", value=False, key="camp_conflict_check")


            # --- Aplicar Filtros al DataFrame ---
            filtered_sim_df = sim_df_analyzed.copy()
            if selected_platform != 'Todas':
                filtered_sim_df = filtered_sim_df[filtered_sim_df['PlatformName'] == selected_platform]
            if selected_campaign != 'Todas':
                filtered_sim_df = filtered_sim_df[filtered_sim_df['CampaignName'] == selected_campaign]
            if selected_category != 'Todas':
                filtered_sim_df = filtered_sim_df[filtered_sim_df['Categoria_Plato'] == selected_category]

            filtered_sim_df = filtered_sim_df[filtered_sim_df['Pct_Margen_Bruto_Campaign'] >= (min_margin_pct / 100.0)]

            if show_conflicts_filter and 'Exclusivity_Conflict' in filtered_sim_df.columns:
                 filtered_sim_df = filtered_sim_df[filtered_sim_df['Exclusivity_Conflict'] == True]

            # --- Mostrar Tabla Filtrada ---
            st.subheader("Resultados de Simulación Filtrados")
            st.write(f"Mostrando {len(filtered_sim_df)} combinaciones Plato-Campaña.")
            # Usar st.data_editor para posible selección futura o simplemente dataframe
            st.dataframe(
                filtered_sim_df.sort_values(by='Pct_Margen_Bruto_Campaign', ascending=False),
                use_container_width=True
                # Puedes añadir configuración de columnas aquí si quieres formatear números, etc.
            )
            # Alerta visual si hay conflictos en los datos mostrados
            if 'Exclusivity_Conflict' in filtered_sim_df.columns and filtered_sim_df['Exclusivity_Conflict'].any():
                 st.info("⚠️ Algunos platos mostrados tienen conflictos de exclusividad (participan en campaña Exclusiva y No Exclusiva). Revise antes de generar el brief.")


            # --- Selección para el Brief ---
            st.subheader("Selección para Generar Brief")
            st.markdown("Selecciona las combinaciones deseadas de la tabla de arriba y usa el multiselect para confirmar tu selección para el brief.")

            if not filtered_sim_df.empty:
                # Crear identificadores únicos para la selección
                # Asegurar que las columnas existen antes de crear el ID
                if {'CampaignID', 'ID_Plato', 'Nombre_Plato'}.issubset(filtered_sim_df.columns):
                    filtered_sim_df['SelectionID'] = filtered_sim_df['CampaignID'] + ' | ' + filtered_sim_df['ID_Plato'] + ' (' + filtered_sim_df['Nombre_Plato'] + ')'
                    options = sorted(filtered_sim_df['SelectionID'].tolist())

                    selected_options = st.multiselect(
                        "Confirmar Selección para Brief:",
                        options=options,
                        key="camp_brief_select"
                    )

                    # --- Generar Brief ---
                    if st.button("Generar Brief de Campaña", key="camp_brief_button"):
                        if selected_options:
                            # Obtener las filas completas correspondientes a las opciones seleccionadas
                            final_selection_df = filtered_sim_df[filtered_sim_df['SelectionID'].isin(selected_options)].copy() # Usar .copy()

                            output_filename = f"campaign_brief_{date.today()}.csv"
                            try:
                                # Llamar a la función para generar el archivo CSV
                                success, message = generate_campaign_brief(final_selection_df, output_filename)

                                if success:
                                    # Ofrecer descarga del archivo generado
                                    with open(output_filename, "rb") as fp:
                                        st.download_button(
                                            label="Descargar Brief Generado (CSV)",
                                            data=fp,
                                            file_name=output_filename,
                                            mime="text/csv"
                                        )
                                    status_placeholder.success(f"Brief generado como '{output_filename}'.")
                                else:
                                     status_placeholder.error(message)

                            except Exception as e:
                                status_placeholder.error(f"Error al generar o descargar el brief: {e}")
                        else:
                            status_placeholder.warning("Por favor, selecciona al menos una combinación para generar el brief.")
                else:
                    st.error("Faltan columnas requeridas (CampaignID, ID_Plato, Nombre_Plato) en los datos filtrados para la selección del brief.")
            else:
                st.info("No hay datos filtrados disponibles para seleccionar.")

# --- Considerar cerrar la conexión al final si no se usa cache_resource ---
# conn = get_connection()
# if conn and conn.is_connected():
#    conn.close()