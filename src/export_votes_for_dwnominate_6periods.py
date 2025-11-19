#!/usr/bin/env python
"""
Export Votes for DW-NOMINATE - 6 Periods (Political Division)

Este script divide el 55º Período Legislativo (2018-2022) en 6 períodos basados en
hitos políticos importantes de Chile, dividiendo cada uno equitativamente:

Períodos Políticos Base:
- P1: Inicio del PL (11/03/2018) hasta Estallido Social (18/10/2019)
- P2: Estallido Social hasta Plebiscito Nacional 2020 (25/10/2020)
- P3: Plebiscito Nacional 2020 hasta Fin del PL (10/03/2022)

Cada período se divide equitativamente en 2 subperíodos:
- P1a, P1b (571 días cada uno aprox.)
- P2a, P2b (187 días cada uno aprox.)
- P3a, P3b (250 días cada uno aprox.)

Usage:
    python export_votes_for_dwnominate_6periods.py --input-dir data/wnominate/input --output-dir data/dwnominate_6periods/input
"""

import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import argparse


def define_6_periods() -> List[Dict]:
    """
    Define 6 periods for DW-NOMINATE analysis based on Chilean political events.

    Each of the 3 major political periods is divided equitably into 2 subperiods.

    Returns:
        List of period definitions with start/end dates
    """
    # Período Político 1: Inicio del PL hasta Estallido Social
    p1_start = datetime(2018, 3, 11)
    p1_end = datetime(2019, 10, 17)  # Día antes del estallido
    p1_days = (p1_end - p1_start).days
    p1_mid = p1_start + timedelta(days=p1_days // 2)

    # Período Político 2: Estallido Social hasta Plebiscito Nacional 2020
    p2_start = datetime(2019, 10, 18)
    p2_end = datetime(2020, 10, 24)  # Día antes del plebiscito
    p2_days = (p2_end - p2_start).days
    p2_mid = p2_start + timedelta(days=p2_days // 2)

    # Período Político 3: Plebiscito Nacional 2020 hasta Fin del PL
    p3_start = datetime(2020, 10, 25)
    p3_end = datetime(2022, 3, 10)
    p3_days = (p3_end - p3_start).days
    p3_mid = p3_start + timedelta(days=p3_days // 2)

    return [
        {
            'id': 'P1a',
            'name': 'Inicio PL - Primera Mitad',
            'description': 'Marzo 2018 - Septiembre 2018 (Pre-Estallido, Parte 1)',
            'start_date': p1_start.strftime('%Y-%m-%d'),
            'end_date': p1_mid.strftime('%Y-%m-%d'),
            'political_context': 'Inicio del gobierno de Sebastián Piñera (2º mandato)'
        },
        {
            'id': 'P1b',
            'name': 'Inicio PL - Segunda Mitad',
            'description': 'Octubre 2018 - Octubre 2019 (Pre-Estallido, Parte 2)',
            'start_date': (p1_mid + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': p1_end.strftime('%Y-%m-%d'),
            'political_context': 'Período previo al estallido social'
        },
        {
            'id': 'P2a',
            'name': 'Estallido Social - Primera Mitad',
            'description': 'Octubre 2019 - Abril 2020 (Estallido y COVID-19)',
            'start_date': p2_start.strftime('%Y-%m-%d'),
            'end_date': p2_mid.strftime('%Y-%m-%d'),
            'political_context': 'Estallido social y llegada de la pandemia'
        },
        {
            'id': 'P2b',
            'name': 'Estallido Social - Segunda Mitad',
            'description': 'Abril 2020 - Octubre 2020 (Pandemia y Acuerdo por la Paz)',
            'start_date': (p2_mid + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': p2_end.strftime('%Y-%m-%d'),
            'political_context': 'Pandemia COVID-19 y preparación del plebiscito'
        },
        {
            'id': 'P3a',
            'name': 'Post-Plebiscito - Primera Mitad',
            'description': 'Octubre 2020 - Agosto 2021 (Constitución y Elecciones)',
            'start_date': p3_start.strftime('%Y-%m-%d'),
            'end_date': p3_mid.strftime('%Y-%m-%d'),
            'political_context': 'Plebiscito aprueba nueva constitución, Convención Constituyente'
        },
        {
            'id': 'P3b',
            'name': 'Post-Plebiscito - Segunda Mitad',
            'description': 'Agosto 2021 - Marzo 2022 (Elecciones Presidenciales)',
            'start_date': (p3_mid + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': p3_end.strftime('%Y-%m-%d'),
            'political_context': 'Elecciones presidenciales y fin del período legislativo'
        }
    ]


def export_votes_for_dwnominate_6periods(
    input_dir: str = "data/wnominate/input",
    output_dir: str = "data/dwnominate_6periods/input"
):
    """
    Exporta datos para DW-NOMINATE divididos en 6 períodos políticos.

    Args:
        input_dir: Directorio con archivos CSV de W-NOMINATE
        output_dir: Directorio de salida para DW-NOMINATE (6 períodos)
    """

    print("="*70)
    print("  DW-NOMINATE Export - 6 Political Periods")
    print("  55º Período Legislativo (2018-2022)")
    print("="*70)
    print(f"\nInput directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Dividing into 6 periods based on political events\n")

    # Verificar archivos necesarios
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
                f"Make sure you have W-NOMINATE CSV files in {input_dir}/"
            )

    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)

    # Definir períodos
    periods = define_6_periods()

    # Mostrar información de períodos
    print("Political Periods Defined:")
    print("-" * 70)
    for i, period in enumerate(periods, 1):
        print(f"\n{i}. {period['id']}: {period['name']}")
        print(f"   Fechas: {period['start_date']} a {period['end_date']}")
        print(f"   Contexto: {period['political_context']}")
    print("\n" + "="*70 + "\n")

    # Cargar datos
    print("Loading data files...")
    votes_matrix_path = os.path.join(input_dir, 'votes_matrix.csv')
    votes_df = pd.read_csv(votes_matrix_path, index_col=0)
    print(
        f"Votes matrix: {votes_df.shape[0]} legislators x {votes_df.shape[1]} votes")

    legislator_meta_path = os.path.join(input_dir, 'legislator_metadata.csv')
    legislator_meta = pd.read_csv(legislator_meta_path)
    print(f"Legislator metadata: {len(legislator_meta)} legislators")

    vote_meta_path = os.path.join(input_dir, 'vote_metadata.csv')
    vote_meta = pd.read_csv(vote_meta_path)
    print(f"Vote metadata: {len(vote_meta)} votes\n")

    # Asignar votaciones a períodos
    print("Assigning votes to political periods...")

    vote_period_map = {}

    for _, vote_row in vote_meta.iterrows():
        vote_id = str(vote_row['vote_id']) if 'vote_id' in vote_row else str(
            vote_row['id'])
        fecha_str = vote_row.get('fecha', '')

        if not fecha_str or pd.isna(fecha_str):
            continue

        try:
            # Parse date
            if ' ' in str(fecha_str):
                fecha = datetime.strptime(str(fecha_str), '%Y-%m-%d %H:%M:%S')
            else:
                fecha = datetime.strptime(str(fecha_str), '%Y-%m-%d')

            # Asignar a período político
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

    # Agregar columna de período
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
    print("\n📊 Votes per political period:")
    for period in periods:
        count = period_counts.get(period['id'], 0)
        print(f"   {period['id']}: {count:,} votes ({period['name']})")

    votes_with_period = vote_meta[vote_meta['period'].notna()]
    print(f"\n{len(votes_with_period):,} votes assigned to periods")
    print(
        f"{len(vote_meta) - len(votes_with_period):,} votes excluded (no period)\n")

    # Crear matrices de votos por período
    print("Creating vote matrices for each period...")

    period_matrices = {}
    period_vote_lists = {}

    for period in periods:
        period_id = period['id']

        # Obtener votaciones de este período
        period_votes = vote_meta[vote_meta['period'] == period_id]

        if len(period_votes) == 0:
            print(f"No votes for {period_id}, skipping...")
            continue

        # Convertir IDs a strings
        vote_ids = [str(
            vid) for vid in period_votes['vote_id' if 'vote_id' in period_votes.columns else 'id'].tolist()]

        # Filtrar columnas de la matriz
        available_vote_ids = [
            vid for vid in vote_ids if vid in votes_df.columns]

        if not available_vote_ids:
            print(
                f"No matching votes in matrix for {period_id}, skipping...")
            continue

        # Crear matriz para este período
        period_matrix = votes_df[available_vote_ids].copy()

        print(
            f"\n   {period_id}: {period_matrix.shape[0]} legislators x {period_matrix.shape[1]} votes")

        # Filtrar por participación mínima
        min_votes_per_legislator = 5  # Reducido para períodos más cortos
        min_legislators_per_vote = 10

        # Filtrar legisladores
        legislator_vote_counts = (period_matrix != 9).sum(axis=1)
        active_legislators = legislator_vote_counts >= min_votes_per_legislator

        # Filtrar votaciones
        vote_participation = (period_matrix != 9).sum(axis=0)
        active_votes = vote_participation >= min_legislators_per_vote

        # Aplicar filtros
        filtered_matrix = period_matrix.loc[active_legislators, active_votes]

        print(
            f"   After filtering: {filtered_matrix.shape[0]} legislators x {filtered_matrix.shape[1]} votes")

        # Ordenar cronológicamente
        period_votes_sorted = period_votes[
            period_votes['vote_id' if 'vote_id' in period_votes.columns else 'id'].astype(
                str).isin(filtered_matrix.columns)
        ]
        period_votes_sorted = period_votes_sorted.sort_values('fecha')

        chronological_order = [
            str(vid) for vid in period_votes_sorted['vote_id' if 'vote_id' in period_votes_sorted.columns else 'id'].tolist()
        ]
        available_cols = [
            col for col in chronological_order if col in filtered_matrix.columns]

        if available_cols:
            filtered_matrix = filtered_matrix[available_cols]
            print(f"   ✓ Votes sorted chronologically")

        period_matrices[period_id] = filtered_matrix
        period_vote_lists[period_id] = [
            int(vid) for vid in filtered_matrix.columns.tolist()]

    if not period_matrices:
        raise ValueError(
            "No periods could be created! Check date ranges and vote metadata.")

    # Asegurar conjunto consistente de legisladores
    print("\nEnsuring consistent legislator set across all periods...")

    all_legislators = set()
    for matrix in period_matrices.values():
        all_legislators.update(matrix.index.tolist())

    all_legislators = sorted(list(all_legislators))
    print(f"   Total unique legislators: {len(all_legislators)}")

    # Reindexar matrices
    for period_id, matrix in period_matrices.items():
        period_matrices[period_id] = matrix.reindex(
            index=all_legislators, fill_value=9)

    # Eliminar legisladores sin votos válidos en algún período
    print("\nChecking for legislators with insufficient votes...")

    legislators_to_remove = set()
    min_required_votes = 1

    for period_id, matrix in period_matrices.items():
        for legislator_id in all_legislators:
            legislator_votes = matrix.loc[legislator_id]
            valid_vote_count = (legislator_votes != 9).sum()

            if valid_vote_count < min_required_votes:
                legislators_to_remove.add(legislator_id)

    if legislators_to_remove:
        legislators_to_remove = sorted(list(legislators_to_remove))
        print(
            f"   Removing {len(legislators_to_remove)} legislators with < {min_required_votes} valid votes in at least one period")

        legislators_to_keep = [
            lid for lid in all_legislators if lid not in legislators_to_remove]

        for period_id in period_matrices.keys():
            period_matrices[period_id] = period_matrices[period_id].loc[legislators_to_keep]

        all_legislators = legislators_to_keep
        print(f"   Final legislator count: {len(all_legislators)}")
    else:
        print(
            f"   All {len(all_legislators)} legislators meet minimum requirements")

    # Exportar matrices
    print("\nExporting vote matrices...")

    for period_id, matrix in period_matrices.items():
        filename = f"{output_dir}/votes_matrix_{period_id.lower()}.csv"
        matrix.to_csv(filename)
        print(
            f"   {os.path.basename(filename)} ({matrix.shape[0]} x {matrix.shape[1]})")

    # Exportar metadata de legisladores
    print("\nExporting legislator metadata...")

    active_legislator_ids = [int(lid) for lid in all_legislators]
    active_legislator_meta = legislator_meta[
        legislator_meta['legislator_id'].astype(int).isin(active_legislator_ids) |
        legislator_meta['id'].astype(int).isin(active_legislator_ids)
    ].copy()

    if 'legislator_id' not in active_legislator_meta.columns:
        active_legislator_meta['legislator_id'] = active_legislator_meta['id']

    active_legislator_meta.to_csv(
        f"{output_dir}/legislator_metadata.csv", index=False)
    print(
        f"   legislator_metadata.csv ({len(active_legislator_meta)} legislators)")

    # Exportar metadata de votaciones
    print("\nExporting vote metadata...")

    all_vote_ids = set()
    for vote_ids in period_vote_lists.values():
        all_vote_ids.update(vote_ids)

    vote_meta_filtered = vote_meta[
        vote_meta['vote_id' if 'vote_id' in vote_meta.columns else 'id'].isin(
            all_vote_ids)
    ].copy()

    vote_meta_filtered.to_csv(f"{output_dir}/vote_metadata.csv", index=False)
    print(f"   vote_metadata.csv ({len(vote_meta_filtered)} votes)")

    # Crear script R
    print("\nCreating R script for DW-NOMINATE (6 periods)...")
    create_r_dwnominate_script_6periods(output_dir, periods, period_matrices)

    # Resumen final
    print("\n" + "="*70)
    print("🎉 EXPORT COMPLETE - 6 POLITICAL PERIODS")
    print("="*70)
    print(f"\nOutput directory: {output_dir}/")
    print(f"\nFiles created:")
    for period_id in period_matrices.keys():
        print(f"   • votes_matrix_{period_id.lower()}.csv")
    print(f"   • legislator_metadata.csv")
    print(f"   • vote_metadata.csv")
    print(f"   • r_dwnominate_6periods_script.R")
    return {
        'periods': len(period_matrices),
        'legislators': len(all_legislators),
        'export_dir': output_dir
    }


def create_r_dwnominate_script_6periods(
    output_dir: str,
    periods: List[Dict],
    period_matrices: Dict
):
    """
    Create R script for DW-NOMINATE with 6 political periods.
    """

    # Generate period loading code
    period_load_code = "# Storage for rollcall objects\nrc_list <- list()\n\n"

    for i, period in enumerate(periods):
        period_id = period['id']
        if period_id not in period_matrices:
            continue

        period_num = i + 1
        period_load_code += f"""# PERIOD {period_num}: {period['name']}
# {period['description']}
# Context: {period['political_context']}
votes_{period_id.lower()} <- read.csv("../../data/dwnominate_6periods/input/votes_matrix_{period_id.lower()}.csv", row.names = 1)
votes_mat_{period_id.lower()} <- as.matrix(votes_{period_id.lower()})

period_legislators_{period_id.lower()} <- rownames(votes_mat_{period_id.lower()})
legis_data_{period_id.lower()} <- data.frame(
  legislator_id = as.integer(period_legislators_{period_id.lower()}),
  row.names = period_legislators_{period_id.lower()},
  stringsAsFactors = FALSE
)
legis_data_{period_id.lower()} <- legis_data_{period_id.lower()} %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = "legislator_id"
  )
legis_data_{period_id.lower()}$party <- ifelse(is.na(legis_data_{period_id.lower()}$partido), "IND", legis_data_{period_id.lower()}$partido)
rownames(legis_data_{period_id.lower()}) <- period_legislators_{period_id.lower()}

rc_{period_id.lower()} <- rollcall(
  data = votes_mat_{period_id.lower()},
  yea = 1,
  nay = 0,
  missing = NA,
  notInLegis = 9,
  legis.names = rownames(votes_mat_{period_id.lower()}),
  vote.names = colnames(votes_mat_{period_id.lower()}),
  desc = "{period['name']}",
  legis.data = legis_data_{period_id.lower()}
)
cat("{period['name']}: ", nrow(rc_{period_id.lower()}$votes), " legislators x ", 
    ncol(rc_{period_id.lower()}$votes), " votes\\n")
rc_list[[{period_num}]] <- rc_{period_id.lower()}

"""

    r_script = f'''# DW-NOMINATE Analysis - 6 Political Periods
# 55º Período Legislativo (2018-2022)
# Divided based on major Chilean political events
# Generated automatically

cat("\\n")
cat("===============================================\\n")
cat("  DW-NOMINATE - 6 Political Periods          \\n")
cat("  55º PL (2018-2022) - Chile                 \\n")
cat("===============================================\\n")
cat("\\n")

# Install required packages
if (!require(pscl)) {{
  cat("Installing pscl...\\n")
  install.packages("pscl")
}}
if (!require(dplyr)) {{
  cat("Installing dplyr...\\n")
  install.packages("dplyr")
}}
if (!require(dwnominate)) {{
  cat("Installing dwnominate...\\n")
  install.packages("remotes")
  remotes::install_github("wmay/dwnominate")
}}

library(pscl)
library(dplyr)
library(dwnominate)

cat("\\nAll packages loaded\\n\\n")

# Load metadata
legislator_meta <- read.csv("../../data/dwnominate_6periods/input/legislator_metadata.csv")
vote_meta <- read.csv("../../data/dwnominate_6periods/input/vote_metadata.csv")

cat("Metadata loaded:\\n")
cat("   Legislators: ", nrow(legislator_meta), "\\n")
cat("   Votes: ", nrow(vote_meta), "\\n\\n")

cat("Loading 6 political periods...\\n\\n")
{period_load_code}

cat("\\nAll 6 periods loaded successfully\\n")
cat("Rollcall list contains ", length(rc_list), " periods\\n\\n")
# Set polarity anchors
cat("Setting polarity anchors...\\n")

# Find legislators in ALL periods
all_period_legislators <- list()
for (i in 1:6) {{
  all_period_legislators[[i]] <- rownames(rc_list[[i]]$votes)
}}

common_legislators <- Reduce(intersect, all_period_legislators)
cat("   Legislators in ALL 6 periods: ", length(common_legislators), "\\n")

# Chilean political spectrum anchors
left_parties <- c("PC", "PS")
right_parties <- c("UDI", "RN")

left_legislators <- legislator_meta$legislator_id[legislator_meta$partido %in% left_parties]
right_legislators <- legislator_meta$legislator_id[legislator_meta$partido %in% right_parties]

# Find left-wing legislator in common set
left_in_common <- left_legislators[as.character(left_legislators) %in% common_legislators]

if (length(left_in_common) > 0) {{
  polarity_anchor <- as.character(left_in_common[1])
  anchor_info <- legislator_meta[legislator_meta$legislator_id == as.integer(polarity_anchor), ]
  cat("   Polarity anchor: ", polarity_anchor, " (", 
      anchor_info$partido[1], " - ", anchor_info$nombres[1], ")\\n\\n")
}} else {{
  polarity_anchor <- common_legislators[1]
  cat("   Fallback polarity anchor: ", polarity_anchor, "\\n\\n")
}}

cat("Running DW-NOMINATE (6 periods)...\\n")
cat("   This may take several minutes.\\n\\n")

# Run DW-NOMINATE
dw_result <- dwnominate(
  rc_list,
  id = "legislator_id",
  dims = 2,
  model = 1,  # Linear change over time
  polarity = polarity_anchor,
  minvotes = 5,  # Reducido para períodos más cortos
  lop = 0.025,  # Lopsided vote threshold (2.5%)
  niter = 4,
  beta = 5.9539,
  w = 0.3463,
  verbose = TRUE
)

cat("\\nDW-NOMINATE estimation complete!\\n\\n")

# Print summary
cat("\\n=== DW-NOMINATE RESULTS ===\\n")
print(summary(dw_result))

# Extract coordinates
legislators <- dw_result$legislators %>%
  rename(
    legislator = ID,
    period = session
  ) %>%
  mutate(legislator = as.integer(legislator))

# Add metadata
legislators <- legislators %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = c("legislator" = "legislator_id")
  )

# Create output directory
output_dir <- "../../data/dwnominate_6periods/output"
if (!dir.exists(output_dir)) {{
  dir.create(output_dir, recursive = TRUE)
}}

# Save combined results
cat("\nSaving results...\n")
write.csv(legislators, file.path(output_dir, "dwnominate_coordinates_all_periods.csv"), row.names = FALSE)
cat("dwnominate_coordinates_all_periods.csv\n")

# Save period-specific files
cat("\nSaving period-specific coordinates...\n")
for (i in 1:6) {{
  period_coords <- legislators %>%
    filter(period == i) %>%
    select(legislator, period, coord1D, coord2D, se1D, se2D, nombres, partido, region, distrito)
  
  period_id <- c("P1a", "P1b", "P2a", "P2b", "P3a", "P3b")[i]
  output_file <- file.path(output_dir, paste0("coordinates_", period_id, "_6periods.csv"))
  write.csv(period_coords, output_file, row.names = FALSE)
  cat("", basename(output_file), " (", nrow(period_coords), " legislators)\\n")
}}

# Save bill parameters
cat("\\nSaving bill parameters...\\n")
write.csv(dw_result$rollcalls, file.path(output_dir, "dwnominate_bill_parameters.csv"), row.names = FALSE)
cat("dwnominate_bill_parameters.csv\\n")

# Create visualization
cat("\\nCreating visualization...\\n")
results_dir <- "../../results"
if (!dir.exists(results_dir)) {{
  dir.create(results_dir, recursive = TRUE)
}}

png(file.path(results_dir, "dwnominate_6periods.png"), width = 1200, height = 800, res = 150)
plot(dw_result)
title(main = "DW-NOMINATE - 6 Political Periods\\n55º PL Chile (2018-2022)", line = 0.5)
dev.off()
cat("dwnominate_6periods.png\\n")

# Summary
cat("\\n=== ANALYSIS COMPLETE ===\\n")
cat("Legislators analyzed: ", length(unique(legislators$legislator)), "\\n")
cat("Total periods: 6\\n")
cat("Model: Linear (model=1)\\n")
cat("Dimensions: 2\\n")

cat("\nAnalysis complete!\n")
cat("output: data/dwnominate_6periods/output/\n")
cat("Next: Run correct_polarity_dwnominate_6periods.R\n\n")
'''

    # Save R script to scripts/r/
    r_scripts_dir = os.path.join(os.path.dirname(
        output_dir), '..', '..', 'scripts', 'r')
    os.makedirs(r_scripts_dir, exist_ok=True)

    script_path = os.path.join(r_scripts_dir, "r_dwnominate_6periods_script.R")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(r_script)

    print(f"   r_dwnominate_6periods_script.R")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Export votes for DW-NOMINATE (6 political periods)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--input-dir',
        type=str,
        default='data/wnominate/input',
        help='Input directory with W-NOMINATE CSV files'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/dwnominate_6periods/input',
        help='Output directory for DW-NOMINATE (6 periods)'
    )

    args = parser.parse_args()

    try:
        result = export_votes_for_dwnominate_6periods(
            args.input_dir, args.output_dir)

        if result:
            print(f"\nExport successful!")
            print(f"   Periods: {result['periods']}")
            print(f"   Legislators: {result['legislators']}")
            print(f"   Directory: {result['export_dir']}")
        else:
            print("\nExport failed!")
            return 1

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
