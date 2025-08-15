# pyntegritydb/visualize.py

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def _get_color_from_rate(rate: float) -> str:
    """Devuelve un color basado en el valor de la tasa de validez."""
    if pd.isna(rate):
        return 'gray'  # Para relaciones con errores o sin datos
    if rate >= 0.995:
        return 'green'
    elif rate >= 0.90:
        return 'orange'
    else:
        return 'red'

def visualize_schema_graph(
    graph: nx.DiGraph, 
    metrics_df: pd.DataFrame, 
    output_path: str = "db_integrity_graph.png"
):
    """
    Genera una visualización del grafo del esquema y la guarda como una imagen.

    Colorea los arcos del grafo según la métrica 'validity_rate':
    - Verde: >= 99.5%
    - Naranja: >= 90%
    - Rojo: < 90%
    - Gris: Con errores o sin datos

    Args:
        graph: El grafo del esquema de NetworkX.
        metrics_df: El DataFrame con los resultados del módulo de métricas.
        output_path: La ruta donde se guardará la imagen generada.
    """
    if graph.number_of_edges() == 0:
        print("⚠️ No hay relaciones en el grafo para visualizar.")
        return

    # Crear una copia del grafo para no modificar el original
    g_visual = graph.copy()

    # Mapear los resultados del DataFrame a los arcos del grafo
    metrics_map = {
        (row['referencing_table'], row['referenced_table']): row['validity_rate']
        for _, row in metrics_df.iterrows()
    }

    # Asignar colores a los arcos basándose en la tasa de validez
    edge_colors = [
        _get_color_from_rate(metrics_map.get((u, v)))
        for u, v in g_visual.edges()
    ]

    # Generar el layout del grafo
    pos = nx.spring_layout(g_visual, k=0.8, iterations=50, seed=42)

    # Dibujar el grafo
    plt.figure(figsize=(16, 12))
    
    nx.draw_networkx_nodes(g_visual, pos, node_size=3000, node_color='skyblue')
    nx.draw_networkx_edges(g_visual, pos, edgelist=g_visual.edges(), edge_color=edge_colors, width=2, arrowsize=20)
    nx.draw_networkx_labels(g_visual, pos, font_size=10)
    
    plt.title("Visualización de la Integridad Referencial de la Base de Datos", size=20)
    plt.axis('off')

    try:
        plt.savefig(output_path, format='png', bbox_inches='tight')
        print(f"✅ Gráfico guardado exitosamente en: {output_path}")
    except Exception as e:
        print(f"❌ No se pudo guardar el gráfico. Error: {e}")
    finally:
        plt.close()