#!/usr/bin/env python
"""
Preparación de datos para el análisis DW-NOMINATE (5 períodos)
Este script divide los datos W-NOMINATE en 5 períodos para el análisis 
dinámico DW-NOMINATE con modelo lineal (modelo=1).

Distribución de periodos (aproximadamente iguales cronológicamente):
P1: 11/03/2018 al 01/11/2018 (aprox. 7,5 meses)
P2: 01/11/2018 al 20/06/2019 (aprox. 7,5 meses)
P3: 20/06/2019 al 10/02/2020 (aprox. 7,5 meses)
P4: 10/02/2020 al 01/10/2020 (aprox. 7,5 meses)
P5: 01/10/2020 al 10/03/2022 (aprox. 17 meses)

Esto abarca el mismo periodo general, pero con mayor detalle:

- P1-P2: Pre-Estallido Social

- P3: Periodo de transición (incluye el inicio del Estallido)

- P4: Apogeo del Estallido Social

- P5: Post-Plebiscito

Uso:
    python prepare_dwnominate_5periods.py --input-dir r_wnominate_data --output-dir r_wnominate_data
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple


# Definiciones de 5 períodos para el modelo lineal DW-NOMINATE
PERIOD_DEFINITIONS = {
    'P1': {
        'name': 'Período 1',
        'start': '2018-03-11',
        'end': '2018-11-01',
        'description': 'Inicio 55° PL - Gobierno Piñera II (inicio)'
    },
    'P2': {
        'name': 'Período 2',
        'start': '2018-11-01',
        'end': '2019-06-20',
        'description': 'Pre-Estallido Social (normalidad)'
    },
    'P3': {
        'name': 'Período 3',
        'start': '2019-06-20',
        'end': '2020-02-10',
        'description': 'Estallido Social (18-Oct-2019) y crisis'
    },
    'P4': {
        'name': 'Período 4',
        'start': '2020-02-10',
        'end': '2020-10-01',
        'description': 'Pandemia COVID-19 y Acuerdo por la Paz'
    },
    'P5': {
        'name': 'Período 5',
        'start': '2020-10-01',
        'end': '2022-03-10',
        'description': 'Post-Plebiscito 2020 y Convención Constitucional'
    }
}


def parse_date(date_str: str) -> datetime:
    """
    Convierte una cadena de fecha en un objeto datetime.
    Admite múltiples formatos encontrados en vote_metadata.
    """
    if pd.isna(date_str):
        return None

    # Probar diferentes formatos de fecha   
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(str(date_str), fmt)
        except ValueError:
            continue

    print(f"⚠️  Could not parse date: {date_str}")
    return None


def classify_vote_by_period(vote_date: datetime) -> str:
    if vote_date is None:
        return 'UNKNOWN'

    for period_code, period_info in PERIOD_DEFINITIONS.items():
        period_start = datetime.strptime(period_info['start'], '%Y-%m-%d')
        period_end = datetime.strptime(period_info['end'], '%Y-%m-%d')

        if period_start <= vote_date < period_end:
            return period_code

    return 'UNKNOWN'


def analyze_period_distribution(vote_metadata_path: str) -> pd.DataFrame:
    print("📊 Analyzing vote distribution across 5 periods...")

    # Load vote metadata
    vote_meta = pd.read_csv(vote_metadata_path)

    # Parse dates and classify periods
    vote_meta['date_parsed'] = vote_meta['fecha'].apply(parse_date)
    vote_meta['period'] = vote_meta['date_parsed'].apply(
        classify_vote_by_period)

    # Statistics by period
    period_stats = vote_meta['period'].value_counts().sort_index()

    print("\n📈 Vote Distribution by Period:")
    print("=" * 70)
    for period in ['P1', 'P2', 'P3', 'P4', 'P5', 'UNKNOWN']:
        if period in period_stats.index:
            count = period_stats[period]
            pct = (count / len(vote_meta)) * 100

            if period in PERIOD_DEFINITIONS:
                info = PERIOD_DEFINITIONS[period]
                print(f"{period}: {count:,} votes ({pct:.1f}%)")
                print(f"    {info['name']}")
                print(f"    {info['start']} to {info['end']}")
                print(f"    {info['description']}")
            else:
                print(f"{period}: {count:,} votes ({pct:.1f}%)")

    print("=" * 70)
    print(f"Total: {len(vote_meta):,} votes\n")

    return vote_meta


# Función para analizar la superposición de legisladores en los 5 períodos
def check_legislator_overlap(votes_matrix_path: str, vote_metadata_with_periods: pd.DataFrame) -> Dict:
    print("👥 Analyzing legislator participation across 5 periods...")

    # Cargar matriz de votos completa
    votes_matrix = pd.read_csv(votes_matrix_path, index_col=0)

    # Obtener IDs de votos para cada período
    period_votes = {}
    for period in ['P1', 'P2', 'P3', 'P4', 'P5']:
        period_vote_ids = vote_metadata_with_periods[
            vote_metadata_with_periods['period'] == period
        ]['vote_id'].astype(str).tolist()

        # Filtrar a votos que existen en la matriz
        available_votes = [
            v for v in period_vote_ids if v in votes_matrix.columns]
        period_votes[period] = available_votes

    # Para cada período, encontrar legisladores activos (votaron al menos una vez, no todos 9)
    active_legislators = {}
    for period, vote_cols in period_votes.items():
        if not vote_cols:
            active_legislators[period] = set()
            continue

        period_matrix = votes_matrix[vote_cols]
        # Legislador es activo si tiene al menos un voto distinto de 9
        is_active = (period_matrix != 9).any(axis=1)
        active_legislators[period] = set(votes_matrix.index[is_active])

    # Calcular superposiciones
    all_periods = set.intersection(
        *[active_legislators[p] for p in ['P1', 'P2', 'P3', 'P4', 'P5']])

    print("\n👥 Legislator Participation:")
    print("=" * 70)
    for period in ['P1', 'P2', 'P3', 'P4', 'P5']:
        count = len(active_legislators[period])
        print(f"{period}: {count} active legislators")

    print(f"\nOverlap:")
    print(f"  All 5 periods: {len(all_periods)} legislators ⭐")
    print("=" * 70)

    if len(all_periods) < 10:
        print("⚠️  WARNING: Very few legislators appear in all 5 periods!")
        print("   Consider adjusting period boundaries.")

    return {
        'period_votes': period_votes,
        'active_legislators': active_legislators,
        'all_periods_overlap': all_periods,
    }


def create_period_matrices(
    votes_matrix_path: str,
    vote_metadata_with_periods: pd.DataFrame,
    output_dir: str,
    min_votes_per_legislator: int = 10,  # Bajar umbral para 5 períodos más pequeños
    min_legislators_per_vote: int = 10
) -> Dict[str, pd.DataFrame]:
    print("\n📊 Creating period-specific vote matrices (5 periods)...")

    # Cargar matriz de votos completa
    votes_matrix = pd.read_csv(votes_matrix_path, index_col=0)

    period_matrices = {}

    for period in ['P1', 'P2', 'P3', 'P4', 'P5']:
        print(f"\n📋 Processing {period}...")

        # Obtener IDs de votos para este período
        period_vote_ids = vote_metadata_with_periods[
            vote_metadata_with_periods['period'] == period
        ]['vote_id'].astype(str).tolist()

        # Filtrar a votos que existen en la matriz
        available_votes = [
            v for v in period_vote_ids if v in votes_matrix.columns]

        if not available_votes:
            print(f"⚠️  No votes found for {period}")
            continue

        # Extraer matriz del período
        period_matrix = votes_matrix[available_votes].copy()

        print(
            f"   Initial: {period_matrix.shape[0]} legislators x {period_matrix.shape[1]} votes")

        # Filtrar legisladores con muy pocos votos
        legislator_vote_counts = (period_matrix != 9).sum(axis=1)
        active_legislators = legislator_vote_counts >= min_votes_per_legislator

        period_matrix = period_matrix.loc[active_legislators, :]
        print(
            f"   After legislator filter (>={min_votes_per_legislator} votes): {period_matrix.shape[0]} legislators")

        # Filtrar votos con muy pocos participantes
        vote_participation = (period_matrix != 9).sum(axis=0)
        active_votes = vote_participation >= min_legislators_per_vote

        period_matrix = period_matrix.loc[:, active_votes]
        print(
            f"   After vote filter (>={min_legislators_per_vote} participants): {period_matrix.shape[1]} votes")

        print(
            f"   ✅ Final: {period_matrix.shape[0]} legislators x {period_matrix.shape[1]} votes")

        # Ordenar votos cronológicamente
        period_vote_meta = vote_metadata_with_periods[
            vote_metadata_with_periods['vote_id'].astype(
                str).isin(period_matrix.columns)
        ].copy()
        period_vote_meta = period_vote_meta.sort_values('date_parsed')

        chronological_order = period_vote_meta['vote_id'].astype(str).tolist()
        available_cols = [
            col for col in chronological_order if col in period_matrix.columns]

        if available_cols:
            period_matrix = period_matrix[available_cols]
            print(f"   📅 Votes sorted chronologically")

        # Guardar
        output_path = os.path.join(
            output_dir, f"votes_matrix_{period.lower()}.csv")
        period_matrix.to_csv(output_path)
        print(f"   💾 Saved to: {output_path}")

        period_matrices[period] = period_matrix

    return period_matrices


def create_period_metadata(
    vote_metadata_with_periods: pd.DataFrame,
    period_matrices: Dict[str, pd.DataFrame],
    output_dir: str
):
    print("\n📝 Creating period-specific metadata files...")

    for period, matrix in period_matrices.items():
        # Filter metadata to votes in this period's matrix
        period_meta = vote_metadata_with_periods[
            vote_metadata_with_periods['vote_id'].astype(
                str).isin(matrix.columns)
        ].copy()

        # Sort chronologically
        period_meta = period_meta.sort_values('date_parsed')

        # Save
        output_path = os.path.join(
            output_dir, f"vote_metadata_{period.lower()}.csv")
        period_meta.to_csv(output_path, index=False)
        print(f"   {period}: {len(period_meta)} votes → {output_path}")


def create_summary_report(
    vote_metadata_with_periods: pd.DataFrame,
    period_matrices: Dict[str, pd.DataFrame],
    overlap_stats: Dict,
    output_dir: str
):
    report_path = os.path.join(
        output_dir, "DWNOMINATE_DATA_SUMMARY_5PERIODS.md")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# DW-NOMINATE Data Preparation Summary (5 Periods)\n\n")
        f.write(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Period Definitions\n\n")
        for period, info in PERIOD_DEFINITIONS.items():
            f.write(f"### {period}: {info['name']}\n")
            f.write(f"- **Date Range**: {info['start']} to {info['end']}\n")
            f.write(f"- **Description**: {info['description']}\n\n")

        f.write("## Vote Distribution\n\n")
        f.write("| Period | Votes | Percentage |\n")
        f.write("|--------|-------|------------|\n")

        period_counts = vote_metadata_with_periods['period'].value_counts()
        total_votes = len(vote_metadata_with_periods)

        for period in ['P1', 'P2', 'P3', 'P4', 'P5']:
            if period in period_counts.index:
                count = period_counts[period]
                pct = (count / total_votes) * 100
                f.write(f"| {period} | {count:,} | {pct:.1f}% |\n")

        f.write(f"| **Total** | **{total_votes:,}** | **100.0%** |\n\n")

        f.write("## Filtered Matrices (After Quality Filters)\n\n")
        f.write("| Period | Legislators | Votes | Density |\n")
        f.write("|--------|-------------|-------|----------|\n")

        for period in ['P1', 'P2', 'P3', 'P4', 'P5']:
            if period in period_matrices:
                matrix = period_matrices[period]
                n_leg = matrix.shape[0]
                n_votes = matrix.shape[1]
                # Calcular densidad (proporción de votos no faltantes)
                density = ((matrix != 9).sum().sum() / (n_leg * n_votes)) * 100
                f.write(
                    f"| {period} | {n_leg} | {n_votes} | {density:.1f}% |\n")

        f.write("\n## Legislator Overlap\n\n")
        f.write(
            f"- **All 5 periods**: {len(overlap_stats['all_periods_overlap'])} legislators ⭐\n\n")

        for period in ['P1', 'P2', 'P3', 'P4', 'P5']:
            count = len(overlap_stats['active_legislators'][period])
            f.write(f"- **{period}**: {count} active legislators\n")

        f.write("\n## Files Generated\n\n")
        f.write("```\n")
        for period in ['P1', 'P2', 'P3', 'P4', 'P5']:
            f.write(f"votes_matrix_{period.lower()}.csv\n")
            f.write(f"vote_metadata_{period.lower()}.csv\n")
        f.write("```\n\n")

    print(f"\n📄 Summary report saved to: {report_path}")


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Prepare data for DW-NOMINATE analysis (5 periods)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--input-dir',
        type=str,
        default='r_wnominate_data',
        help='Directory containing W-NOMINATE data files'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='r_wnominate_data',
        help='Directory to save DW-NOMINATE data files'
    )

    parser.add_argument(
        '--min-votes-per-legislator',
        type=int,
        default=10, 
        help='Minimum votes per legislator to include'
    )

    parser.add_argument(
        '--min-legislators-per-vote',
        type=int,
        default=10,
        help='Minimum legislators per vote to include'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("DW-NOMINATE DATA PREPARATION (5 PERIODS)")
    print("=" * 70)

    # Archivos de ruta
    vote_metadata_path = os.path.join(args.input_dir, 'vote_metadata.csv')
    votes_matrix_path = os.path.join(args.input_dir, 'votes_matrix.csv')

    # Verificar si los archivos existen
    if not os.path.exists(vote_metadata_path):
        print(f"❌ Error: {vote_metadata_path} not found")
        sys.exit(1)

    if not os.path.exists(votes_matrix_path):
        print(f"❌ Error: {votes_matrix_path} not found")
        sys.exit(1)

    # Crear directorio de salida
    os.makedirs(args.output_dir, exist_ok=True)

    # Paso 1: Analizar distribución por período
    vote_metadata_with_periods = analyze_period_distribution(
        vote_metadata_path)

    # Paso 2: Verificar superposición de legisladores
    overlap_stats = check_legislator_overlap(
        votes_matrix_path, vote_metadata_with_periods)

    # Paso 3: Crear matrices específicas por período
    period_matrices = create_period_matrices(
        votes_matrix_path,
        vote_metadata_with_periods,
        args.output_dir,
        args.min_votes_per_legislator,
        args.min_legislators_per_vote
    )

    # Paso 4: Crear metadatos específicos por período
    create_period_metadata(vote_metadata_with_periods,
                           period_matrices, args.output_dir)

    # Paso 5: Crear informe resumen
    create_summary_report(
        vote_metadata_with_periods,
        period_matrices,
        overlap_stats,
        args.output_dir
    )

    print("\n" + "=" * 70)
    print("✅ DATA PREPARATION COMPLETE (5 PERIODS)")
    print("=" * 70)
    print(f"\n📁 Output directory: {args.output_dir}")


if __name__ == "__main__":
    main()
