# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), y este proyecto se adhiere al [Versionamiento Semántico](https://semver.org/spec/v2.0.0.html).

---
## [0.3.0] - 2025-08-17

### Added
- **Mejoras de Usabilidad en la CLI**:
    - Se añadió el flag `--visualize` para generar un mapa visual de la salud del esquema.
    - Se implementó la opción `--output-file` para guardar los reportes directamente en un archivo.
- **Documentación Profesional**: Se ha configurado Sphinx y el proyecto ahora se publica automáticamente en Read the Docs.

### Changed
- **Calidad del Código**: Se integró la medición de cobertura de código con `pytest-cov`, alcanzando un 92% de cobertura en las pruebas.
- **Pruebas**: Se han actualizado las pruebas unitarias y de integración para cubrir las nuevas funcionalidades de la CLI.

---
## [0.2.0] - 2025-08-15

### Added
- **Análisis de Consistencia de Atributos**: Se implementó la característica principal para verificar la consistencia de datos desnormalizados a través de la nueva sección `consistency_checks` en `config.yml`.
- **Sistema de Alertas y Umbrales**: La herramienta ahora lee una sección de `thresholds` en el archivo de configuración y genera alertas si se violan los umbrales de calidad.
- **Salida con Código de Error**: La CLI ahora termina con un código de salida `1` si se encuentran alertas, facilitando su integración en flujos de trabajo automatizados (CI/CD).

### Changed
- **CLI**: Se añadió el argumento `--config` para especificar la ruta al archivo de configuración.
- **Reportes**: El reporte de la CLI y el formato JSON ahora incluyen una sección de "Alertas" y "Consistencia de Atributos".
- **Pruebas**: Se expandieron las pruebas de integración para cubrir los nuevos escenarios de consistencia y alertas.

---
## [0.1.0] - 2025-08-15

### Added
- **Lanzamiento Inicial**: Primera versión pública de `pyntegritydb`.
- **Análisis de Completitud**: Implementación del núcleo de la biblioteca para calcular `validity_rate` y `orphan_rate` (filas huérfanas).
- **Soporte Multi-DB**: Conexión a bases de datos a través de SQLAlchemy.
- **Reportes Flexibles**: Generación de reportes en formatos `cli`, `json` y `csv`.
- **Interfaz de Línea de Comandos (CLI)**: Punto de entrada principal `pyntegritydb` para ejecutar los análisis.
- **Visualización Experimental**: Módulo para generar una imagen del grafo de relaciones.
- **Pruebas Unitarias**: Cobertura de pruebas unitarias para todos los módulos principales.
- **Documentación Inicial**: Creación de los archivos `README.md` y `docs/USAGE.md`.