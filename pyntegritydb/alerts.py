# pyntegritydb/alerts.py

import pandas as pd

def check_thresholds(
    completeness_df: pd.DataFrame, 
    consistency_df: pd.DataFrame, 
    config: dict
) -> list:
    """
    Compara los resultados de las métricas con los umbrales definidos en la configuración.

    Args:
        completeness_df: DataFrame con los resultados del análisis de completitud.
        consistency_df: DataFrame con los resultados del análisis de consistencia.
        config: Diccionario de configuración cargado del archivo YAML.

    Returns:
        Una lista de mensajes de alerta si se viola algún umbral.
    """
    alerts = []
    if "thresholds" not in config:
        return alerts

    thresholds = config["thresholds"]
    default_thresholds = thresholds.get("default", {})
    table_specific_thresholds = thresholds.get("tables", {})

    # Revisar métricas de completitud
    for _, row in completeness_df.iterrows():
        table_name = row["referencing_table"]
        # Usa el umbral específico de la tabla o el umbral por defecto
        table_rules = table_specific_thresholds.get(table_name, default_thresholds)
        
        if "validity_rate" in table_rules:
            if row["validity_rate"] < table_rules["validity_rate"]:
                alerts.append(
                    f"ALERTA [Completitud]: La tabla '{table_name}' viola el umbral de 'validity_rate'. "
                    f"Esperado >= {table_rules['validity_rate']:.2%}, "
                    f"Obtenido = {row['validity_rate']:.2%}"
                )

    # Revisar métricas de consistencia
    if consistency_df is not None:
        for _, row in consistency_df.iterrows():
            table_name = row["referencing_table"]
            table_rules = table_specific_thresholds.get(table_name, default_thresholds)

            if "consistency_rate" in table_rules:
                if row["consistency_rate"] < table_rules["consistency_rate"]:
                    alerts.append(
                        f"ALERTA [Consistencia]: El atributo '{table_name}.{row['referencing_attribute']}' "
                        f"viola el umbral de 'consistency_rate'. "
                        f"Esperado >= {table_rules['consistency_rate']:.2%}, "
                        f"Obtenido = {row['consistency_rate']:.2%}"
                    )

    return alerts