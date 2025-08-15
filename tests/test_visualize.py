# tests/test_visualize.py

import pytest
import pandas as pd
import networkx as nx
from unittest.mock import patch, MagicMock

from pyntegritydb.visualize import visualize_schema_graph, _get_color_from_rate

@pytest.fixture
def sample_data():
    """Crea un grafo y un DataFrame de ejemplo para las pruebas."""
    graph = nx.DiGraph()
    graph.add_edge("orders", "users")       # Tendrá alta validez -> verde
    graph.add_edge("logs", "events")        # Tendrá validez media -> naranja
    graph.add_edge("old_data", "archive")   # Tendrá baja validez -> rojo
    
    metrics_data = {
        'referencing_table': ['orders', 'logs', 'old_data'],
        'referenced_table': ['users', 'events', 'archive'],
        'validity_rate': [1.0, 0.95, 0.80],
    }
    metrics_df = pd.DataFrame(metrics_data)
    
    return graph, metrics_df

def test_get_color_from_rate():
    """Prueba la lógica de asignación de colores."""
    assert _get_color_from_rate(1.0) == 'green'
    assert _get_color_from_rate(0.995) == 'green'
    assert _get_color_from_rate(0.95) == 'orange'
    assert _get_color_from_rate(0.89) == 'red'
    assert _get_color_from_rate(float('nan')) == 'gray'

@patch('pyntegritydb.visualize.plt')
@patch('pyntegritydb.visualize.nx')
def test_visualize_schema_graph_calls(mock_nx, mock_plt, sample_data):
    """
    Prueba que las funciones de dibujo y guardado son llamadas correctamente.
    """
    graph, metrics_df = sample_data
    output_path = "test_graph.png"

    visualize_schema_graph(graph, metrics_df, output_path)

    # Verificar que se intentó dibujar el grafo
    assert mock_nx.draw_networkx_edges.called
    
    # Extraer los argumentos con los que se llamó a draw_networkx_edges
    # para verificar la lógica de los colores.
    call_args, call_kwargs = mock_nx.draw_networkx_edges.call_args
    edge_colors = call_kwargs.get('edge_color', [])
    
    # Verificar que los colores se asignaron correctamente según la lógica
    assert edge_colors == ['green', 'orange', 'red']

    # Verificar que se intentó guardar la figura
    mock_plt.savefig.assert_called_once_with(output_path, format='png', bbox_inches='tight')
    mock_plt.close.assert_called_once()