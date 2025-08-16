import sys
import argparse
from . import connect, schema, metrics, report, config, alerts, visualize
import pandas as pd

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
    parser.add_argument(
        "--config",
        type=str,
        help="Ruta al archivo de configuración (config.yml) para análisis avanzados como la consistencia de atributos."
    )
    parser.add_argument(
        "--visualize",
        action="store_true", # Es un flag, no necesita valor
        help="Genera una imagen del grafo de relaciones de la base de datos."
    )
    parser.add_argument(
        "--output-image",
        type=str,
        default="db_integrity_graph.png",
        help="Ruta para guardar la imagen del grafo (usado con --visualize)."
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Ruta para guardar el reporte en un archivo en lugar de mostrarlo en la consola."
    )
    
    args = parser.parse_args()
    config_data = None
    consistency_df = pd.DataFrame()

    try:
        # Si se proporciona un archivo de configuración, cárgalo.
        if args.config:
            print(f"🔩 Cargando configuración desde: {args.config}")
            config_data = config.load_config(args.config)

        # 1. Conectar a la base de datos
        print("🔌 Conectando a la base de datos...")
        engine = connect.create_db_engine(args.db_uri)
        
        # 2. Extraer esquema y construir grafo
        schema_graph = schema.get_schema_graph(engine)
        
        if schema_graph.number_of_edges() == 0:
            print("\nNo se encontraron relaciones de clave foránea para analizar.")
            return

        # 3. Calcular métricas
        completeness_df = metrics.analyze_database_completeness(engine, schema_graph)

        # 4. Si hay configuración, calcular métricas de consistencia
        if config_data:
            consistency_df = metrics.analyze_attribute_consistency(
                engine, schema_graph, config_data)

        # 5. Alertas
        alert_messages = []
        if config_data:
            alert_messages = alerts.check_thresholds(
                completeness_df,
                consistency_df,
                config_data
            )

        # 6. Visualización
        if args.visualize:
            print(f"\n🎨 Generando visualización del grafo en: {args.output_image}")
            visualize.visualize_schema_graph(
                graph=schema_graph,
                metrics_df=completeness_df, # Basamos los colores en la completitud
                output_path=args.output_image
            )
        
        # 7. Generar y mostrar el reporte
        print("\n📊 Reporte de Integridad Referencial:")
        final_report = report.generate_report(
            completeness_df=completeness_df,
            consistency_df=consistency_df,
            alerts=alert_messages,
            report_format=args.format
        )

        # 8. Guardar o imprimir el reporte
        if args.output_file:
            try:
                with open(args.output_file, 'w') as f:
                    f.write(final_report)
                print(f"✅ Reporte guardado exitosamente en: {args.output_file}")
            except IOError as e:
                print(f"❌ Error al escribir en el archivo '{args.output_file}': {e}")
                sys.exit(1)
        else:
            print("\n📊 Reporte de Calidad de Datos:")
            print(final_report)
    
        # 9. Aviso de alertas de calidad
        if alert_messages:
            print("\n❌ Se encontraron violaciones a los umbrales de calidad.")
            sys.exit(1)

    except (ValueError, ConnectionError) as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado: {e}")

if __name__ == '__main__':
    main()