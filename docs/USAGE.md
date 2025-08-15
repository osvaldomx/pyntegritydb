# Guía de Uso Detallada de pyntegritydb

Bienvenido a la guía de uso de `pyntegritydb`. Aquí encontrarás explicaciones detalladas sobre cada una de las funcionalidades de la herramienta, desde el uso avanzado de la línea de comandos hasta la interpretación de los reportes.

---
## 1. Uso de la Línea de Comandos (CLI)

El comando principal es `pyntegritydb` y su estructura básica es la siguiente:

```bash
pyntegritydb <db_uri> [opciones]
```

### Argumentos Principales

* **`db_uri`** (Obligatorio): La [URI de conexión de SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) para tu base de datos.
    * **SQLite**: `"sqlite:///ruta/a/tu/database.db"`
    * **PostgreSQL**: `"postgresql://usuario:contraseña@host:puerto/nombre_db"`
    * **MySQL**: `"mysql+pymysql://usuario:contraseña@host:puerto/nombre_db"`

* **`--format <formato>`** (Opcional): Especifica el formato de salida del reporte. El valor por defecto es `cli`.
    * `cli`: Una tabla formateada para la consola.
    * `json`: Salida en formato JSON, ideal para APIs.
    * `csv`: Salida en formato de valores separados por comas.

---
## 2. Interpretación de los Reportes

`pyntegritydb` genera un análisis detallado por cada relación de clave foránea encontrada. A continuación se explica qué significa cada métrica.

### Métricas Clave

* **`total_rows`**: El número total de filas en la tabla de origen (la que contiene la clave foránea).
* **`orphan_rows_count`**: El número absoluto de filas cuya clave foránea no tiene una correspondencia en la tabla de destino (o es nula). **Este es el indicador principal de un problema.**
* **`valid_rows_count`**: El número de filas con una referencia válida.
* **`null_rows_count`**: El número de filas donde la clave foránea es `NULL`.
* **`validity_rate`**: El porcentaje de filas válidas (`valid_rows_count / total_rows`). Una tasa del 100% (1.0) es ideal.
* **`orphan_rate`**: El porcentaje de filas huérfanas (`orphan_rows_count / total_rows`). Un valor de 0% (0.0) es ideal.
* **`fk_density`**: El porcentaje de filas donde la clave foránea no es nula. Mide qué tan "poblada" o utilizada es una relación.

### Ejemplo de Salida (Formato `cli`)

```
📊 Reporte de Integridad Referencial:
+-----------------+------------------+-----------------+-----------------+-------------+
| Tabla de Origen | Tabla de Destino | Tasa de Validez | Filas Huérfanas | Total Filas |
+=================+==================+=================+=================+=============+
| orders          | users            | 75.00%          | 1               | 4           |
| order_items     | products         | 100.00%         | 0               | 5000        |
+-----------------+------------------+-----------------+-----------------+-------------+

Resumen del Análisis:
---------------------
Relaciones analizadas: 2
Relaciones con filas huérfanas: 1
```
En este ejemplo, la relación `orders -> users` tiene un problema, con una fila huérfana y una tasa de validez del 75%.

---
## 3. Visualización del Grafo

(Funcionalidad futura) La herramienta puede generar una imagen del grafo de tu esquema para un diagnóstico visual rápido.



### Interpretación de Colores

* **Verde**: Relación saludable (`validity_rate` >= 99.5%).
* **Naranja**: Relación con advertencias (`validity_rate` >= 90%).
* **Rojo**: Relación con problemas críticos (`validity_rate` < 90%).
* **Gris**: Relación para la cual no se pudieron calcular las métricas (posiblemente por un error).

---
## 4. Archivo de Configuración (Próximamente en v0.2.0)

Podrás definir umbrales de aceptación en un archivo `config.yml` para que `pyntegritydb` genere alertas automáticas cuando se violen tus estándares de calidad de datos.

### Ejemplo de `config.yml`

```yaml
# Umbrales de aceptación para las métricas

thresholds:
  # Umbral por defecto para todas las relaciones
  default:
    validity_rate: 0.99
    
  # Umbrales específicos para la tabla 'orders'
  tables:
    orders:
      validity_rate: 1.0 # La tabla 'orders' debe ser perfecta
```