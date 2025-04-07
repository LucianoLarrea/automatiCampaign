import streamlit as st
import pandas as pd
import mysql.connector
import os
import plotly.express as px
from datetime import datetime, date # Asegurar importar date tambien
import io
import logging # Importar logging
from textwrap import dedent # Para prompts multilínea

# --- Importar módulos del proyecto ---
# Asumiendo que están en el mismo directorio o PYTHONPATH
from price_updaters import update_insumo_prices, update_competitor_prices
from snapshot_creator import create_financial_snapshot # Asume que devuelve (bool, str)
from db_connection import connect_db # Asume que devuelve conexión o None
# --- Importar módulos de campaña y LLM ---
from campaign_analyzer import get_campaign_simulation_data, analyze_campaigns_simplified, generate_campaign_brief # Asumen que devuelven (bool, str/data) o DataFrame
import LLM_integrator # Importa tu nuevo módulo
import google.generativeai as genai # Necesario para el manejo del modelo

# --- Configuración de Logging (Opcional pero recomendado) ---
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuración de la página ---
st.set_page_config(page_title="Atomick - Finanzas y Campañas", layout="wide")

# --- Título y descripción ---
st.title("📈 Sistema Financiero y de Campañas Atomick")

# --- Inicializar Session State ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [] # Lista de {"role": "user/assistant", "content": "..."}
if 'campaign_results' not in st.session_state:
    st.session_state.campaign_results = None # DataFrame con resultados filtrados de campañas
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = None # Objeto del modelo Gemini inicializado

# --- Crear conexión (Cacheada) ---
@st.cache_resource
def get_connection():
    conn = connect_db()
    return conn

# --- Funciones auxiliares (si se necesitan) ---
def show_data_preview(df, title):
    st.subheader(title)
    if df is not None and not df.empty:
        st.dataframe(df.head(20)) # Mostrar más filas quizás
    else:
        st.info(f"No hay datos para mostrar en '{title}'.")

# --- Barra Lateral de Navegación ---
st.sidebar.title("Navegación")
option = st.sidebar.radio(
    "Selecciona una opción:",
    ("Ver Datos Actuales", "Actualizar Precios", "Crear Snapshot", "Ver Historial", "Análisis de Campañas", "Chat con Asistente") # Opción añadida
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
            available_views = [
                "INSUMOS", "PLATOS", "CAMPAIGNS", "FINANCIAL_PARAMS",
                "V_PLATOS_COSTOS", "V_PLATOS_FINANCIALS", "V_CAMPAIGN_SIMULATION",
                "PLATOS_FINANCIALS_HISTORY" # Añadido historial aquí también
            ]
            view_option = st.selectbox(
                "Selecciona una tabla o vista para visualizar:",
                available_views
            )

            if view_option:
                query = f"SELECT * FROM {view_option} LIMIT 500;"
                df_view = pd.read_sql_query(query, conn) # Advertencia Pandas aquí
                st.dataframe(df_view, use_container_width=True)
                st.caption(f"Mostrando hasta 500 filas de '{view_option}'.")

        except mysql.connector.Error as err:
            status_placeholder.error(f"Error de base de datos al cargar vista '{view_option}': {err}")
        except Exception as e:
            status_placeholder.error(f"Error inesperado al cargar vista '{view_option}': {e}")
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
        uploaded_insumos_csv = st.file_uploader("Carga archivo CSV de insumos (nuevos_precios_insumos.csv)", type="csv", key="ins_upload")
        if uploaded_insumos_csv is not None:
            if st.button("Actualizar Precios de Insumos", key="ins_update_btn"):
                with st.spinner("Actualizando precios de insumos..."):
                    try:
                        # Guardar temporalmente y pasar ruta (o adaptar función)
                        with open("temp_insumos.csv", "wb") as f:
                            f.write(uploaded_insumos_csv.getbuffer())
                        # Asume que la función devuelve (bool, message)
                        success, message = update_insumo_prices(conn, file_path="temp_insumos.csv")
                        os.remove("temp_insumos.csv")
                        if success:
                            status_placeholder.success(message)
                        else:
                            status_placeholder.error(message)
                    except Exception as e:
                        status_placeholder.error(f"Error procesando archivo de insumos: {e}")

        st.divider()

        # --- Actualizar Competencia ---
        st.subheader("2. Actualizar Precios de Competencia desde Excel/CSV")
        uploaded_competencia = st.file_uploader("Carga archivo Excel/CSV de competencia (precios_competencia.xlsx/csv)", type=["xlsx", "csv"], key="comp_upload")
        if uploaded_competencia is not None:
             if st.button("Actualizar Precios de Competencia", key="comp_update_btn"):
                with st.spinner("Actualizando precios de competencia..."):
                    try:
                        # Guardar temporalmente y pasar ruta (o adaptar función)
                        file_ext = uploaded_competencia.name.split('.')[-1]
                        temp_comp_file = f"temp_competencia.{file_ext}"
                        with open(temp_comp_file, "wb") as f:
                            f.write(uploaded_competencia.getbuffer())
                        success, message = update_competitor_prices(conn, file_path=temp_comp_file)
                        os.remove(temp_comp_file)
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
    st.write("Esto consultará los datos financieros actuales (basados en V_PLATOS_FINANCIALS) y los guardará en la tabla de historial (`PLATOS_FINANCIALS_HISTORY`).")
    conn = get_connection()
    if not (conn and conn.is_connected()):
        status_placeholder.error("Error de conexión a la base de datos. No se puede crear snapshot.")
    else:
        if st.button("Crear Snapshot Ahora", key="snap_create_btn"):
            with st.spinner("Creando snapshot..."):
                try:
                    success, message = create_financial_snapshot(conn) # Asume que devuelve (bool, message)
                    if success:
                        status_placeholder.success(message)
                        # Limpiar caché de historial si es relevante
                        # load_history_data_cached.clear()
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
        # --- Cargar Datos Históricos (Cacheado) ---
        @st.cache_data(ttl=600) # Cachear por 10 mins
        def load_history_data_cached():
            _conn = get_connection()
            if _conn:
                # Incluir Nombre_Plato en la consulta
                query = """
                    SELECT
                        h.*, p.Nombre_Plato
                    FROM PLATOS_FINANCIALS_HISTORY h
                    LEFT JOIN PLATOS p ON h.ID_Plato = p.ID_Plato
                    ORDER BY h.SnapshotTimestamp DESC, h.ID_Plato;
                """
                try:
                    df = pd.read_sql_query(query, _conn) # Advertencia Pandas aquí
                    # Convertir timestamp a datetime y formatear
                    if 'SnapshotTimestamp' in df.columns:
                        df['SnapshotTimestampDT'] = pd.to_datetime(df['SnapshotTimestamp'])
                        df['SnapshotDate'] = df['SnapshotTimestampDT'].dt.date
                    return df
                except Exception as e:
                    st.error(f"Error al cargar historial: {e}")
                    return pd.DataFrame()
            return pd.DataFrame()

        df_history = load_history_data_cached()

        if df_history.empty:
            st.warning("No hay datos en el historial financiero.")
        else:
            st.write(f"Total de registros en el historial: {len(df_history)}")

            # --- Filtros para el historial ---
            st.subheader("Filtrar Historial")
            col1, col2 = st.columns(2)
            with col1:
                platos_hist = ['Todos'] + sorted(df_history['ID_Plato'].unique())
                selected_plato_hist = st.selectbox("Selecciona un Plato:", platos_hist, key="hist_plato_select")
            with col2:
                fechas_hist = ['Todas'] + sorted(df_history['SnapshotDate'].unique(), reverse=True)
                selected_fecha_hist = st.selectbox("Selecciona una Fecha (Snapshot):", fechas_hist, key="hist_fecha_select")

            # Aplicar filtros al DataFrame del historial
            filtered_history_df = df_history.copy()
            if selected_plato_hist != 'Todos':
                filtered_history_df = filtered_history_df[filtered_history_df['ID_Plato'] == selected_plato_hist]
            if selected_fecha_hist != 'Todas':
                filtered_history_df = filtered_history_df[filtered_history_df['SnapshotDate'] == selected_fecha_hist]


            st.subheader("Datos Históricos Filtrados")
            # Mostrar Timestamp formateado
            display_cols_hist = [col for col in filtered_history_df.columns if col not in ['SnapshotTimestampDT', 'SnapshotDate']]
            # Reordenar columnas si Nombre_Plato existe
            if 'Nombre_Plato' in display_cols_hist:
                 id_idx = display_cols_hist.index('ID_Plato')
                 display_cols_hist.insert(id_idx + 1, display_cols_hist.pop(display_cols_hist.index('Nombre_Plato')))
            st.dataframe(filtered_history_df[display_cols_hist])

            # --- Visualizaciones del Historial ---
            if not filtered_history_df.empty:
                st.subheader("Visualizaciones (Basadas en datos filtrados)")
                # Usar solo los datos del último snapshot disponible en el set filtrado
                if not filtered_history_df.empty:
                    last_snapshot_time_dt = filtered_history_df['SnapshotTimestampDT'].max()
                    df_last_snap = filtered_history_df[filtered_history_df['SnapshotTimestampDT'] == last_snapshot_time_dt].copy() # Usar .copy()
                    last_snapshot_time_str = last_snapshot_time_dt.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(last_snapshot_time_dt) else "N/A"

                    # Asegurar Nombre_Plato para graficos (usar ID si falta)
                    df_last_snap['Plot_Label'] = df_last_snap['Nombre_Plato'].fillna(df_last_snap['ID_Plato'])


                    tab1, tab2 = st.tabs(["Margen Bruto %", "Costos vs Precios"])

                    with tab1:
                        if not df_last_snap.empty:
                            fig1 = px.bar(
                                df_last_snap.sort_values('Porcentaje_Margen_Bruto_PctMBA_Hist', ascending=False).head(15), # Mostrar más?
                                x='Plot_Label', # Usar etiqueta combinada
                                y='Porcentaje_Margen_Bruto_PctMBA_Hist',
                                title=f"Top Platos por Margen Bruto (%) - Snapshot {last_snapshot_time_str}",
                                labels={'Porcentaje_Margen_Bruto_PctMBA_Hist': 'Margen Bruto (%)', 'Plot_Label': 'Plato'},
                                color='Porcentaje_Margen_Bruto_PctMBA_Hist',
                                color_continuous_scale=px.colors.sequential.Blues_r, # Invertido
                                text_auto='.1%'
                            )
                            fig1.update_layout(yaxis_tickformat=".0%")
                            st.plotly_chart(fig1, use_container_width=True)
                        else: st.info("No hay datos del último snapshot filtrado para graficar.")

                    with tab2:
                        if not df_last_snap.empty:
                            # Ajuste para tamaño no negativo
                            df_last_snap['Size_For_Plot'] = df_last_snap['Margen_Bruto_Actual_MBA_Hist'].clip(lower=0).fillna(0) # Asegura no negativos y no NaN

                            fig2 = px.scatter(
                                df_last_snap,
                                x='Costo_Plato_Hist', y='Precio_Competencia_Hist',
                                hover_name='Plot_Label', # Usar etiqueta combinada
                                size='Size_For_Plot', # Usar tamaño ajustado
                                color='Porcentaje_Margen_Bruto_PctMBA_Hist',
                                color_continuous_scale=px.colors.sequential.Viridis,
                                title=f"Relación Costo vs Precio Competencia - Snapshot {last_snapshot_time_str}",
                                labels={
                                    'Costo_Plato_Hist': 'Costo del Plato ($)',
                                    'Precio_Competencia_Hist': 'Precio de Competencia ($)',
                                    'Size_For_Plot': 'Margen Bruto ($) (Tamaño >= 0)', # Etiqueta actualizada
                                    'Porcentaje_Margen_Bruto_PctMBA_Hist': 'Margen Bruto (%)',
                                    'Plot_Label': 'Plato'
                                }
                            )
                            fig2.update_layout(coloraxis_colorbar_tickformat=".0%")
                            st.plotly_chart(fig2, use_container_width=True)
                        else: st.info("No hay datos del último snapshot filtrado para graficar.")
                else:
                    st.info("No hay datos históricos filtrados para visualizar.")

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
            _conn = get_connection()
            if _conn:
                df = get_campaign_simulation_data(_conn) # Llama a la función del analyzer
                if df is not None and not df.empty:
                    # Aplicar análisis simplificado para obtener flag de conflicto
                    df_analyzed = analyze_campaigns_simplified(df) # Llama a la función del analyzer
                    return df_analyzed
                else:
                    logging.warning("get_campaign_simulation_data devolvió vacío o None.")
                    return pd.DataFrame() # Devolver vacío si falla la carga
            logging.error("No se pudo obtener conexión en load_simulation_data_cached.")
            return pd.DataFrame()

        sim_df_analyzed = load_simulation_data_cached()

        if sim_df_analyzed.empty:
            st.warning("No se pudieron cargar los datos de simulación o no hay campañas/platos elegibles.")
        else:
            # --- Filtros Interactivos (en área principal) ---
            with st.expander("Filtros de Simulación", expanded=True):
                 # (Mismos filtros que antes: Platform, Campaign, Category, Margin Slider, Conflict Checkbox)
                col1, col2, col3 = st.columns(3)
                with col1:
                    platforms = ['Todas'] + sorted(sim_df_analyzed['PlatformName'].unique())
                    selected_platform = st.selectbox("Plataforma", platforms, key="camp_platform")
                with col2:
                    available_campaigns = ['Todas']
                    temp_df_camp = sim_df_analyzed # Usar df analizado aqui
                    if selected_platform != 'Todas':
                         temp_df_camp = sim_df_analyzed[sim_df_analyzed['PlatformName'] == selected_platform]
                    # Asegurar que CampaignName existe antes de llamar a unique()
                    if 'CampaignName' in temp_df_camp.columns:
                         available_campaigns += sorted(temp_df_camp['CampaignName'].unique())
                    selected_campaign = st.selectbox("Campaña", available_campaigns, key="camp_campaign")
                with col3:
                     # Asegurar que Categoria_Plato existe antes de llamar a unique()
                    if 'Categoria_Plato' in sim_df_analyzed.columns:
                         categories = ['Todas'] + sorted(sim_df_analyzed['Categoria_Plato'].dropna().unique())
                    else:
                         categories = ['Todas']
                    selected_category = st.selectbox("Categoría Plato", categories, key="camp_category")

                min_margin_pct = st.slider(
                    "Margen Bruto Mínimo Aceptable (%)",
                     min_value=-100.0, # Rango fijo para evitar errores si min() es NaN
                     max_value=100.0,  # Rango fijo
                     value=0.0, # Por defecto mostrar solo rentables >= 0%
                     step=1.0,
                     key="camp_margin_slider"
                )
                show_conflicts_filter = st.checkbox("Mostrar Solo Conflictos de Exclusividad", value=False, key="camp_conflict_check")


            # --- Aplicar Filtros al DataFrame ---
            filtered_sim_df = sim_df_analyzed.copy()
            if selected_platform != 'Todas':
                filtered_sim_df = filtered_sim_df[filtered_sim_df['PlatformName'] == selected_platform]
            if selected_campaign != 'Todas' and 'CampaignName' in filtered_sim_df.columns:
                filtered_sim_df = filtered_sim_df[filtered_sim_df['CampaignName'] == selected_campaign]
            if selected_category != 'Todas' and 'Categoria_Plato' in filtered_sim_df.columns:
                filtered_sim_df = filtered_sim_df[filtered_sim_df['Categoria_Plato'] == selected_category]

            # Filtrar por margen solo si la columna existe y es numérica
            if 'Pct_Margen_Bruto_Campaign' in filtered_sim_df.columns:
                 filtered_sim_df['Pct_Margen_Bruto_Campaign'] = pd.to_numeric(filtered_sim_df['Pct_Margen_Bruto_Campaign'], errors='coerce')
                 filtered_sim_df = filtered_sim_df[filtered_sim_df['Pct_Margen_Bruto_Campaign'] >= (min_margin_pct / 100.0)]
            else:
                 st.warning("Columna 'Pct_Margen_Bruto_Campaign' no encontrada para filtrar por margen.")


            if show_conflicts_filter and 'Exclusivity_Conflict' in filtered_sim_df.columns:
                 filtered_sim_df = filtered_sim_df[filtered_sim_df['Exclusivity_Conflict'] == True]

            # --- GUARDAR RESULTADOS FILTRADOS EN SESSION STATE ---
            st.session_state['campaign_results'] = filtered_sim_df
            if not filtered_sim_df.empty:
                st.success("Resultados del análisis filtrados y listos para consultar en la sección 'Chat con Asistente'.")
            # --- FIN GUARDAR EN SESSION STATE ---


            # --- Mostrar Tabla Filtrada ---
            st.subheader("Resultados de Simulación Filtrados")
            st.write(f"Mostrando {len(filtered_sim_df)} combinaciones Plato-Campaña.")
            st.dataframe(
                filtered_sim_df.sort_values(by='Pct_Margen_Bruto_Campaign', ascending=False) if 'Pct_Margen_Bruto_Campaign' in filtered_sim_df else filtered_sim_df,
                use_container_width=True
            )
            if 'Exclusivity_Conflict' in filtered_sim_df.columns and filtered_sim_df['Exclusivity_Conflict'].any():
                 st.info("⚠️ Algunos platos mostrados tienen conflictos de exclusividad. Revise antes de generar el brief.")


            # --- Selección para el Brief ---
            st.subheader("Selección para Generar Brief")
            st.markdown("Selecciona las combinaciones deseadas para incluir en el archivo CSV del brief.")

            if not filtered_sim_df.empty:
                if {'CampaignID', 'ID_Plato', 'Nombre_Plato'}.issubset(filtered_sim_df.columns):
                    filtered_sim_df['SelectionID'] = filtered_sim_df['CampaignID'] + ' | ' + filtered_sim_df['ID_Plato'] + ' (' + filtered_sim_df['Nombre_Plato'].fillna('?') + ')' # Handle potential NaN in Nombre_Plato
                    options = sorted(filtered_sim_df['SelectionID'].tolist())

                    selected_options = st.multiselect(
                        "Confirmar Selección para Brief:",
                        options=options,
                        key="camp_brief_select"
                    )

                    # --- Generar Brief ---
                    if st.button("Generar Brief de Campaña", key="camp_brief_button"):
                        if selected_options:
                            final_selection_df = filtered_sim_df[filtered_sim_df['SelectionID'].isin(selected_options)].copy()
                            output_filename = f"campaign_brief_{date.today()}.csv"
                            try:
                                success_brief, message_brief = generate_campaign_brief(final_selection_df, output_filename)
                                if success_brief:
                                    with open(output_filename, "rb") as fp:
                                        st.download_button(
                                            label="Descargar Brief Generado (CSV)",
                                            data=fp, file_name=output_filename, mime="text/csv"
                                        )
                                    status_placeholder.success(message_brief)
                                else:
                                     status_placeholder.error(message_brief)
                            except Exception as e:
                                status_placeholder.error(f"Error al generar o descargar el brief: {e}")
                        else:
                            status_placeholder.warning("Por favor, selecciona al menos una combinación para generar el brief.")
                else:
                    st.error("Faltan columnas (CampaignID, ID_Plato, Nombre_Plato) en datos filtrados para selección del brief.")
            else:
                st.info("No hay datos filtrados disponibles para seleccionar.")


# ==============================================================================
# --- SECCIÓN: Chat con Asistente ---
# ==============================================================================
elif option == "Chat con Asistente":
    st.header("💬 Chat con Asistente AI (Gemini)")

    # --- Verificar si hay resultados de análisis en session state ---
    if 'campaign_results' not in st.session_state or st.session_state['campaign_results'] is None or st.session_state['campaign_results'].empty:
        st.warning("Por favor, primero ejecuta un 'Análisis de Campañas' para generar resultados antes de usar el chat.")
        st.info("Ve a la sección 'Análisis de Campañas', aplica los filtros deseados y los resultados se guardarán para el chat.")
        st.stop() # Detener si no hay datos
    else:
        # Acceder a los resultados almacenados
        analysis_df_for_chat = st.session_state['campaign_results']
        st.info(f"Usando los resultados del último análisis filtrado ({len(analysis_df_for_chat)} opciones). Vuelve a 'Análisis de Campañas' para actualizar si es necesario.")

    # --- Inicializar modelo Gemini (una vez por sesión) ---
    if st.session_state.gemini_model is None:
        with st.spinner("Inicializando asistente AI..."):
            st.session_state.gemini_model = LLM_integrator.init_gemini()

    model = st.session_state.gemini_model

    if not model:
        st.error("No se pudo inicializar el modelo de lenguaje. Verifica la API Key (variable de entorno GOOGLE_API_KEY) y la configuración.")
        st.stop()

    # --- Mostrar Historial del Chat ---
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Consultas Predefinidas (en la barra lateral) ---
    st.sidebar.subheader("Consultas Predefinidas")
    predefined_options = list(LLM_integrator.PREDEFINED_QUERIES.items())
    for key, question in predefined_options:
        # Usar 'st.sidebar.button' para las preguntas predefinidas
        if st.sidebar.button(question, key=f"predef_{key}"):
            with st.chat_message("user"): # Mostrar pregunta predefinida como del usuario
                 st.markdown(question)
            st.session_state.chat_history.append({"role": "user", "content": question})

            with st.spinner("Consultando al asistente..."):
                response = LLM_integrator.get_predefined_query_response(model, key, analysis_df_for_chat)

            # Mostrar respuesta y añadir al historial
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            # No usar st.rerun() aquí, dejar que el flujo normal lo actualice

    # --- Input del Usuario (Chat Libre) ---
    if user_prompt := st.chat_input("Haz una pregunta sobre los resultados del análisis..."):
        # Añadir y mostrar mensaje del usuario
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Preparar y enviar a LLM
        with st.spinner("Pensando..."):
            # Formatear contexto con los datos actuales en session_state
            context_summary = LLM_integrator.format_data_for_llm(analysis_df_for_chat)

            # Construir prompt para consulta libre
            full_prompt = dedent(f"""
                Eres ATOMICK-AI, un asistente analista. Responde la pregunta del usuario basándote *únicamente* en el siguiente contexto sobre análisis de campañas de delivery. Si la pregunta no puede responderse con el contexto, indícalo claramente. Sé conciso.

                Contexto del Análisis:
                ---
                {context_summary}
                ---

                Pregunta del Usuario: {user_prompt}

                Respuesta Concisa:
            """)
            response = LLM_integrator.get_llm_response(model, full_prompt)

        # Añadir y mostrar respuesta del asistente
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
        # Streamlit se re-ejecuta automáticamente después del chat_input

# --- FIN ---