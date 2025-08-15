# pyntegritydb/report.py

import json
import pandas as pd
from tabulate import tabulate

def _format_cli(df: pd.DataFrame) -> str:
    """Formatea los resultados en una tabla bonita para la línea de comandos."""
    if df.empty:
        return "No se encontraron relaciones para analizar."

    # Seleccionar y renombrar columnas para una mejor legibilidad
    display_df = df.copy()
    display_df['validity_rate'] = (display_df['validity_rate'] * 100).map('{:.2f}%'.format)
    display_df['orphan_rate'] = (display_df['orphan_rate'] * 100).map('{:.2f}%'.format)
    display_df['fk_density'] = (display_df['fk_density'] * 100).map('{:.2f}%'.format)
    
    headers = {
        'referencing_table': 'Tabla de Origen',
        'referenced_table': 'Tabla de Destino',
        'validity_rate': 'Tasa de Validez',
        'orphan_rows_count': 'Filas Huérfanas',
        'total_rows': 'Total Filas'
    }
    
    display_df = display_df[headers.keys()].rename(columns=headers)
    
    # Crear la tabla usando tabulate
    table = tabulate(display_df, headers='keys', tablefmt='grid', showindex=False)
    
    # Añadir un resumen
    total_relations = len(df)
    relations_with_orphans = len(df[df['orphan_rows_count'] > 0])
    summary = (
        f"\nResumen del Análisis:\n"
        f"---------------------\n"
        f"Relaciones analizadas: {total_relations}\n"
        f"Relaciones con filas huérfanas: {relations_with_orphans}\n"
    )
    
    return table + summary

def _format_json(df: pd.DataFrame) -> str:
    """Convierte los resultados a un formato JSON (lista de objetos)."""
    return df.to_json(orient='records', indent=4)

def _format_csv(df: pd.DataFrame) -> str:
    """Convierte los resultados a formato CSV."""
    return df.to_csv(index=False)

def generate_report(df: pd.DataFrame, report_format: str = 'cli') -> str:
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
        return _format_cli(df)
    elif report_format == 'json':
        return _format_json(df)
    elif report_format == 'csv':
        return _format_csv(df)
    else:
        raise ValueError(f"Formato de reporte no soportado: '{report_format}'. Opciones válidas: 'cli', 'json', 'csv'.")