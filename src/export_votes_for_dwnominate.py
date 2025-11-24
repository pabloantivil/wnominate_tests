#!/usr/bin/env python
"""
Export Votes for DW-NOMINATE from Existing CSV Files

Esta versión alternativa NO requiere MongoDB. En su lugar, lee los archivos CSV
que ya fueron exportados previamente para W-NOMINATE y los divide por períodos.

Usage:
    python export_votes_for_dwnominate.py --input-dir data/input --output-dir data/dwnominate/input
"""

import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime
from typing import Dict, List, Tuple
import argparse


def define_periods() -> List[Dict]:
    """
    Define 5 periods for DW-NOMINATE analysis.

    Periods are divided as follows:
    - P1: 2018 (full year)
    - P2: 2019 (full year)
    - P3: 2020 First Semester (January-June)
    - P4: 2020 Second Semester (July-December)
    - P5: 2021 (full year)

    Year 2020 is split into two semesters to achieve the minimum 5 periods
    required for DW-NOMINATE model=1 (linear). 2020 was chosen because it has
    the most voting activity (794 votes total).

    Returns:
        List of period definitions with start/end dates
    """
    return [
        {
            'id': 'P1',
            'name': 'Año 2018',
            'start_date': '2018-01-01',
            'end_date': '2018-12-31'
        },
        {
            'id': 'P2',
            'name': 'Año 2019',
            'start_date': '2019-01-01',
            'end_date': '2019-12-31'
        },
        {
            'id': 'P3',
            'name': '2020 Semestre 1',
            'start_date': '2020-01-01',
            'end_date': '2020-06-30'
        },
        {
            'id': 'P4',
            'name': '2020 Semestre 2',
            'start_date': '2020-07-01',
            'end_date': '2020-12-31'
        },
        {
            'id': 'P5',
            'name': 'Año 2021',
            'start_date': '2021-01-01',
            'end_date': '2021-12-31'
        }
    ]


def export_votes_for_dwnominate_from_csv(input_dir: str = "data/input",
                                         output_dir: str = "data/dwnominate/input"):
    """
    Exporta datos para DW-NOMINATE desde archivos CSV existentes.

    Args:
        input_dir: Directorio con archivos CSV de W-NOMINATE
        output_dir: Directorio de salida para DW-NOMINATE
    """

    print(f"Converting W-NOMINATE CSV data to DW-NOMINATE format...")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Dividing into 5 periods: 2018, 2019, 2020-S1, 2020-S2, 2021\n")

    # Verificar que existen los archivos necesarios
    required_files = [
        'votes_matrix.csv',
        'legislator_metadata.csv',
        'vote_metadata.csv'
    ]

    for filename in required_files:
        filepath = os.path.join(input_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Required file not found: {filepath}\n"
                f"Make sure you have the W-NOMINATE CSV files in {input_dir}/"
            )

    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)

    # Define periods
    periods = define_periods()

    # 1. Cargar matriz de votos completa
    print("Loading votes matrix...")
    votes_matrix_path = os.path.join(input_dir, 'votes_matrix.csv')
    votes_df = pd.read_csv(votes_matrix_path, index_col=0)
    print(
        f"Loaded matrix: {votes_df.shape[0]} legislators x {votes_df.shape[1]} votes")
    # 2. Cargar metadata de legisladores
    print("Loading legislator metadata...")
    legislator_meta_path = os.path.join(input_dir, 'legislator_metadata.csv')
    legislator_meta = pd.read_csv(legislator_meta_path)
    print(f"Loaded {len(legislator_meta)} legislators")

    # 3. Cargar metadata de votaciones
    print("Loading vote metadata...")
    vote_meta_path = os.path.join(input_dir, 'vote_metadata.csv')
    vote_meta = pd.read_csv(vote_meta_path)
    print(f"Loaded {len(vote_meta)} votes\n")

    # 4. Asignar votaciones a períodos según fecha
    print("Assigning votes to legislative periods...")

    vote_period_map = {}

    for _, vote_row in vote_meta.iterrows():
        vote_id = str(vote_row['vote_id']) if 'vote_id' in vote_row else str(
            vote_row['id'])
        fecha_str = vote_row.get('fecha', '')

        if not fecha_str or pd.isna(fecha_str):
            continue

        try:
            # Parse date (varios formatos posibles)
            if ' ' in str(fecha_str):
                fecha = datetime.strptime(str(fecha_str), '%Y-%m-%d %H:%M:%S')
            else:
                fecha = datetime.strptime(str(fecha_str), '%Y-%m-%d')

            # Asignar a período
            for period in periods:
                period_start = datetime.strptime(
                    period['start_date'], '%Y-%m-%d')
                period_end = datetime.strptime(period['end_date'], '%Y-%m-%d')

                if period_start <= fecha <= period_end:
                    vote_period_map[vote_id] = period['id']
                    break

        except Exception as e:
            print(f"Could not parse date for vote {vote_id}: {fecha_str}")
            continue

    # Agregar columna de período a vote_meta
    vote_meta['period'] = vote_meta.apply(
        lambda row: vote_period_map.get(
            str(row['vote_id']) if 'vote_id' in row else str(row['id']),
            None
        ),
        axis=1
    )

    # Contar votos por período
    period_counts = vote_meta[vote_meta['period'].notna()].groupby(
        'period').size()
    print("\nVotes per period:")
    for period in periods:
        count = period_counts.get(period['id'], 0)
        print(f"   {period['id']} ({period['name']}): {count:,} votes")

    votes_with_period = vote_meta[vote_meta['period'].notna()]
    print(f"\n{len(votes_with_period)} votes successfully assigned to periods")
    print(f"{len(vote_meta) - len(votes_with_period)} votes without period assignment (excluded)\n")

    # 5. Crear matriz de votos para cada período
    print("Creating vote matrices for each period...")
    period_matrices = {}
    period_vote_lists = {}

    for period in periods:
        period_id = period['id']

        # Obtener IDs de votaciones para este período
        period_votes = vote_meta[vote_meta['period'] == period_id]

        if len(period_votes) == 0:
            print(f"No votes found for {period_id}, skipping...")
            continue

        # Convertir IDs a strings para comparar con columnas de la matriz
        vote_ids = [str(
            vid) for vid in period_votes['vote_id' if 'vote_id' in period_votes.columns else 'id'].tolist()]

        # Filtrar columnas de la matriz que corresponden a este período
        available_vote_ids = [
            vid for vid in vote_ids if vid in votes_df.columns]

        if not available_vote_ids:
            print(
                f"No matching votes found in matrix for {period_id}, skipping...")
            continue

        # Crear matriz para este período
        period_matrix = votes_df[available_vote_ids].copy()

        print(
            f"\n   {period_id}: {period_matrix.shape[0]} legislators x {period_matrix.shape[1]} votes")

        # Filtrar para mínima participación
        min_votes_per_legislator = 10
        min_legislators_per_vote = 10

        # Filtrar legisladores (considerando que 9 = "not in legislature")
        legislator_vote_counts = (period_matrix != 9).sum(axis=1)
        active_legislators = legislator_vote_counts >= min_votes_per_legislator

        # Filtrar votaciones
        vote_participation = (period_matrix != 9).sum(axis=0)
        active_votes = vote_participation >= min_legislators_per_vote

        # Aplicar filtros
        filtered_matrix = period_matrix.loc[active_legislators, active_votes]

        print(
            f"   Final matrix: {filtered_matrix.shape[0]} legislators x {filtered_matrix.shape[1]} votes")

        # Ordenar cronológicamente
        period_votes_sorted = period_votes[period_votes[(
            'vote_id' if 'vote_id' in period_votes.columns else 'id')].astype(str).isin(filtered_matrix.columns)]
        period_votes_sorted = period_votes_sorted.sort_values('fecha')

        chronological_order = [str(
            vid) for vid in period_votes_sorted['vote_id' if 'vote_id' in period_votes_sorted.columns else 'id'].tolist()]
        available_cols = [
            col for col in chronological_order if col in filtered_matrix.columns]

        if available_cols:
            filtered_matrix = filtered_matrix[available_cols]
            print(f"   Votes sorted chronologically")

        period_matrices[period_id] = filtered_matrix
        period_vote_lists[period_id] = [
            int(vid) for vid in filtered_matrix.columns.tolist()]

    if not period_matrices:
        raise ValueError(
            "No periods could be created! Check your date ranges and vote metadata.")

    # 6. Asegurar conjunto consistente de legisladores
    print("\nEnsuring consistent legislator set across periods...")

    # Obtener unión de todos los legisladores
    all_legislators = set()
    for matrix in period_matrices.values():
        all_legislators.update(matrix.index.tolist())

    all_legislators = sorted(list(all_legislators))
    print(
        f"   Total unique legislators across all periods: {len(all_legislators)}")

    # Reindexar todas las matrices con los mismos legisladores
    for period_id, matrix in period_matrices.items():
        period_matrices[period_id] = matrix.reindex(
            index=all_legislators, fill_value=9)

    # CRÍTICO: Eliminar legisladores que tienen 0 votos válidos en CUALQUIER período
    # DW-NOMINATE requiere que cada legislador tenga votos válidos en TODOS los períodos
    # o al menos usar minvotes correctamente
    print("\nChecking for legislators with insufficient votes in any period...")

    legislators_to_remove = set()
    min_required_votes = 1  # Al menos 1 voto válido (no-9) por período

    for period_id, matrix in period_matrices.items():
        for legislator_id in all_legislators:
            legislator_votes = matrix.loc[legislator_id]
            valid_vote_count = (legislator_votes != 9).sum()

            if valid_vote_count < min_required_votes:
                legislators_to_remove.add(legislator_id)

    if legislators_to_remove:
        legislators_to_remove = sorted(list(legislators_to_remove))
        print(
            f"   Removing {len(legislators_to_remove)} legislators with < {min_required_votes} valid votes in at least one period:")

        # Mostrar en qué períodos tienen problemas
        for lid in legislators_to_remove:
            period_issues = []
            for period_id, matrix in period_matrices.items():
                valid_count = (matrix.loc[lid] != 9).sum()
                if valid_count < min_required_votes:
                    period_issues.append(f"{period_id}:{valid_count}")
            print(f"      - Legislator {lid}: {', '.join(period_issues)}")

        # Actualizar todas las matrices
        legislators_to_keep = [
            lid for lid in all_legislators if lid not in legislators_to_remove]

        for period_id in period_matrices.keys():
            period_matrices[period_id] = period_matrices[period_id].loc[legislators_to_keep]

        all_legislators = legislators_to_keep
        print(f"   Final legislator count: {len(all_legislators)}")
    else:
        print(f"   All legislators meet minimum vote requirements in all periods")

    # 7. Exportar matrices de votos por período
    print("\nExporting vote matrices...")

    for period_id, matrix in period_matrices.items():
        filename = f"{output_dir}/votes_matrix_{period_id.lower()}.csv"
        matrix.to_csv(filename)
        print(f"   {filename} ({matrix.shape[0]} x {matrix.shape[1]})")

    # 8. Exportar metadata de legisladores
    print("\nExporting legislator metadata...")

    active_legislator_ids = [int(lid) for lid in all_legislators]

    # Filtrar metadata solo para legisladores activos
    active_legislator_meta = legislator_meta[
        legislator_meta['legislator_id'].astype(int).isin(active_legislator_ids) |
        legislator_meta['id'].astype(int).isin(active_legislator_ids)
    ].copy()

    # Asegurar que legislator_id existe
    if 'legislator_id' not in active_legislator_meta.columns:
        active_legislator_meta['legislator_id'] = active_legislator_meta['id']

    active_legislator_meta.to_csv(
        f"{output_dir}/legislator_metadata.csv", index=False)
    print(
        f"   legislator_metadata.csv ({len(active_legislator_meta)} legislators)")

    # 9. Exportar metadata de votaciones con asignación de períodos
    print("\nExporting vote metadata with period assignments...")

    # Filtrar solo votaciones que están en algún período
    all_vote_ids = set()
    for vote_ids in period_vote_lists.values():
        all_vote_ids.update(vote_ids)

    vote_meta_filtered = vote_meta[
        vote_meta[('vote_id' if 'vote_id' in vote_meta.columns else 'id')].isin(
            all_vote_ids)
    ].copy()

    vote_meta_filtered.to_csv(f"{output_dir}/vote_metadata.csv", index=False)
    print(f"vote_metadata.csv ({len(vote_meta_filtered)} votes)")

    print(f"\nOutput directory: {output_dir}/")
    print(f"\nFiles created:")
    for period_id in period_matrices.keys():
        print(f"   • votes_matrix_{period_id.lower()}.csv")
    print(f"   • legislator_metadata.csv")
    print(f"   • vote_metadata.csv")
    print(f"   • r_dwnominate_script.R")

    print(f"\nPróximos pasos:")
    print(f"   1. cd scripts/r")
    print(f"   2. Rscript r_dwnominate_script.R")
    print(f"   3. Los resultados se guardarán en data/dwnominate/output/")
    print(f"   4. Usar csv_dwnominate_graph.py para visualizar resultados")

    return {
        'periods': len(period_matrices),
        'legislators': len(all_legislators),
        'export_dir': output_dir
    }

def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Export votes for DW-NOMINATE from existing CSV files (no MongoDB required)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--input-dir',
        type=str,
        default='data/input',
        help='Input directory with W-NOMINATE CSV files (default: data/input)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/dwnominate/input',
        help='Output directory for DW-NOMINATE files (default: data/dwnominate/input)'
    )

    args = parser.parse_args()

    try:
        result = export_votes_for_dwnominate_from_csv(
            args.input_dir, args.output_dir)

        if result:
            print(f"\n✅ Exportación exitosa!")
            print(f"   Períodos: {result['periods']}")
            print(f"   Legisladores: {result['legislators']}")
            print(f"   Directorio: {result['export_dir']}")
        else:
            print("\n❌ Exportación fallida!")
            return 1

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
