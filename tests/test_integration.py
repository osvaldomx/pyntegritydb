# tests/test_integration.py

import pytest
import subprocess
import os
import sys
import yaml
from .setup_test_db import create_test_database

# --- Constantes para los archivos de prueba ---
DB_PATH = "test_integration_db.sqlite"
CONFIG_PATH = "test_integration_config.yml"
REPORT_OUTPUT_PATH = "test_output_report.json"
IMAGE_OUTPUT_PATH = "test_output_graph.png"

DB_URI_DEFAULT = f"sqlite:///{DB_PATH}"
DB_URI_FROM_ENV = os.getenv("DB_URI")

@pytest.fixture(scope="module")
def test_environment():
    """
    Fixture que crea todos los archivos necesarios antes de las pruebas
    y los elimina al finalizar.
    """
    # 1. Crear la base de datos de prueba
    create_test_database(DB_PATH)
    
    # 2. Crear el archivo de configuración de prueba
    config_data = {
        "thresholds": {
            "default": {
                "validity_rate": 0.95,      # Umbral que será violado (obtendremos 75%)
                "consistency_rate": 0.90    # Umbral que será violado (obtendremos 66.67%)
            }
        },
        "consistency_checks": {
            "orders": [{
                "on_fk": ["user_id"],
                "attributes": {"customer_name": "name"}
            }]
        }
    }
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config_data, f)
        
    yield # Aquí es donde se ejecutan las pruebas
    
    # 3. Limpieza posterior de todos los archivos generados
    for path in [DB_PATH, CONFIG_PATH, REPORT_OUTPUT_PATH, IMAGE_OUTPUT_PATH]:
        if os.path.exists(path):
            os.remove(path)

def test_cli_full_integration(test_environment):
    """
    Prueba el flujo completo: análisis, alertas, guardado de reporte y visualización.
    """
    db_uri = DB_URI_FROM_ENV if DB_URI_FROM_ENV else DB_URI_DEFAULT
    
    # Ejecuta el comando completo. Esperamos que falle (exit code 1) porque hay alertas.
    result = subprocess.run(
        [
            sys.executable, "-m", "pyntegritydb.cli", 
            db_uri, 
            "--config", CONFIG_PATH,
            "--format", "json", # Usamos JSON para facilitar la verificación del contenido
            "--output-file", REPORT_OUTPUT_PATH,
            "--visualize",
            "--output-image", IMAGE_OUTPUT_PATH
        ],
        capture_output=True,
        text=True
    )
    
    # --- Verificaciones ---

    # 1. Verificar que el programa terminó con un código de error debido a las alertas
    assert result.returncode == 1, "El programa debería salir con código 1 si hay alertas"
    
    # 2. Verificar que el archivo de reporte fue creado y no está vacío
    assert os.path.exists(REPORT_OUTPUT_PATH)
    assert os.path.getsize(REPORT_OUTPUT_PATH) > 0
    
    # 3. Verificar que el archivo de imagen fue creado
    assert os.path.exists(IMAGE_OUTPUT_PATH)
    assert os.path.getsize(IMAGE_OUTPUT_PATH) > 0
    
    # 4. Verificar los mensajes clave en la salida de la consola
    output = result.stdout
    assert "✅ Reporte guardado exitosamente" in output
    assert "✅ Gráfico guardado exitosamente" in output
    assert "❌ Se encontraron violaciones a los umbrales de calidad" in output