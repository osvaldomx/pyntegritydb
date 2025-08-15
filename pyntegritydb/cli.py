import argparse
from . import connect, schema, metrics, report

def main():
    """
    Función principal de la interfaz de línea de comandos (CLI).
    """
    parser = argparse.ArgumentParser(
        description="Analiza la integridad referencial de una base de datos y genera un reporte."
    )
    parser.add_argument(
        "db_uri", 
        type=str, 
        help="La URI de conexión de la base de datos (ej. 'sqlite:///database.db')."
    )
    parser.add_argument(
        "--format", 
        type=str, 
        default="cli", 
        choices=['cli', 'json', 'csv'],
        help="El formato del reporte de salida."
    )
    
    args = parser.parse_args()

    try:
        # 1. Conectar a la base de datos
        print("🔌 Conectando a la base de datos...")
        engine = connect.create_db_engine(args.db_uri)
        
        # 2. Extraer esquema y construir grafo
        schema_graph = schema.get_schema_graph(engine)
        
        if schema_graph.number_of_edges() == 0:
            print("\nNo se encontraron relaciones de clave foránea para analizar.")
            return

        # 3. Calcular métricas
        metrics_df = metrics.analyze_database_completeness(engine, schema_graph)
        
        # 4. Generar y mostrar el reporte
        print("\n📊 Reporte de Integridad Referencial:")
        final_report = report.generate_report(metrics_df, report_format=args.format)
        print(final_report)

    except (ValueError, ConnectionError) as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado: {e}")

if __name__ == '__main__':
    main()