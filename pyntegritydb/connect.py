from sqlalchemy import create_engine, Engine
from sqlalchemy.exc import OperationalError

def create_engine_from_uri(uri: str) -> Engine | None:
    """
    Creates a SQLAlchemy engine from a database URI.

    Parameters:
        uri (str): Database connection URI.

    Returns:
        engine (sqlalchemy.Engine): SQLAlchemy engine object.
    """
    try:
        engine = create_engine(uri)
        return engine
    except OperationalError as e:
        print(f"Connection failed: {e}")
        return None
    
def test_connection(engine: Engine) -> bool:
    """
    Tests the connection to the database using the provided engine.

    Parameters:
        engine (sqlalchemy.Engine): SQLAlchemy engine object.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False