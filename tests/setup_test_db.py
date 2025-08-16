# tests/setup_test_db.py
from sqlalchemy import create_engine, text

def create_test_database(db_uri: str):
    """
    Crea y puebla una base de datos (SQLite, Postgres, o MySQL) para las pruebas.
    """
    engine = create_engine(db_uri)
    dialect = engine.dialect.name

    # Define las sentencias SQL con un marcador de posición para las comillas
    # Usaremos {q} que cambiaremos a " o ` según el dialecto
    statements = [
        'DROP TABLE IF EXISTS {q}orders{q}',
        'DROP TABLE IF EXISTS {q}users{q}',
        '''CREATE TABLE {q}users{q} (
            {q}id{q} INTEGER PRIMARY KEY, 
            {q}name{q} TEXT NOT NULL
        )''',
        '''CREATE TABLE {q}orders{q} (
            {q}order_id{q} INTEGER PRIMARY KEY, {q}user_id{q} INTEGER, {q}product{q} TEXT, 
            {q}customer_name{q} TEXT, FOREIGN KEY ({q}user_id{q}) REFERENCES {q}users{q} ({q}id{q}))''',
        'INSERT INTO {q}users{q} ({q}id{q}, {q}name{q}) VALUES (1, \'Alice\'), (2, \'Bob\')',
        'INSERT INTO {q}orders{q} ({q}order_id{q}, {q}user_id{q}, {q}product{q}, {q}customer_name{q}) VALUES (101, 1, \'Laptop\', \'Alice\')',
        'INSERT INTO {q}orders{q} ({q}order_id{q}, {q}user_id{q}, {q}product{q}, {q}customer_name{q}) VALUES (102, 2, \'Mouse\', \'Bob\')',
        'INSERT INTO {q}orders{q} ({q}order_id{q}, {q}user_id{q}, {q}product{q}, {q}customer_name{q}) VALUES (103, 1, \'Keyboard\', \'Alicia\')',
        'INSERT INTO {q}orders{q} ({q}order_id{q}, {q}user_id{q}, {q}product{q}, {q}customer_name{q}) VALUES (104, 99, \'Monitor\', \'Charlie\')'
    ]
    
    # Selecciona el carácter de comilla correcto
    quote_char = '`' if dialect == 'mysql' else '"'
    
    # Formatea las sentencias con el carácter correcto
    formatted_statements = [s.format(q=quote_char) for s in statements]

    with engine.connect() as connection:
        # Lógica para desactivar FKs (si es necesario)
        if dialect == 'mysql':
            connection.execute(text('SET FOREIGN_KEY_CHECKS=0;'))
        elif dialect == 'postgresql':
            connection.execute(text('SET session_replication_role = replica'))

        # Ejecución de sentencias
        with connection.begin():
            for stmt in formatted_statements:
                try:
                    connection.execute(text(stmt))
                except Exception as e:
                    if "does not exist" not in str(e):
                        print(f"Error ejecutando statement: {stmt}\n{e}")
                        raise e
        
        # Reactivar FKs
        if dialect == 'mysql':
            connection.execute(text('SET FOREIGN_KEY_CHECKS=1;'))
        elif dialect == 'postgresql':
            connection.execute(text('SET session_replication_role = DEFAULT'))