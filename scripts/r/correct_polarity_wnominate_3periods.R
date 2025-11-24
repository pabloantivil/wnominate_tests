# Script para corregir polaridad de W-NOMINATE (3 períodos del 55º PL)
# Aplica inversión simple en ambas dimensiones

library(dplyr)

cat("\n=== CORRECCIÓN DE POLARIDAD W-NOMINATE (3 PERÍODOS) ===\n\n")

# Definir períodos
periodos <- c("p1", "p2", "p3")

# Directorios
input_dir <- "../../data/wnominate_3periods/output"
output_dir <- input_dir # Mismo directorio

# Procesar cada período
for (periodo in periodos) {
    cat("Procesando", toupper(periodo), "...\n")

    # Cargar coordenadas
    archivo_input <- file.path(input_dir, sprintf("wnominate_coordinates_%s.csv", periodo))

    if (!file.exists(archivo_input)) {
        cat("Archivo no encontrado:", archivo_input, "\n\n")
        next
    }

    coords <- read.csv(archivo_input)

    # Mostrar estadísticas antes de corrección
    cat("  Antes de corrección:\n")
    cat(
        "    coord1D - Media:", round(mean(coords$coord1D, na.rm = TRUE), 3),
        " | Rango: [", round(min(coords$coord1D, na.rm = TRUE), 3), ",",
        round(max(coords$coord1D, na.rm = TRUE), 3), "]\n"
    )
    cat(
        "    coord2D - Media:", round(mean(coords$coord2D, na.rm = TRUE), 3),
        " | Rango: [", round(min(coords$coord2D, na.rm = TRUE), 3), ",",
        round(max(coords$coord2D, na.rm = TRUE), 3), "]\n"
    )

    # Aplicar inversión simple (igual que W-NOMINATE original)
    coords$coord1D <- -coords$coord1D
    coords$coord2D <- -coords$coord2D

    # Mostrar estadísticas después de corrección
    cat("  Después de corrección:\n")
    cat(
        "    coord1D - Media:", round(mean(coords$coord1D, na.rm = TRUE), 3),
        " | Rango: [", round(min(coords$coord1D, na.rm = TRUE), 3), ",",
        round(max(coords$coord1D, na.rm = TRUE), 3), "]\n"
    )
    cat(
        "    coord2D - Media:", round(mean(coords$coord2D, na.rm = TRUE), 3),
        " | Rango: [", round(min(coords$coord2D, na.rm = TRUE), 3), ",",
        round(max(coords$coord2D, na.rm = TRUE), 3), "]\n"
    )

    # Guardar coordenadas corregidas
    archivo_output <- file.path(output_dir, sprintf("wnominate_coordinates_%s_corrected.csv", periodo))
    write.csv(coords, archivo_output, row.names = FALSE)

    cat("Guardado:", archivo_output, "\n\n")
}

cat("=== CORRECCIÓN COMPLETADA ===\n\n")
cat("Archivos generados:\n")
cat("  - wnominate_coordinates_p1_corrected.csv\n")
cat("  - wnominate_coordinates_p2_corrected.csv\n")
cat("  - wnominate_coordinates_p3_corrected.csv\n\n")

cat("Siguiente paso: Ejecutar grafico_trayectorias_wnominate_3periods.py\n")
