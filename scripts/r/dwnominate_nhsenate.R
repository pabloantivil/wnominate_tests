# ============================================================================
# Script R: Ejecutar DW-NOMINATE y exportar coordenadas para Python
# ============================================================================

library(dwnominate)

# Cargar dataset
data(nhsenate)

cat("Ejecutando DW-NOMINATE con modelo cúbico (model = 3)...\n\n")

# Ejecutar DW-NOMINATE con modelo cúbico
results <- dwnominate(
  rc_list = nhsenate,
  model = 3  # Modelo cúbico
)

cat("\n============================================================================\n")
cat("EXPORTANDO COORDENADAS A CSV\n")
cat("============================================================================\n\n")

# Extraer dataframe de legisladores con todas las coordenadas
legislators_df <- results$legislators

# Verificar estructura
cat("Columnas disponibles en legislators:\n")
print(names(legislators_df))
cat("\n")

cat("Primeras filas:\n")
print(head(legislators_df))
cat("\n")

# Crear directorio de salida si no existe
if (!dir.exists("output_nhsenate")) {
  dir.create("output_nhsenate")
}

# Exportar coordenadas completas
write.csv(legislators_df, 
          "output_nhsenate/nhsenate_coordinates_model3.csv", 
          row.names = FALSE)

cat("✓ Coordenadas exportadas a: output_nhsenate/nhsenate_coordinates_model3.csv\n")

# También exportar información de votaciones
rollcalls_df <- results$rollcalls
write.csv(rollcalls_df,
          "output_nhsenate/nhsenate_rollcalls_model3.csv",
          row.names = FALSE)

cat("✓ Votaciones exportadas a: output_nhsenate/nhsenate_rollcalls_model3.csv\n")

# Resumen de datos exportados
cat("\n============================================================================\n")
cat("RESUMEN DE DATOS EXPORTADOS\n")
cat("============================================================================\n")
cat("Total legisladores:", nrow(legislators_df), "\n")
cat("Total votaciones:", nrow(rollcalls_df), "\n")
cat("Dimensiones estimadas:", results$dimensions, "\n")
cat("Número de sesiones:", length(unique(legislators_df$congress)), "\n")
cat("\nPartidos únicos:\n")
print(table(legislators_df$party))

cat("\n✓ Script completado. Archivos listos para análisis en Python.\n")