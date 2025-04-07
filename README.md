# Sistema de Actualización y Snapshot Financiero

Este sistema permite actualizar precios de insumos y competencia, y crear snapshots financieros para análisis histórico en la base de datos Atomick.

## Estructura del Proyecto

```
├── main.py                # Punto de entrada del programa
├── config.py              # Configuración centralizada
├── db_connection.py       # Módulo de conexión a base de datos
├── price_updaters.py      # Funciones para actualizar precios
├── snapshot_creator.py    # Funciones para crear snapshots financieros
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Este archivo
```

## Requisitos

- Python 3.6+
- MySQL/MariaDB
- Dependencias en `requirements.txt`

## Instalación

1. Clone este repositorio
2. Instale las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Configure las variables de entorno o ajuste `config.py`:
   - `DB_HOST`: Host de la base de datos
   - `DB_USER`: Usuario de la base de datos
   - `DB_PASSWORD`: Contraseña
   - `DB_NAME`: Nombre de la base de datos

## Uso

Execute el programa principal:

```
python main.py
```

El script realizará las siguientes operaciones:
1. Actualizar precios de insumos desde CSV
2. Actualizar precios de competencia desde Excel
3. Crear un snapshot financiero en la tabla de historial

## Estructura de Archivos de Entrada

### CSV de Precios de Insumos
Ubicación por defecto: `4-Brief/Gemini/nuevos_precios_insumos.csv`
Columnas requeridas:
- `ID_Insumo`: Identificador del insumo
- `Nuevo_Costo_Compra`: Nuevo costo de compra
- `Nueva_Unidad_Compra`: Nueva unidad de medida

### Excel de Precios de Competencia
Ubicación por defecto: `4-Brief/Gemini/precios_competencia.xlsx`
Columnas requeridas:
- `ID_Plato`: Identificador del plato
- `Precio_Competencia_Nuevo`: Nuevo precio de competencia

## Registro y Monitoreo

Las operaciones se registran en `snapshot_job.log` con detalles de fecha, nivel y mensaje.

## Dependencias Principales

- mysql-connector-python: Conexión a MySQL
- pandas: Procesamiento de datos
- Otras dependencias en `requirements.txt`

## Base de Datos

El sistema interactúa con las siguientes tablas:
- `INSUMOS`: Actualización de precios de insumos
- `PLATOS`: Actualización de precios de competencia
- `V_PLATOS_FINANCIALS`: Vista para cálculos financieros
- `PLATOS_FINANCIALS_HISTORY`: Historial de snapshots financieros

## Mantenimiento

Para añadir nuevas fuentes de datos o modificar la lógica:
- Actualizar los módulos correspondientes en `price_updaters.py`
- Modificar la estructura del snapshot en `snapshot_creator.py`
- Ajustar la configuración en `config.py` según sea necesario

## Mejoras a futuro

UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.

La advertencia aparece porque estás usando pd.read_sql_query (probablemente en app.py y campaign_analyzer.py) pasándole directamente la conexión creada por mysql-connector-python (desde db_connection.py).

¿Es un error? No, es solo una advertencia (UserWarning). Pandas indica que, aunque funcione, ellos prueban y soportan oficialmente mejor las conexiones a través de SQLAlchemy.

¿Qué significa? Tu código probablemente funciona bien ahora, pero usar la conexión directa de mysql-connector no está tan probado por Pandas como usar SQLAlchemy, y podría haber casos no contemplados o cambios futuros.

Recomendación: Para seguir las mejores prácticas de Pandas y asegurar mayor compatibilidad futura, considera usar SQLAlchemy para manejar la conexión:
Añade SQLAlchemy a tu requirements.txt.
Modifica db_connection.py para crear un engine de SQLAlchemy en lugar de devolver la conexión directa de mysql.connector.
Pasa ese engine de SQLAlchemy a las funciones pd.read_sql_query en tu código.
Hacer esto eliminará la advertencia y alineará tu proyecto con el método preferido por Pandas para interactuar con bases de datos.

En Ver historial: Error inesperado al cargar historial: Value of 'x' is not the name of a column in 'data_frame'. Expected one of ['SnapshotID', 'SnapshotTimestamp', 'ID_Plato', 'Costo_Plato_Hist', 'Precio_Competencia_Hist', 'Market_Discount_Used', 'IVA_Rate_Used', 'Commission_Rate_Used', 'PBA_Hist', 'PNA_Hist', 'COGS_Partner_Actual_Hist', 'Costo_Total_CT_Hist', 'Margen_Bruto_Actual_MBA_Hist', 'Porcentaje_Margen_Bruto_PctMBA_Hist'] but received: Nombre_Plato

Causa Probable:

Revisando el código de app.py que unificamos [cite: Gemini/app.py], en la sección "Ver Historial", dentro de la primera pestaña de visualización ("Margen Bruto"), la línea que crea el gráfico de barras es:

Python

fig1 = px.bar(
    df_last_snap.sort_values('Porcentaje_Margen_Bruto_PctMBA_Hist', ascending=False).head(10),
    x='Nombre_Plato', # <--- AQUI EL PROBLEMA
    y='Porcentaje_Margen_Bruto_PctMBA_Hist',
    # ... resto de parámetros ...
)
El problema es que estás usando x='Nombre_Plato'. Aunque tu consulta SQL intenta traer p.Nombre_Plato con un LEFT JOIN, si un ID_Plato existe en PLATOS_FINANCIALS_HISTORY pero fue borrado de la tabla PLATOS, el LEFT JOIN resultará en un valor NULL para Nombre_Plato en esa fila. Plotly puede tener problemas al intentar usar una columna con NULLs o potencialmente si todas las filas filtradas para df_last_snap resultan tener NULL en esa columna, podría interpretarlo como que la columna no es válida para el eje 'x'.

Solución Concisa:

Modifica la línea del px.bar en la sección "Ver Historial" de tu app.py [cite: Gemini/app.py] para usar ID_Plato (que siempre existirá y no será NULL) en el eje x, en lugar de Nombre_Plato.

Cambia esto:

Python

x='Nombre_Plato',
Por esto:

Python

x='ID_Plato',
También sería prudente hacer lo mismo para hover_name en el px.scatter por robustez, cambiando hover_name='Nombre_Plato' por hover_name='ID_Plato', aunque el error actual parece provenir del gráfico de barras.


Fuentes y contenido relacionado
