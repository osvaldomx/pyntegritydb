# pyntegritydb/report.py

import json
import pandas as pd
from tabulate import tabulate

# def _format_cli(df: pd.DataFrame) -> str:
#     """Formatea los resultados en una tabla bonita para la línea de comandos."""
#     if df.empty:
#         return "No se encontraron relaciones para analizar."

#     # Seleccionar y renombrar columnas para una mejor legibilidad
#     display_df = df.copy()
#     display_df['validity_rate'] = (display_df['validity_rate'] * 100).map('{:.2f}%'.format)
#     display_df['orphan_rate'] = (display_df['orphan_rate'] * 100).map('{:.2f}%'.format)
#     display_df['fk_density'] = (display_df['fk_density'] * 100).map('{:.2f}%'.format)
    
#     headers = {
#         'referencing_table': 'Tabla de Origen',
#         'referenced_table': 'Tabla de Destino',
#         'validity_rate': 'Tasa de Validez',
#         'orphan_rows_count': 'Filas Huérfanas',
#         'total_rows': 'Total Filas'
#     }
    
#     display_df = display_df[headers.keys()].rename(columns=headers)
    
#     # Crear la tabla usando tabulate
#     table = tabulate(display_df, headers='keys', tablefmt='grid', showindex=False)
    
#     # Añadir un resumen
#     total_relations = len(df)
#     relations_with_orphans = len(df[df['orphan_rows_count'] > 0])
#     summary = (
#         f"\nResumen del Análisis:\n"
#         f"---------------------\n"
#         f"Relaciones analizadas: {total_relations}\n"
#         f"Relaciones con filas huérfanas: {relations_with_orphans}\n"
#     )
    
#     return table + summary

# def _format_json(df: pd.DataFrame) -> str:
#     """Convierte los resultados a un formato JSON (lista de objetos)."""
#     return df.to_json(orient='records', indent=4)

# def _format_csv(df: pd.DataFrame) -> str:
#     """Convierte los resultados a formato CSV."""
#     return df.to_csv(index=False)

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

def generate_report(
    completeness_df: pd.DataFrame, 
    consistency_df: pd.DataFrame = None, 
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
        completeness_report = _format_completeness_cli(completeness_df)
        consistency_report = _format_consistency_cli(consistency_df) if consistency_df is not None and not consistency_df.empty else ""
        return f"{completeness_report}{consistency_report}"

    elif report_format == 'json':
        # Devuelve un objeto JSON con dos claves principales
        report_data = {
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
