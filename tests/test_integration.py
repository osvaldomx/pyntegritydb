# tests/test_integration.py

import pytest
import subprocess
import os
import sys
import yaml
from sqlalchemy import create_engine, text
from .setup_test_db import create_test_schema

# --- Constantes para los archivos de prueba ---
DB_PATH = "test_integration_db.sqlite"
CONFIG_PATH = "test_integration_config.yml"
REPORT_OUTPUT_PATH = "test_output_report.json"
IMAGE_OUTPUT_PATH = "test_output_graph.png"

@pytest.fixture(scope="module")
def test_db():
    """Fixture que crea y limpia solo la base de datos."""
    db_uri = os.getenv("DB_URI", f"sqlite:///{DB_PATH}")
    
    # Esta función necesita create_engine y text, que ahora están importados
    create_test_schema(db_uri) 
    
    # La prueba necesita insertar datos también
    engine = create_engine(db_uri)
    dialect = engine.dialect.name
    data_statements = [
        "INSERT INTO `users` (`id`, `name`) VALUES (1, 'Alice'), (2, 'Bob')",
        "INSERT INTO `orders` (`order_id`, `user_id`, `product`, `customer_name`) VALUES (101, 1, 'Laptop', 'Alice')",
        "INSERT INTO `orders` (`order_id`, `user_id`, `product`, `customer_name`) VALUES (102, 2, 'Mouse', 'Bob')",
        "INSERT INTO `orders` (`order_id`, `user_id`, `product`, `customer_name`) VALUES (103, 1, 'Keyboard', 'Alicia')",
        "INSERT INTO `orders` (`order_id`, `user_id`, `product`, `customer_name`) VALUES (104, 99, 'Monitor', 'Charlie')"
    ]
    
    with engine.connect() as connection:
        if dialect == 'mysql':
            connection.execute(text('SET FOREIGN_KEY_CHECKS=0;'))
        elif dialect == 'postgresql':
            connection.execute(text('SET session_replication_role = replica'))
        
        with connection.begin():
            for stmt in data_statements:
                connection.execute(text(stmt))

        if dialect == 'mysql':
            connection.execute(text('SET FOREIGN_KEY_CHECKS=1;'))
        elif dialect == 'postgresql':
            connection.execute(text('SET session_replication_role = DEFAULT'))
            
    yield db_uri  # Pasa la URI a la prueba
    
    if "sqlite" in db_uri and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_cli_full_integration(test_db):
    """
    Prueba el flujo completo: análisis, alertas, guardado de reporte y visualización.
    """
    db_uri = test_db # Recibe la URI desde la fixture

    config_data = {
        "thresholds": {
            "default": {"validity_rate": 0.95, "consistency_rate": 0.90}
        },
        "consistency_checks": {
            "orders": [{"on_fk": ["user_id"], "attributes": {"customer_name": "name"}}]
        }
    }
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config_data, f)

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pyntegritydb.cli",
                db_uri,
                "--config", CONFIG_PATH,
                "--format", "json",
                "--output-file", REPORT_OUTPUT_PATH,
                "--visualize",
                "--output-image", IMAGE_OUTPUT_PATH
            ],
            capture_output=True,
            text=True
        )
        
        # --- Verificaciones ---
        assert result.returncode == 1, f"El programa debería salir con código 1. STDOUT: {result.stdout}, STDERR: {result.stderr}"
        
        output = result.stdout
        assert os.path.exists(REPORT_OUTPUT_PATH)
        assert os.path.exists(IMAGE_OUTPUT_PATH)
        assert "Reporte guardado exitosamente" in output
        assert "Gráfico guardado exitosamente" in output
        assert "Se encontraron violaciones a los umbrales de calidad" in output

    finally:
        # Limpieza de los archivos generados por la prueba
        for path in [CONFIG_PATH, REPORT_OUTPUT_PATH, IMAGE_OUTPUT_PATH]:
            if os.path.exists(path):
                os.remove(path)