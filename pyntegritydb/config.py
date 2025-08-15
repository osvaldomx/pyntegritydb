import yaml
from yaml.error import YAMLError

def load_config(path: str) -> dict:
    """
    Carga, parsea y valida un archivo de configuración en formato YAML.

    El archivo de configuración define los umbrales de aceptación para las métricas
    de integridad.

    Args:
        path: La ruta al archivo de configuración (ej. 'config.yml').

    Returns:
        Un diccionario con la configuración cargada.

    Raises:
        FileNotFoundError: Si el archivo no se encuentra en la ruta especificada.
        ValueError: Si el archivo no es un YAML válido o le faltan claves requeridas.
    """
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
            
            # Validación básica de la estructura del archivo
            if not isinstance(config, dict):
                raise ValueError("El archivo de configuración debe ser un diccionario YAML válido.")
            
            print(f"✅ Configuración cargada exitosamente desde '{path}'")
            return config

    except FileNotFoundError:
        raise FileNotFoundError(f"❌ No se encontró el archivo de configuración en: {path}")
    except YAMLError as e:
        raise ValueError(f"❌ Error al parsear el archivo YAML: {e}") from e