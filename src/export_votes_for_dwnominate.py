#!/usr/bin/env python
"""
Export Votes for DW-NOMINATE from Existing CSV Files

Esta versión alternativa NO requiere MongoDB. En su lugar, lee los archivos CSV
que ya fueron exportados previamente para W-NOMINATE y los divide por períodos.

Usage:
    python export_votes_for_dwnominate.py --input-dir data/input --output-dir data/dwnominate
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
                                         output_dir: str = "data/dwnominate"):
    """
    Exporta datos para DW-NOMINATE desde archivos CSV existentes.

    Args:
        input_dir: Directorio con archivos CSV de W-NOMINATE
        output_dir: Directorio de salida para DW-NOMINATE
    """

    print(f"🔍 Converting W-NOMINATE CSV data to DW-NOMINATE format...")
    print(f"📂 Input directory: {input_dir}")
    print(f"📂 Output directory: {output_dir}")
    print(f"📅 Dividing into 5 periods: 2018, 2019, 2020-S1, 2020-S2, 2021\n")

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
                f"❌ Required file not found: {filepath}\n"
                f"Make sure you have the W-NOMINATE CSV files in {input_dir}/"
            )

    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)

    # Define periods
    periods = define_periods()

    # 1. Cargar matriz de votos completa
    print("📥 Loading votes matrix...")
    votes_matrix_path = os.path.join(input_dir, 'votes_matrix.csv')
    votes_df = pd.read_csv(votes_matrix_path, index_col=0)
    print(
        f"✅ Loaded matrix: {votes_df.shape[0]} legislators x {votes_df.shape[1]} votes")

    # 2. Cargar metadata de legisladores
    print("📥 Loading legislator metadata...")
    legislator_meta_path = os.path.join(input_dir, 'legislator_metadata.csv')
    legislator_meta = pd.read_csv(legislator_meta_path)
    print(f"✅ Loaded {len(legislator_meta)} legislators")

    # 3. Cargar metadata de votaciones
    print("📥 Loading vote metadata...")
    vote_meta_path = os.path.join(input_dir, 'vote_metadata.csv')
    vote_meta = pd.read_csv(vote_meta_path)
    print(f"✅ Loaded {len(vote_meta)} votes\n")

    # 4. Asignar votaciones a períodos según fecha
    print("📅 Assigning votes to legislative periods...")

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
            print(f"⚠️  Could not parse date for vote {vote_id}: {fecha_str}")
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
    print("\n📊 Votes per period:")
    for period in periods:
        count = period_counts.get(period['id'], 0)
        print(f"   {period['id']} ({period['name']}): {count:,} votes")

    votes_with_period = vote_meta[vote_meta['period'].notna()]
    print(f"\n✅ {len(votes_with_period)} votes successfully assigned to periods")
    print(f"⚠️  {len(vote_meta) - len(votes_with_period)} votes without period assignment (excluded)\n")

    # 5. Crear matriz de votos para cada período
    print("📊 Creating vote matrices for each period...")

    period_matrices = {}
    period_vote_lists = {}

    for period in periods:
        period_id = period['id']

        # Obtener IDs de votaciones para este período
        period_votes = vote_meta[vote_meta['period'] == period_id]

        if len(period_votes) == 0:
            print(f"⚠️  No votes found for {period_id}, skipping...")
            continue

        # Convertir IDs a strings para comparar con columnas de la matriz
        vote_ids = [str(
            vid) for vid in period_votes['vote_id' if 'vote_id' in period_votes.columns else 'id'].tolist()]

        # Filtrar columnas de la matriz que corresponden a este período
        available_vote_ids = [
            vid for vid in vote_ids if vid in votes_df.columns]

        if not available_vote_ids:
            print(
                f"⚠️  No matching votes found in matrix for {period_id}, skipping...")
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
            f"   After filtering: {filtered_matrix.shape[0]} legislators x {filtered_matrix.shape[1]} votes")

        # NUEVO: Filtrar votaciones unánimes (todas Sí o todas No)
        # DW-NOMINATE requiere variación en las votaciones
        non_unanimous_votes = []
        unanimous_count = 0

        for col in filtered_matrix.columns:
            vote_data = filtered_matrix[col]
            # Contar solo votos válidos (no 9 = ausente)
            valid_votes = vote_data[vote_data != 9]

            if len(valid_votes) > 0:
                yeas = (valid_votes == 1).sum()
                nays = (valid_votes == 0).sum()

                # Incluir solo si hay al menos 1 Sí Y al menos 1 No
                if yeas > 0 and nays > 0:
                    non_unanimous_votes.append(col)
                else:
                    unanimous_count += 1

        if unanimous_count > 0:
            print(
                f"   Removed {unanimous_count} unanimous votes (no variation)")

        filtered_matrix = filtered_matrix[non_unanimous_votes]
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
            "❌ No periods could be created! Check your date ranges and vote metadata.")

    # 6. Asegurar conjunto consistente de legisladores
    print("\n🔄 Ensuring consistent legislator set across periods...")

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
    print("\n🔍 Checking for legislators with insufficient votes in any period...")

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
            f"   ⚠️  Removing {len(legislators_to_remove)} legislators with < {min_required_votes} valid votes in at least one period:")

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
        print(f"   ✅ Final legislator count: {len(all_legislators)}")
    else:
        print(f"   ✅ All legislators meet minimum vote requirements in all periods")

    # 7. Exportar matrices de votos por período
    print("\n💾 Exporting vote matrices...")

    for period_id, matrix in period_matrices.items():
        filename = f"{output_dir}/votes_matrix_{period_id.lower()}.csv"
        matrix.to_csv(filename)
        print(f"   ✅ {filename} ({matrix.shape[0]} x {matrix.shape[1]})")

    # 8. Exportar metadata de legisladores
    print("\n💾 Exporting legislator metadata...")

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
        f"   ✅ legislator_metadata.csv ({len(active_legislator_meta)} legislators)")

    # 9. Exportar metadata de votaciones con asignación de períodos
    print("\n💾 Exporting vote metadata with period assignments...")

    # Filtrar solo votaciones que están en algún período
    all_vote_ids = set()
    for vote_ids in period_vote_lists.values():
        all_vote_ids.update(vote_ids)

    vote_meta_filtered = vote_meta[
        vote_meta[('vote_id' if 'vote_id' in vote_meta.columns else 'id')].isin(
            all_vote_ids)
    ].copy()

    vote_meta_filtered.to_csv(f"{output_dir}/vote_metadata.csv", index=False)
    print(f"   ✅ vote_metadata.csv ({len(vote_meta_filtered)} votes)")

    # 10. Crear script R para DW-NOMINATE
    print("\n📝 Creating R script for DW-NOMINATE...")

    create_r_dwnominate_script(output_dir, periods, period_matrices)

    # 11. Resumen
    print("\n" + "="*60)
    print("🎉 EXPORT COMPLETE!")
    print("="*60)
    print(f"\n📂 Output directory: {output_dir}/")
    print(f"\n📄 Files created:")
    for period_id in period_matrices.keys():
        print(f"   • votes_matrix_{period_id.lower()}.csv")
    print(f"   • legislator_metadata.csv")
    print(f"   • vote_metadata.csv")
    print(f"   • r_dwnominate_script.R")

    print(f"\n🚀 Próximos pasos:")
    print(f"   1. cd {output_dir}")
    print(f"   2. Rscript r_dwnominate_script.R")
    print(f"   3. Los resultados se guardarán en archivos dwnominate_coordinates_*.csv")
    print(f"   4. Usar csv_dwnominate_graph.py para visualizar resultados")

    return {
        'periods': len(period_matrices),
        'legislators': len(all_legislators),
        'export_dir': output_dir
    }


def create_r_dwnominate_script(output_dir: str, periods: List[Dict],
                               period_matrices: Dict):
    """
    Create R script for running DW-NOMINATE analysis.

    Args:
        output_dir: Output directory path
        periods: List of period definitions
        period_matrices: Dictionary of period matrices
    """

    # Generate period loading code with legis.data
    period_load_code = "# Storage for rollcall objects\nrc_list <- list()\n\n"

    for i, period in enumerate(periods):
        period_id = period['id']
        if period_id not in period_matrices:
            continue

        period_num = i + 1
        period_load_code += f"""# PERIOD {period_num}: {period['name']}
votes_{period_id.lower()} <- read.csv("votes_matrix_{period_id.lower()}.csv", row.names = 1)
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
cat("✅ {period['name']}: ", nrow(rc_{period_id.lower()}$votes), " legislators x ", 
    ncol(rc_{period_id.lower()}$votes), " votes\\n")
rc_list[[{period_num}]] <- rc_{period_id.lower()}

"""

    r_script = f'''# DW-NOMINATE Analysis Script for Chilean Congressional Data
# 55th Legislative Period (2018-2022) divided into 5 periods
# Generated automatically from CSV files

cat("\\n")
cat("===============================================\\n")
cat("  DW-NOMINATE Analysis - Chilean Congress     \\n")
cat("  55th Legislative Period (2018-2022)         \\n")
cat("===============================================\\n")
cat("\\n")

# Install required packages if not already installed
if (!require(pscl)) {{
  cat("📦 Installing pscl package...\\n")
  install.packages("pscl")
}}
if (!require(dplyr)) {{
  cat("📦 Installing dplyr package...\\n")
  install.packages("dplyr")
}}
if (!require(dwnominate)) {{
  cat("📦 Installing dwnominate package...\\n")
  install.packages("remotes")
  remotes::install_github("wmay/dwnominate")
}}

library(pscl)
library(dplyr)
library(dwnominate)

cat("\\n✅ All packages loaded successfully\\n\\n")

# Load metadata
legislator_meta <- read.csv("legislator_metadata.csv")
vote_meta <- read.csv("vote_metadata.csv")

cat("📊 Metadata loaded:\\n")
cat("   Legislators: ", nrow(legislator_meta), "\\n")
cat("   Votes: ", nrow(vote_meta), "\\n\\n")

cat("📅 Loading vote matrices for each period...\\n\\n")

{period_load_code}
cat("\\n✅ All periods loaded successfully\\n\\n")
cat("📋 Rollcall list contains ", length(rc_list), " periods\\n\\n")

# Set polarity anchors based on Chilean political spectrum
cat("🎯 Setting polarity anchors...\\n")

# Find legislators present in ALL periods for consistent polarity
all_period_legislators <- list()
for (i in 1:5) {{
  all_period_legislators[[i]] <- rownames(rc_list[[i]]$votes)
}}

common_legislators <- Reduce(intersect, all_period_legislators)
cat("   Legislators present in ALL 5 periods: ", length(common_legislators), "\\n")

# For Chilean politics:
# Left-wing parties (should be negative): PC, PS
# Right-wing parties (should be positive): UDI, RN

right_parties <- c("UDI", "RN")
left_parties <- c("PC", "PS")

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
  # Fallback
  polarity_anchor <- common_legislators[1]
  cat("   Using fallback polarity anchor: ", polarity_anchor, "\\n\\n")
}}

cat("🚀 Running DW-NOMINATE...\\n")
cat("   This may take several minutes depending on data size.\\n\\n")

# Run DW-NOMINATE with id parameter
dw_result <- dwnominate(
  rc_list,
  id = "legislator_id",  # CRÍTICO: identificador único de legisladores
  dims = 2,              # 2 dimensions
  model = 1,             # Linear change over time
  polarity = polarity_anchor,
  minvotes = 10,         # Minimum votes for a legislator to be included
  lop = 0.025,           # Lopsided vote threshold (exclude near-unanimous)
  niter = 4,             # 4 iterations (usually sufficient)
  beta = 5.9539,         # Spatial error parameter (default)
  w = 0.3463,            # Second dimension weight (default)
  verbose = TRUE
)

cat("\\n✅ DW-NOMINATE estimation complete!\\n\\n")

# Print summary
cat("\\n=== DW-NOMINATE RESULTS SUMMARY ===\\n")
print(summary(dw_result))

# Extract legislator coordinates
legislators <- dw_result$legislators

# Rename columns to match our expected names
legislators <- legislators %>%
  rename(
    legislator = ID,
    period = session
  ) %>%
  mutate(
    legislator = as.integer(legislator)
  )

# Add metadata
legislators <- legislators %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = c("legislator" = "legislator_id")
  )

# Save full results
cat("\\n💾 Saving coordinates for all periods combined...\\n")
write.csv(legislators, "dwnominate_coordinates_all_periods.csv", row.names = FALSE)
cat("   ✅ dwnominate_coordinates_all_periods.csv (", nrow(legislators), " rows)\\n")

# Save period-specific files
cat("\\n💾 Saving coordinates for each period...\\n")
for (i in 1:5) {{
  period_coords <- legislators %>%
    filter(period == i) %>%
    select(legislator, period, coord1D, coord2D, se1D, se2D, nombres, partido, region, distrito)
  
  output_file <- paste0("dwnominate_coordinates_p", i, ".csv")
  write.csv(period_coords, output_file, row.names = FALSE)
  cat("   ✅ ", output_file, " (", nrow(period_coords), " legislators)\\n")
}}

# Also save bill/vote parameters
cat("\\n💾 Saving bill parameters...\\n")
write.csv(dw_result$rollcalls, "dwnominate_bill_parameters.csv")
cat("   ✅ dwnominate_bill_parameters.csv\\n")

# Create a combined file with all periods
cat("\\n💾 Creating combined coordinates file...\\n")
all_coords <- data.frame()

for (i in 1:length(rc_list)) {{
  period_name <- paste0("P", i)
  coords <- dw_result$legislators[, c(paste0("coord1D.", i), paste0("coord2D.", i))]
  colnames(coords) <- c("coord1D", "coord2D")
  coords$legislator_id <- rownames(coords)
  coords$period <- period_name
  coords$nombres <- legislator_meta$nombres[match(coords$legislator_id, legislator_meta$legislator_id)]
  coords$partido <- legislator_meta$partido[match(coords$legislator_id, legislator_meta$legislator_id)]
  
  all_coords <- rbind(all_coords, coords)
}}

write.csv(all_coords, "dwnominate_coordinates_all_periods.csv", row.names = FALSE)
cat("   ✅ dwnominate_coordinates_all_periods.csv (", nrow(all_coords), " rows)\\n")

# Plot results
cat("\\n📊 Creating visualization...\\n")

png("dwnominate_map.png", width = 1200, height = 800, res = 150)
plot(dw_result, main = "Chilean Congressional DW-NOMINATE Map\\n55th Legislative Period (2018-2022)")
dev.off()

cat("   ✅ dwnominate_map.png\\n")

# Summary statistics
cat("\\n=== ANALYSIS SUMMARY ===\\n")
cat("Total legislators: ", nrow(dw_result$legislators), "\\n")
cat("Total periods: ", length(rc_list), "\\n")
cat("Model type: Linear (model=1)\\n")
cat("Dimensions: 2\\n")
cat("Iterations: 4\\n")

cat("\\n✅ DW-NOMINATE analysis complete!\\n\\n")
cat("📂 Output files:\\n")
cat("   • dwnominate_coordinates_p1.csv through p5.csv (period-specific)\\n")
cat("   • dwnominate_coordinates_all_periods.csv (combined)\\n")
cat("   • dwnominate_bill_parameters.csv\\n")
cat("   • dwnominate_map.png\\n\\n")

cat("💡 Next steps:\\n")
cat("   1. Review the coordinate files\\n")
cat("   2. Use csv_dwnominate_graph.py to create custom visualizations\\n")
cat("   3. Compare results across periods to see ideology evolution\\n\\n")
'''

    script_path = f"{output_dir}/r_dwnominate_script.R"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(r_script)

    print(f"   ✅ {script_path}")


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
        default='data/dwnominate',
        help='Output directory for DW-NOMINATE files (default: data/dwnominate)'
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
