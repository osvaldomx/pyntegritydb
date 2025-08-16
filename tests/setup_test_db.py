from sqlalchemy import create_engine, text

def create_test_schema(db_uri: str):
    """Crea el esquema de tablas (vacías) en la base de datos de prueba."""
    engine = create_engine(db_uri)
    
    # Usaremos acentos graves ` que son más compatibles. PostgreSQL los entiende.
    schema_statements = [
        'DROP TABLE IF EXISTS `orders`',
        'DROP TABLE IF EXISTS `users`',
        '''CREATE TABLE `users` (
            `id` INTEGER PRIMARY KEY, 
            `name` TEXT NOT NULL
        )''',
        '''CREATE TABLE `orders` (
            `order_id` INTEGER PRIMARY KEY, `user_id` INTEGER, `product` TEXT, 
            `customer_name` TEXT, FOREIGN KEY (`user_id`) REFERENCES `users`(`id`))'''
    ]

    with engine.connect() as connection:
        with connection.begin():
            for stmt in schema_statements:
                try:
                    connection.execute(text(stmt))
                except Exception as e:
                    # Ignorar error si la tabla no existía en el DROP
                    if "Unknown table" not in str(e) and "does not exist" not in str(e):
                        raise e