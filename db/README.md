# 🗄️ Base de Datos del Proyecto

Este directorio contiene los backups versionados del esquema de la base de datos utilizada en este proyecto.

---

## 📁 Estructura

db/
├── backups/
│       └── 2025-04-06-inicial.sql
└── README.md


- **backups/**: Contiene archivos `.sql` con los esquemas y/o datos exportados desde MySQL Workbench.
- **README.md**: Este documento.

---

## 🔁 Restaurar un backup

Para restaurar el esquema de la base de datos en un entorno local o de desarrollo:

1. Abrí una terminal.
2. Ejecutá el siguiente comando:

```bash
mysql -u TU_USUARIO -p TU_BASE_DE_DATOS < backups/2025-04-06-inicial.sql
```

## ✍️ Notas
Este backup solo contiene el esquema (estructura de tablas, relaciones, etc.). No incluye datos.

Se recomienda hacer un nuevo backup del esquema cada vez que se realicen cambios estructurales importantes en la base.

Usá nombres de archivo con formato YYYY-MM-DD-descripcion.sql para mantener un historial claro.

## 🛠 Herramientas recomendadas
MySQL Workbench: Para exportar el esquema o datos manualmente.

mysqldump: Para automatizar la exportación desde la terminal.

