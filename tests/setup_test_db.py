# tests/setup_test_db.py
import sqlite3

def create_test_database(db_path="test_db.sqlite"):
    """Crea y puebla una base de datos SQLite para las pruebas de integración."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Eliminar tablas si ya existen para una creación limpia
    cursor.execute('DROP TABLE IF EXISTS "orders"')
    cursor.execute('DROP TABLE IF EXISTS "users"')

    # Crear tablas
    cursor.execute('''
    CREATE TABLE "users" (
        "id" INTEGER PRIMARY KEY,
        "name" TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE "orders" (
        "order_id" INTEGER PRIMARY KEY,
        "user_id" INTEGER,
        "product" TEXT,
        "customer_name" TEXT,
        FOREIGN KEY ("user_id") REFERENCES "users" ("id")
    )
    ''')

    # Insertar datos de prueba
    cursor.execute('INSERT INTO "users" ("id", "name") VALUES (1, \'Alice\'), (2, \'Bob\')')
    
    # Insertar datos en orders
    cursor.execute('INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (101, 1, \'Laptop\', \'Alice\')')
    cursor.execute('INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (102, 2, \'Mouse\', \'Bob\')')
    cursor.execute('INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (103, 1, \'Keyboard\', \'Alicia\')')
    cursor.execute('INSERT INTO "orders" ("order_id", "user_id", "product", "customer_name") VALUES (104, 99, \'Monitor\', \'Charlie\')')


    conn.commit()
    conn.close()
    print(f"Base de datos de prueba '{db_path}' creada exitosamente.")

if __name__ == '__main__':
    create_test_database()