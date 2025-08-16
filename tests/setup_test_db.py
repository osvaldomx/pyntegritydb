# tests/setup_test_db.py
from sqlalchemy import create_engine, text

def create_test_database(db_uri: str):
    """
    Crea y puebla una base de datos (SQLite, Postgres, o MySQL) para las pruebas.
    Maneja las restricciones de FK para poder insertar datos huérfanos.
    """
    engine = create_engine(db_uri)
    
    # Sentencias de creación de esquema
    schema_statements = [
        'DROP TABLE IF EXISTS "orders"',
        'DROP TABLE IF EXISTS "users"',
        'CREATE TABLE "users" ("id" INTEGER PRIMARY KEY, "name" TEXT NOT NULL)',
        '''CREATE TABLE "orders" (
            "order_id" INTEGER PRIMARY KEY, "user_id" INTEGER, "product" TEXT, 
            "customer_name" TEXT, FOREIGN KEY ("user_id") REFERENCES "users" ("id"))'''
    ]
    
    # Sentencias de inserción de datos
    data_statements = [
        'INSERT INTO "users" ("id", "name") VALUES (1, \'Alice\'), (2, \'Bob\')',
        'INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (101, 1, \'Laptop\', \'Alice\')',
        'INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (102, 2, \'Mouse\', \'Bob\')',
        'INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (103, 1, \'Keyboard\', \'Alicia\')',
        # Esta es la fila huérfana que causa el error
        'INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (104, 99, \'Monitor\', \'Charlie\')'
    ]

    with engine.connect() as connection:
        with connection.begin():
            # Siempre se crea el esquema primero
            for stmt in schema_statements:
                connection.execute(text(stmt))

        # Lógica específica por dialecto para insertar datos
        dialect = connection.dialect.name
        
        if dialect == 'postgresql':
            # En PostgreSQL, desactivamos temporalmente los triggers de FK
            connection.execute(text('SET session_replication_role = replica'))
            with connection.begin():
                for stmt in data_statements:
                    connection.execute(text(stmt))
            connection.execute(text('SET session_replication_role = DEFAULT'))
        elif dialect == 'mysql':
            # En MySQL, desactivamos las revisiones de FK
            connection.execute(text('SET FOREIGN_KEY_CHECKS=0;'))
            with connection.begin():
                for stmt in data_statements:
                    connection.execute(text(stmt))
            connection.execute(text('SET FOREIGN_KEY_CHECKS=1;'))
        else: # SQLite
            with connection.begin():
                # SQLite no impone FKs por defecto en muchas configuraciones
                for stmt in data_statements:
                    connection.execute(text(stmt))