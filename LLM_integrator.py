# llm_integrator.py
import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import logging
from textwrap import dedent # Para limpiar strings multilínea (prompts)
from dotenv import load_dotenv
load_dotenv()

# --- Configuración de Logging ---
# (Puedes usar el logger configurado en tu app principal si prefieres)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Variables Globales (Opcional) ---
# Podrías definir el modelo aquí si siempre será el mismo
MODEL_NAME = 'gemini-2.0-flash' # O el modelo que prefieras/necesites

# --- 1. Inicialización del Cliente ---

def init_gemini():
    """
    Inicializa y configura el cliente de la API de Google Generative AI.
    Lee la API Key desde la variable de entorno GOOGLE_API_KEY.

    Returns:
        El objeto del modelo generativo inicializado o None si falla.
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logging.error("La variable de entorno GOOGLE_API_KEY no está configurada.")
            st.error("Error de Configuración: Falta la API Key de Google AI.") # Mensaje para Streamlit
            return None
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        logging.info(f"Cliente Gemini inicializado con el modelo '{MODEL_NAME}'.")
        return model
    except Exception as e:
        logging.error(f"Error al inicializar el cliente Gemini: {e}")
        st.error(f"Error inicializando Gemini: {e}") # Mensaje para Streamlit
        return None

# --- 2. Formateo de Datos para Contexto ---

def format_data_for_llm(analysis_df: pd.DataFrame, top_n=5) -> str:
    """
    Crea un resumen de texto conciso del DataFrame de análisis de campañas
    para usar como contexto en los prompts del LLM.

    Args:
        analysis_df: DataFrame con resultados de V_CAMPAIGN_SIMULATION
                     (Debe incluir columnas relevantes como Pct_Margen_Bruto_Campaign,
                      PlatformName, CampaignName, Nombre_Plato, ID_Plato,
                      Precio_Bruto_Campaign, Margen_Bruto_Campaign, Exclusivity_Conflict).
        top_n: Cuántas campañas top listar.

    Returns:
        Un string con el resumen formateado.
    """
    if analysis_df is None or analysis_df.empty:
        return "No hay datos de análisis de campañas disponibles para formatear."

    try:
        # Limpieza y preparación de datos
        df = analysis_df.copy()
        df['Pct_Margen_Bruto_Campaign'] = pd.to_numeric(df['Pct_Margen_Bruto_Campaign'], errors='coerce')
        df['Margen_Bruto_Campaign'] = pd.to_numeric(df['Margen_Bruto_Campaign'], errors='coerce')
        df.dropna(subset=['Pct_Margen_Bruto_Campaign', 'Margen_Bruto_Campaign'], inplace=True) # Eliminar filas con problemas numéricos

        total_options = len(df)
        profitable_options = df[df['Margen_Bruto_Campaign'] > 0]
        num_profitable = len(profitable_options)

        # Construir el resumen
        summary_lines = []
        summary_lines.append(f"Resumen del Análisis de Campañas ({total_options} opciones simuladas):")
        summary_lines.append(f"- {num_profitable} ({num_profitable/total_options:.1%} aprox.) opciones son rentables (Margen Bruto > $0).")

        # Top N más rentables
        if not profitable_options.empty:
            top_profitable = profitable_options.nlargest(top_n, 'Pct_Margen_Bruto_Campaign')
            summary_lines.append(f"\nTop {len(top_profitable)} Opciones Más Rentables (por % Margen Bruto):")
            for _, row in top_profitable.iterrows():
                 summary_lines.append(
                    f"  - {row.get('Nombre_Plato','N/A')} ({row.get('ID_Plato','N/A')}) en '{row.get('CampaignName','N/A')}' ({row.get('PlatformName','N/A')}) "
                    f"-> Precio: ${row.get('Precio_Bruto_Campaign',0):.2f}, Margen: {row.get('Pct_Margen_Bruto_Campaign',0):.1%}"
                )

        # Conflictos de Exclusividad (si la columna existe)
        if 'Exclusivity_Conflict' in df.columns:
            conflicts = df[df['Exclusivity_Conflict'] == True]
            if not conflicts.empty:
                conflicting_platos_names = conflicts['Nombre_Plato'].unique()
                summary_lines.append(f"\nConflictos de Exclusividad Detectados:")
                summary_lines.append(f"  - Platos afectados: {', '.join(conflicting_platos_names)}")
            else:
                 summary_lines.append("\n- No se detectaron conflictos de exclusividad.")

        # Podrías añadir más secciones aquí (peores márgenes, resumen por plataforma, etc.)

        return "\n".join(summary_lines)

    except Exception as e:
        logging.error(f"Error al formatear datos para LLM: {e}")
        return "Error interno al procesar los datos del análisis."


# --- 3. Interacción con API LLM ---

def get_llm_response(model, prompt: str) -> str:
    """
    Envía un prompt al modelo Gemini inicializado y devuelve la respuesta textual.

    Args:
        model: El objeto del modelo GenerativeModel inicializado.
        prompt: El prompt completo a enviar.

    Returns:
        La respuesta del LLM como string, o un mensaje de error.
    """
    if not model:
        return "Error: El modelo Gemini no está inicializado."
    logging.info(f"Enviando prompt a Gemini (longitud: {len(prompt)} caracteres)...")
    try:
        # Configuración opcional para la generación
        generation_config = genai.types.GenerationConfig(
            # temperature=0.7, # Más creatividad vs. más determinismo
            max_output_tokens=1500 # Ajustar según necesidad
        )
        # Considera añadir safety_settings si necesitas ajustar los filtros de seguridad
        # safety_settings=[...]

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            # safety_settings=safety_settings
            )

        # Verificar si la respuesta tiene contenido
        if response.parts:
             response_text = response.text
             logging.info("Respuesta recibida de Gemini.")
             return response_text
        else:
             # Informar si fue bloqueado o simplemente no hubo respuesta
             feedback = response.prompt_feedback
             block_reason = feedback.block_reason.name if feedback.block_reason else "Ninguno"
             logging.warning(f"Respuesta de Gemini vacía o bloqueada. Razón: {block_reason}. Feedback: {feedback}")
             return f"El asistente no pudo generar una respuesta (Razón: {block_reason}). Por favor, reformula la pregunta."

    except Exception as e:
        # Capturar errores específicos de la API si es posible
        logging.error(f"Error durante la llamada a la API de Gemini: {e}")
        return f"Error de comunicación con el asistente ({type(e).__name__}). Intenta de nuevo más tarde."


# --- 4. Consultas Predefinidas ---

# Diccionario con las preguntas para mostrar al usuario
PREDEFINED_QUERIES = {
    "resumen": "Dame un resumen general del análisis de campañas.",
    "top_rentables": f"¿Cuáles son las {5} campañas/platos más rentables por % de margen?", # Usar top_n
    "conflictos": "¿Hay platos con conflictos de exclusividad y cuáles son?",
    "plataforma_rentable": "¿Cuál plataforma parece tener las opciones más rentables en promedio (basado en el top N)?",
    # Puedes añadir más preguntas relevantes
}

# Diccionario con los templates de prompts para cada consulta predefinida
PROMPT_TEMPLATES = {
    "resumen": dedent("""
        Eres ATOMICK-AI, un asistente de análisis financiero para restaurantes que usan delivery.
        Basándote *únicamente* en el siguiente resumen de datos de simulación de campañas, proporciona un resumen ejecutivo muy breve (2-3 frases clave) sobre la situación general (rentabilidad, conflictos si los hay).

        Resumen de Datos del Análisis:
        ---
        {context_summary}
        ---

        Resumen Ejecutivo para el usuario:
    """),

    "top_rentables": dedent("""
        Eres ATOMICK-AI, un asistente analista.
        Extrae *únicamente* del siguiente resumen de datos la lista de las opciones de campaña/plato más rentables mencionadas (generalmente el top 5). Lista cada opción claramente con Plato, Campaña, Plataforma, Precio y % Margen.

        Resumen de Datos del Análisis:
        ---
        {context_summary}
        ---

        Las opciones más rentables mencionadas son:
    """),

    "conflictos": dedent("""
        Eres ATOMICK-AI, un asistente analista.
        Revisa el siguiente resumen de datos e informa si se detectaron conflictos de exclusividad.
        * Si se detectaron, lista los nombres de los platos afectados mencionados en el resumen.
        * Si *no* se detectaron, indica claramente que no hay conflictos.
        Responde basándote *solo* en la información provista.

        Resumen de Datos del Análisis:
        ---
        {context_summary}
        ---

        Informe de Conflictos de Exclusividad:
    """),

    "plataforma_rentable": dedent("""
        Eres ATOMICK-AI, un asistente analista.
        Observando la lista de las opciones más rentables en el siguiente resumen de datos, ¿parece alguna plataforma destacar por tener varias de las opciones más rentables? Menciona la plataforma(s) si es evidente en el top listado. Responde basándote *solo* en la información provista.

        Resumen de Datos del Análisis:
        ---
        {context_summary}
        ---

        Plataforma(s) destacada(s) en el top de rentabilidad:
    """),

}

# --- 5. Función Principal para Consultas Predefinidas ---

def get_predefined_query_response(model, query_key: str, analysis_df: pd.DataFrame) -> str:
    """
    Genera una respuesta para una consulta predefinida usando el LLM.

    Args:
        model: El objeto del modelo GenerativeModel inicializado.
        query_key: La clave de la consulta predefinida (ej: "resumen").
        analysis_df: El DataFrame con los resultados del análisis de campañas.

    Returns:
        La respuesta generada por el LLM o un mensaje de error.
    """
    # Validaciones
    if query_key not in PROMPT_TEMPLATES or query_key not in PREDEFINED_QUERIES:
        logging.error(f"Clave de consulta predefinida inválida: {query_key}")
        return f"Error: Consulta predefinida '{query_key}' no reconocida."
    if model is None:
        return "Error: El modelo LLM no está disponible."
    if analysis_df is None or analysis_df.empty:
         return "No hay datos de análisis de campañas para procesar esta consulta. Ejecuta el análisis primero."

    logging.info(f"Procesando consulta predefinida: {query_key}")

    # 1. Formatear contexto
    context_summary = format_data_for_llm(analysis_df)
    if "Error" in context_summary: # Manejar error de formateo
        return context_summary

    # 2. Obtener template y crear prompt final
    prompt_template = PROMPT_TEMPLATES[query_key]
    final_prompt = prompt_template.format(context_summary=context_summary)

    # 3. Llamar al LLM
    response = get_llm_response(model, final_prompt)

    return response

# --- Fin de llm_integrator.py ---