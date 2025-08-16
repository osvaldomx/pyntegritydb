# pyntegritydb

[![PyPI version](https://badge.fury.io/py/pyntegritydb.svg)](https://badge.fury.io/py/pyntegritydb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/pyntegritydb)](https://pypi.org/project/pyntegritydb/)
[![Build Status](https://github.com/osvaldomx/pyntegritydb/actions/workflows/python-package.yml/badge.svg)](https://github.com/osvaldomx/pyntegritydb/actions)


**pyntegritydb** es una herramienta de línea de comandos para analizar y medir la calidad de la integridad referencial en bases de datos relacionales. Basada en el paper académico ["Referential Integrity Quality Metrics"](https://www2.cs.uh.edu/~ordonez/pdfwww/w-2008-DSS-refint.pdf), la biblioteca te ayuda a diagnosticar rápidamente relaciones rotas o "huérfanas" en tu esquema.



---
## Características Principales

* **Análisis Dual**: Mide tanto la **Completitud** (filas huérfanas) como la **Consistencia** (datos desnormalizados incorrectos).
* **Sistema de Alertas**: Define umbrales de calidad en un archivo `config.yml` y recibe alertas si tus datos no cumplen con los estándares.
* **Soporte Multi-DB**: Compatible con cualquier base de datos que soporte SQLAlchemy (PostgreSQL, MySQL, SQLite, etc.).
* **Reportes Flexibles**: Genera reportes en múltiples formatos: tabla para la consola (`cli`), `json` o `csv`.
* **Fácil de Usar**: Diseñada como una herramienta de línea de comandos simple y directa.

---
## Instalación

Instala `pyntegritydb` directamente desde PyPI:

```bash
pip install pyntegritydb
```

---
## Guía de Inicio Rápido

El uso más potente de `pyntegritydb` es combinando un análisis con un archivo de configuración.

### 1. Crea tu Archivo de Configuración

En tu proyecto, crea un archivo `config.yml`:

```yaml
# config.yml
thresholds:
  default:
    validity_rate: 0.99 # Al menos 99% de las FKs deben ser válidas
    
  tables:
    orders:
      validity_rate: 1.0 # La tabla 'orders' debe ser perfecta

consistency_checks:
  orders: 
    - on_fk: ["user_id"]
      attributes:
        customer_name: name
```

### 2. Ejecuta el Análisis

Usa el comando `pyntegritydb` apuntando a tu base de datos y a tu archivo de configuración.



```bash
pyntegritydb "postgresql://user:pass@host/db" --config config.yml
```

### 3. Interpreta el Reporte

`pyntegritydb` generará un reporte completo en tu consola, mostrando primero las alertas, y luego los análisis detallados.

```
🚦 Reporte de Alertas 🚦
=========================
- ALERTA [Completitud]: La tabla 'orders' viola el umbral de 'validity_rate'. Esperado >= 100.00%, Obtenido = 98.50%

### Reporte de Completitud (Filas Huérfanas) ###
+-----------------+------------------+-----------------+-----------------+-------------+
| Tabla de Origen | Tabla de Destino | Tasa de Validez | Filas Huérfanas | Total Filas |
+=================+==================+=================+=================+=============+
| orders          | users            | 98.50%          | 15              | 1000        |
+-----------------+------------------+-----------------+-----------------+-------------+
...
```
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