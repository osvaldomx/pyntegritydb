import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import networkx as nx

from pyntegritydb.cli import main

@patch('pyntegritydb.cli.report')
@patch('pyntegritydb.cli.metrics')
@patch('pyntegritydb.cli.schema')
@patch('pyntegritydb.cli.connect')
@patch('argparse.ArgumentParser.parse_args')
def test_main_cli_flow(
    mock_parse_args, mock_connect, mock_schema, mock_metrics, mock_report
):
    """
    Prueba el flujo completo de la CLI, simulando cada módulo.
    """
    # 1. Configuración de los mocks
    # Simular argumentos de línea de comandos
    mock_parse_args.return_value = MagicMock(db_uri="sqlite:///test.db", format="cli")
    
    # Simular un grafo y un dataframe de resultados
    mock_graph = nx.DiGraph()
    mock_graph.add_edge("table_a", "table_b")
    mock_df = pd.DataFrame({'validity_rate': [0.99]})

    # Asignar los valores de retorno a los módulos simulados
    mock_connect.create_db_engine.return_value = MagicMock()
    mock_schema.get_schema_graph.return_value = mock_graph
    mock_metrics.analyze_database_completeness.return_value = mock_df
    mock_report.generate_report.return_value = "Reporte de prueba"

    # 2. Ejecutar la función principal
    main()

    # 3. Verificaciones
    # Verificar que cada módulo fue llamado en el orden correcto
    mock_connect.create_db_engine.assert_called_once_with("sqlite:///test.db")
    mock_schema.get_schema_graph.assert_called_once()
    mock_metrics.analyze_database_completeness.assert_called_once()
    mock_report.generate_report.assert_called_once_with(mock_df, report_format="cli")

@patch('pyntegritydb.cli.connect.create_db_engine')
@patch('argparse.ArgumentParser.parse_args')
def test_main_cli_handles_connection_error(mock_parse_args, mock_create_engine):
    """
    Prueba que la CLI maneja correctamente un error de conexión.
    """
    # Simular argumentos
    mock_parse_args.return_value = MagicMock(db_uri="invalid_uri", format="cli")
    
    # Simular que la conexión falla
    mock_create_engine.side_effect = ValueError("Conexión fallida")

    # Ejecutar main y verificar que no se lance una excepción no controlada
    main()

    # Verificar que se intentó conectar
    mock_create_engine.assert_called_once_with("invalid_uri")