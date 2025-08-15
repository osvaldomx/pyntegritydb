import networkx as nx
from sqlalchemy.engine import Engine

from .connect import get_db_inspector

def get_schema_graph(engine: Engine) -> nx.DiGraph:
    """
    Extrae el esquema de la base de datos y lo representa como un grafo dirigido.

    Cada nodo en el grafo es una tabla, y cada arco dirigido representa una
    relación de clave foránea (FK), apuntando desde la tabla que contiene la FK
    hacia la tabla que contiene la clave primaria (PK) referenciada.

    Los detalles de la relación (columnas implicadas) se almacenan como
    atributos en el arco.

    Args:
        engine: El motor de SQLAlchemy para la base de datos.

    Returns:
        Un grafo DiGraph de NetworkX que representa las relaciones FK del esquema.
    """
    inspector = get_db_inspector(engine)
    schema_graph = nx.DiGraph()
    
    print("🔎 Extrayendo esquema de la base de datos...")
    
    # Itera sobre todos los esquemas disponibles (importante para BBDD como PostgreSQL)
    for schema in inspector.get_schema_names():
        # Obtiene las tablas para el esquema actual
        for table_name in inspector.get_table_names(schema=schema):
            # Añade cada tabla como un nodo en el grafo
            schema_graph.add_node(table_name, type='table')
            
            # Obtiene las claves foráneas para la tabla actual
            try:
                fks = inspector.get_foreign_keys(table_name, schema=schema)
                for fk in fks:
                    # Añade un arco desde la tabla que referencia hacia la tabla referenciada
                    schema_graph.add_edge(
                        table_name, 
                        fk['referred_table'], 
                        # Almacena metadatos importantes en el arco para su uso posterior
                        constrained_columns=fk['constrained_columns'],
                        referred_columns=fk['referred_columns']
                    )
            except Exception as e:
                print(f"⚠️ No se pudieron obtener las FKs para la tabla '{table_name}': {e}")

    node_count = schema_graph.number_of_nodes()
    edge_count = schema_graph.number_of_edges()
    print(f"✅ Grafo construido: {node_count} tablas y {edge_count} relaciones encontradas.")
    
    return schema_graph