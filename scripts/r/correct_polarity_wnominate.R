# Corregir la polaridad de las coordenadas W-NOMINATE
# Este script invierte la primera dimensión para que coincida con las convenciones del espectro político chileno

library(dplyr)

cat("Corrigiendo la polaridad de las coordenadas W-NOMINATE...\n")

# Cargar las coordenadas originales desde data/wnominate/output
coords_original <- read.csv("../../data/wnominate/output/wnominate_coordinates.csv")

cat(sprintf("Cargados %d legisladores\n", nrow(coords_original)))

# Mostrar la distribución actual por partido en la primera dimensión
cat("\n=== DISTRIBUCIÓN ACTUAL (ANTES DE LA CORRECCIÓN) ===\n")
if ("party" %in% colnames(coords_original)) {
  party_stats <- coords_original %>%
    group_by(party) %>%
    summarise(
      count = n(),
      mean_coord1D = round(mean(coord1D, na.rm = TRUE), 3),
      .groups = "drop"
    ) %>%
    arrange(mean_coord1D)

  print(party_stats)

  # Mostrar ejemplos específicos
  cat("\nPosiciones actuales (deberían ser invertidas):\n")
  cat("- PS (izquierda): media =", round(mean(coords_original$coord1D[coords_original$party == "PS"], na.rm = TRUE), 3), "(debería ser negativa)\n")
  cat("- UDI (derecha): media =", round(mean(coords_original$coord1D[coords_original$party == "UDI"], na.rm = TRUE), 3), "(debería ser positiva)\n")
}

# Aplicar la corrección: invertir ambas dimensiones
coords_corrected <- coords_original
coords_corrected$coord1D <- -coords_corrected$coord1D
coords_corrected$coord2D <- -coords_corrected$coord2D # También invertir la segunda dimensión

cat("\nCorrecciones aplicadas:\n")
cat("   - Primera dimensión (Económica): invertida para coincidir con Izquierda(-) ← → Derecha(+)\n")
cat("   - Segunda dimensión (Social): invertida para coincidir con Liberal(-) ← → Conservador(+)\n")

cat("\n=== DESPUÉS DE LA CORRECCIÓN ===\n")
if ("party" %in% colnames(coords_corrected)) {
  party_stats_corrected <- coords_corrected %>%
    group_by(party) %>%
    summarise(
      count = n(),
      mean_coord1D = round(mean(coord1D, na.rm = TRUE), 3),
      .groups = "drop"
    ) %>%
    arrange(mean_coord1D)

  print(party_stats_corrected)

  # Mostrar ejemplos corregidos
  cat("\nPosiciones corregidas:\n")
  cat("- PS (izquierda): media =", round(mean(coords_corrected$coord1D[coords_corrected$party == "PS"], na.rm = TRUE), 3), "(ahora negativa ✓)\n")
  cat("- UDI (derecha): media =", round(mean(coords_corrected$coord1D[coords_corrected$party == "UDI"], na.rm = TRUE), 3), "(ahora positiva ✓)\n")
}

# Crear directorio de salida si no existe
output_dir <- "../../data/wnominate/output"
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# Guardar las coordenadas corregidas
write.csv(coords_corrected, file.path(output_dir, "wnominate_coordinates_corrected.csv"), row.names = FALSE)

cat("\nCoordenadas corregidas guardadas en:", file.path(output_dir, "wnominate_coordinates_corrected.csv"), "\n")

# Crear un gráfico de comparación
if ("party" %in% colnames(coords_corrected)) {
  library(ggplot2)

  # Crear directorio de resultados si no existe
  images_dir <- "../../results"
  if (!dir.exists(images_dir)) {
    dir.create(images_dir, recursive = TRUE)
  }

  # Crear grafico corregido
  p_corrected <- ggplot(coords_corrected, aes(x = coord1D, y = coord2D, color = party)) +
    geom_point(alpha = 0.7, size = 2) +
    labs(
      title = "Puntos Ideales del Congreso Chileno W-NOMINATE (Polaridad Corregida)",
      x = "Primera Dimensión (Económica: Izquierda ← → Derecha)",
      y = "Segunda Dimensión (Social: Liberal ← → Conservador)",
      color = "Partido"
    ) +
    geom_hline(yintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.7) +
    geom_vline(xintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.7) +
    theme_minimal() +
    theme(legend.position = "bottom") +
    # Añadir anotaciones para aclarar el espacio político
    annotate("text", x = -0.8, y = -0.8, label = "Izquierda\nLiberal\n(PC, PS)", size = 3, color = "gray30") +
    annotate("text", x = 0.8, y = 0.8, label = "Derecha\nConservador\n(UDI, RN)", size = 3, color = "gray30")

  ggsave(file.path(images_dir, "wnominate_map_corrected_polarity.png"), p_corrected, width = 12, height = 8, dpi = 300)
  cat("📈 Gráfico corregido guardado en:", file.path(images_dir, "wnominate_map_corrected_polarity.png"), "\n")

  # También crear una comparación lado a lado
  coords_original$version <- "Original"
  coords_corrected$version <- "Corregido"
  coords_combined <- rbind(coords_original, coords_corrected)

  p_comparison <- ggplot(coords_combined, aes(x = coord1D, y = coord2D, color = party)) +
    geom_point(alpha = 0.6, size = 1.5) +
    facet_wrap(~version, ncol = 2) +
    labs(
      title = "W-NOMINATE Coordenadas: Antes vs Después de la Corrección de Polaridad",
      x = "Primera dimensión (económica)",
      y = "Segunda dimensión (social)",
      color = "Partido"
    ) +
    geom_hline(yintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.5) +
    geom_vline(xintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.5) +
    theme_minimal() +
    theme(legend.position = "bottom")

  ggsave(file.path(images_dir, "wnominate_polarity_comparison.png"), p_comparison, width = 14, height = 7, dpi = 300)
  cat("Gráfico de comparación guardado en:", file.path(images_dir, "wnominate_polarity_comparison.png"), "\n")
}

cat("\nCorrección de polaridad completada!\n")
cat("   - Los partidos de izquierda (PC, PS) ahora están en el lado negativo (izquierda)\n")
cat("   - Los partidos de derecha (UDI, RN) ahora están en el lado positivo (derecha)\n")
cat("   - Esto coincide con la convención estándar del espectro político\n")
