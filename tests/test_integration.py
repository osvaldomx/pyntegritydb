# tests/test_integration.py

import pytest
import subprocess
import os
import sys
import yaml
from .setup_test_db import create_test_database

DB_PATH = "test_integration_db.sqlite"
CONFIG_PATH = "test_integration_config.yml"

@pytest.fixture(scope="module")
def test_db_and_config():
    """
    Fixture que crea la base de datos y el archivo de configuración antes de las pruebas
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
    
    # 3. Limpieza posterior
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)

def test_cli_full_integration_with_alerts(test_db_and_config):
    """
    Prueba el flujo completo de la aplicación, incluyendo la generación de alertas.
    """
    db_uri = f"sqlite:///{DB_PATH}"
    
    # Ejecuta el comando. Esperamos que falle (exit code 1) porque hay alertas.
    # Por eso, NO usamos check=True.
    result = subprocess.run(
        [
            sys.executable, "-m", "pyntegritydb.cli", 
            db_uri, 
            "--config", CONFIG_PATH,
            "--format", "cli"
        ],
        capture_output=True,
        text=True
    )
    
    # 1. Verificar que el programa terminó con un código de error
    assert result.returncode == 1, "El programa debería salir con código 1 si hay alertas"
    
    output = result.stdout
    
    # 2. Verificar la sección de Alertas
    assert "🚦 Reporte de Alertas 🚦" in output
    assert "ALERTA [Completitud]: La tabla 'orders' viola el umbral de 'validity_rate'" in output
    assert "ALERTA [Consistencia]: El atributo 'orders.customer_name' viola el umbral de 'consistency_rate'" in output
    
    # 3. Verificar el reporte de Completitud
    assert "Reporte de Completitud (Filas Huérfanas)" in output
    assert "75.00%" in output  # 3 de 4 filas válidas
    
    # 4. Verificar el reporte de Consistencia
    assert "Reporte de Consistencia de Atributos" in output
    assert "66.67%" in output # 2 de 3 filas consistentes