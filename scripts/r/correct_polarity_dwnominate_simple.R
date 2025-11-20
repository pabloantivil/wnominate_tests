# Corrección simple de polaridad para DW-NOMINATE (6 períodos)
# Basado en correct_polarity_wnominate.R - inversión directa sin validación compleja

library(dplyr)

cat("🔄 Corrigiendo polaridad de DW-NOMINATE (6 períodos)...\n\n")

# Procesar cada período
periodos <- c("P1a", "P1b", "P2a", "P2b", "P3a", "P3b", "all_periods")

for (periodo in periodos) {
    cat(sprintf("=== Procesando %s ===\n", periodo))

    # Cargar coordenadas originales
    if (periodo == "all_periods") {
        input_file <- "../../data/dwnominate_6periods/output/dwnominate_coordinates_all_periods.csv"
    } else {
        input_file <- sprintf("../../data/dwnominate_6periods/output/coordinates_%s_6periods.csv", periodo)
    }

    if (!file.exists(input_file)) {
        cat(sprintf("⚠️  Archivo no encontrado: %s\n\n", input_file))
        next
    }

    coords <- read.csv(input_file)
    cat(sprintf("📊 Cargados %d legisladores\n", nrow(coords)))

    # Invertir AMBAS dimensiones (igual que W-NOMINATE)
    coords$coord1D <- -coords$coord1D
    coords$coord2D <- -coords$coord2D

    cat("✅ Dimensiones invertidas:\n")
    cat("   - coord1D: INVERTIDO → Izquierda(-) ← → Derecha(+)\n")
    cat("   - coord2D: INVERTIDO → Conservador(-) ← → Progresista(+)\n")

    # Guardar coordenadas corregidas
    if (periodo == "all_periods") {
        output_file <- "../../data/dwnominate_6periods/output/dwnominate_coordinates_all_periods_corrected.csv"
    } else {
        output_file <- sprintf("../../data/dwnominate_6periods/output/coordinates_%s_6periods_corrected.csv", periodo)
    }
    write.csv(coords, output_file, row.names = FALSE)

    cat(sprintf("💾 Guardado: %s\n\n", output_file))
}

cat("🎯 Corrección completada para todos los períodos!\n")
