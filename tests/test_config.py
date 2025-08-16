import pytest
from unittest.mock import patch, mock_open

from pyntegritydb.config import load_config

def test_load_config_success():
    """
    Prueba la carga exitosa de un archivo de configuración YAML válido.
    """
    # Contenido YAML simulado
    mock_yaml_content = """
    thresholds:
      default:
        validity_rate: 0.99
        orphan_rate: 0.01
      tables:
        orders:
          validity_rate: 1.0
    """
    
    # Simula la apertura y lectura del archivo
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)) as mock_file:
        config = load_config("dummy/path/config.yml")

        # Verificaciones
        mock_file.assert_called_once_with("dummy/path/config.yml", "r")
        assert "thresholds" in config
        assert config["thresholds"]["default"]["validity_rate"] == 0.99
        assert config["thresholds"]["tables"]["orders"]["validity_rate"] == 1.0

def test_load_config_file_not_found():
    """
    Prueba que se lance un FileNotFoundError si el archivo no existe.
    """
    # Simula el error FileNotFoundError al intentar abrir el archivo
    with patch("builtins.open", side_effect=FileNotFoundError) as mock_file:
        with pytest.raises(FileNotFoundError, match="No se encontró el archivo"):
            load_config("non_existent_file.yml")

def test_load_config_invalid_yaml():
    """
    Prueba que se lance un ValueError si el archivo YAML está malformado.
    """
    mock_invalid_yaml = "thresholds:\n  default:\n    validity_rate: 0.99\n- unindent_error"
    
    with patch("builtins.open", mock_open(read_data=mock_invalid_yaml)):
        with pytest.raises(ValueError, match="Error al parsear el archivo YAML"):
            load_config("invalid.yml")

