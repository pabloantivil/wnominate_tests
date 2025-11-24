# Corrección de polaridad para DW-NOMINATE (5 períodos)

library(dplyr)

cat("Corrigiendo polaridad de DW-NOMINATE (5 períodos)...\n\n")

# Procesar cada período
periodos <- c("p1", "p2", "p3", "p4", "p5", "all_periods")

for (periodo in periodos) {
  cat(sprintf("=== Procesando %s ===\n", toupper(periodo)))

  # Cargar coordenadas originales
  if (periodo == "all_periods") {
    input_file <- "../../data/dwnominate/output/dwnominate_coordinates_all_periods.csv"
  } else {
    input_file <- sprintf("../../data/dwnominate/output/dwnominate_coordinates_%s.csv", periodo)
  }

  if (!file.exists(input_file)) {
    cat(sprintf("Archivo no encontrado: %s\n\n", input_file))
    next
  }

  coords <- read.csv(input_file)
  cat(sprintf("Cargados %d legisladores\n", nrow(coords)))

  # Invertir AMBAS dimensiones (igual que W-NOMINATE)
  coords$coord1D <- -coords$coord1D
  coords$coord2D <- -coords$coord2D

  cat("Dimensiones invertidas:\n")
  cat("   - coord1D: INVERTIDO → Izquierda(-) ← → Derecha(+)\n")
  cat("   - coord2D: INVERTIDO → Conservador(-) ← → Progresista(+)\n")

  # Guardar coordenadas corregidas
  if (periodo == "all_periods") {
    output_file <- "../../data/dwnominate/output/dwnominate_coordinates_all_periods_corrected.csv"
  } else {
    output_file <- sprintf("../../data/dwnominate/output/dwnominate_coordinates_%s_corrected.csv", periodo)
  }
  write.csv(coords, output_file, row.names = FALSE)

  cat(sprintf("Guardado: %s\n\n", output_file))
}

cat("Corrección completada para todos los períodos!\n")
