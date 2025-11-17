#!/usr/bin/env Rscript
################################################################################
# Correct Polarity for DW-NOMINATE Bootstrap Results
#
# Este script invierte coord1D para que:
# - Valores negativos = Izquierda
# - Valores positivos = Derecha
#
# Procesa coordenadas de bootstrap (3 períodos: 2019, 2020, 2021)
#
# Uso:
#   cd scripts/r
#   Rscript correct_polarity_dwnominate_bootstrap.R
################################################################################

suppressPackageStartupMessages({
    library(dplyr)
})

cat("\n")
cat("================================================================================\n")
cat("🔄 Corrección de Polaridad - DW-NOMINATE Bootstrap\n")
cat("================================================================================\n\n")

# Configuración de directorios
base_dir <- "../../"
output_dir <- file.path(base_dir, "data", "dwnominate_bootstrap", "output")

cat("📂 Directorio de trabajo:\n")
cat(sprintf("   • %s\n\n", output_dir))

################################################################################
# 1. PROCESAR ARCHIVO COMBINADO
################################################################################

cat("================================================================================\n")
cat("📊 PASO 1: Procesar Archivo Combinado\n")
cat("================================================================================\n\n")

combined_file <- file.path(output_dir, "dwnominate_coordinates_all_periods_bootstrap.csv")

if (file.exists(combined_file)) {
    cat(sprintf("📖 Leyendo: %s\n", basename(combined_file)))

    coords <- read.csv(combined_file, stringsAsFactors = FALSE)

    cat(sprintf("   • Filas originales: %d\n", nrow(coords)))
    cat(sprintf("   • Columnas: %d\n", ncol(coords)))
    cat("\n")

    # Invertir coord1D
    cat("🔄 Invirtiendo coord1D...\n")
    original_mean <- mean(coords$coord1D, na.rm = TRUE)
    coords$coord1D <- -coords$coord1D
    corrected_mean <- mean(coords$coord1D, na.rm = TRUE)

    cat(sprintf("   • Media original: %.4f\n", original_mean))
    cat(sprintf("   • Media corregida: %.4f\n", corrected_mean))
    cat("\n")

    # Guardar archivo corregido
    corrected_file <- file.path(output_dir, "dwnominate_coordinates_all_periods_bootstrap_corrected.csv")
    write.csv(coords, corrected_file, row.names = FALSE)

    cat(sprintf("✅ Guardado: %s\n", basename(corrected_file)))
    cat("\n")
} else {
    cat(sprintf("⚠️  Archivo no encontrado: %s\n", basename(combined_file)))
    cat("   Saltando procesamiento del archivo combinado.\n\n")
}

################################################################################
# 2. PROCESAR ARCHIVOS POR PERÍODO
################################################################################

cat("================================================================================\n")
cat("📅 PASO 2: Procesar Archivos por Período\n")
cat("================================================================================\n\n")

# Períodos estimados (no incluye bootstrap)
period_ids <- c(1, 2, 3)
period_names <- c("2019", "2020", "2021")

for (i in seq_along(period_ids)) {
    period_id <- period_ids[i]
    period_name <- period_names[i]

    period_file <- file.path(output_dir, sprintf("coordinates_P%d_bootstrap.csv", period_id))

    if (!file.exists(period_file)) {
        cat(sprintf("⚠️  Período %d (%s): archivo no encontrado\n", period_id, period_name))
        next
    }

    cat(sprintf("📖 Procesando Período %d (%s)...\n", period_id, period_name))

    # Leer archivo
    period_coords <- read.csv(period_file, stringsAsFactors = FALSE)

    cat(sprintf("   • Filas: %d\n", nrow(period_coords)))

    # Estadísticas antes de corrección
    original_range <- range(period_coords$coord1D, na.rm = TRUE)
    original_mean <- mean(period_coords$coord1D, na.rm = TRUE)

    # Invertir coord1D
    period_coords$coord1D <- -period_coords$coord1D

    # Estadísticas después de corrección
    corrected_range <- range(period_coords$coord1D, na.rm = TRUE)
    corrected_mean <- mean(period_coords$coord1D, na.rm = TRUE)

    cat(sprintf("   • Rango original: [%.4f, %.4f]\n", original_range[1], original_range[2]))
    cat(sprintf("   • Rango corregido: [%.4f, %.4f]\n", corrected_range[1], corrected_range[2]))
    cat(sprintf(
        "   • Media original: %.4f → Media corregida: %.4f\n",
        original_mean, corrected_mean
    ))

    # Guardar archivo corregido
    corrected_file <- file.path(output_dir, sprintf("coordinates_P%d_bootstrap_corrected.csv", period_id))
    write.csv(period_coords, corrected_file, row.names = FALSE)

    cat(sprintf("   ✅ Guardado: %s\n", basename(corrected_file)))
    cat("\n")
}

################################################################################
# 3. RESUMEN FINAL
################################################################################

cat("================================================================================\n")
cat("📋 RESUMEN FINAL\n")
cat("================================================================================\n\n")

cat("✅ Corrección de polaridad completada\n\n")

cat("📁 Archivos generados (con polaridad corregida):\n")
cat(sprintf("   • %s/\n", output_dir))
cat("     - dwnominate_coordinates_all_periods_bootstrap_corrected.csv\n")
cat("     - coordinates_P1_bootstrap_corrected.csv (2019)\n")
cat("     - coordinates_P2_bootstrap_corrected.csv (2020)\n")
cat("     - coordinates_P3_bootstrap_corrected.csv (2021)\n")
cat("\n")

cat("📊 Interpretación de coord1D (después de corrección):\n")
cat("   • coord1D < 0: Izquierda\n")
cat("   • coord1D > 0: Derecha\n")
cat("   • coord1D ≈ 0: Centro\n")
cat("\n")

cat("================================================================================\n")
cat("🚀 PRÓXIMOS PASOS\n")
cat("================================================================================\n\n")

cat("1. Visualizar período individual con labels:\n")
cat("   python src/csv_dwnominate_graph.py \\\n")
cat("     --period P1 --labels \\\n")
cat("     --csv-file data/dwnominate_bootstrap/output/coordinates_P1_bootstrap_corrected.csv \\\n")
cat("     --output results/dwnominate_p1_bootstrap.png\n")
cat("\n")

cat("2. Gráfico de evolución (3 períodos: 2019-2021):\n")
cat("   python src/csv_dwnominate_graph.py \\\n")
cat("     --evolution \\\n")
cat("     --csv-dir data/dwnominate_bootstrap/output \\\n")
cat("     --output results/dwnominate_evolution_bootstrap.png\n")
cat("\n")

cat("3. Comparar con análisis de 5 o 6 períodos:\n")
cat("   - Bootstrap usa 2018 para anclar + 3 períodos anuales (2019-2021)\n")
cat("   - Análisis de 6 períodos usa semestres (2019-2021)\n")
cat("   - Compara estabilidad y detalle temporal\n")
cat("\n")

cat("================================================================================\n\n")

cat("✅ Script completado exitosamente.\n\n")
