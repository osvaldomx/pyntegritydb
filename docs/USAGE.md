# Guía de Uso Detallada de pyntegritydb

Bienvenido al manual de usuario de `pyntegritydb`. Aquí encontrarás explicaciones detalladas sobre cada una de las funcionalidades de la herramienta, desde el uso avanzado de la línea de comandos hasta la creación de un archivo de configuración completo.

---
## 1. Uso de la Línea de Comandos (CLI)

El comando principal es `pyntegritydb` y su estructura es la siguiente:

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

* **`--config <ruta>`** (Opcional): Ruta al archivo de configuración `config.yml`. Activa funcionalidades avanzadas como el análisis de consistencia y el sistema de alertas.

---
## 2. Archivo de Configuración (`config.yml`)

El archivo `config.yml` es el centro de control para las funcionalidades avanzadas. Puede contener dos secciones principales: `thresholds` y `consistency_checks`.



### `thresholds`: Sistema de Alertas

Esta sección te permite definir los umbrales de calidad para tus datos. Si una métrica no cumple con el umbral, se generará una alerta.

```yaml
thresholds:
  # Umbrales por defecto que se aplicarán a todas las tablas.
  default:
    validity_rate: 0.99    # Tasa de validez de completitud
    consistency_rate: 0.98 # Tasa de validez de consistencia

  # Umbrales específicos para tablas críticas.
  # Estos sobrescriben los valores por defecto.
  tables:
    orders:
      # La tabla 'orders' debe tener una integridad perfecta.
      validity_rate: 1.0
```

### `consistency_checks`: Análisis de Consistencia

Esta sección define qué atributos desnormalizados deben ser verificados.

```yaml
consistency_checks:
  # La clave principal es la tabla de origen (la que tiene la FK).
  orders: 
    # Cada elemento de la lista es una prueba de consistencia
    # basada en una FK específica de esa tabla.
    - on_fk: ["user_id"]
      # Atributos a comparar: {columna_en_orders: columna_en_users}
      attributes:
        customer_name: name
        
    - on_fk: ["product_id"]
      attributes:
        product_price: price
```

---
## 3. Interpretación de los Reportes

El reporte de la CLI está dividido en hasta tres secciones.

### Sección de Alertas
Aparece solo si se usa un archivo de configuración y se viola un umbral.

```
🚦 Reporte de Alertas 🚦
=========================
- ALERTA [Completitud]: La tabla 'orders' viola el umbral de 'validity_rate'. Esperado >= 100.00%, Obtenido = 98.50%
```

### Reporte de Completitud
Mide las referencias rotas o "huérfanas".

* **Tasa de Validez**: Porcentaje de filas con una clave foránea válida. **Un 100% es ideal.**
* **Filas Huérfanas**: Conteo de filas con una clave foránea inválida. **Un 0 es ideal.**

### Reporte de Consistencia de Atributos
Aparece solo si se configura. Mide si los datos desnormalizados son correctos.

* **Tasa de Consistencia**: De las filas con FK válida, qué porcentaje tiene los atributos consistentes. **Un 100% es ideal.**
* **Filas Inconsistentes**: Conteo de filas con datos desnormalizados incorrectos. **Un 0 es ideal.**