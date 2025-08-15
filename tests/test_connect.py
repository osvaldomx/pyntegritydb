import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError

from pyntegritydb.connect import create_db_engine

def test_create_db_engine_success():
    """
    Prueba que el motor se crea exitosamente con una URI válida.
    Utilizamos un 'mock' para simular SQLAlchemy y no requerir una BD real.
    """
    # Usamos patch para reemplazar 'create_engine' de SQLAlchemy con un mock
    with patch('pyntegritydb.connect.create_engine') as mock_create_engine:
        # Configuramos el mock para que se comporte como si la conexión fuera exitosa
        mock_engine = MagicMock()
        mock_engine.dialect.name = 'sqlite'
        mock_create_engine.return_value = mock_engine

        # La URI es para una base de datos en memoria (no se crea realmente)
        uri = "sqlite:///:memory:"
        engine = create_db_engine(uri)

        # Verificamos que se llamó a create_engine con la URI correcta
        mock_create_engine.assert_called_once_with(uri)
        # Verificamos que el motor devuelto es el que simulamos
        assert engine is not None
        assert engine.dialect.name == 'sqlite'

def test_create_db_engine_invalid_uri():
    """
    Prueba que se lanza un ValueError si la URI es claramente inválida.
    """
    # pytest.raises verifica que el código dentro del bloque 'with'
    # lanza la excepción esperada.
    with pytest.raises(ValueError, match="La URI de conexión proporcionada es inválida"):
        create_db_engine("esto_no_es_una_uri")

def test_create_db_engine_connection_failure():
    """
    Prueba que se lanza un ValueError si SQLAlchemy no puede conectar a la BD.
    """
    with patch('pyntegritydb.connect.create_engine') as mock_create_engine:
        # Configuramos el mock para que falle al intentar conectar
        mock_engine = MagicMock()
        # Simulamos un error de conexión (ej. contraseña incorrecta)
        mock_engine.connect.side_effect = OperationalError("test error", {}, "")
        mock_create_engine.return_value = mock_engine

        uri = "postgresql://user:wrong_pass@host/db"
        
        with pytest.raises(ValueError, match="No se pudo conectar a la base de datos"):
            create_db_engine(uri)