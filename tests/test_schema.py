import pytest
import networkx as nx
from unittest.mock import MagicMock, patch

from pyntegritydb.schema import get_schema_graph

@pytest.fixture
def mock_inspector():
    """Crea un mock del inspector de SQLAlchemy para las pruebas."""
    inspector = MagicMock()

    # Define la estructura de la base de datos simulada
    inspector.get_schema_names.return_value = ['public']
    inspector.get_table_names.return_value = ['users', 'orders', 'products', 'categories']

    # Define las claves foráneas simuladas
    def get_fks_side_effect(table_name, schema=None):
        if table_name == 'orders':
            return [
                {
                    'constrained_columns': ['user_id'],
                    'referred_table': 'users',
                    'referred_columns': ['id']
                },
                {
                    'constrained_columns': ['product_id'],
                    'referred_table': 'products',
                    'referred_columns': ['id']
                }
            ]
        return []

    inspector.get_foreign_keys.side_effect = get_fks_side_effect
    return inspector

def test_get_schema_graph_structure(mock_inspector):
    """
    Prueba que el grafo se construye correctamente a partir de un esquema simulado.
    """
    mock_engine = MagicMock() # No necesitamos un motor real, solo el inspector

    # Sobrescribimos 'get_db_inspector' para que devuelva nuestro mock
    with patch('pyntegritydb.schema.get_db_inspector', return_value=mock_inspector):
        graph = get_schema_graph(mock_engine)

    # Verificaciones sobre la estructura del grafo
    assert isinstance(graph, nx.DiGraph), "El resultado debe ser un DiGraph de NetworkX"
    assert graph.number_of_nodes() == 4, "Debe haber 4 tablas como nodos"
    assert graph.number_of_edges() == 2, "Debe haber 2 relaciones FK como arcos"

    # Verificaciones sobre las relaciones específicas
    assert graph.has_edge('orders', 'users'), "Debe existir una relación de 'orders' a 'users'"
    assert graph.has_edge('orders', 'products'), "Debe existir una relación de 'orders' a 'products'"
    assert not graph.has_edge('users', 'orders'), "La relación no debe ser bidireccional"

    # Verificación de los metadatos almacenados en el arco
    edge_data = graph.get_edge_data('orders', 'users')
    assert edge_data['constrained_columns'] == ['user_id']
    assert edge_data['referred_columns'] == ['id']