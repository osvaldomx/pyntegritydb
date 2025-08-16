import pytest
import pandas as pd
import json

from pyntegritydb.report import generate_report

@pytest.fixture
def sample_metrics_df():
    """Crea un DataFrame de ejemplo para usar en las pruebas."""
    data = {
        'referencing_table': ['orders', 'order_items'],
        'referenced_table': ['users', 'products'],
        'fk_columns': ['user_id', 'product_id'],
        'total_rows': [1000, 5000],
        'orphan_rows_count': [50, 0],
        'valid_rows_count': [950, 5000],
        'null_rows_count': [10, 20],
        'orphan_rate': [0.05, 0.0],
        'validity_rate': [0.95, 1.0],
        'fk_density': [0.99, 0.996]
    }
    return pd.DataFrame(data)

def test_generate_report_cli_format(sample_metrics_df):
    """Prueba que el formato CLI se genere y contenga los datos clave."""
    report = generate_report(
        completeness_df=sample_metrics_df,
        alerts=[],
        report_format='cli'
    )
    assert isinstance(report, str)
    assert 'Tasa de Validez' in report
    assert '95.00%' in report
    assert 'orders' in report
    assert 'Resumen de Completitud' in report
    assert "🚦 Reporte de Alertas 🚦" not in report

def test_generate_report_json_format(sample_metrics_df):
    """Prueba que el formato JSON sea válido y contenga los datos correctos."""
    report = generate_report(
        completeness_df=sample_metrics_df,
        alerts=[],
        report_format='json'
    )
    data = json.loads(report)
    
    assert isinstance(data, dict)
    assert 'completeness_analysis' in data
    assert 'consistency_analysis' in data
    assert data['completeness_analysis'][0]['validity_rate'] == 0.95

def test_generate_report_csv_format(sample_metrics_df):
    """Prueba que el formato CSV se genere con el encabezado y datos correctos."""
    report = generate_report(
        completeness_df=sample_metrics_df,
        alerts=[],
        report_format='csv'
    )
    
    assert isinstance(report, str)
    lines = report.strip().split('\n')
    assert len(lines) == 3  # 1 encabezado + 2 filas de datos
    assert lines[0] == 'referencing_table,referenced_table,fk_columns,total_rows,orphan_rows_count,valid_rows_count,null_rows_count,orphan_rate,validity_rate,fk_density'
    assert lines[1].startswith('orders,users,user_id')

def test_generate_report_unsupported_format(sample_metrics_df):
    """Prueba que se lance un ValueError para un formato no soportado."""
    with pytest.raises(ValueError, match="Formato de reporte no soportado: 'xml'"):
        generate_report(
            completeness_df=sample_metrics_df, 
            report_format='xml'
        )


def test_generate_report_with_alerts_cli(sample_metrics_df):
    """Prueba que la sección de alertas se muestre en el reporte CLI."""
    alerts = ["ALERTA: La tabla 'orders' tiene una validez de 95.00%"]
    
    report = generate_report(
        completeness_df=sample_metrics_df,
        alerts=alerts,
        report_format='cli'
    )
    
    assert "🚦 Reporte de Alertas 🚦" in report
    assert "ALERTA: La tabla 'orders'" in report

def test_generate_report_with_alerts_json(sample_metrics_df):
    """Prueba que las alertas se incluyan en el reporte JSON."""
    alerts = ["ALERTA: Test"]
    
    report = generate_report(
        completeness_df=sample_metrics_df,
        alerts=alerts,
        report_format='json'
    )
    data = json.loads(report)
    
    assert "alerts" in data
    assert data["alerts"] == alerts







