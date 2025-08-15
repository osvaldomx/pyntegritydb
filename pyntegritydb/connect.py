from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

def create_db_engine(uri: str) -> Engine:
    """
    Crea y valida un motor de SQLAlchemy a partir de una URI de conexión.

    Esta función toma una URI estándar de base de datos, intenta establecer una
    conexión y, si tiene éxito, devuelve un motor de SQLAlchemy listo para ser
    utilizado por otros módulos de la biblioteca.

    Args:
        uri: La URI de la base de datos (ej. "postgresql://user:pass@host/db").

    Returns:
        Una instancia del motor de SQLAlchemy si la conexión es exitosa.

    Raises:
        ValueError: Si la URI es inválida o la conexión falla, proporcionando
                    un mensaje claro sobre la causa del error.
    """
    if not isinstance(uri, str) or "://" not in uri:
        raise ValueError("La URI de conexión proporcionada es inválida. El formato esperado es 'dialect+driver://user:pass@host/db'.")
    
    try:
        engine = create_engine(uri)
        # Intenta conectar para validar la URI, credenciales y disponibilidad de la BD.
        # El bloque 'with' asegura que la conexión se cierre correctamente.
        with engine.connect():
            pass
        
        print(f"✅ Conexión exitosa al motor: {engine.dialect.name}")
        return engine
    except SQLAlchemyError as e:
        # Captura cualquier error de SQLAlchemy para dar un feedback más útil.
        raise ValueError(f"❌ No se pudo conectar a la base de datos. Error: {e}") from e

    
def get_db_inspector(engine: Engine) -> object:
    """
    Obtiene un objeto inspector de SQLAlchemy para el motor dado.

    El inspector es una herramienta de bajo nivel que permite extraer
    metadatos del esquema de la base de datos, como tablas, columnas y
    restricciones.

    Args:
        engine: Una instancia activa del motor de SQLAlchemy.

    Returns:
        Un objeto Inspector.
    """
    return inspect(engine)