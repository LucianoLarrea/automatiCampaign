# Agendar la Ejecución:
## Linux/macOS: 
Usa cron. Abre la configuración con crontab -e y añade una línea similar a esta para ejecutarlo todos los días a las 3 AM:
Bash

0 3 * * * /usr/bin/python3 /ruta/completa/a/tu/snapshot_job.py >> /ruta/completa/a/tu/snapshot_job.log 2>&1
(Ajusta las rutas y la hora). >> ... 2>&1 redirige la salida estándar y de error al archivo de log.

## Windows: 
Usa el Programador de Tareas (Task Scheduler). Crea una nueva tarea, define el disparador (Trigger) para que sea diario a la hora que quieras, y en la acción (Action) selecciona "Iniciar un programa", indica la ruta a tu intérprete python.exe y en "Agregar argumentos" pones la ruta completa a tu snapshot_job.py. Configura también dónde guardar logs si es necesario.