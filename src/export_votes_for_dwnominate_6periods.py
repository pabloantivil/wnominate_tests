#!/usr/bin/env python
"""
Export Votes for DW-NOMINATE - 6 Períodos Semestrales (2019-2021)

Esta versión crea 6 períodos basados en semestres desde 2019 hasta 2021:
- P1: 2019 Semestre 1 (Enero-Junio)
- P2: 2019 Semestre 2 (Julio-Diciembre)
- P3: 2020 Semestre 1 (Enero-Junio)
- P4: 2020 Semestre 2 (Julio-Diciembre)
- P5: 2021 Semestre 1 (Enero-Junio)
- P6: 2021 Semestre 2 (Julio-Diciembre)

Usage:
    python export_votes_for_dwnominate_6periods.py --input-dir data/wnominate/input --output-dir data/dwnominate_6periods/input
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
    Define 6 períodos semestrales para análisis DW-NOMINATE.

    Períodos divididos por semestre:
    - P1: 2019 Semestre 1 (Enero-Junio)
    - P2: 2019 Semestre 2 (Julio-Diciembre)
    - P3: 2020 Semestre 1 (Enero-Junio)
    - P4: 2020 Semestre 2 (Julio-Diciembre)
    - P5: 2021 Semestre 1 (Enero-Junio)
    - P6: 2021 Semestre 2 (Julio-Diciembre)

    Returns:
        Lista de definiciones de períodos con fechas inicio/fin
    """
    return [
        {
            'id': 'P1',
            'name': '2019 Semestre 1',
            'start_date': '2019-01-01',
            'end_date': '2019-06-30'
        },
        {
            'id': 'P2',
            'name': '2019 Semestre 2',
            'start_date': '2019-07-01',
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
            'name': '2021 Semestre 1',
            'start_date': '2021-01-01',
            'end_date': '2021-06-30'
        },
        {
            'id': 'P6',
            'name': '2021 Semestre 2',
            'start_date': '2021-07-01',
            'end_date': '2021-12-31'
        }
    ]


def export_votes_for_dwnominate_from_csv(input_dir: str = "data/wnominate/input",
                                         output_dir: str = "data/dwnominate_6periods/input"):
    """
    Exporta datos para DW-NOMINATE desde archivos CSV existentes (6 períodos).

    Args:
        input_dir: Directorio con archivos CSV de W-NOMINATE
        output_dir: Directorio de salida para DW-NOMINATE
    """

    print(f"🔍 Convirtiendo datos W-NOMINATE a formato DW-NOMINATE (6 períodos)...")
    print(f"📂 Directorio de entrada: {input_dir}")
    print(f"📂 Directorio de salida: {output_dir}")
    print(f"📅 Dividiendo en 6 períodos semestrales: 2019-S1, 2019-S2, 2020-S1, 2020-S2, 2021-S1, 2021-S2\n")

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
                f"❌ Archivo requerido no encontrado: {filepath}\n"
                f"Asegúrate de tener los archivos CSV de W-NOMINATE en {input_dir}/"
            )

    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)

    # Leer archivos CSV
    print("📖 Leyendo archivos CSV...")
    votes_matrix = pd.read_csv(os.path.join(
        input_dir, 'votes_matrix.csv'), index_col=0)
    legislator_metadata = pd.read_csv(
        os.path.join(input_dir, 'legislator_metadata.csv'))
    vote_metadata = pd.read_csv(os.path.join(input_dir, 'vote_metadata.csv'))

    print(
        f"   ✅ Matriz de votos: {votes_matrix.shape[0]} legisladores × {votes_matrix.shape[1]} votaciones")
    print(f"   ✅ Metadata legisladores: {len(legislator_metadata)} registros")
    print(f"   ✅ Metadata votaciones: {len(vote_metadata)} registros\n")

    # Definir períodos
    periods = define_periods()

    # Convertir fechas en vote_metadata
    vote_metadata['fecha'] = pd.to_datetime(vote_metadata['fecha'])

    # Dividir votaciones por período
    print("📅 Dividiendo votaciones por período...")
    period_votes = {}
    period_stats = []

    for period in periods:
        period_id = period['id']
        start = pd.to_datetime(period['start_date'])
        end = pd.to_datetime(period['end_date'])

        # Filtrar votaciones del período
        mask = (vote_metadata['fecha'] >= start) & (
            vote_metadata['fecha'] <= end)
        period_vote_metadata = vote_metadata[mask].copy()

        if len(period_vote_metadata) == 0:
            print(
                f"   ⚠️  {period['name']}: 0 votaciones encontradas - PERÍODO VACÍO")
            continue

        # Obtener IDs de votaciones
        vote_ids = period_vote_metadata['vote_id'].astype(str).tolist()

        # Filtrar matriz de votos
        available_vote_ids = [
            vid for vid in vote_ids if vid in votes_matrix.columns]

        if len(available_vote_ids) == 0:
            print(
                f"   ⚠️  {period['name']}: 0 votaciones en matriz - PERÍODO VACÍO")
            continue

        period_matrix = votes_matrix[available_vote_ids].copy()

        # Guardar para este período
        period_votes[period_id] = {
            'matrix': period_matrix,
            'vote_metadata': period_vote_metadata[period_vote_metadata['vote_id'].astype(str).isin(available_vote_ids)],
            'name': period['name']
        }

        stats = {
            'period': period_id,
            'name': period['name'],
            'votes': len(available_vote_ids),
            'legislators': period_matrix.shape[0]
        }
        period_stats.append(stats)

        print(f"   ✅ {period['name']}: {stats['votes']} votaciones")

    if len(period_votes) == 0:
        raise ValueError(
            "❌ No se encontraron votaciones en ningún período. Verifica las fechas.")

    print(f"\n📊 Total de períodos con datos: {len(period_votes)}\n")

    # Filtrar legisladores que aparecen en TODOS los períodos
    print("👥 Filtrando legisladores consistentes...")

    # Obtener legisladores que están en cada período
    legislators_per_period = {
        period_id: set(data['matrix'].index)
        for period_id, data in period_votes.items()
    }

    # Intersección: legisladores que aparecen en TODOS los períodos
    common_legislators = set.intersection(*legislators_per_period.values())

    print(
        f"   📋 Legisladores en todos los períodos: {len(common_legislators)}")

    if len(common_legislators) == 0:
        raise ValueError(
            "❌ No hay legisladores que aparezcan en todos los períodos.\n"
            "DW-NOMINATE requiere que los mismos legisladores aparezcan en todos los períodos."
        )

    # Filtrar metadata de legisladores
    common_legislators_list = sorted(list(common_legislators))
    filtered_legislator_metadata = legislator_metadata[
        legislator_metadata['legislator_id'].isin(common_legislators_list)
    ].copy()

    # Aplicar filtros de calidad
    print("\n🔍 Aplicando filtros de calidad...")

    # Parámetros de filtrado
    min_legislators = 20  # Mínimo de legisladores que votaron
    min_votes = 10        # Mínimo de votos por legislador en cada período

    # Filtrar votaciones por período
    filtered_period_votes = {}

    for period_id, data in period_votes.items():
        period_matrix = data['matrix'].loc[common_legislators_list].copy()
        period_vote_meta = data['vote_metadata'].copy()

        # Filtrar votaciones con suficientes legisladores
        valid_votes = []
        for col in period_matrix.columns:
            vote_data = period_matrix[col]
            valid_count = (vote_data != 9).sum()  # No abstenciones/ausencias

            if valid_count >= min_legislators:
                valid_votes.append(col)

        if len(valid_votes) == 0:
            print(
                f"   ⚠️  {data['name']}: 0 votaciones válidas después de filtrar")
            continue

        # Aplicar filtro de votaciones
        period_matrix = period_matrix[valid_votes]
        period_vote_meta = period_vote_meta[
            period_vote_meta['vote_id'].astype(str).isin(valid_votes)
        ]

        # Filtrar legisladores con suficientes votos
        valid_legislators = []
        for leg_id in period_matrix.index:
            leg_votes = period_matrix.loc[leg_id]
            valid_count = (leg_votes != 9).sum()

            if valid_count >= min_votes:
                valid_legislators.append(leg_id)

        if len(valid_legislators) == 0:
            print(
                f"   ⚠️  {data['name']}: 0 legisladores válidos después de filtrar")
            continue

        # Aplicar filtro de legisladores
        period_matrix = period_matrix.loc[valid_legislators]

        filtered_period_votes[period_id] = {
            'matrix': period_matrix,
            'vote_metadata': period_vote_meta,
            'name': data['name']
        }

        print(
            f"   ✅ {data['name']}: {len(valid_legislators)} legisladores × {len(valid_votes)} votaciones")

    if len(filtered_period_votes) == 0:
        raise ValueError(
            "❌ No hay datos después de aplicar filtros de calidad")

    # Actualizar lista de legisladores comunes (después de filtros)
    legislators_after_filter = {
        period_id: set(data['matrix'].index)
        for period_id, data in filtered_period_votes.items()
    }
    final_common_legislators = set.intersection(
        *legislators_after_filter.values())
    final_common_legislators_list = sorted(list(final_common_legislators))

    print(
        f"\n   📋 Legisladores finales consistentes: {len(final_common_legislators_list)}")

    # Filtrar matrices finales
    for period_id in filtered_period_votes:
        filtered_period_votes[period_id]['matrix'] = filtered_period_votes[period_id]['matrix'].loc[
            final_common_legislators_list
        ]

    # Actualizar metadata de legisladores
    final_legislator_metadata = legislator_metadata[
        legislator_metadata['legislator_id'].isin(
            final_common_legislators_list)
    ].copy()

    # Exportar archivos CSV por período
    print("\n💾 Exportando archivos CSV por período...")

    for period_id, data in filtered_period_votes.items():
        period_matrix = data['matrix']
        period_vote_meta = data['vote_metadata']

        # Nombre de archivos con prefijo del período
        votes_file = os.path.join(output_dir, f'{period_id}_votes_matrix.csv')
        vote_meta_file = os.path.join(
            output_dir, f'{period_id}_vote_metadata.csv')

        # Guardar matriz de votos
        period_matrix.to_csv(votes_file)

        # Guardar metadata de votaciones
        period_vote_meta.to_csv(vote_meta_file, index=False)

        print(f"   ✅ {data['name']}: {votes_file}")

    # Guardar metadata de legisladores (única para todos los períodos)
    legislator_file = os.path.join(output_dir, 'legislator_metadata.csv')
    final_legislator_metadata.to_csv(legislator_file, index=False)
    print(f"   ✅ Metadata de legisladores: {legislator_file}")

    # Crear archivo de información de períodos
    periods_info_file = os.path.join(output_dir, 'periods_info.csv')
    periods_df = pd.DataFrame([
        {
            'period_id': period_id,
            'period_name': data['name'],
            'num_votes': data['matrix'].shape[1],
            'num_legislators': data['matrix'].shape[0]
        }
        for period_id, data in filtered_period_votes.items()
    ])
    periods_df.to_csv(periods_info_file, index=False)
    print(f"   ✅ Información de períodos: {periods_info_file}")

    # Resumen final
    print("\n" + "="*70)
    print("✅ EXPORTACIÓN COMPLETADA - 6 PERÍODOS SEMESTRALES")
    print("="*70)
    print(f"\n📊 Resumen:")
    print(f"   • Total de períodos: {len(filtered_period_votes)}")
    print(
        f"   • Legisladores consistentes: {len(final_common_legislators_list)}")
    print(
        f"   • Votaciones totales: {sum(data['matrix'].shape[1] for data in filtered_period_votes.values())}")
    print(f"\n📁 Archivos generados en: {output_dir}/")
    print(
        f"   • {len(filtered_period_votes)} archivos de matrices de votos (P*_votes_matrix.csv)")
    print(
        f"   • {len(filtered_period_votes)} archivos de metadata de votaciones (P*_vote_metadata.csv)")
    print(f"   • 1 archivo de metadata de legisladores (legislator_metadata.csv)")
    print(f"   • 1 archivo de información de períodos (periods_info.csv)")

    print("\n" + "="*70)
    print("📋 DETALLES POR PERÍODO:")
    print("="*70)
    for period_id, data in filtered_period_votes.items():
        print(f"\n{data['name']} ({period_id}):")
        print(f"   • Votaciones: {data['matrix'].shape[1]}")
        print(f"   • Legisladores: {data['matrix'].shape[0]}")
        print(f"   • Archivo: {period_id}_votes_matrix.csv")

    print("\n" + "="*70)
    print("🚀 SIGUIENTE PASO:")
    print("="*70)
    print("\nPara ejecutar DW-NOMINATE con estos datos:")
    print("   1. Ejecuta el script R correspondiente:")
    print(f"      cd scripts/r")
    print(f"      Rscript r_dwnominate_6periods_script.R")
    print("\n" + "="*70 + "\n")

    return filtered_period_votes, final_legislator_metadata


def main():
    """Función principal con argumentos CLI"""
    parser = argparse.ArgumentParser(
        description='Exportar datos de W-NOMINATE a DW-NOMINATE (6 períodos semestrales 2019-2021)'
    )
    parser.add_argument(
        '--input-dir',
        type=str,
        default='data/wnominate/input',
        help='Directorio con archivos CSV de W-NOMINATE (default: data/wnominate/input)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/dwnominate_6periods/input',
        help='Directorio de salida para DW-NOMINATE (default: data/dwnominate_6periods/input)'
    )

    args = parser.parse_args()

    try:
        export_votes_for_dwnominate_from_csv(
            input_dir=args.input_dir,
            output_dir=args.output_dir
        )
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        raise


if __name__ == "__main__":
    main()
