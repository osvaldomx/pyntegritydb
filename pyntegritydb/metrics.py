import pandas as pd
import networkx as nx
from sqlalchemy.engine import Engine
from sqlalchemy import text

def _get_quoted_name(name: str, dialect: str) -> str:
    """Devuelve el nombre del identificador con las comillas correctas para el dialecto."""
    if dialect == 'mysql':
        return f'`{name}`'
    return f'"{name}"'

def _calculate_fk_completeness(
    engine: Engine, 
    referencing_table: str, 
    referencing_columns: list, 
    referenced_table: str, 
    referenced_columns: list
) -> dict:
    dialect = engine.dialect.name
    q = lambda name: _get_quoted_name(name, dialect)
    
    join_condition = " AND ".join(
        f"t1.{q(ref_col)} = t2.{q(pk_col)}"
        for ref_col, pk_col in zip(referencing_columns, referenced_columns)
    )
    orphan_condition = " OR ".join(f"t2.{q(pk_col)} IS NULL" for pk_col in referenced_columns)
    null_fk_condition = " OR ".join(f"t1.{q(ref_col)} IS NULL" for ref_col in referencing_columns)

    query = text(f"""
    SELECT
        COUNT(*) AS total_rows,
        COUNT(CASE WHEN {orphan_condition} THEN 1 END) AS orphan_rows,
        COUNT(CASE WHEN {null_fk_condition} THEN 1 END) AS null_rows
    FROM
        {q(referencing_table)} AS t1
    LEFT JOIN
        {q(referenced_table)} AS t2 ON {join_condition}
    """)
    
    try:
        with engine.connect() as connection:
            result = connection.execute(query).mappings().first()
    except Exception as e:
        print(f"❌ Error al ejecutar la consulta para {referencing_table} -> {referenced_table}: {e}")
        return {'error': str(e)}

    total_rows = result.get('total_rows', 0)
    orphan_rows = result.get('orphan_rows', 0)
    null_rows = result.get('null_rows', 0)
    
    if total_rows == 0:
        return {'total_rows': 0, 'orphan_rows_count': 0, 'valid_rows_count': 0, 'null_rows_count': 0, 'orphan_rate': 0.0, 'validity_rate': 1.0, 'fk_density': 1.0}
        
    valid_rows = total_rows - orphan_rows
    
    return {'total_rows': total_rows, 'orphan_rows_count': orphan_rows, 'valid_rows_count': valid_rows, 'null_rows_count': null_rows, 'orphan_rate': orphan_rows / total_rows, 'validity_rate': valid_rows / total_rows, 'fk_density': (total_rows - null_rows) / total_rows}

def _calculate_single_consistency(engine: Engine, check_details: dict) -> dict:
    dialect = engine.dialect.name
    q = lambda name: _get_quoted_name(name, dialect)
    
    ref_table = check_details['referencing_table']
    pk_table = check_details['referenced_table']
    ref_attr = check_details['referencing_attribute']
    pk_attr = check_details['referenced_attribute']
    join_columns = check_details['join_columns']

    formatted_join = " AND ".join(
        f"t1.{q(orig)} = t2.{q(dest)}" for orig, dest in join_columns
    )

    query = text(f"""
    SELECT
        COUNT(*) AS total_valid_rows,
        COUNT(CASE 
            WHEN (t1.{q(ref_attr)} != t2.{q(pk_attr)}) OR 
                 (t1.{q(ref_attr)} IS NULL AND t2.{q(pk_attr)} IS NOT NULL) OR
                 (t1.{q(ref_attr)} IS NOT NULL AND t2.{q(pk_attr)} IS NULL)
            THEN 1 
            END) AS inconsistent_rows
    FROM
        {q(ref_table)} AS t1
    INNER JOIN
        {q(pk_table)} AS t2 ON {formatted_join}
    """)
    
    with engine.connect() as connection:
        result = connection.execute(query).mappings().first()
    
    total_rows = result.get('total_valid_rows', 0)
    inconsistent = result.get('inconsistent_rows', 0)

    if total_rows == 0:
        return {'total_valid_rows': 0, 'inconsistent_rows': 0, 'consistency_rate': 1.0}

    return {'total_valid_rows': total_rows, 'inconsistent_rows': inconsistent, 'consistency_rate': (total_rows - inconsistent) / total_rows}

def analyze_attribute_consistency(engine: Engine, schema_graph: nx.DiGraph, config: dict) -> pd.DataFrame:
    if "consistency_checks" not in config:
        return pd.DataFrame()

    results = []
    checks = config["consistency_checks"]
    print("\n🔬 Analizando consistencia de atributos...")

    for ref_table, check_list in checks.items():
        for check_item in check_list:
            fk_origin_cols = check_item['on_fk']
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

            for ref_attr, pk_attr in check_item['attributes'].items():
                print(f"  -> Verificando: {ref_table}.{ref_attr} vs {pk_table}.{pk_attr}")
                check_details = {
                    'referencing_table': ref_table,
                    'referenced_table': pk_table,
                    'referencing_attribute': ref_attr,
                    'referenced_attribute': pk_attr,
                    'join_columns': list(zip(fk_origin_cols, fk_dest_cols))
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
