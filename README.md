# pyntegritydb

[![PyPI version](https://badge.fury.io/py/pyntegritydb.svg)](https://badge.fury.io/py/pyntegritydb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/pyntegritydb)](https://pypi.org/project/pyntegritydb/)
[![Build Status](https://github.com/tu_usuario/pyntegritydb/actions/workflows/ci.yml/badge.svg)](https://github.com/osvaldomx/pyntegritydb/actions)


**pyntegritydb** es una herramienta de línea de comandos para analizar y medir la calidad de la integridad referencial en bases de datos relacionales. Basada en el paper académico ["Referential Integrity Quality Metrics"](https://www2.cs.uh.edu/~ordonez/pdfwww/w-2008-DSS-refint.pdf), la biblioteca te ayuda a diagnosticar rápidamente relaciones rotas o "huérfanas" en tu esquema.



---
## Características Principales

* **Análisis Basado en Métricas**: Calcula métricas clave como `validity_rate` y `orphan_rate` para cada relación.
* **Soporte Multi-DB**: Compatible con cualquier base de datos que soporte SQLAlchemy (PostgreSQL, MySQL, SQLite, etc.).
* **Reportes Flexibles**: Genera reportes en múltiples formatos: tabla para la consola (`cli`), `json` o `csv`.
* **Visualización de Esquema**: Crea un grafo visual de las relaciones de tu base de datos, coloreando las conexiones según su "salud".
* **Fácil de Usar**: Diseñada como una herramienta de línea de comandos simple y directa.

---
## Instalación

Instala `pyntegritydb` directamente desde PyPI:

```bash
pip install pyntegritydb
```

---
## Guía de Inicio Rápido

Puedes analizar tu base de datos con un único comando, pasándole la URI de conexión de SQLAlchemy.

### 1. Ejecutar un Análisis Básico

El siguiente comando se conectará a una base de datos SQLite y mostrará un reporte en la consola.

```bash
pyntegritydb "sqlite:///ruta/a/tu/database.db"
```

### 2. Generar Reporte en JSON

Usa el argumento `--format` para cambiar el formato de salida.

```bash
pyntegritydb "postgresql://user:pass@host/db" --format json
```

### 3. Generar una Visualización del Grafo

Próximamente se añadirá la funcionalidad para generar y guardar el grafo visual directamente desde la CLI.

---
## Desarrollo

Si quieres contribuir al proyecto, sigue estos pasos:

1.  **Clona el repositorio:**
    ```bash
    git clone [https://github.com/tu_usuario/pyntegritydb.git](https://github.com/tu_usuario/pyntegritydb.git)
    cd pyntegritydb
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instala las dependencias en modo editable:**
    ```bash
    pip install -e ".[dev]" 
    # (Necesitarás definir los 'dev' extras en pyproject.toml para pytest, etc.)
    ```
4.  **Ejecuta las pruebas:**
    ```bash
    pytest
    ```

---
## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.