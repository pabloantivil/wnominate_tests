
# W-NOMINATE Analysis Script for Chilean Congressional Data
# Generado automáticamente a partir de la exportación de MongoDB

# Instalar los paquetes necesarios si aún no están instalados
if (!require(pscl)) install.packages("pscl")
if (!require(wnominate)) install.packages("wnominate") 
if (!require(dplyr)) install.packages("dplyr")

library(pscl)
library(wnominate)
library(dplyr)

# Cargar los datos
votes_matrix <- read.csv("votes_matrix.csv", row.names = 1)
legislator_meta <- read.csv("legislator_metadata.csv")
vote_meta <- read.csv("vote_metadata.csv")

# Convertir a matriz
votes_mat <- as.matrix(votes_matrix)

# Crear objeto rollcall
rc <- rollcall(
  data = votes_mat,
  yea = 1,           # "Sí" votes
  nay = 0,           # "No" votes  
  missing = NA,      # True missing (shouldn't have any)
  notInLegis = 9,    # Abstentions, absences, etc.
  legis.names = rownames(votes_mat),
  vote.names = colnames(votes_mat),
  desc = "Votaciones en el Congreso de Chile - Conjunto de datos de prueba"
)

# Imprimir resumen del objeto rollcall
cat("\n=== ROLLCALL OBJECT SUMMARY ===\n")
print(summary(rc))

# Encuentra anclas de polaridad (legisladores más extremos)
# Es posible que desees especificarlos manualmente en función de tu conocimiento de la política chilena.
cat("\n=== ENCONTRANDO ANCLAJES DE POLARIDAD ===\n")

# Método 1: Utilice la información del partido si está disponible
if ("partido" %in% colnames(legislator_meta)) {
  cat("Partidos en el conjunto de datos:\n")
  party_counts <- legislator_meta %>% 
    count(partido, sort = TRUE) %>%
    head(10)
  print(party_counts)
  
  # Puede establecer anclas manualmente en función de los partidos de izquierda/derecha conocidos
  # Ejemplo (ajustar según su conocimiento de la política chilena):
  # left_anchor <- legislator_meta$legislator_id[legislator_meta$partido == "PC"][1]  # Partido Comunista
  # right_anchor <- legislator_meta$legislator_id[legislator_meta$partido == "UDI"][1] # Unión Demócrata Independiente
}

# étodo 2: Especificación manual de polaridad (recomendado)
cat("\nEstableciendo anclas de polaridad en función del espectro político chileno...\n")

# Encuentra legisladores extremos por partido
# En la primera dimensión de W-NOMINATE: Negativo = Izquierda, Positivo = Derecha
# Por lo tanto, necesitamos: UDI/RN (derecha) como ancla positiva, PC/PS (izquierda) como ancla negativa
right_parties <- c("UDI", "RN") # Unión Demócrata Independiente, Renovación Nacional (derecha, debería ser positivo)
left_parties <- c("PC", "PS")  # Partido Comunista, Partido Socialista (izquierda, debería ser negativo)

# Conseguir legisladores de partidos extremistas
left_legislators <- legislator_meta$legislator_id[legislator_meta$partido %in% left_parties]
right_legislators <- legislator_meta$legislator_id[legislator_meta$partido %in% right_parties]

# Debug: Comprobar qué ID de legislador hay realmente en el objeto de lista 
cat("Nombres de filas en el objeto rollcall (primeros 10):\n")
print(head(rownames(rc$votes), 10))
cat("IDs de legisladores disponibles en los metadatos (primeros 10):\n")
print(head(legislator_meta$legislator_id, 10))

# Establezca anclajes de polaridad utilizando índices de fila (no IDs)
if (length(left_legislators) > 0 && length(right_legislators) > 0) {
  # Encontrar índices de fila para los legisladores de polaridad
  # El primer ancla debe ser negativa (izquierda), la segunda debe ser positiva (derecha)
  left_idx <- which(rownames(rc$votes) == left_legislators[1])
  right_idx <- which(rownames(rc$votes) == right_legislators[1])
  
  if (length(left_idx) > 0 && length(right_idx) > 0) {
    # Vector de polaridad W-NOMINATE: [anclaje negativo, anclaje positivo]
    polarity_vec <- c(left_idx, right_idx)  # left = negative, right = positive
    cat(sprintf("Uso de anclas de polaridad: fila %d (ID %s, %s, negativo) y fila %d (ID %s, %s, positivo)\n", 
                left_idx, left_legislators[1], legislator_meta$partido[legislator_meta$legislator_id == left_legislators[1]][1],
                right_idx, right_legislators[1], legislator_meta$partido[legislator_meta$legislator_id == right_legislators[1]][1]))
  } else {
    # Respaldo: usar la primera y la última fila
    polarity_vec <- c(1, nrow(rc$votes))
    cat(sprintf("Fallback polarity anchors: row 1 and row %d\n", nrow(rc$votes)))
  }
} else {
  # Respaldo: usar la primera y la última fila
  polarity_vec <- c(1, nrow(rc$votes))
  cat(sprintf("Fallback polarity anchors: row 1 and row %d\n", nrow(rc$votes)))
}

cat("\nEjecución de W-NOMINATE con especificación de polaridad manual...\n")

# Run W-NOMINATE
wnom_result <- wnominate(
  rc,
  dims = 2,           # 2 dimensiones
  polarity = polarity_vec, # Anclas de polaridad manuales (índices de fila)
  minvotes = 20,      # Votos mínimos por legislador (ya filtrados)
  lop = 0.025,        # Umbral de votos desproporcionados
  trials = 3,         # Número de ensayos (aumentar para más precisión)
  verbose = TRUE      # Mostrar progreso
)

# Imprimir resumen de resultados
cat("\n=== W-NOMINATE RESULTADOS ===\n")
print(summary(wnom_result))

# Extract coordinates
coordinates <- wnom_result$legislators[, c("coord1D", "coord2D")]
coordinates$legislator_id <- rownames(coordinates)
coordinates$legislator_name <- legislator_meta$nombre[match(coordinates$legislator_id, legislator_meta$legislator_id)]
coordinates$party <- legislator_meta$partido[match(coordinates$legislator_id, legislator_meta$legislator_id)]

# Save results
write.csv(coordinates, "wnominate_coordinates.csv", row.names = FALSE)
write.csv(wnom_result$rollcalls, "wnominate_bill_parameters.csv")

cat("\n=== RESULTADOS GUARDADOS ===\n")
cat("Coordenadas guardadas en: wnominate_coordinates.csv\n")
cat("Bill parameters guardados en: wnominate_bill_parameters.csv\n")

# Gráfico básico
plot(wnom_result, main = "Mapa W-NOMINATE del Congreso de Chile")

# Gráfico mejorado con colores del grupo (si hay datos del grupo disponibles)
if ("partido" %in% colnames(legislator_meta)) {
  library(ggplot2)
  
  p <- ggplot(coordinates, aes(x = coord1D, y = coord2D, color = party, label = legislator_name)) +
    geom_point(alpha = 0.7, size = 2) +
    geom_text(size = 2, alpha = 0.7, check_overlap = TRUE) +
    labs(
      title = "Puntos Ideales del Congreso Chileno W-NOMINATE",
      x = "Primera Dimensión (Económica: Izquierda ← → Derecha)",
      y = "Segunda Dimensión (Social: Liberal-Conservador)", 
      color = "Partido"
    ) +
    geom_hline(yintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.7) +
    geom_vline(xintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.7) +
    theme_minimal() +
    theme(legend.position = "bottom") +
    # Añadir anotaciones para aclarar el espacio político
    annotate("text", x = -0.8, y = -0.8, label = "Izquierda\n(PC, PS)", size = 3, color = "gray30") +
    annotate("text", x = 0.8, y = -0.8, label = "Derecha\n(UDI, RN)", size = 3, color = "gray30")

  ggsave("wnominate_map_with_parties.png", p, width = 12, height = 8, dpi = 300)
  cat("Gráfico mejorado guardado en: wnominate_map_with_parties.png\n")
}

cat("\n=== ANÁLISIS COMPLETO ===\n")
cat("¡Compara estas coordenadas con tus resultados de pynominate!\n")
