# Análisis W-NOMINATE con anclajes de polaridad adecuados
# Usando Amaro Labra (PC, extrema izquierda) y Enrique Van Rysselberghe (UDI, extrema derecha)

library(wnominate)

# Cargar los datos desde data/input
votes_matrix <- as.matrix(read.csv("../../data/input/votes_matrix.csv", row.names = 1))
legislator_metadata <- read.csv("../../data/input/legislator_metadata.csv")
vote_metadata <- read.csv("../../data/input/vote_metadata.csv")

# Relacionar los metadatos de la legisladora con la matriz de votos
vote_matrix_ids <- as.numeric(rownames(votes_matrix))
matched_metadata <- legislator_metadata[legislator_metadata$legislator_id %in% vote_matrix_ids, ]

# Reordenar los metadatos para que coincidan con el orden de la matriz de votos
matched_metadata <- matched_metadata[match(vote_matrix_ids, matched_metadata$legislator_id), ]

# Crear un objeto rollcall: permitirle utilizar códigos predeterminados
rc <- rollcall(votes_matrix)

cat("Resumen del conjunto de datos:\n")
cat("Legisladores:", nrow(votes_matrix), "\n")
cat("Votos:", ncol(votes_matrix), "\n")

# Definir anclajes de polaridad utilizando posiciones de fila
# Amaro Labra (1043, PC, extrema izquierda) debería ser negativo (izquierda) - posición 42
# Enrique Van Rysselberghe (959, UDI, extrema derecha) debería ser positivo (derecha) - posición 140
amaro_pos <- which(rownames(votes_matrix) == "1043")
enrique_pos <- which(rownames(votes_matrix) == "959")
polarity_anchors <- c(amaro_pos, enrique_pos) # posiciones para Amaro Labra y Van Rysselberghe

cat("\nUsando anclajes de polaridad:\n")
cat("Ancla izquierda (negativa): Posición", amaro_pos, "- Legislador 1043 (Amaro Labra, PC)\n")
cat("Ancla derecha (positiva): Posición", enrique_pos, "- Legislador 959 (Enrique Van Rysselberghe, UDI)\n")

# Ejecute W-NOMINATE con la especificación de polaridad adecuada
result <- wnominate(rc,
    dims = 2,
    trials = 3,
    polarity = polarity_anchors,
    verbose = TRUE
)

# Extraer coordenadas
coordinates <- result$legislators[, c("coord1D", "coord2D")]
# Agregar IDs de legisladores originales como nombres de fila
coordinates <- cbind(legislator_id = rownames(votes_matrix), coordinates)
rownames(coordinates) <- rownames(votes_matrix)

cat("\nResultados de W-NOMINATE con anclajes de polaridad:\n")
cat("Clasificación Correcta: ", result$fits[1], "%\n")
cat("APRE: ", result$fits[2], "\n")
cat("GMP: ", result$fits[3], "\n")

# Verificar que la polaridad es correcta (usar IDs de legisladores originales)
amaro_coords <- coordinates[rownames(coordinates) == "1043", c("coord1D", "coord2D")]
enrique_coords <- coordinates[rownames(coordinates) == "959", c("coord1D", "coord2D")]

# Convertir a vectores numéricos para una impresión adecuada
amaro_coord1D <- as.numeric(amaro_coords[1, "coord1D"])
amaro_coord2D <- as.numeric(amaro_coords[1, "coord2D"])
enrique_coord1D <- as.numeric(enrique_coords[1, "coord1D"])
enrique_coord2D <- as.numeric(enrique_coords[1, "coord2D"])

cat("\nVerificación de Polaridad:\n")
cat("Amaro Labra (PC, debería ser negativo):", amaro_coord1D, amaro_coord2D, "\n")
cat("Enrique Van Rysselberghe (UDI, debería ser positivo):", enrique_coord1D, enrique_coord2D, "\n")

# Guardar resultados con la orientación adecuada
coordinates_with_metadata <- merge(coordinates, legislator_metadata,
    by.x = "row.names", by.y = "legislator_id",
    all.x = TRUE
)
names(coordinates_with_metadata)[1] <- "legislator_id"

# Crear directorio de salida si no existe
output_dir <- "../../data/output"
if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
}

write.csv(coordinates_with_metadata, file.path(output_dir, "wnominate_coordinates_proper_polarity.csv"), row.names = FALSE)

cat("\nCoordenadas guardadas en:", file.path(output_dir, "wnominate_coordinates_proper_polarity.csv"), "\n")

# Guardar parámetros de votación
write.csv(result$rollcalls, file.path(output_dir, "wnominate_bill_parameters_proper_polarity.csv"), row.names = TRUE)

cat("Bill parameters guardados en:", file.path(output_dir, "wnominate_bill_parameters_proper_polarity.csv"), "\n")
