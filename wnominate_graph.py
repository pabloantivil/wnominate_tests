#!/usr/bin/env python
"""
W-NOMINATE Graphing Module

Este módulo proporciona una interfaz gráfica para los cálculos de W-NOMINATE. 
Utiliza la canalización wnominate_api.py para obtener y procesar los datos, 
y luego grafica los resultados con matplotlib.

Usage:
    # Calculate for specific votation IDs:
    python wnominate_graph.py --votation-ids 1,2,3,4,5
    
    # Calculate for ALL votes in database (TEMPORARY FEATURE):
    python wnominate_graph.py --all-votes --db-name database_example
    
    # Load and plot from JSON results file:
    python wnominate_graph.py --json-file all_votes_dwnominate_database_example.json

    # Load and plot pre-calculated results:
    python wnominate_graph.py --debug-file results.json
    
Note: The --all-votes feature is TEMPORARY and will be removed after analysis.
      It processes ALL votes in your database and may take considerable time.
"""

import os
import sys
import json
import argparse
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any

# Import from the main module
from wnominate_api import calculate_wnominate, get_mongodb_connection
import pymongo


def get_all_votation_ids(db_name: str = "database_example") -> List[int]:
    """
    Obtiene todos los ID de votación de la base de datos MongoDB, ordenados por fecha.

    Args:
        db_name: Nombre de la base de datos MongoDB

    Returns:
        Lista de todos los IDs de votación ordenados por fecha (el más antiguo primero)
    """
    print("🔍 Obteniendo todos los IDs de votación de la base de datos...")

    try:
        client = get_mongodb_connection()
        db = client[db_name]
        votaciones = db["votaciones"]

        # Obtener todas las votaciones ordenadas por fecha
        cursor = votaciones.find({}, {"id": 1, "fecha": 1}).sort("fecha", 1)

        votation_ids = []
        total_count = 0

        for doc in cursor:
            total_count += 1
            votation_id = doc.get("id")
            if votation_id is not None:
                votation_ids.append(int(votation_id))

        print(
            f"✅ Se encontraron {len(votation_ids)} votaciones de {total_count} documentos totales")

        if len(votation_ids) != total_count:
            print(
                f"⚠️  Advertencia: {total_count - len(votation_ids)} documentos tenían IDs faltantes o inválidos")

        if not votation_ids:
            print("❌ ¡No se encontraron IDs de votación válidos en la base de datos!")
            return []

        print(
            f"📊 Rango de fechas: Primer ID = {votation_ids[0]}, Último ID = {votation_ids[-1]}")
        print(
            f"💡 IDs de muestra: {votation_ids[:10]}{'...' if len(votation_ids) > 10 else ''}")

        return votation_ids

    except Exception as e:
        print(f"❌ Error al obtener IDs de votación: {e}")
        raise


def parse_votation_ids(ids_str: str) -> List[int]:
    """
    Analiza una cadena de IDs de votación separadas por comas en una lista de números enteros.

    Args:
        ids_str: Cadena de IDs de votación separados por comas

    Returns:
        Lista de IDs de votación enteros
    """
    try:
        return [int(id_str.strip()) for id_str in ids_str.split(',') if id_str.strip()]
    except ValueError:
        print("Error: Los IDs de votación deben ser enteros separados por comas")
        sys.exit(1)


def generate_colors_by_party(idpt_results: Dict[str, List[float]], db_name: str = "database_example") -> Dict[str, str]:
    """
    Generar un mapeo de colores para cada parlamentario en función de su partido.

    Args:
        idpt_results: Las coordenadas W-NOMINATE para cada parlamentario
        db_name: Nombre de la base de datos MongoDB

    Returns:
        Diccionario que mapea los IDs de los parlamentarios a colores
    """
    import pymongo
    from wnominate_api import get_mongodb_connection

    # Conectar a MongoDB
    client = get_mongodb_connection()
    db = client[db_name]
    parlamentarios = db["parlamentarios"]

    # Definir mapeo de colores para partidos
    party_colors = {
        "PC": "#0066FF",       # Partido Colorado (Azul)
        "PN": "#FFFFFF",       # Partido Nacional (Blanco)
        "FA": "#FF0000",       # Frente Amplio (Rojo)
        "CA": "#FFD700",       # Cabildo Abierto (Amarillo/Dorado)
        "PI": "#FF6600",       # Partido Independiente (Naranja)
        "PG": "#00CC00",       # Partido Verde (Verde)
        # Partido Ecologista Radical Intransigente (Púrpura)
        "PERI": "#800080",
        "AP": "#996633",       # Asamblea Popular (Café)
        "PT": "#000000",       # Partido de los Trabajadores (Negro)
        "UP": "#FF00FF",       # Unidad Popular (Magenta)
        # Color por defecto para partidos desconocidos (Gris)
        "Default": "#CCCCCC"
    }

    # Crear mapeo de colores para cada parlamentario
    color_map = {}

    for member_id in idpt_results.keys():
        # Extraer ID numérico del ID de miembro (eliminar prefijo 'M')
        numeric_id = int(member_id[1:]) if member_id.startswith(
            'M') else int(member_id)

        # Encontrar parlamentario en la base de datos
        parlamentario = parlamentarios.find_one({"id": numeric_id})

        if parlamentario and "partido" in parlamentario:
            partido = parlamentario["partido"]
            color_map[member_id] = party_colors.get(
                partido, party_colors["Default"])
        else:
            color_map[member_id] = party_colors["Default"]

    return color_map


def generate_labels(idpt_results: Dict[str, List[float]], db_name: str = "databas_example") -> Dict[str, str]:
    """
    Generar etiquetas para cada parlamentario.

    Args:
        idpt_results: Las coordenadas de W-NOMINATE para cada parlamentario
        db_name: Nombre de la base de datos MongoDB

    Returns:
        Diccionario que mapea los IDs de los parlamentarios a etiquetas
    """
    import pymongo
    from wnominate_api import get_mongodb_connection

    # Conectar a MongoDB
    client = get_mongodb_connection()
    db = client[db_name]
    parlamentarios = db["parlamentarios"]

    # Crear mapeo de etiquetas para cada parlamentario
    label_map = {}

    for member_id in idpt_results.keys():
        # Extraer ID numérico del ID de miembro (eliminar prefijo 'M')
        numeric_id = int(member_id[1:]) if member_id.startswith(
            'M') else int(member_id)

        # Encontrar parlamentario en la base de datos
        parlamentario = parlamentarios.find_one({"id": numeric_id})

        if parlamentario and "nombre" in parlamentario:
            # Crear una etiqueta corta con nombre y partido
            nombre = parlamentario.get("nombre", "Desconocido")
            partido = parlamentario.get("partido", "")

            # Usar apellido o primera parte del nombre para mantenerlo corto
            if " " in nombre:
                nombre = nombre.split(" ")[-1]  # Apellido

            label_map[member_id] = f"{nombre} ({partido})"
        else:
            label_map[member_id] = member_id

    return label_map


def convert_to_plottable_format(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convertir los resultados sin procesar de W-NOMINATE a un formato adecuado para su representación gráfica.
    Esto maneja múltiples formatos de coordenadas:
    - {'xcoord': x, 'ycoord': y} formato (nuevo formato)
    - {'idpt': [x, y]} formato (estructura anidada)
    - [x, y] formato (lista simple)

    Args:
        results: Resultados sin procesar de la cálculo de W-NOMINATE

    Returns:
       Diccionario con estructura simplificada para representar gráficamente (coordenadas [x, y])
    """
    converted = {"idpt": {}}

    if 'idpt' not in results:
        print("Error: No se encontró la clave 'idpt' en los resultados")
        print(f"Claves disponibles: {list(results.keys())}")
        return converted

    idpt_data = results['idpt']
    print(f"Procesando {len(idpt_data)} parlamentarios...")

    success_count = 0
    for member_id, member_data in idpt_data.items():
        try:
            # Manejar diferentes formatos de coordenadas
            if isinstance(member_data, dict):
                if 'xcoord' in member_data and 'ycoord' in member_data:
                    # Formato nuevo: {'xcoord': x, 'ycoord': y}
                    x = float(member_data['xcoord'])
                    y = float(member_data['ycoord'])
                    converted["idpt"][member_id] = [x, y]
                    success_count += 1
                elif 'idpt' in member_data:
                    # Formato anidado: {'idpt': [x, y], 'meta': {...}}
                    coords = member_data['idpt']
                    if hasattr(coords, '__iter__') and len(coords) >= 2:
                        x, y = float(coords[0]), float(coords[1])
                        converted["idpt"][member_id] = [x, y]
                        success_count += 1
                    else:
                        print(
                            f"Advertencia: Coordenadas anidadas inválidas para miembro {member_id}")
                else:
                    print(
                        f"Advertencia: Formato de diccionario desconocido para miembro {member_id}: {list(member_data.keys())}")
            elif hasattr(member_data, '__iter__') and len(member_data) >= 2:
                # Formato de lista/array simple: [x, y]
                x, y = float(member_data[0]), float(member_data[1])
                converted["idpt"][member_id] = [x, y]
                success_count += 1
            else:
                print(
                    f"Advertencia: Formato de coordenadas inválido para miembro {member_id}: {type(member_data)}")

        except (ValueError, TypeError, IndexError) as e:
            print(
                f"Advertencia: Error al procesar coordenadas para miembro {member_id}: {e}")
            continue

    print(
        f"✅ Se convirtieron exitosamente {success_count}/{len(idpt_data)} pares de coordenadas")

    return converted


def plot_wnominate_map(results: Dict[str, Any], output_file: str = None, show_labels: bool = True, db_name: str = "database_example"):
    """
    Graficar el mapa W-NOMINATE con las coordenadas calculadas.

    Args:
        results: Resultados de calculate_wnominate
        output_file: Ruta para guardar la imagen del gráfico (opcional)
        show_labels: Si se deben mostrar etiquetas para cada punto
    """
    # Convertir resultados crudos a formato graficable
    converted_results = convert_to_plottable_format(results)

    if 'idpt' not in converted_results:
        print("Error: No se encontraron coordenadas IDPT en los resultados convertidos")
        return

    # Extraer coordenadas
    idpt = converted_results['idpt']

    # Verificar si hay coordenadas válidas
    if not idpt:
        print("Error: No se encontraron coordenadas válidas en los resultados convertidos")
        return

    # Información de depuración sobre la estructura
    print(f"Número de parlamentarios: {len(idpt)}")
    first_key = next(iter(idpt))
    print(
        f"Formato de coordenadas de muestra para {first_key}: {idpt[first_key]}")

    # Verificar caso degenerado (todos los mismos valores)
    all_coords = []
    for member_id, coords in idpt.items():
        # Manejar formatos de lista y array numpy
        if isinstance(coords, (list, np.ndarray)) and len(coords) >= 2:
            # Extraer como valores flotantes para asegurar consistencia
            x, y = float(coords[0]), float(coords[1])
            all_coords.append((x, y))

    if not all_coords:
        print(
            "Error: No se encontraron coordenadas 2D válidas en los resultados convertidos")
        # Mostrar una muestra de los datos para ayudar a depurar
        sample_data = {k: v for k, v in list(idpt.items())[:5]}
        print(f"Datos de muestra: {sample_data}")
        return

    # Imprimir mensaje de éxito
    print(
        f"Se extrajeron exitosamente {len(all_coords)} pares de coordenadas válidos")

    # Verificar si todos los puntos están en las mismas coordenadas (caso degenerado)
    x_vals = [x for x, y in all_coords]
    y_vals = [y for x, y in all_coords]

    if len(set(x_vals)) <= 1 and len(set(y_vals)) <= 1:
        print("Advertencia: Todos los puntos tienen las mismas coordenadas. El gráfico puede no ser informativo.")

    # Generar colores por partido
    colors = generate_colors_by_party(idpt, db_name)

    # Generar etiquetas
    labels = generate_labels(idpt) if show_labels else {}

    # Crear figura
    plt.figure(figsize=(12, 10))

    # Graficar cada punto
    for member_id, coords in idpt.items():
        # Manejar formatos de lista y array numpy
        if isinstance(coords, (list, np.ndarray)) and len(coords) >= 2:
            # Extraer como valores flotantes para asegurar consistencia
            x, y = float(coords[0]), float(coords[1])
            color = colors.get(member_id, "#CCCCCC")

            plt.scatter(x, y, color=color, s=100,
                        edgecolors='black', alpha=0.7)

            if show_labels and member_id in labels:
                plt.annotate(labels[member_id],
                             (x, y),
                             textcoords="offset points",
                             xytext=(0, 5),
                             ha='center',
                             fontsize=8)

    # Agregar líneas de referencia
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)

    # Agregar círculo unitario para mostrar límite del espacio latente teórico (x² + y² = 0.25)
    theta = np.linspace(0, 2*np.pi, 100)
    circle_x = 0.5 * np.cos(theta)
    circle_y = 0.5 * np.sin(theta)
    plt.plot(circle_x, circle_y, color='red', linestyle='--', alpha=0.5, linewidth=2,
             label='Límite Teórico (x² + y² = 0.25)')

    # Agregar título y etiquetas
    plt.title('Mapa W-NOMINATE', fontsize=16)
    plt.xlabel('Primera Dimensión', fontsize=12)
    plt.ylabel('Segunda Dimensión', fontsize=12)

    # Agregar cuadrícula
    plt.grid(True, linestyle='--', alpha=0.3)

    # Establecer relación de aspecto igual solo si tenemos coordenadas variadas
    if len(set(x_vals)) > 1 or len(set(y_vals)) > 1:
        plt.axis('equal')

    # Agregar leyenda para el círculo de límite
    plt.legend(loc='upper right', fontsize=10, framealpha=0.8)

    # Agregar borde
    plt.gca().spines['top'].set_visible(True)
    plt.gca().spines['right'].set_visible(True)
    plt.gca().spines['bottom'].set_visible(True)
    plt.gca().spines['left'].set_visible(True)

    # Guardar o mostrar gráfico
    if output_file:
        try:
            # Obtener ruta absoluta para mejor reporte
            abs_path = os.path.abspath(output_file)
            plt.savefig(abs_path, dpi=300, bbox_inches='tight')
            print(f"Gráfico guardado exitosamente en: {abs_path}")

            # Verificar que el archivo fue creado
            if os.path.exists(abs_path):
                file_size = os.path.getsize(abs_path)
                print(f"Tamaño de archivo: {file_size} bytes")
            else:
                print(
                    "Advertencia: El archivo no fue creado a pesar de no haber errores")
        except Exception as e:
            print(f"Error al guardar gráfico: {str(e)}")
    else:
        plt.tight_layout()
        plt.show()


def parse_arguments():
    """
    Analizar argumentos de la línea de comandos.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Generar gráfico W-NOMINATE para un conjunto de IDs de votación')

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '--votation-ids',
        type=str,
        help='Lista de IDs de votación separados por comas para incluir en el cálculo'
    )

    group.add_argument(
        '--debug-file',
        type=str,
        help='Ruta a un archivo JSON pre-calculado con resultados de W-NOMINATE para graficar (omite el cálculo)'
    )

    group.add_argument(
        '--json-file',
        type=str,
        help='Ruta a un archivo JSON de resultados (como all_votes_dwnominate_*.json) para cargar y graficar directamente'
    )

    group.add_argument(
        '--all-votes',
        action='store_true',
        help='Calcular DW-NOMINATE para TODOS los votos en la base de datos (ordenados por fecha)'
    )

    parser.add_argument(
        '--db-name',
        type=str,
        default="database_example",
        help='Nombre de la base de datos de MongoDB'
    )

    parser.add_argument(
        '--maxiter',
        type=int,
        default=10,
        help='Número máximo de iteraciones'
    )

    parser.add_argument(
        '--cores',
        type=int,
        default=1,
        help='Número de núcleos de CPU a utilizar'
    )

    parser.add_argument(
        '--xtol',
        type=float,
        default=1e-4,
        help='Tolerancia de convergencia'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Ruta para guardar la imagen del gráfico (si no se especifica, muestra el gráfico)'
    )

    parser.add_argument(
        '--no-labels',
        action='store_true',
        help='No mostrar etiquetas en el gráfico'
    )

    return parser.parse_args()


def main():
    """
    Función principal para el uso de CLI.
    """
    args = parse_arguments()

    try:
        # Comprueba si estamos cargando desde un archivo de resultados JSON
        if args.json_file:
            print(f"📂 Cargando archivo de resultados JSON: {args.json_file}")

            if not os.path.exists(args.json_file):
                print(f"❌ Error: Archivo no encontrado: {args.json_file}")
                sys.exit(1)

            try:
                with open(args.json_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)

                print(f"✅ Resultados JSON cargados correctamente")
                if 'idpt' in results:
                    print(
                        f"   📊 Se encontraron coordenadas para {len(results['idpt'])} parlamentarios")
                if 'bp' in results:
                    print(
                        f"   📋 Se encontraron parámetros de proyecto para {len(results['bp'])} votos")

            except json.JSONDecodeError as e:
                print(f"❌ Error al analizar el archivo JSON: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"❌ Error al cargar el archivo JSON: {e}")
                sys.exit(1)

            # Resultados de la grafica
            print("🎨 Generando visualización a partir de los datos JSON...")
            plot_wnominate_map(
                results=results,
                output_file=args.output,
                show_labels=not args.no_labels,
                db_name=args.db_name
            )
            return

        # Comprobar si estamos depurando con un archivo guardado
        if args.debug_file:
            print(f"Cargando archivo de depuración: {args.debug_file}")
            with open(args.debug_file, 'r', encoding='utf-8') as f:
                results = json.load(f)

            # Plot results
            plot_wnominate_map(
                results=results,
                output_file=args.output,
                show_labels=not args.no_labels,
                db_name=args.db_name
            )
            return

        # Determinar los IDs de votación a utilizar
        if args.all_votes:
            print("🚀 CALCULANDO DW-NOMINATE PARA TODOS LOS VOTOS EN LA BASE DE DATOS")
            print("=" * 60)
            print("⚠️  ADVERTENCIA: Esto procesará TODOS los votos en su base de datos!")
            print(
                "    Esto puede tardar mucho tiempo y utilizar recursos computacionales significativos.")
            print("    Asegúrese de tener suficiente memoria y potencia de procesamiento.")
            print("=" * 60)

            # Pide confirmación
            response = input(
                "¿Quieres continuar? (si/no): ").lower().strip()
            if response not in ['si', 'y']:
                print("Operación cancelada.")
                return

            # Obtener todos los IDs de votación
            votation_ids = get_all_votation_ids(args.db_name)

            if not votation_ids:
                print("❌ No se encontraron IDs de votación. No se puede continuar.")
                return

            print(f"📋 Se procesarán {len(votation_ids)} votaciones")

        else:
            # Analizar identificaciones de votación específicas
            votation_ids = parse_votation_ids(args.votation_ids)

        print(f"🔢 Procesando {len(votation_ids)} IDs de votación")
        if len(votation_ids) <= 20:
            print(f"📝 IDs de votación: {votation_ids}")
        else:
            print(f"📝 Primeros 10 IDs: {votation_ids[:10]}...")
            print(f"📝 Últimos 10 IDs: {votation_ids[-10:]}")

        print(f"⚙️  Parámetros de cálculo:")
        print(f"   Base de datos: {args.db_name}")
        print(f"   Máximas iteraciones: {args.maxiter}")
        print(f"   Núcleos de CPU: {args.cores}")
        print(f"   Tolerancia a la convergencia: {args.xtol}")
        print()

        # Calculate W-NOMINATE
        print("🔄 Iniciando cálculo de DW-NOMINATE...")
        results = calculate_wnominate(
            votation_ids=votation_ids,
            db_name=args.db_name,
            maxiter=args.maxiter,
            cores=args.cores,
            xtol=args.xtol
        )

        # Comprobar si los resultados contienen los datos necesarios
        if not results or 'idpt' not in results or not results['idpt']:
            print(
                "❌ Advertencia: El cálculo se completó pero no se generaron coordenadas válidas.")
            print("Estructura de resultados:", json.dumps(
                results, indent=2, default=str)[:500] + "...")
            sys.exit(1)

        print(f"✅ Cálculo de DW-NOMINATE completado con éxito!")
        print(
            f"   📊 Se encontraron coordenadas para {len(results['idpt'])} parlamentarios")
        print(f"   🗳️  Se procesaron {len(votation_ids)} votaciones")

        if 'bp' in results:
            print(
                f"   📋 Se calcularon parámetros de proyecto para {len(results['bp'])} votaciones")

        # Guardar los resultados en un archivo si se procesan todos los votos
        if args.all_votes:
            output_file = f"all_votes_dwnominate_{args.db_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2,
                          ensure_ascii=False, default=str)
            print(f"💾 Todos los resultados se guardaron en: {output_file}")

        # Plot results
        print("🎨 Generando visualización...")
        plot_wnominate_map(
            results=results,
            output_file=args.output,
            show_labels=not args.no_labels,
            db_name=args.db_name
        )

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
