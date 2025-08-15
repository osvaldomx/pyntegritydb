# tests/test_integration.py

import pytest
import subprocess
import os
import sys
import yaml
from .setup_test_db import create_test_database

DB_PATH = "test_integration_db.sqlite"
CONFIG_PATH = "test_config.yml"

@pytest.fixture(scope="module")
def test_db():
    """
    Fixture de Pytest que crea la base de datos antes de las pruebas
    y la elimina después de que todas las pruebas en el módulo hayan terminado.
    """
    create_test_database(DB_PATH)
    yield
    os.remove(DB_PATH)

def test_cli_end_to_end_run(test_db):
    """
    Ejecuta la CLI como un subproceso contra la base de datos de prueba
    y verifica que la salida contenga los resultados esperados.
    """
    # Construye la URI para la base de datos de prueba
    db_uri = f"sqlite:///{DB_PATH}"
    
    # Ejecuta el comando pyntegritydb desde la línea de comandos
    result = subprocess.run(
        ["pyntegritydb", db_uri, "--format", "cli"],
        capture_output=True,
        text=True,
        check=True  # Lanza una excepción si el comando falla
    )
    
    # Verifica que la salida no esté vacía y no contenga errores
    assert result.stderr == ""
    output = result.stdout
    
    # Verifica los puntos clave del reporte generado
    assert "Reporte de Integridad Referencial" in output
    assert "orders" in output  # Nombre de la tabla de origen
    assert "users" in output   # Nombre de la tabla de destino
    
    # Verifica los resultados numéricos esperados
    # (4 filas en total, 1 huérfana -> 75% de validez)
    assert "75.00%" in output           # Tasa de Validez
    assert "1" in output                # Filas Huérfanas
    assert "4" in output                # Total Filas
    assert "Relaciones con filas huérfanas: 1" in output # Resumen


def test_cli_consistency_end_to_end_run(test_db):
    """
    Ejecuta la CLI con un archivo de configuración para probar el análisis
    de consistencia de atributos.
    """
    # 1. Crear el archivo de configuración temporal
    config_data = {
        "consistency_checks": {
            "orders": [
                {
                    "on_fk": ["user_id"],
                    "attributes": {
                        "customer_name": "name"
                    }
                }
            ]
        }
    }
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config_data, f)
    
    db_uri = f"sqlite:///{DB_PATH}"

    try:
        # 2. Ejecutar el comando pyntegritydb con el argumento --config
        result = subprocess.run(
            [
                sys.executable, "-m", "pyntegritydb.cli", 
                db_uri, 
                "--format", "cli",
                "--config", CONFIG_PATH # 👇 Argumento para la nueva funcionalidad
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        output = result.stdout
        
        # 3. Verificar la salida del reporte de consistencia
        assert "Analizando consistencia de atributos" in output
        assert "Verificando: orders.customer_name vs users.name" in output
        # (De 3 filas con FK válida, 1 es inconsistente -> 66.67% de consistencia)
        # Aquí buscaríamos el reporte de consistencia, que aún no hemos diseñado.
        # Por ahora, verificamos que el análisis se haya ejecutado.
        
    finally:
        # 4. Limpiar el archivo de configuración temporal
        os.remove(CONFIG_PATH)