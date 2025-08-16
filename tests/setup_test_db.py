# tests/setup_test_db.py
from sqlalchemy import create_engine, text

def create_test_database(db_uri: str):
    """
    Crea y puebla una base de datos (SQLite, Postgres, o MySQL) para las pruebas.
    """
    engine = create_engine(db_uri)
    
    # Lista de sentencias SQL para crear el esquema y los datos
    statements = [
        'DROP TABLE IF EXISTS "orders"',
        'DROP TABLE IF EXISTS "users"',
        '''
        CREATE TABLE "users" (
            "id" INTEGER PRIMARY KEY,
            "name" TEXT NOT NULL
        )
        ''',
        '''
        CREATE TABLE "orders" (
            "order_id" INTEGER PRIMARY KEY,
            "user_id" INTEGER,
            "product" TEXT,
            "customer_name" TEXT,
            FOREIGN KEY ("user_id") REFERENCES "users" ("id")
        )
        ''',
        'INSERT INTO "users" ("id", "name") VALUES (1, \'Alice\'), (2, \'Bob\')',
        'INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (101, 1, \'Laptop\', \'Alice\')',
        'INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (102, 2, \'Mouse\', \'Bob\')',
        'INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (103, 1, \'Keyboard\', \'Alicia\')',
        'INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (104, 99, \'Monitor\', \'Charlie\')'
    ]

    with engine.connect() as connection:
        for stmt in statements:
            try:
                # Usamos text() para asegurar la compatibilidad
                connection.execute(text(stmt))
                # En algunas BBDD (como Postgres en transacciones) se necesita un commit explícito
                if connection.dialect.name == 'postgresql':
                    connection.commit()
            except Exception as e:
                # Ignorar errores si la tabla no existía en el DROP, pero imprimir otros
                if "does not exist" not in str(e):
                    print(f"Error ejecutando statement: {stmt}\n{e}")
                    raise e
        # Commit final para transacciones que lo requieran
        connection.commit()

if __name__ == '__main__':
    # Para pruebas locales
    create_test_database("sqlite:///test_db.sqlite")
    print("Base de datos de prueba local creada exitosamente.")