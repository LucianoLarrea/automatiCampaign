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

### Fase 6: Automatización (Python + Cloud/OS)

* **Tarea 6.1:** Preparar el script Python principal (`snapshot_job.py` o `main.py`) para ejecución desatendida (manejo de argumentos, configuración externa).
* **Tarea 6.2:** Configurar el agendador (Scheduler).
    * **Opción Cloud (Recomendada):** Google Cloud Scheduler para disparar un Cloud Run Job o Cloud Function.
    * **Opción Local/VM:** Cron (Linux) o Task Scheduler (Windows).
* **Tarea 6.3:** Configurar monitoreo y alertas básicas para el job agendado.
* **Entregable:** Proceso automático y agendado para actualizaciones y snapshots.

### Fase 7: Despliegue en Google Cloud (GCP)

* **Tarea 7.1:** Configurar Instancia de Cloud SQL for MySQL.
    * Migrar esquema y datos.
    * Configurar acceso y seguridad.
* **Tarea 7.2:** Desplegar el Job Backend (Python).
    * Contenerizar el script (Dockerfile).
    * Subir imagen a Google Container Registry (GCR) o Artifact Registry.
    * Crear y configurar Cloud Run Job (o Cloud Function).
    * Configurar Cloud Scheduler para invocar el Job/Function.
    * Configurar Secret Manager para credenciales de BD.
* **Tarea 7.3:** Desplegar la App Streamlit (Python).
    * Contenerizar la app Streamlit (Dockerfile).
    * Subir imagen a GCR/Artifact Registry.
    * Crear y configurar servicio de Cloud Run (o App Engine).
    * Configurar acceso público/privado según necesidad (IAM, IAP).
    * Configurar Secret Manager para credenciales de BD.
* **Entregable:** Sistema completamente desplegado y funcional en GCP.

### Fase 8: Documentación y Entrega

* **Tarea 8.1:** Completar/Actualizar `README.md` (instalación, configuración, uso, arquitectura).
* **Tarea 8.2:** Documentar proceso de despliegue y mantenimiento.
* **Tarea 8.3:** Limpieza de código, revisión final y entrega.
* **Entregable:** Proyecto documentado y entregado.

## 4. Consideraciones Clave

* **SQLAlchemy:** Migrar la conexión y las interacciones (especialmente con Pandas) a SQLAlchemy para robustez y seguir recomendaciones.
* **Seguridad:** No hardcodear credenciales. Usar variables de entorno o Secret Manager en GCP.
* **Fuentes de Datos:** Definir claramente cómo y con qué frecuencia se obtendrán los archivos/APIs de precios. Implementar validaciones en la carga.
* **Rendimiento:** Indexar adecuadamente las tablas MySQL. Optimizar consultas en Vistas si es necesario. Usar caching (`@st.cache_data`, `@st.cache_resource`) en Streamlit.
* **Manejo de Errores:** Implementar `try-except` y logging detallado en Python y procedimientos/funciones SQL si aplica.
* **Testing:** Realizar pruebas unitarias (Python), pruebas de integración (Python-DB) y pruebas funcionales (Streamlit UI). Validar cálculos.

## 5. Mantenimiento y Próximos Pasos

* Monitoreo regular de jobs agendados y rendimiento de la aplicación/BD.
* Backups periódicos de la base de datos (Cloud SQL ofrece esto).
* Actualización de dependencias (Python, Streamlit, etc.).
* Posibles mejoras futuras: Interfaz de usuario más avanzada, más tipos de análisis, integración con APIs de plataformas de delivery, etc.