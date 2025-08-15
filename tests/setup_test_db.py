# tests/setup_test_db.py
import sqlite3

def create_test_database(db_path="test_db.sqlite"):
    """Crea y puebla una base de datos SQLite para las pruebas de integración."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crear tablas
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        product TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Insertar datos de prueba
    cursor.execute("INSERT INTO users (id, name) VALUES (1, 'Alice'), (2, 'Bob')")
    
    # Datos válidos y una fila huérfana (user_id=99 no existe)
    cursor.execute("INSERT INTO orders (order_id, user_id, product) VALUES (101, 1, 'Laptop')")
    cursor.execute("INSERT INTO orders (order_id, user_id, product) VALUES (102, 2, 'Mouse')")
    cursor.execute("INSERT INTO orders (order_id, user_id, product) VALUES (103, 1, 'Keyboard')")
    cursor.execute("INSERT INTO orders (order_id, user_id, product) VALUES (104, 99, 'Monitor')") # Fila huérfana

    conn.commit()
    conn.close()
    print(f"Base de datos de prueba '{db_path}' creada exitosamente.")

if __name__ == '__main__':
    create_test_database()