# pyntegritydb/report.py

import json
import pandas as pd
from tabulate import tabulate

def _format_completeness_cli(df: pd.DataFrame) -> str:
    """Formatea los resultados de completitud para la CLI."""
    if df.empty:
        return "No se encontraron relaciones de clave foránea para analizar.\n"

    df['validity_rate'] = (df['validity_rate'] * 100).map('{:.2f}%'.format)
    headers = {
        'referencing_table': 'Tabla de Origen',
        'referenced_table': 'Tabla de Destino',
        'validity_rate': 'Tasa de Validez',
        'orphan_rows_count': 'Filas Huérfanas',
        'total_rows': 'Total Filas'
    }
    display_df = df[headers.keys()].rename(columns=headers)
    
    table = tabulate(display_df, headers='keys', tablefmt='grid', showindex=False)
    
    summary = (
        f"\nResumen de Completitud:\n"
        f"------------------------\n"
        f"Relaciones analizadas: {len(df)}\n"
        f"Relaciones con filas huérfanas: {len(df[df['orphan_rows_count'] > 0])}\n"
    )
    return f"### Reporte de Completitud (Filas Huérfanas) ###\n{table}{summary}"

def _format_consistency_cli(df: pd.DataFrame) -> str:
    """Formatea los resultados de consistencia para la CLI."""
    if df.empty:
        return "" # No muestra nada si no hay análisis de consistencia

    df['consistency_rate'] = (df['consistency_rate'] * 100).map('{:.2f}%'.format)
    headers = {
        'referencing_table': 'Tabla de Origen',
        'referencing_attribute': 'Atributo de Origen',
        'referenced_attribute': 'Atributo de Destino',
        'consistency_rate': 'Tasa de Consistencia',
        'inconsistent_rows': 'Filas Inconsistentes'
    }
    display_df = df[headers.keys()].rename(columns=headers)

    table = tabulate(display_df, headers='keys', tablefmt='grid', showindex=False)
    return f"\n### Reporte de Consistencia de Atributos ###\n{table}\n"

def _format_alerts_cli(alerts: list) -> str:
    """Formatea la sección de alertas para la CLI."""
    if not alerts:
        return ""
    
    header = "🚦 Reporte de Alertas 🚦"
    separator = "=" * len(header)
    # Une cada mensaje de alerta con un salto de línea
    alerts_text = "\n".join(f"- {msg}" for msg in alerts)
    
    return f"{header}\n{separator}\n{alerts_text}\n\n"

def generate_report(
    completeness_df: pd.DataFrame, 
    consistency_df: pd.DataFrame | None = None,
    alerts: list | None = None,
    report_format: str = 'cli'
) -> str:
    """
    Genera un reporte de los resultados de las métricas en el formato especificado.

    Args:
        df: DataFrame de Pandas con los resultados del módulo de métricas.
        report_format: El formato de salida ('cli', 'json', 'csv').

    Returns:
        Una cadena de texto con el reporte formateado.
        
    Raises:
        ValueError: Si el formato de reporte no es soportado.
    """
    if report_format == 'cli':
        # Combina los reportes de completitud y consistencia
        alerts_report = _format_alerts_cli(alerts if alerts else [])
        completeness_report = _format_completeness_cli(completeness_df)
        consistency_report = _format_consistency_cli(consistency_df) if consistency_df is not None and not consistency_df.empty else ""
        return f"{alerts_report}{completeness_report}{consistency_report}"

    elif report_format == 'json':
        # Devuelve un objeto JSON con dos claves principales
        report_data = {
            "alerts": alerts if alerts else [],
            "completeness_analysis": completeness_df.to_dict(orient='records'),
            "consistency_analysis": consistency_df.to_dict(orient='records') if consistency_df is not None else []
        }
        return json.dumps(report_data, indent=4)

    elif report_format == 'csv':
        # Para CSV, es mejor devolver solo el reporte principal
        # o requerir dos archivos de salida. Por ahora, solo devolvemos el de completitud.
        print("Advertencia: El formato CSV solo exportará el análisis de completitud.")
        return completeness_df.to_csv(index=False)
        
    else:
        raise ValueError(f"Formato de reporte no soportado: '{report_format}'. Opciones válidas: 'cli', 'json', 'csv'.")
