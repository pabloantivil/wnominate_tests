#!/usr/bin/env python
"""
CSV W-NOMINATE Graphing Module

Este módulo adapta el archivo wnominate_graph.py existente para trabajar con archivos de coordenadas 
CSV del análisis R W-NOMINATE, proporcionando una visualización liviana de los resultados.

Uso:
    # Plot from CSV coordinates file:
    python csv_wnominate_graph.py --csv-file data/wnominate/output/wnominate_coordinates.csv
    
    # Plot with custom output file:
    python csv_wnominate_graph.py --csv-file data/wnominate/output/wnominate_coordinates.csv --output results/wnominate_map.png
    
    # Compare R results with pynominate JSON results:
    python csv_wnominate_graph.py --csv-file data/wnominate/output/wnominate_coordinates.csv --compare-json data/wnominate/output/allvotes-dwnominate.json
"""

import os
import sys
import json
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, Optional


def load_csv_coordinates(csv_file: str) -> Dict[str, Any]:
    """
    Cargar las coordenadas W-NOMINATE desde el archivo CSV y conviértalas al formato de gráfico.

    Args:
        csv_file: Ruta al archivo CSV con columnas: legislator_id, coord1D, coord2D, partido, nombres

    Returns:
        Diccionario en formato compatible con las funciones de graficado existentes
    """
    print(f"Cargando coordenadas CSV desde: {csv_file}")

    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Archivo CSV no encontrado: {csv_file}")

    # Leer archivo CSV
    df = pd.read_csv(csv_file)
    print(f"Cargado {len(df)} legisladores desde CSV")

    # Verificar las columnas requeridas
    required_cols = ['legislator_id', 'coord1D', 'coord2D']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Faltan columnas requeridas en CSV: {missing_cols}")

    # Convertir a formato de gráfico
    results = {"idpt": {}}

    for _, row in df.iterrows():
        legislator_id = str(row['legislator_id'])
        x_coord = float(row['coord1D'])
        y_coord = float(row['coord2D']) if not pd.isna(row['coord2D']) else 0.0

        # Almacenar en el formato esperado por las funciones de graficado
        results["idpt"][legislator_id] = [x_coord, y_coord]

    print(f"📊 Convertidos {len(results['idpt'])} pares de coordenadas")
    return results


def load_legislator_metadata(csv_dir: str) -> Dict[str, Dict[str, str]]:
    """
    Cargar metadatos del legislador (nombres, partidos) desde el CSV de metadatos.

    Args:
        csv_dir: Directorio que contiene los archivos CSV

    Returns:
        Diccionario que mapea legislator_id a metadatos
    """
    # Buscar primero en data/wnominate/input (ubicación correcta según nueva estructura)
    # Determinar la ruta base del proyecto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    metadata_file = os.path.join(
        project_root, 'data', 'wnominate', 'input', 'legislator_metadata.csv')

    # Si no se encuentra, intentar en el directorio proporcionado (compatibilidad con estructura antigua)
    if not os.path.exists(metadata_file):
        metadata_file = os.path.join(csv_dir, 'legislator_metadata.csv')

    if not os.path.exists(metadata_file):
        print(f"Archivo de metadatos no encontrado: {metadata_file}")
        return {}

    print(f"Cargando metadatos de legisladores desde: {metadata_file}")
    df = pd.read_csv(metadata_file)

    metadata = {}
    for _, row in df.iterrows():
        legislator_id = str(row['legislator_id'])
        metadata[legislator_id] = {
            'nombres': row.get('nombres', ''),
            'partido': row.get('partido', ''),
            'region': row.get('region', ''),
            'distrito': row.get('distrito', '')
        }

    print(f"✅ Cargada metadata para {len(metadata)} legisladores")
    return metadata


def create_party_colors_for_chile() -> Dict[str, str]:
    """
    Definir mapeo de colores para los partidos políticos chilenos.

    Returns:
        Diccionario que mapea códigos de partidos a colores
    """
    return {
        # Far Left / Izquierda (rojo oscuro a rojo)
        "PC": "#800026",           # Partido Comunista - rgb(128,0,38)
        "IC": "#BD0026",           # Izquierda Ciudadana - rgb(189,0,38)
        "CS": "#E31A1C",           # Convergencia Social - rgb(227,26,28)
        "PH": "#FC4E2A",           # Partido Humanista - rgb(252,78,42)

        # Center-Left / Centro-Izquierda (rojo-naranja a naranja claro)
        "PS": "#FD793C",           # Partido Socialista - rgb(253,121,60)
        "COM": "#FE9E4C",          # Partido Comunes - rgb(254,158,76)
        "PRad": "#FEB476",         # Partido Radical - rgb(254,180,118)
        "Prad": "#FEB476",         # Partido Radical (alternativa)
        "PR": "#FEB476",           # Partido Radical (alternativa)
        "PRO": "#FFC8A0",          # Partido Progresista - rgb(255,200,160)

        # Left-Alternative / Izquierda Alternativa (naranja muy claro)
        "RD": "#FFE6CC",           # Revolución Democrática - rgb(255,230,204)

        # Independent/Green / Independientes y Verdes (verde/amarillo-verde)
        # Independientes - rgb(0,255,0) - verde brillante
        "IND": "#00FF00",
        # Federación Regionalista Verde Social - rgb(251,255,134)
        "FRVS": "#FBFF86",

        # Center / Centro (amarillo)
        "DC": "#FFFF00",           # Democracia Cristiana - rgb(255,255,0)

        # Center-Liberal / Centro-Liberal (verde claro a celeste)
        # Partido por la Democracia - rgb(215,255,157)
        "PPD": "#D7FF9D",
        "PL": "#5DC0BE",           # Partido Liberal - rgb(93,192,190)
        "PEV": "#54ABC0",          # Partido Ecologista Verde - rgb(84,171,192)

        # Center-Right / Centro-Derecha (azul medio)
        "EVOP": "#1D91C0",         # Evolución Política - rgb(29,145,192)

        # Right / Derecha (azul oscuro)
        "RN": "#225EA8",           # Renovación Nacional - rgb(34,94,168)

        # Far Right / Derecha (azul muy oscuro)
        # Unión Demócrata Independiente - rgb(37,52,148)
        "UDI": "#253494",
        "PRep": "#081D58",         # Partido Republicano - rgb(8,29,88)
        "Prep": "#081D58",         # Partido Republicano (alternativa)

        # Other / Otros
        # Partido Regionalista Independiente (marrón)
        "PRI": "#996633",
        "S/I": "#7D7D7D",          # Sin Información - rgb(125,125,125)
        "NOINFO": "#7D7D7D",       # Sin Información (alternativa)

        # Default
        "Default": "#CCCCCC"       # Unknown parties (Light Gray)
    }


def plot_csv_wnominate(csv_file: str, output_file: Optional[str] = None,
                       show_labels: bool = False, title: str = "W-NOMINATE Map from R Analysis"):
    """
    Graficar las coordenadas W-NOMINATE desde el archivo CSV.

    Args:
        csv_file: Ruta al archivo de coordenadas CSV
        output_file: Ruta opcional para guardar la imagen del gráfico
        show_labels: Si se deben mostrar las etiquetas de los legisladores en el gráfico
        title: Título del gráfico
    """
    # Cargar coordenadas
    results = load_csv_coordinates(csv_file)

    # Cargar metadatos para colores y etiquetas
    csv_dir = os.path.dirname(csv_file)
    metadata = load_legislator_metadata(csv_dir)

    # Crear mapeo de colores para partidos
    party_colors = create_party_colors_for_chile()

    # Generar colores para cada legislador
    colors = {}
    for legislator_id in results["idpt"].keys():
        if legislator_id in metadata and metadata[legislator_id]['partido']:
            party = metadata[legislator_id]['partido']
            colors[legislator_id] = party_colors.get(
                party, party_colors["Default"])
        else:
            colors[legislator_id] = party_colors["Default"]

    # Crear etiquetas si se solicita
    labels = {}
    if show_labels:
        for legislator_id in results["idpt"].keys():
            if legislator_id in metadata:
                name = metadata[legislator_id]['nombres']
                party = metadata[legislator_id]['partido']
                if party:
                    labels[legislator_id] = f"{name} ({party})"
                else:
                    labels[legislator_id] = name
            else:
                labels[legislator_id] = f"ID {legislator_id}"

    # Crear gráfico
    plt.figure(figsize=(12, 8))

    x_vals = []
    y_vals = []
    plot_colors = []
    plot_labels = []

    for legislator_id, coords in results["idpt"].items():
        x, y = coords[0], coords[1]
        x_vals.append(x)
        y_vals.append(y)
        plot_colors.append(colors.get(legislator_id, party_colors["Default"]))
        plot_labels.append(labels.get(
            legislator_id, legislator_id) if show_labels else "")

    # Crear un diagrama de dispersión
    scatter = plt.scatter(x_vals, y_vals, c=plot_colors,
                          s=60, alpha=0.7, edgecolors='black', linewidth=0.5)

    # Agregar etiquetas si se solicita
    if show_labels and labels:
        for i, (x, y) in enumerate(zip(x_vals, y_vals)):
            plt.annotate(plot_labels[i], (x, y), xytext=(5, 5), textcoords='offset points',
                         fontsize=8, alpha=0.8)

    # Agregar líneas de ejes
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)

    # Agregar límite de círculo unitario
    theta = np.linspace(0, 2*np.pi, 100)
    # R W-NOMINATE normalmente utiliza el círculo unitario
    circle_x = 1.0 * np.cos(theta)
    circle_y = 1.0 * np.sin(theta)
    plt.plot(circle_x, circle_y, color='red', linestyle='--', alpha=0.5, linewidth=2,
             label='Límite del Círculo Unitario')

    # Formato
    plt.title(title, fontsize=16)
    plt.xlabel('First Dimension (Economic: Left ← → Right)', fontsize=12)
    plt.ylabel('Second Dimension (Social Issues)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.3)

    # Crear leyenda para partidos
    unique_parties = set()
    for legislator_id in results["idpt"].keys():
        if legislator_id in metadata and metadata[legislator_id]['partido']:
            unique_parties.add(metadata[legislator_id]['partido'])

    legend_elements = []
    for party in sorted(unique_parties):
        if party in party_colors:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                              markerfacecolor=party_colors[party],
                                              markersize=8, label=party))

    if legend_elements:
        plt.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5),
                   fontsize=10, framealpha=0.8)

    # Establecer límites de ejes
    x_range = max(x_vals) - min(x_vals)
    y_range = max(y_vals) - min(y_vals)
    margin = 0.1
    plt.xlim(min(x_vals) - x_range * margin, max(x_vals) + x_range * margin)
    plt.ylim(min(y_vals) - y_range * margin, max(y_vals) + y_range * margin)

    # Guardar o mostrar gráfico
    plt.tight_layout()

    if output_file:
        abs_path = os.path.abspath(output_file)
        plt.savefig(abs_path, dpi=300, bbox_inches='tight')
        print(f"📊 Gráfico guardado en: {abs_path}")

        if os.path.exists(abs_path):
            file_size = os.path.getsize(abs_path)
            print(f"   Tamaño del archivo: {file_size:,} bytes")
    else:
        plt.show()


def compare_with_pynominate(csv_file: str, json_file: str, output_file: Optional[str] = None):
    """
    Crear un gráfico de comparación entre los resultados de R W-NOMINATE (CSV) y los resultados de pynominate (JSON).    
    Args:
        csv_file: Ruta a los resultados CSV de R W-NOMINATE
        json_file: Ruta para obtener resultados JSON de Pynominate  
        output_file: Ruta opcional para guardar el gráfico de comparación
    """
    print("📊 Creando un gráfico de comparación entre R W-NOMINATE y pynominate...")

    # Cargar resultados de R
    r_results = load_csv_coordinates(csv_file)
    csv_dir = os.path.dirname(csv_file)
    metadata = load_legislator_metadata(csv_dir)

    # Cargar resultados de Pynominate
    if not os.path.exists(json_file):
        raise FileNotFoundError(
            f"Archivo JSON de pynominate no encontrado: {json_file}")

    with open(json_file, 'r', encoding='utf-8') as f:
        py_results = json.load(f)

    # Crear gráfico de comparación
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    party_colors = create_party_colors_for_chile()

    # Resultados del gráfico R (panel izquierdo)
    for legislator_id, coords in r_results["idpt"].items():
        x, y = coords[0], coords[1]
        party = metadata.get(legislator_id, {}).get('partido', '')
        color = party_colors.get(party, party_colors["Default"])
        ax1.scatter(x, y, c=color, s=60, alpha=0.7,
                    edgecolors='black', linewidth=0.5)

    ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax1.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    ax1.set_title('R W-NOMINATE Results', fontsize=14)
    ax1.set_xlabel('First Dimension')
    ax1.set_ylabel('Second Dimension')
    ax1.grid(True, alpha=0.3)

    # Gráfico de resultados de Pynominate (panel derecho)
    if 'idpt' in py_results:
        for legislator_id, coords in py_results["idpt"].items():
            if isinstance(coords, list) and len(coords) >= 2:
                x, y = coords[0], coords[1]
            elif isinstance(coords, dict) and 'xcoord' in coords and 'ycoord' in coords:
                x, y = coords['xcoord'], coords['ycoord']
            else:
                continue

            # Id del legislador del mapa (pynominate puede tener un formato diferente)
            clean_id = legislator_id.replace(
                'M', '') if legislator_id.startswith('M') else legislator_id
            party = metadata.get(clean_id, {}).get('partido', '')
            color = party_colors.get(party, party_colors["Default"])
            ax2.scatter(x, y, c=color, s=60, alpha=0.7,
                        edgecolors='black', linewidth=0.5)

    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax2.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    ax2.set_title('pynominate Results', fontsize=14)
    ax2.set_xlabel('First Dimension')
    ax2.set_ylabel('Second Dimension')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_file:
        abs_path = os.path.abspath(output_file)
        plt.savefig(abs_path, dpi=300, bbox_inches='tight')
        print(f"📊 Gráfico de comparación guardado en: {abs_path}")
    else:
        plt.show()


def parse_arguments():
    """Analizar argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Plot W-NOMINATE coordinates from CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--csv-file',
        type=str,
        required=True,
        help='Path to CSV file with W-NOMINATE coordinates'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Path to save the plot image (if not specified, shows the plot)'
    )

    parser.add_argument(
        '--no-labels',
        action='store_true',
        help='Do not show labels on the plot'
    )

    parser.add_argument(
        '--compare-json',
        type=str,
        help='Path to pynominate JSON file for comparison plot'
    )

    parser.add_argument(
        '--title',
        type=str,
        default="W-NOMINATE Map from R Analysis",
        help='Custom title for the plot'
    )

    return parser.parse_args()


def main():
    """Función principal para el uso de la CLI."""
    args = parse_arguments()

    try:
        if args.compare_json:
            # Crear gráfico de comparación
            compare_with_pynominate(
                args.csv_file, args.compare_json, args.output)
        else:
            # Crear gráfico único a partir del CSV
            plot_csv_wnominate(
                csv_file=args.csv_file,
                output_file=args.output,
                show_labels=not args.no_labels,
                title=args.title
            )

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
