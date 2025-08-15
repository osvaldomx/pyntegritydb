# tests/test_integration.py

import pytest
import subprocess
import os
from .setup_test_db import create_test_database

DB_PATH = "test_integration_db.sqlite"

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