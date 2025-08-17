# Guía de Uso Detallada de pyntegritydb

Bienvenido al manual de usuario de `pyntegritydb`. Aquí encontrarás explicaciones detalladas sobre cada una de las funcionalidades de la herramienta.

---
## 1. Uso de la Línea de Comandos (CLI)

El comando principal es `pyntegritydb` y su estructura es la siguiente:

```bash
pyntegritydb <db_uri> [opciones]
```

### Argumentos Principales

* **`db_uri`** (Obligatorio): La [URI de conexión de SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) para tu base de datos.

* **`--format <formato>`** (Opcional): Especifica el formato de salida del reporte.
    * Opciones: `cli`, `json`, `csv`.
    * Default: `cli`.

* **`--config <ruta>`** (Opcional): Ruta al archivo `config.yml`. Activa el análisis de consistencia y el sistema de alertas.

* **`--output-file <ruta>`** (Opcional): Guarda la salida del reporte en el archivo especificado. Si no se usa, el reporte se muestra en la consola.

* **`--visualize`** (Opcional): Es un flag que activa la generación de una imagen del grafo de relaciones.

* **`--output-image <ruta>`** (Opcional): Especifica la ruta y el nombre del archivo para la imagen generada.
    * Default: `db_integrity_graph.png`.

---
## 2. Archivo de Configuración (`config.yml`)

El archivo `config.yml` es el centro de control para las funcionalidades avanzadas. Puede contener dos secciones principales: `thresholds` y `consistency_checks`.

### `thresholds`: Sistema de Alertas

Esta sección te permite definir los umbrales de calidad para tus datos.

```yaml
thresholds:
  default:
    validity_rate: 0.99
    consistency_rate: 0.98
  tables:
    orders:
      validity_rate: 1.0
```

### `consistency_checks`: Análisis de Consistencia

Esta sección define qué atributos desnormalizados deben ser verificados.

```yaml
consistency_checks:
  orders: 
    - on_fk: ["user_id"]
      attributes:
        customer_name: name
```

---
## 3. Interpretación de los Reportes

El reporte de la CLI está dividido en hasta tres secciones: Alertas, Completitud y Consistencia.

* **Alertas**: Aparece solo si se usa un `config.yml` y se viola un umbral.
* **Completitud**: Mide las referencias rotas o "huérfanas" (`validity_rate`).
* **Consistencia**: Mide si los datos desnormalizados son correctos (`consistency_rate`).