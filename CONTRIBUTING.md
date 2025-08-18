# Guía de Contribución para pyntegritydb

¡Gracias por tu interés en contribuir a `pyntegritydb`! Estamos emocionados de recibir ayuda de la comunidad. Esta guía te proporcionará todo lo que necesitas para empezar.

## Cómo Contribuir

Puedes contribuir de varias maneras:
* Reportando bugs.
* Sugiriendo nuevas funcionalidades.
* Escribiendo o mejorando la documentación.
* Enviando Pull Requests con correcciones o nuevas características.

## Reportando Bugs

Si encuentras un bug, por favor, abre un "Issue" en GitHub. Asegúrate de incluir:
1.  La versión de `pyntegritydb` que estás usando.
2.  Los pasos exactos para reproducir el error.
3.  El comportamiento que esperabas y lo que realmente ocurrió.
4.  Cualquier registro de error (`traceback`) completo.

## Proponiendo Nuevas Funcionalidades

Nos encanta escuchar nuevas ideas. Abre un "Issue" y descríbela. Esto nos permite discutir la viabilidad de la característica antes de que se invierta tiempo en el desarrollo.

## Proceso de Desarrollo y Pull Requests

1.  **Haz un "Fork"** del repositorio y clónalo en tu máquina local.
2.  **Crea una nueva rama** para tus cambios: `git checkout -b feat/nombre-de-tu-funcionalidad`.
3.  **Configura el entorno de desarrollo**:
    ```bash
    # Crea y activa un entorno virtual
    python3 -m venv venv
    source venv/bin/activate
    
    # Instala el proyecto y las dependencias de desarrollo
    pip install -e ".[dev]"
    ```
4.  **Realiza tus cambios**. Asegúrate de seguir los estándares de código (PEP 8).
5.  **Añade pruebas unitarias** para cualquier nueva funcionalidad o corrección de bug.
6.  **Verifica que todas las pruebas pasen**:
    ```bash
    pytest
    ```
7.  **Haz "Commit"** de tus cambios con un mensaje claro y descriptivo.
8.  **Haz "Push"** a tu rama: `git push origin feat/nombre-de-tu-funcionalidad`.
9.  **Abre un Pull Request (PR)** en GitHub. Asegúrate de que la descripción del PR sea clara y explique los cambios que has realizado.

Una vez enviado, revisaremos tu PR lo antes posible. ¡Gracias de nuevo por tu contribución!