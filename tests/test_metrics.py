import pytest
import pandas as pd
import networkx as nx
from unittest.mock import MagicMock, patch

from pyntegritydb.metrics import _calculate_fk_completeness, analyze_database_completeness

@pytest.fixture
def mock_engine_connect():
    """Fixture que simula una conexión y un resultado de consulta exitoso."""
    # Simula el objeto 'result' que devuelve SQLAlchemy
    mock_result = MagicMock()
    mock_result.mappings.return_value.first.return_value = {
        'total_rows': 100,
        'orphan_rows': 5,
        'null_rows': 10
    }
    
    # Simula el gestor de contexto 'with engine.connect() as connection:'
    mock_connection = MagicMock()
    mock_connection.__enter__.return_value.execute.return_value = mock_result
    
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_connection
    return mock_engine

def test_calculate_fk_completeness_logic(mock_engine_connect):
    """
    Prueba la lógica de cálculo de la función auxiliar con datos simulados.
    """
    metrics = _calculate_fk_completeness(
        mock_engine_connect, "orders", ["user_id"], "users", ["id"]
    )

    assert metrics['total_rows'] == 100
    assert metrics['orphan_rows_count'] == 5
    assert metrics['valid_rows_count'] == 95
    assert metrics['null_rows_count'] == 10
    assert metrics['orphan_rate'] == 0.05
    assert metrics['validity_rate'] == 0.95
    assert metrics['fk_density'] == 0.90

def test_analyze_database_completeness_flow():
    """
    Prueba el flujo de la función principal: que itere el grafo y devuelva un DataFrame.
    """
    # 1. Crear un grafo de prueba
    test_graph = nx.DiGraph()
    test_graph.add_edge(
        "orders", "users", 
        constrained_columns=["user_id"], referred_columns=["id"]
    )
    
    # 2. Simular la función de cálculo para que siempre devuelva lo mismo
    mock_metrics_result = {'total_rows': 100, 'validity_rate': 0.95}
    
    # 3. 'patch' para reemplazar la función de cálculo real por nuestro mock
    with patch('pyntegritydb.metrics._calculate_fk_completeness', return_value=mock_metrics_result) as mock_calculator:
        df_results = analyze_database_completeness(MagicMock(), test_graph)

        # 4. Verificaciones
        mock_calculator.assert_called_once() # Verificar que se llamó al calculador
        assert isinstance(df_results, pd.DataFrame)
        assert len(df_results) == 1 # Debe haber una fila por cada relación en el grafo
        assert df_results.iloc[0]['referencing_table'] == 'orders'
        assert df_results.iloc[0]['validity_rate'] == 0.95