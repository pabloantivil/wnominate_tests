# Script para ejecutar W-NOMINATE en los 3 períodos del 55º PL
# P1: 11/03/2018 - 18/10/2019 (Inicio PL hasta Estallido Social)
# P2: 18/10/2019 - 25/10/2020 (Estallido Social hasta Plebiscito 2020)
# P3: 25/10/2020 - 10/03/2022 (Plebiscito 2020 hasta Fin PL)

# Instalar paquetes necesarios si no están instalados
if (!require(pscl)) install.packages("pscl")
if (!require(wnominate)) install.packages("wnominate")
if (!require(dplyr)) install.packages("dplyr")

library(pscl)
library(wnominate)
library(dplyr)

cat("\n=== W-NOMINATE POR PERÍODOS (3 períodos del 55º PL) ===\n")

# Definir períodos
periodos <- c("p1", "p2", "p3")
nombres_periodos <- c(
    "P1: 11/03/2018 - 18/10/2019 (Inicio PL → Estallido Social)",
    "P2: 18/10/2019 - 25/10/2020 (Estallido Social → Plebiscito 2020)",
    "P3: 25/10/2020 - 10/03/2022 (Plebiscito 2020 → Fin PL)"
)

# Crear directorio de salida
output_dir <- "../../data/wnominate_3periods/output"
if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
}

# Cargar metadata de legisladores
legislator_meta <- read.csv("../../data/wnominate_3periods/input/legislator_metadata.csv")

cat("Metadata cargada:", nrow(legislator_meta), "legisladores en total\n")
cat("Partidos disponibles:", paste(unique(legislator_meta$partido), collapse = ", "), "\n\n")

# Definir partidos para anclas de polaridad
right_parties <- c("UDI", "RN") # Derecha (debería ser positivo)
left_parties <- c("PC", "PS") # Izquierda (debería ser negativo)

# Ejecutar W-NOMINATE para cada período
for (i in 1:length(periodos)) {
    periodo <- periodos[i]
    cat("\n", paste(rep("=", 70), collapse = ""), "\n")
    cat("PROCESANDO", nombres_periodos[i], "\n")
    cat(paste(rep("=", 70), collapse = ""), "\n\n")

    # Cargar matriz de votaciones del período
    votes_file <- sprintf("../../data/wnominate_3periods/input/votes_matrix_%s.csv", periodo)

    if (!file.exists(votes_file)) {
        cat("Archivo no encontrado:", votes_file, "\n")
        next
    }

    # Cargar con row.names = 1 (igual que el script funcional)
    votes_matrix <- read.csv(votes_file, row.names = 1)

    cat("Matriz de votaciones cargada:", nrow(votes_matrix), "legisladores\n")
    cat("   Votaciones:", ncol(votes_matrix), "\n")

    # Convertir a matriz (igual que el script funcional)
    votes_mat <- as.matrix(votes_matrix)

    # Crear objeto rollcall con los MISMOS parámetros que el script funcional
    rc <- rollcall(
        data = votes_mat,
        yea = 1, # "Sí" votes
        nay = 0, # "No" votes
        missing = NA, # True missing (shouldn't have any)
        notInLegis = 9, # Abstentions, absences, etc.
        legis.names = rownames(votes_mat),
        vote.names = colnames(votes_mat),
        desc = nombres_periodos[i]
    )

    cat("\n=== ROLLCALL OBJECT SUMMARY ===\n")
    print(summary(rc))

    # Calcular anclas de polaridad (igual que el script funcional)
    cat("\n=== ESTABLECIENDO ANCLAS DE POLARIDAD ===\n")

    # Obtener legisladores de partidos extremos
    left_legislators <- legislator_meta$legislator_id[legislator_meta$partido %in% left_parties]
    right_legislators <- legislator_meta$legislator_id[legislator_meta$partido %in% right_parties]

    # Encontrar índices de fila para las anclas de polaridad
    if (length(left_legislators) > 0 && length(right_legislators) > 0) {
        # Buscar legisladores de izquierda y derecha que estén en este período
        left_idx <- NULL
        right_idx <- NULL

        for (leg_id in left_legislators) {
            idx <- which(rownames(rc$votes) == as.character(leg_id))
            if (length(idx) > 0) {
                left_idx <- idx
                break
            }
        }

        for (leg_id in right_legislators) {
            idx <- which(rownames(rc$votes) == as.character(leg_id))
            if (length(idx) > 0) {
                right_idx <- idx
                break
            }
        }

        if (!is.null(left_idx) && !is.null(right_idx)) {
            polarity_vec <- c(left_idx, right_idx)
            cat(sprintf(
                "Anclas de polaridad: fila %d (ID %s, izquierda) y fila %d (ID %s, derecha)\n",
                left_idx, rownames(rc$votes)[left_idx],
                right_idx, rownames(rc$votes)[right_idx]
            ))
        } else {
            # Respaldo: usar la primera y la última fila
            polarity_vec <- c(1, nrow(rc$votes))
            cat(sprintf("Usando anclas de respaldo: fila 1 y fila %d\n", nrow(rc$votes)))
        }
    } else {
        # Respaldo: usar la primera y la última fila
        polarity_vec <- c(1, nrow(rc$votes))
        cat(sprintf("Usando anclas de respaldo: fila 1 y fila %d\n", nrow(rc$votes)))
    }

    cat("\nEjecutando W-NOMINATE para", toupper(periodo), "...\n")

    # Ejecutar W-NOMINATE con los MISMOS parámetros que el script funcional
    result <- tryCatch(
        {
            wnominate(
                rcObject = rc,
                dims = 2,
                polarity = polarity_vec, # Anclas calculadas, no fijas
                minvotes = 20, # Igual que el script funcional
                lop = 0.025,
                trials = 3,
                verbose = TRUE # Activado para ver progreso
            )
        },
        error = function(e) {
            cat("Error ejecutando W-NOMINATE:", e$message, "\n")
            return(NULL)
        }
    )

    if (is.null(result)) {
        cat("Saltando período", toupper(periodo), "debido a error\n")
        next
    }

    cat("\n=== W-NOMINATE RESULTADOS ===\n")
    print(summary(result))

    # Extraer coordenadas (igual que el script funcional)
    coordinates <- result$legislators[, c("coord1D", "coord2D")]
    coordinates$legislator_id <- rownames(coordinates)
    coordinates$legislator_name <- legislator_meta$nombre[match(coordinates$legislator_id, legislator_meta$legislator_id)]
    coordinates$party <- legislator_meta$partido[match(coordinates$legislator_id, legislator_meta$legislator_id)]

    # Guardar resultados
    output_file <- sprintf("%s/wnominate_coordinates_%s.csv", output_dir, periodo)
    write.csv(coordinates, output_file, row.names = FALSE)

    cat("\nCoordenadas guardadas:", output_file, "\n")
    cat("   Legisladores procesados:", nrow(coordinates), "\n")
}

cat("\n", paste(rep("=", 70), collapse = ""), "\n")
cat("W-NOMINATE COMPLETADO PARA TODOS LOS PERÍODOS\n")
cat(paste(rep("=", 70), collapse = ""), "\n\n")

cat("Archivos generados en:", output_dir, "\n")
cat("  - wnominate_coordinates_p1.csv\n")
cat("  - wnominate_coordinates_p2.csv\n")
cat("  - wnominate_coordinates_p3.csv\n\n")

cat("Siguiente paso: Ejecutar correct_polarity_wnominate_3periods.R\n")
cat("Luego: Generar gráfico de trayectorias no lineales\n\n")

cat("=== ANÁLISIS COMPLETO ===\n")
