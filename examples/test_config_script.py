# test_config_script.py

# Importamos la función que queremos probar
from pyntegritydb.config import load_config
from pathlib import Path

# Ruta a nuestro archivo de configuración
CONFIG_PATH = Path(__file__).parent / 'config.yml'

print(f"Intentando cargar la configuración desde: {CONFIG_PATH}\n")

try:
    # Llamamos a la función
    config_data = load_config(CONFIG_PATH)
    
    # Si tiene éxito, imprimimos los datos cargados
    print("¡Configuración cargada exitosamente! ✅")
    print("---------------------------------------")
    print("Datos cargados:")
    
    # Imprimimos de forma legible
    import json
    print(json.dumps(config_data, indent=2))
    
except (FileNotFoundError, ValueError) as e:
    # Si falla, imprimimos el error
    print(f"Error durante la carga: {e} ❌")