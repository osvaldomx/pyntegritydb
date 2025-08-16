# tests/test_alerts.py

import pytest
import pandas as pd
from pyntegritydb.alerts import check_thresholds

@pytest.fixture
def sample_data_for_alerts():
    """Prepara datos de prueba para verificar las alertas."""
    completeness_df = pd.DataFrame([
        # Esta fila viola el umbral de 'orders' (1.0)
        {"referencing_table": "orders", "validity_rate": 0.99},
        # Esta fila viola el umbral por defecto (0.95)
        {"referencing_table": "logs", "validity_rate": 0.94}
    ])
    
    consistency_df = pd.DataFrame([
        # Esta fila viola el umbral de consistencia por defecto (0.98)
        {
            "referencing_table": "shipments",
            "referencing_attribute": "product_name",
            "consistency_rate": 0.97
        }
    ])
    
    config = {
        "thresholds": {
            "default": {
                "validity_rate": 0.95,
                "consistency_rate": 0.98
            },
            "tables": {
                "orders": {
                    "validity_rate": 1.0
                }
            }
        }
    }
    return completeness_df, consistency_df, config

def test_check_thresholds_triggers_alerts(sample_data_for_alerts):
    """Prueba que se generen alertas cuando se violan los umbrales."""
    completeness_df, consistency_df, config = sample_data_for_alerts
    
    alerts = check_thresholds(completeness_df, consistency_df, config)
    
    assert len(alerts) == 3
    assert "ALERTA [Completitud]: La tabla 'orders'" in alerts[0]
    assert "ALERTA [Completitud]: La tabla 'logs'" in alerts[1]
    assert "ALERTA [Consistencia]: El atributo 'shipments.product_name'" in alerts[2]

def test_check_thresholds_no_alerts(sample_data_for_alerts):
    """Prueba que no se generen alertas si los datos son correctos."""
    _, _, config = sample_data_for_alerts
    
    # Datos que CUMPLEN con los umbrales
    good_completeness_df = pd.DataFrame([{"referencing_table": "orders", "validity_rate": 1.0}])
    good_consistency_df = pd.DataFrame([{"referencing_table": "shipments", "referencing_attribute": "a", "consistency_rate": 0.99}])

    alerts = check_thresholds(good_completeness_df, good_consistency_df, config)
    
    assert len(alerts) == 0