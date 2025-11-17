# Correct the polarity of DW-NOMINATE coordinates - 6 Períodos
# Este script invierte la primera dimensión para que coincida con el espectro político chileno
# Maneja 6 períodos semestrales (P1-P6)

library(dplyr)

cat("\n")
cat("===============================================\n")
cat("  DW-NOMINATE Polarity Correction             \n")
cat("  Chilean Congress - 6 Períodos Semestrales   \n")
cat("===============================================\n")
cat("\n")

cat("🔄 Corrigiendo polaridad de coordenadas DW-NOMINATE...\n\n")

# Definir rutas
input_dir <- "../../data/dwnominate_6periods/output"
output_dir <- "../../data/dwnominate_6periods/output"

# Crear directorios de salida si no existen
if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
}

# Función para corregir archivo de un período individual
correct_period_file <- function(period_id) {
  input_file <- file.path(input_dir, paste0("coordinates_P", period_id, "_6periods.csv"))
  output_file <- file.path(output_dir, paste0("coordinates_P", period_id, "_6periods_corrected.csv"))

  if (!file.exists(input_file)) {
    cat(sprintf("⚠️  Archivo de período P%s no encontrado: %s\n", period_id, input_file))
    return(NULL)
  }    # Cargar coordenadas originales
    coords_original <- read.csv(input_file)

    cat(sprintf("📂 Período %s: Cargados %d legisladores\n", period_id, nrow(coords_original)))

    # Mostrar distribución actual por partido en primera dimensión
    if ("partido" %in% colnames(coords_original)) {
        # Mostrar ejemplos específicos
        ps_mean <- mean(coords_original$coord1D[coords_original$partido == "PS"], na.rm = TRUE)
        pc_mean <- mean(coords_original$coord1D[coords_original$partido == "PC"], na.rm = TRUE)
        udi_mean <- mean(coords_original$coord1D[coords_original$partido == "UDI"], na.rm = TRUE)
        rn_mean <- mean(coords_original$coord1D[coords_original$partido == "RN"], na.rm = TRUE)

        cat(sprintf(
            "   Actual: PS = %.3f, PC = %.3f, UDI = %.3f, RN = %.3f\n",
            ps_mean, pc_mean, udi_mean, rn_mean
        ))
    }

    # Aplicar corrección: invertir primera dimensión
    coords_corrected <- coords_original
    coords_corrected$coord1D <- -coords_corrected$coord1D

    # Mostrar distribución corregida
    if ("partido" %in% colnames(coords_corrected)) {
        ps_mean_corrected <- mean(coords_corrected$coord1D[coords_corrected$partido == "PS"], na.rm = TRUE)
        pc_mean_corrected <- mean(coords_corrected$coord1D[coords_corrected$partido == "PC"], na.rm = TRUE)
        udi_mean_corrected <- mean(coords_corrected$coord1D[coords_corrected$partido == "UDI"], na.rm = TRUE)
        rn_mean_corrected <- mean(coords_corrected$coord1D[coords_corrected$partido == "RN"], na.rm = TRUE)

        cat(sprintf(
            "   Corregido: PS = %.3f ✓, PC = %.3f ✓, UDI = %.3f ✓, RN = %.3f ✓\n",
            ps_mean_corrected, pc_mean_corrected, udi_mean_corrected, rn_mean_corrected
        ))
    }

    # Guardar coordenadas corregidas
    write.csv(coords_corrected, output_file, row.names = FALSE)
    cat(sprintf("   ✅ Guardado: %s\n\n", basename(output_file)))

    return(coords_corrected)
}

# Procesar los 6 períodos
cat("📅 Procesando archivos de períodos individuales...\n\n")
all_corrected <- list()
period_ids <- c(1, 2, 3, 4, 5, 6)

for (period_id in period_ids) {
  corrected <- correct_period_file(period_id)
  if (!is.null(corrected)) {
    all_corrected[[period_id]] <- corrected
  }
}

# Ahora corregir el archivo combinado
cat("\n📊 Procesando archivo combinado (coordenadas todos los períodos)...\n")
combined_file <- file.path(input_dir, "dwnominate_coordinates_all_periods_6p.csv")

if (file.exists(combined_file)) {
  coords_all_original <- read.csv(combined_file)

  cat(sprintf("   Cargados %d legisladores (coordenadas finales)\n", nrow(coords_all_original)))

  # Mostrar estadísticas originales
  if ("partido" %in% colnames(coords_all_original)) {
    ps_mean <- mean(coords_all_original$coord1D[coords_all_original$partido == "PS"], na.rm = TRUE)
    pc_mean <- mean(coords_all_original$coord1D[coords_all_original$partido == "PC"], na.rm = TRUE)
    udi_mean <- mean(coords_all_original$coord1D[coords_all_original$partido == "UDI"], na.rm = TRUE)
    rn_mean <- mean(coords_all_original$coord1D[coords_all_original$partido == "RN"], na.rm = TRUE)

    cat(sprintf(
      "   Actual: PS = %.3f, PC = %.3f, UDI = %.3f, RN = %.3f\n",
      ps_mean, pc_mean, udi_mean, rn_mean
    ))
  }

  # Aplicar corrección
  coords_all_corrected <- coords_all_original
  coords_all_corrected$coord1D <- -coords_all_corrected$coord1D

  # Mostrar estadísticas corregidas
  if ("partido" %in% colnames(coords_all_corrected)) {
    ps_mean_corrected <- mean(coords_all_corrected$coord1D[coords_all_corrected$partido == "PS"], na.rm = TRUE)
    pc_mean_corrected <- mean(coords_all_corrected$coord1D[coords_all_corrected$partido == "PC"], na.rm = TRUE)
    udi_mean_corrected <- mean(coords_all_corrected$coord1D[coords_all_corrected$partido == "UDI"], na.rm = TRUE)
    rn_mean_corrected <- mean(coords_all_corrected$coord1D[coords_all_corrected$partido == "RN"], na.rm = TRUE)

    cat(sprintf(
      "   Corregido: PS = %.3f ✓, PC = %.3f ✓, UDI = %.3f ✓, RN = %.3f ✓\n",
      ps_mean_corrected, pc_mean_corrected, udi_mean_corrected, rn_mean_corrected
    ))
  }

  # Guardar archivo combinado corregido
  output_combined <- file.path(output_dir, "dwnominate_coordinates_all_periods_6p_corrected.csv")
  write.csv(coords_all_corrected, output_combined, row.names = FALSE)
  cat(sprintf("   ✅ Guardado: %s\n", basename(output_combined)))
} else {
  cat(sprintf("   ⚠️  Archivo combinado no encontrado: %s\n", combined_file))
}

# Resumen final
cat("\n")
cat("===============================================\n")
cat("  CORRECCIÓN DE POLARIDAD COMPLETADA          \n")
cat("===============================================\n")
cat("\n")

cat("📁 Archivos corregidos en:", output_dir, "\n")
cat("   • coordinates_P1_6periods_corrected.csv\n")
cat("   • coordinates_P2_6periods_corrected.csv\n")
cat("   • coordinates_P3_6periods_corrected.csv\n")
cat("   • coordinates_P4_6periods_corrected.csv\n")
cat("   • coordinates_P5_6periods_corrected.csv\n")
cat("   • coordinates_P6_6periods_corrected.csv\n")
cat("   • dwnominate_coordinates_all_periods_6p_corrected.csv (combinado)\n")

cat("\n✅ Polaridad corregida:\n")
cat("   • Izquierda (PS, PC): valores NEGATIVOS\n")
cat("   • Derecha (UDI, RN): valores POSITIVOS\n")

cat("\n🚀 SIGUIENTE PASO:\n")
cat("   Generar visualizaciones con coordenadas corregidas:\n")
cat("   python ../../src/csv_dwnominate_graph_6periods.py --corrected\n")

cat("\n")
cat("===============================================\n\n")
