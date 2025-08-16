import pytest
import subprocess
import os
import sys
import yaml
from sqlalchemy import create_engine, text

# --- Constantes para los archivos de prueba ---
DB_PATH = "test_integration_db.sqlite"
CONFIG_PATH = "test_integration_config.yml"
REPORT_OUTPUT_PATH = "test_output_report.json"
IMAGE_OUTPUT_PATH = "test_output_graph.png"

def create_local_sqlite_db(db_uri: str):
    """
    Función auxiliar para crear una base de datos SQLite para pruebas locales.
    Usa la sintaxis de acentos graves (`) que es compatible con SQLite.
    """
    engine = create_engine(db_uri)
    statements = [
        'DROP TABLE IF EXISTS `orders`',
        'DROP TABLE IF EXISTS `users`',
        '''CREATE TABLE `users` (
            `id` INTEGER PRIMARY KEY, 
            `name` TEXT NOT NULL
        )''',
        '''CREATE TABLE `orders` (
            `order_id` INTEGER PRIMARY KEY, `user_id` INTEGER, `product` TEXT, 
            `customer_name` TEXT, FOREIGN KEY (`user_id`) REFERENCES `users`(`id`))''',
        "INSERT INTO `users` (`id`, `name`) VALUES (1, 'Alice'), (2, 'Bob')",
        "INSERT INTO `orders` (`order_id`, `user_id`, `product`, `customer_name`) VALUES (101, 1, 'Laptop', 'Alice')",
        "INSERT INTO `orders` (`order_id`, `user_id`, `product`, `customer_name`) VALUES (102, 2, 'Mouse', 'Bob')",
        "INSERT INTO `orders` (`order_id`, `user_id`, `product`, `customer_name`) VALUES (103, 1, 'Keyboard', 'Alicia')",
        "INSERT INTO `orders` (`order_id`, `user_id`, `product`, `customer_name`) VALUES (104, 99, 'Monitor', 'Charlie')"
    ]
    with engine.connect() as connection:
        with connection.begin():
            for stmt in statements:
                connection.execute(text(stmt))

@pytest.fixture(scope="module")
def test_environment():
    """
    Prepara el entorno para la prueba.
    En CI, las bases de datos (Postgres/MySQL) ya existen gracias a Docker.
    Para pruebas locales, crea una base de datos SQLite.
    """
    db_uri = os.getenv("DB_URI", f"sqlite:///{DB_PATH}")

    # Si estamos corriendo localmente, creamos la BD SQLite.
    if "sqlite" in db_uri:
        create_local_sqlite_db(db_uri)
    
    # Crear el archivo de configuración que se usará en todas las pruebas.
    config_data = {
        "thresholds": {
            "default": {
                "validity_rate": 0.95,
                "consistency_rate": 0.90
            }
        },
        "consistency_checks": {
            "orders": [{"on_fk": ["user_id"], "attributes": {"customer_name": "name"}}]
        }
    }
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config_data, f)
        
    yield db_uri  # Pasa la URI a la prueba
    
    # Limpieza posterior de todos los archivos generados
    for path in [DB_PATH, CONFIG_PATH, REPORT_OUTPUT_PATH, IMAGE_OUTPUT_PATH]:
        if os.path.exists(path):
            os.remove(path)

def test_cli_full_integration(test_environment):
    """
    Prueba el flujo completo: análisis, alertas, guardado de reporte y visualización.
    """
    db_uri = test_environment
    
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
    
    # Verificar que el programa terminó con un código de error debido a las alertas
    assert result.returncode == 1, f"El programa debería salir con código 1. STDOUT: {result.stdout}, STDERR: {result.stderr}"
    
    # Verificar que los archivos de salida fueron creados
    assert os.path.exists(REPORT_OUTPUT_PATH)
    assert os.path.exists(IMAGE_OUTPUT_PATH)
    
    # Verificar los mensajes clave en la salida de la consola
    output = result.stdout
    assert "Reporte guardado exitosamente" in output
    assert "Gráfico guardado exitosamente" in output
    assert "Se encontraron violaciones a los umbrales de calidad" in output