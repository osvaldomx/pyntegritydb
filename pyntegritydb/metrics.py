import pandas as pd
import networkx as nx
from sqlalchemy.engine import Engine
from sqlalchemy import text


def _calculate_fk_completeness(
    engine: Engine, 
    referencing_table: str, 
    referencing_columns: list, 
    referenced_table: str, 
    referenced_columns: list
) -> dict:
    """
    Función auxiliar que calcula las métricas para una única relación FK.
    
    Ejecuta una única consulta SQL optimizada con LEFT JOIN para obtener
    los conteos necesarios y luego calcula las tasas y densidades.
    """
    # Construcción robusta de la consulta para manejar claves simples y compuestas
    join_condition = " AND ".join(
        f't1."{ref_col}" = t2."{pk_col}"'
        for ref_col, pk_col in zip(referencing_columns, referenced_columns)
    )
    
    # Una fila es huérfana si, tras el join, la PK de la tabla referenciada es NULL
    orphan_condition = " OR ".join(f't2."{pk_col}" IS NULL' for pk_col in referenced_columns)
    
    # Una FK es nula si cualquiera de sus columnas en la tabla de origen es NULL
    null_fk_condition = " OR ".join(f't1."{ref_col}" IS NULL' for ref_col in referencing_columns)

    query = text(f"""
    SELECT
        COUNT(*) AS total_rows,
        COUNT(CASE WHEN {orphan_condition} THEN 1 END) AS orphan_rows,
        COUNT(CASE WHEN {null_fk_condition} THEN 1 END) AS null_rows
    FROM
        "{referencing_table}" AS t1
    LEFT JOIN
        "{referenced_table}" AS t2 ON {join_condition}
    """)
    
    try:
        with engine.connect() as connection:
            result = connection.execute(query).mappings().first()
    except Exception as e:
        print(f"❌ Error al ejecutar la consulta para {referencing_table} -> {referenced_table}: {e}")
        return {
            'error': str(e)
        }

    total_rows = result.get('total_rows', 0)
    orphan_rows = result.get('orphan_rows', 0)
    null_rows = result.get('null_rows', 0)
    
    # Evitar división por cero si la tabla está vacía
    if total_rows == 0:
        return {
            'total_rows': 0,
            'orphan_rows_count': 0,
            'valid_rows_count': 0,
            'null_rows_count': 0,
            'orphan_rate': 0.0,
            'validity_rate': 1.0,
            'fk_density': 1.0,
        }
        
    valid_rows = total_rows - orphan_rows
    
    return {
        'total_rows': total_rows,
        'orphan_rows_count': orphan_rows,
        'valid_rows_count': valid_rows,
        'null_rows_count': null_rows,
        'orphan_rate': orphan_rows / total_rows,
        'validity_rate': valid_rows / total_rows,
        'fk_density': (total_rows - null_rows) / total_rows,
    }


def _calculate_single_consistency(engine: Engine, check_details: dict) -> dict:
    """Calcula la consistencia para un par de atributos específico."""
    ref_table = check_details['referencing_table']
    pk_table = check_details['referenced_table']
    ref_attr = check_details['referencing_attribute']
    pk_attr = check_details['referenced_attribute']
    join_condition = check_details['join_condition']

    # Esta consulta solo opera sobre filas donde la FK es válida (INNER JOIN)
    # y compara los valores de los atributos especificados.
    query = text(f"""
    SELECT
        COUNT(*) AS total_valid_rows,
        COUNT(CASE 
            WHEN (t1."{ref_attr}" != t2."{pk_attr}") OR 
                 (t1."{ref_attr}" IS NULL AND t2."{pk_attr}" IS NOT NULL) OR
                 (t1."{ref_attr}" IS NOT NULL AND t2."{pk_attr}" IS NULL)
            THEN 1 
            END) AS inconsistent_rows
    FROM
        "{ref_table}" AS t1
    INNER JOIN
        "{pk_table}" AS t2 ON {join_condition}
    """)
    
    with engine.connect() as connection:
        result = connection.execute(query).mappings().first()
    
    total_rows = result.get('total_valid_rows', 0)
    inconsistent = result.get('inconsistent_rows', 0)

    if total_rows == 0:
        return {'total_valid_rows': 0, 'inconsistent_rows': 0, 'consistency_rate': 1.0}

    return {
        'total_valid_rows': total_rows,
        'inconsistent_rows': inconsistent,
        'consistency_rate': (total_rows - inconsistent) / total_rows
    }


def analyze_attribute_consistency(
        engine: Engine, 
        schema_graph: nx.DiGraph, 
        config: dict) -> pd.DataFrame:
    """
    Analiza la consistencia de atributos basado en la configuración proporcionada.
    """
    if "consistency_checks" not in config:
        return pd.DataFrame()

    results = []
    checks = config["consistency_checks"]

    print("\n🔬 Analizando consistencia de atributos...")

    for ref_table, check_list in checks.items():
        for check_item in check_list:
            fk_origin_cols = check_item['on_fk']
            
            # Encontrar la relación en el grafo para obtener la tabla y columnas de destino
            target_edge = None
            for u, v, data in schema_graph.edges(data=True):
                if u == ref_table and data['constrained_columns'] == fk_origin_cols:
                    target_edge = (u, v, data)
                    break
            
            if not target_edge:
                print(f"⚠️  Advertencia: No se encontró la relación FK '{fk_origin_cols}' en la tabla '{ref_table}'. Saltando chequeo.")
                continue

            pk_table = target_edge[1]
            fk_dest_cols = target_edge[2]['referred_columns']

            join_condition = " AND ".join(
                f't1."{orig}" = t2."{dest}"' for orig, dest in zip(fk_origin_cols, fk_dest_cols)
            )

            for ref_attr, pk_attr in check_item['attributes'].items():
                print(f"  -> Verificando: {ref_table}.{ref_attr} vs {pk_table}.{pk_attr}")
                check_details = {
                    'referencing_table': ref_table,
                    'referenced_table': pk_table,
                    'referencing_attribute': ref_attr,
                    'referenced_attribute': pk_attr,
                    'join_condition': join_condition
                }
                
                metrics = _calculate_single_consistency(engine, check_details)
                results.append({**check_details, **metrics})

    print("✅ Análisis de consistencia completado.")
    return pd.DataFrame(results)


def analyze_database_completeness(
        engine: Engine, 
        schema_graph: nx.DiGraph) -> pd.DataFrame:
    """
    Analiza todas las relaciones FK en el grafo y calcula sus métricas de completitud.

    Itera sobre cada arco del grafo, invoca al calculador de métricas y consolida
    los resultados en un único DataFrame de Pandas.

    Args:
        engine: El motor de SQLAlchemy.
        schema_graph: El grafo del esquema de la base de datos.

    Returns:
        Un DataFrame de Pandas con los resultados de las métricas para cada FK.
    """
    results = []
    
    print(f"\n🚀 Analizando {schema_graph.number_of_edges()} relaciones...")
    
    for u, v, data in schema_graph.edges(data=True):
        referencing_table = u
        referenced_table = v
        
        print(f"  -> Calculando: {referencing_table} -> {referenced_table}")
        
        metrics = _calculate_fk_completeness(
            engine,
            referencing_table,
            data['constrained_columns'],
            referenced_table,
            data['referred_columns']
        )
        
        if 'error' in metrics:
            # Si hubo un error, se añade a los resultados para informar al usuario
            results.append({
                'referencing_table': referencing_table,
                'referenced_table': referenced_table,
                'fk_columns': ', '.join(data['constrained_columns']),
                'error': metrics['error'],
            })
        else:
            results.append({
                'referencing_table': referencing_table,
                'referenced_table': referenced_table,
                'fk_columns': ', '.join(data['constrained_columns']),
                **metrics
            })
            
    print("✅ Análisis completado.")
    return pd.DataFrame(results)
