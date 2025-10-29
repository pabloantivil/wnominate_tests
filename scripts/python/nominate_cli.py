#!/usr/bin/env python
"""
W-NOMINATE CLI

Una interfaz de línea de comandos para calcular las coordenadas de W-NOMINATE a partir de una lista de IDs de votación.
Este script encapsula el módulo wnominate_api.
"""

from src.wnominate_api import calculate_wnominate, save_results_to_file
import sys
import os
import argparse

# Agregar la raíz del proyecto al path para importar desde src
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')))


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Calcular coordenadas de W-NOMINATE para un conjunto de IDs de votación'
    )

    parser.add_argument(
        'votation_ids',
        type=int,
        nargs='+',
        help='Lista de IDs de votación para incluir en el cálculo'
    )

    parser.add_argument(
        '--db-name',
        type=str,
        default="database_example",
        help='Nombre de la base de datos MongoDB (por defecto: database_example)'
    )

    parser.add_argument(
        '--maxiter',
        type=int,
        default=30,
        help='Número máximo de iteraciones (por defecto: 30)'
    )

    parser.add_argument(
        '--cores',
        type=int,
        default=1,
        help='Número de núcleos de CPU a utilizar (por defecto: 1)'
    )

    parser.add_argument(
        '--xtol',
        type=float,
        default=1e-4,
        help='Tolerancia de convergencia (por defecto: 1e-4)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Ruta al archivo JSON de salida (si no se especifica, se imprime en stdout))'
    )

    return parser.parse_args()


def main():
    """
    Función principal para el uso de CLI.
    """
    args = parse_arguments()

    try:
        print(
            f"Calculando W-NOMINATE para los IDs de votación: {args.votation_ids}", file=sys.stderr)

        # Calcular W-NOMINATE
        results = calculate_wnominate(
            votation_ids=args.votation_ids,
            db_name=args.db_name,
            maxiter=args.maxiter,
            cores=args.cores,
            xtol=args.xtol
        )

        # Guardar o imprimir resultados
        if args.output:
            save_results_to_file(results, args.output)
            print(f"Resultados guardados en {args.output}", file=sys.stderr)
        else:
            import json
            print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
