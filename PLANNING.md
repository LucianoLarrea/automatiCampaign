# PLANNING.md - Proyecto Atomick: Finanzas y Campañas

## 1. Objetivo del Proyecto

Desarrollar un sistema integral en Python y MySQL para gestionar el costeo de platos, calcular indicadores financieros base, simular la rentabilidad de campañas en plataformas de delivery (Rappi, PedidosYa, MercadoPago), analizar datos históricos y visualizar la información a través de una interfaz web interactiva (Streamlit). El sistema debe permitir la actualización periódica de precios y ser desplegable en Google Cloud.

## 2. Stack Tecnológico

* **Base de Datos:** MySQL (Desplegado preferentemente en Google Cloud SQL)
* **Backend/Lógica:** Python 3.x
    * **Manipulación de Datos:** Pandas
    * **Conexión BD:** SQLAlchemy (Recomendado) + mysql-connector-python (como driver)
    * **Otros:** openpyxl (para Excel), logging
* **Frontend/UI:** Streamlit
* **Visualización:** Plotly Express (integrado con Streamlit)
* **Despliegue:** Google Cloud Platform (GCP)
    * **Base de Datos:** Cloud SQL for MySQL
    * **Backend Job (Updates + Snapshot):** Cloud Scheduler + Cloud Run (o Cloud Functions si es simple)
    * **Frontend (Streamlit):** Cloud Run (Recomendado) o App Engine
    * **Gestión de Secretos:** Secret Manager
    * **Contenerización:** Docker (Opcional pero recomendado para despliegue)
* **Control de Versiones:** Git / GitHub (o similar)
* **LLM:** Google Generative AI (Gemini)
    * **Librería Python:** `google-generativeai`

## 3. Fases del Proyecto

### Fase 1: Fundación - Base de Datos y Costeo (SQL)

* **Tarea 1.1:** Diseño final y creación/ajuste del esquema SQL completo en MySQL.
    * Tablas: `INSUMOS`, `PLATOS` (con `Precio_Venta_Base`, `Precio_Competencia`, `Categoria_Plato`), `SUBRECETAS_DEFINICION`, `SUBRECETAS_COMPOSICION`, `RECETAS_DEFINICION`, `RECETAS_COMPOSICION`, `PLATOS_PACKAGING`, `FINANCIAL_PARAMS`, `CAMPAIGNS`, `PLATOS_FINANCIALS_HISTORY`.
    * Relaciones y constraints.
* **Tarea 1.2:** Creación/Validación de Vistas SQL para costeo.
    * `V_SUBRECETAS_COSTOS`
    * `V_RECETAS_COSTOS`
    * `V_PLATOS_COSTOS`
* **Tarea 1.3:** Carga inicial de datos (Insumos, Platos base, Parámetros iniciales, Campañas de ejemplo).
* **Entregable:** Esquema SQL funcional con vistas de costeo y datos iniciales.

### Fase 2: Métricas Base y Simulación (SQL)

* **Tarea 2.1:** Creación/Validación de la Vista `V_PLATOS_FINANCIALS`.
    * Cálculo de PBA, PNA, Margen Base, etc., leyendo desde `V_PLATOS_COSTOS`, `PLATOS` y `FINANCIAL_PARAMS`.
* **Tarea 2.2:** Creación/Validación de la Vista `V_CAMPAIGN_SIMULATION`.
    * Cálculo de precios y márgenes de campaña, uniendo `PLATOS`, `V_PLATOS_COSTOS`, `CAMPAIGNS` y `FINANCIAL_PARAMS`.
* **Entregable:** Vistas SQL funcionales para métricas base y simulación de campañas.

### Fase 3: Backend - Actualizaciones y Snapshot (Python)

* **Tarea 3.1:** Refactorizar `db_connection.py` para usar SQLAlchemy (Recomendado).
* **Tarea 3.2:** Finalizar `price_updaters.py`.
    * Implementar lectura robusta de CSV/Excel (o APIs si aplica) para precios de insumos y competencia.
    * Implementar lógica de actualización en BD (con `UPDATE`). Incluir recálculo de `Costo_Por_Unidad_Uso`.
* **Tarea 3.3:** Finalizar `snapshot_job.py` (o `snapshot_creator.py` + `main.py`).
    * Orquestar llamadas: `update_insumo_prices` -> `update_competitor_prices` -> `create_financial_snapshot`.
    * Implementar `create_financial_snapshot` para leer de `V_PLATOS_FINANCIALS` (o vistas/tablas base) y escribir en `PLATOS_FINANCIALS_HISTORY`.
* **Tarea 3.4:** Implementar configuración centralizada (`config.py` o variables de entorno) y logging robusto.
* **Entregable:** Scripts Python funcionales y testeados para actualizar precios y crear snapshots.

### Fase 4: Backend - Análisis de Campañas (Python)

* **Tarea 4.1:** Finalizar `campaign_analyzer.py`.
    * `get_campaign_simulation_data`: Función para leer de `V_CAMPAIGN_SIMULATION` (preferiblemente con SQLAlchemy) a un DataFrame.
    * `analyze_campaigns_simplified`: Función para añadir flag `Exclusivity_Conflict`.
    * `generate_campaign_brief`: Función para exportar selección a CSV.
* **Entregable:** Módulo Python funcional para obtener y preparar datos de simulación.

### Fase 5: Frontend - Interfaz Streamlit (Python)

* **Tarea 5.1:** Unificar y refinar `app.py`.
    * Implementar la navegación por radio buttons.
    * Integrar todas las secciones: Ver Datos, Actualizar Precios, Crear Snapshot, Ver Historial, Análisis de Campañas.
* **Tarea 5.2:** Implementar interactividad en "Análisis de Campañas".
    * Filtros (expander/columnas), visualización de tabla (`st.dataframe`), selección (`st.multiselect`), generación y descarga de brief (`st.button`, `st.download_button`).
* **Tarea 5.3:** Implementar/Mejorar visualizaciones en "Ver Historial" (Plotly).
* **Tarea 5.4:** Mejorar manejo de errores y feedback al usuario en la UI (`st.error`, `st.success`, `st.warning`, `st.spinner`).
* **Entregable:** Aplicación Streamlit funcional y desplegable.

### Fase 6: Integración de Asistente LLM (Gemini)

* **Tarea 6.1:** Configurar Acceso a API Gemini.
    * Obtener API Key de Google AI Studio o Google Cloud.
    * Añadir `google-generativeai` a `requirements.txt` e instalar.
    * Implementar gestión segura de API Key (variables de entorno, `st.secrets`, Google Secret Manager para despliegue).
* **Tarea 6.2:** Desarrollar Módulo `llm_integrator.py`.
    * Función para inicializar el cliente de Gemini (`genai.configure`, `genai.GenerativeModel`).
    * Función `format_data_for_llm(df)`: Selecciona y formatea datos clave del DataFrame de análisis (ej: top N campañas rentables, resúmenes por plataforma) en texto conciso para el contexto del prompt.
    * Función `get_llm_response(prompt, context_data_string)`: Envía prompt + contexto a la API de Gemini y maneja la respuesta.
    * Definir estructuras/diccionarios para consultas predefinidas y sus prompts asociados.
    * Función `get_predefined_query_response(query_key, analysis_df)`: Obtiene prompt, formatea datos con `format_data_for_llm`, llama a `get_llm_response`.
* **Tarea 6.3:** Modificar `app.py` para Persistencia y Sección Chat.
    * Utilizar `st.session_state` para almacenar los resultados del análisis de campañas (ej: `st.session_state['campaign_results'] = filtered_df`) cuando se generan/filtran en la sección "Análisis de Campañas".
    * Añadir opción "Chat con Asistente" a la navegación (`st.sidebar.radio`).
    * Crear el bloque `elif option == "Chat con Asistente":`.
    * Dentro del bloque:
        * Verificar si `st.session_state['campaign_results']` existe; si no, mostrar mensaje para ejecutar análisis primero.
        * Configurar cliente Gemini (con API key segura).
        * Implementar interfaz de chat (historial en `st.session_state`, input de usuario con `st.text_input`).
        * Añadir selectbox o botones para las consultas predefinidas.
        * Lógica para manejar consultas predefinidas (llamando a `get_predefined_query_response`).
        * Lógica para manejar consultas libres (formatear contexto, construir prompt, llamar a `get_llm_response`).
* **Tarea 6.4:** Definir y Testear Prompts y Consultas.
    * Redactar prompts efectivos para Gemini que incluyan el contexto formateado.
    * Definir 3-5 consultas predefinidas útiles (ej: "¿Cuál es la campaña más rentable en general?", "¿Qué margen tiene el plato X en la campaña Y?", "¿Hay conflictos de exclusividad?").
    * Probar la calidad y relevancia de las respuestas del LLM.
* **Entregable:** Módulo `llm_integrator.py` funcional, sección de chat interactiva en Streamlit con consultas predefinidas y libres, usando resultados persistentes en la sesión.


### Fase 7: Automatización y Scheduling (Python + Cloud/OS)

* **Tarea 7.1:** Preparar el script Python principal (`snapshot_job.py` o `main.py`) para ejecución desatendida (manejo de argumentos, configuración externa).
* **Tarea 7.2:** Configurar el agendador (Scheduler).
    * **Opción Cloud (Recomendada):** Google Cloud Scheduler para disparar un Cloud Run Job o Cloud Function.
    * **Opción Local/VM:** Cron (Linux) o Task Scheduler (Windows).
* **Tarea 7.3:** Configurar monitoreo y alertas básicas para el job agendado.
* **Entregable:** Proceso automático y agendado para actualizaciones y snapshots.

### Fase 8: Despliegue en Google Cloud (GCP)

* **Tarea 8.1:** Configurar Instancia de Cloud SQL for MySQL.
    * Migrar esquema y datos.
    * Configurar acceso y seguridad.
* **Tarea 8.2:** Desplegar el Job Backend (Python).
    * Contenerizar el script (Dockerfile).
    * Subir imagen a Google Container Registry (GCR) o Artifact Registry.
    * Crear y configurar Cloud Run Job (o Cloud Function).
    * Configurar Cloud Scheduler para invocar el Job/Function.
    * Configurar Secret Manager para credenciales de BD.
    * Configurar Secret Manager para API Key de Gemini además de credenciales BD.
* **Tarea 8.3:** Desplegar la App Streamlit (Python).
    * Contenerizar la app Streamlit (Dockerfile).
    * Subir imagen a GCR/Artifact Registry.
    * Crear y configurar servicio de Cloud Run (o App Engine).
    * Configurar acceso público/privado según necesidad (IAM, IAP).
    * Configurar Secret Manager para credenciales de BD.
    * Asegurar que la app desplegada pueda acceder a la API Key de Gemini (vía Secret Manager o variables de entorno configuradas en Cloud Run/App Engine).
* **Entregable:** Sistema completamente desplegado y funcional en GCP, incluyendo la funcionalidad de chat con LLM.

### Fase 9: Documentación y Entrega

* **Tarea 9.1:** Completar/Actualizar `README.md` (instalación, configuración, uso, arquitectura).
* **Tarea 9.2:** Documentar proceso de despliegue y mantenimiento.
* **Tarea 9.3:** Limpieza de código, revisión final y entrega.
* **Entregable:** Proyecto documentado y entregado.

## 4. Consideraciones Clave

* **SQLAlchemy:** Migrar la conexión y las interacciones (especialmente con Pandas) a SQLAlchemy para robustez y seguir recomendaciones.
* **Seguridad:** No hardcodear credenciales. Usar variables de entorno o Secret Manager en GCP.
* **Fuentes de Datos:** Definir claramente cómo y con qué frecuencia se obtendrán los archivos/APIs de precios. Implementar validaciones en la carga.
* **Rendimiento:** Indexar adecuadamente las tablas MySQL. Optimizar consultas en Vistas si es necesario. Usar caching (`@st.cache_data`, `@st.cache_resource`) en Streamlit.
* **Manejo de Errores:** Implementar `try-except` y logging detallado en Python y procedimientos/funciones SQL si aplica.
* **Testing:** Realizar pruebas unitarias (Python), pruebas de integración (Python-DB) y pruebas funcionales (Streamlit UI). Validar cálculos.
* **Gestión API Key LLM:** Es crucial manejar la API Key de Gemini de forma segura, especialmente en el despliegue (NO hardcodearla).
* **Calidad de Prompts:** La utilidad del LLM dependerá mucho de la calidad de los prompts y del contexto que se le proporcione (`format_data_for_llm`).
* **Costos LLM:** Tener en cuenta los posibles costos asociados al uso de la API de Gemini.
* **Persistencia de Sesión:** `st.session_state` mantiene los datos solo mientras dura la sesión del navegador del usuario. Si se cierra la pestaña, se pierde. Para persistencia mayor, se necesitaría guardar resultados en BD o archivos.

## 5. Mantenimiento y Próximos Pasos

* Monitoreo regular de jobs agendados y rendimiento de la aplicación/BD.
* Backups periódicos de la base de datos (Cloud SQL ofrece esto).
* Actualización de dependencias (Python, Streamlit, etc.).
* Posibles mejoras futuras: Interfaz de usuario más avanzada, más tipos de análisis, integración con APIs de plataformas de delivery, etc.
* Refinar prompts y consultas predefinidas del LLM basado en el uso.
* Evaluar y optimizar costos de API LLM.