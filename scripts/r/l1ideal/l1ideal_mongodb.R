# L1IDEAL CON DATOS REALES DE MONGODB
# Script para ejecutar l1ideal con votaciones reales desde MongoDB

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Librerías necesarias
library(mongolite) # Conexión a MongoDB
library(l1ideal) # Modelo l1ideal
library(pscl) # Objeto rollcall
library(ggplot2) # Visualizaciones
library(coda) # Análisis MCMC

# Configuración de MongoDB
MONGODB_URL <- "urlmongo"
DB_NAME <- "nombre_bd"

cat("\n", paste(rep("=", 70), collapse = ""), "\n")
cat("L1IDEAL CON DATOS REALES DE VOTACIONES\n")
cat(paste(rep("=", 70), collapse = ""), "\n\n")

# =============================================================================
# FUNCIÓN 1: CONECTAR A MONGODB
# =============================================================================

conectar_mongodb <- function(db_name = DB_NAME, mongo_url = MONGODB_URL) {
    cat("Conectando a MongoDB...\n")
    cat(sprintf("   URL: %s\n", mongo_url))
    cat(sprintf("   Base de datos: %s\n", db_name))

    tryCatch(
        {
            # Crear conexiones a las colecciones
            votos_diputados <- mongo(
                collection = "VotosDiputados",
                db = db_name,
                url = mongo_url
            )

            parlamentarios <- mongo(
                collection = "parlamentarios",
                db = db_name,
                url = mongo_url
            )

            votaciones <- mongo(
                collection = "votaciones",
                db = db_name,
                url = mongo_url
            )

            # Verificar conexión
            n_votos <- votos_diputados$count()
            n_parlamentarios <- parlamentarios$count()
            n_votaciones <- votaciones$count()

            cat("Conexión exitosa\n")
            cat(sprintf("Votos en BD: %d\n", n_votos))
            cat(sprintf("Parlamentarios: %d\n", n_parlamentarios))
            cat(sprintf("Votaciones: %d\n", n_votaciones))

            return(list(
                votos = votos_diputados,
                parlamentarios = parlamentarios,
                votaciones = votaciones
            ))
        },
        error = function(e) {
            cat("Error conectando a MongoDB:\n")
            cat(sprintf("   %s\n", e$message))
            stop("No se pudo conectar a MongoDB")
        }
    )
}

# =============================================================================
# FUNCIÓN 2: OBTENER IDS DE VOTACIONES
# =============================================================================

obtener_votation_ids <- function(colecciones, filtro = NULL) {
    cat("\n📋 Obteniendo lista de votaciones...\n")

    # Si no hay filtro, obtener todas
    if (is.null(filtro)) {
        cat("   Extrayendo TODAS las votaciones de la base de datos\n")
        votaciones_docs <- colecciones$votaciones$find(
            query = "{}",
            fields = '{"id": 1}'
        )
    } else {
        votaciones_docs <- colecciones$votaciones$find(
            query = filtro,
            fields = '{"id": 1}'
        )
    }

    votation_ids <- votaciones_docs$id

    cat(sprintf("%d votaciones encontradas\n", length(votation_ids)))

    return(votation_ids)
}

# =============================================================================
# FUNCIÓN 3: CONSTRUIR MATRIZ DE VOTACIONES
# =============================================================================

construir_matriz_votos <- function(colecciones, votation_ids) {
    cat("\nConstruyendo matriz de votaciones...\n")
    cat(sprintf("   Procesando %d votaciones\n", length(votation_ids)))

    # 1. Obtener todos los parlamentarios
    cat("Cargando parlamentarios...\n")
    parlamentarios_df <- colecciones$parlamentarios$find("{}")
    cat(sprintf("      %d parlamentarios encontrados\n", nrow(parlamentarios_df)))

    # Obtener IDs de parlamentarios (campo "id")
    parl_ids <- parlamentarios_df$id
    n_legis <- length(parl_ids)

    # 2. Obtener información de votaciones (metadata)
    cat("Cargando información de votaciones...\n")
    votation_ids_str <- paste(votation_ids, collapse = ",")
    votaciones_query <- sprintf('{"id": {"$in": [%s]}}', votation_ids_str)
    votaciones_df <- colecciones$votaciones$find(votaciones_query)
    cat(sprintf("      %d votaciones (metadata) cargadas\n", nrow(votaciones_df)))

    # Ordenar por fecha si existe el campo
    if ("fecha" %in% names(votaciones_df)) {
        votaciones_df <- votaciones_df[order(votaciones_df$fecha), ]
        cat("      Votaciones ordenadas por fecha\n")
    }

    vote_ids <- votaciones_df$id
    n_votes <- length(vote_ids)


    cat("Cargando votos\n")
    votos_query <- sprintf('{"id": {"$in": [%s]}}', votation_ids_str)
    votos_diputados_df <- colecciones$votos$find(votos_query)
    cat(sprintf("      %d documentos de votación cargados\n", nrow(votos_diputados_df)))

    # 4. Crear matriz de votaciones
    cat("Creando matriz de votaciones...\n")
    cat(sprintf(
        "      Dimensiones: %d legisladores x %d votaciones\n",
        n_legis, n_votes
    ))

    # Inicializar matriz con 2 (missing/abstención por defecto)
    # Usaremos IDs numéricos como nombres de filas/columnas
    votes_matrix <- matrix(
        2, # Valor por defecto: abstención/missing
        nrow = n_legis,
        ncol = n_votes,
        dimnames = list(as.character(parl_ids), as.character(vote_ids))
    )

    cat("      Llenando matriz con votos...\n")

    votos_procesados <- 0
    for (i in 1:nrow(votos_diputados_df)) {
        voto_doc <- votos_diputados_df[i, ]
        votacion_id <- as.character(voto_doc$id)

        detalle <- voto_doc$detalle

        if (!is.null(detalle) && length(detalle) > 0) {
            # Convertir detalle a lista nombrada si no lo es
            if (is.list(detalle)) {
                # detalle es una lista: {parl_id: voto}
                for (parl_id_str in names(detalle)) {
                    valor_voto <- detalle[[parl_id_str]]
                    parl_id <- as.character(parl_id_str)

                    # Verificar que el parlamentario y votación existen en la matriz
                    if (parl_id %in% rownames(votes_matrix) &&
                        votacion_id %in% colnames(votes_matrix)) {
                        # Mapear voto
                        # Python: 1→1 (Yes), 0→-1 (No), otros→0 (Abstención)
                        # l1ideal: 1 (Yea), 0 (Nay), 2 (Missing)
                        if (!is.null(valor_voto) && !is.na(valor_voto)) {
                            if (valor_voto == 1) {
                                votes_matrix[parl_id, votacion_id] <- 1 # Sí
                            } else if (valor_voto == 0) {
                                votes_matrix[parl_id, votacion_id] <- 0 # No
                            } else {
                                votes_matrix[parl_id, votacion_id] <- 2 # Abstención
                            }
                            votos_procesados <- votos_procesados + 1
                        }
                    }
                }
            }
        }

        # Progreso cada 100 votaciones
        if (i %% 100 == 0) {
            cat(sprintf(
                "      Procesadas %d/%d votaciones (%.1f%%)\n",
                i, nrow(votos_diputados_df), 100 * i / nrow(votos_diputados_df)
            ))
        }
    }

    cat(sprintf("Matriz completada: %d votos procesados\n", votos_procesados))

    # 5. Preparar metadata de legisladores
    cat("Preparando metadata de legisladores...\n")
    legis_data <- data.frame(
        id = parl_ids,
        stringsAsFactors = FALSE
    )

    # Agregar información de parlamentarios (nombre, partido)
    for (i in 1:nrow(legis_data)) {
        parl_id <- legis_data$id[i]
        parl_info <- parlamentarios_df[parlamentarios_df$id == parl_id, ]

        if (nrow(parl_info) > 0) {
            # Extraer nombre
            legis_data$nombre[i] <- if ("nombre" %in% names(parl_info)) parl_info$nombre[1] else NA

            # Extraer partido del campo "periodo"
            # Puede tener formatos:
            #   - "1520726400, 1646956799, PS"
            #   - "1520726400, 1646956799, partido = "PS")"
            if ("periodo" %in% names(parl_info) && !is.na(parl_info$periodo[1])) {
                periodo_parts <- strsplit(as.character(parl_info$periodo[1]), ",")[[1]]
                partido_raw <- trimws(periodo_parts[length(periodo_parts)])

                # Limpiar formato: extraer solo la sigla entre comillas
                # "partido = "PS")" → "PS"
                # "PS" → "PS"
                partido_clean <- gsub('.*"([^"]+)".*', "\\1", partido_raw)

                # Si no tenía comillas, usar el texto limpio
                if (partido_clean == partido_raw && grepl("partido\\s*=", partido_raw)) {
                    partido_clean <- NA
                }

                legis_data$partido[i] <- partido_clean
            } else {
                legis_data$partido[i] <- NA
            }
        }
    }

    # 6. Preparar metadata de votaciones
    cat("Preparando metadata de votaciones...\n")
    votes_data <- data.frame(
        id = vote_ids,
        fecha = if ("fecha" %in% names(votaciones_df)) votaciones_df$fecha else NA,
        stringsAsFactors = FALSE
    )

    # Estadísticas finales
    cat("\nESTADÍSTICAS DE LA MATRIZ:\n")
    cat(sprintf("      Total de celdas: %d\n", n_legis * n_votes))
    cat(sprintf(
        "      Votos Sí: %d (%.1f%%)\n",
        sum(votes_matrix == 1, na.rm = TRUE),
        100 * sum(votes_matrix == 1, na.rm = TRUE) / (n_legis * n_votes)
    ))
    cat(sprintf(
        "      Votos No: %d (%.1f%%)\n",
        sum(votes_matrix == 0, na.rm = TRUE),
        100 * sum(votes_matrix == 0, na.rm = TRUE) / (n_legis * n_votes)
    ))
    cat(sprintf(
        "      Abstención/Ausente: %d (%.1f%%)\n",
        sum(votes_matrix == 2, na.rm = TRUE),
        100 * sum(votes_matrix == 2, na.rm = TRUE) / (n_legis * n_votes)
    ))
    cat(sprintf(
        "      Missing: %d (%.1f%%)\n",
        sum(is.na(votes_matrix)),
        100 * sum(is.na(votes_matrix)) / (n_legis * n_votes)
    ))

    return(list(
        votes_matrix = votes_matrix,
        legis_data = legis_data,
        votes_data = votes_data
    ))
}

# =============================================================================
# FUNCIÓN 4: CREAR OBJETO ROLLCALL
# =============================================================================

crear_rollcall <- function(datos) {
    cat("\nCreando objeto rollcall...\n")

    rc <- pscl::rollcall(
        data = datos$votes_matrix,
        yea = 1,
        nay = 0,
        missing = 2,
        notInLegis = NA,
        legis.names = datos$legis_data$id,
        legis.data = datos$legis_data,
        vote.names = datos$votes_data$id,
        vote.data = datos$votes_data
    )

    cat("Objeto rollcall creado exitosamente\n")
    cat(sprintf("   Clase: %s\n", class(rc)))

    return(rc)
}

# =============================================================================
# FUNCIÓN 5: EJECUTAR L1IDEAL
# =============================================================================

ejecutar_l1ideal <- function(rc, dimensions = 2, mcmc = 100, thin = 10,
                             burnin = 100, minvotes = 20, lop = 0,
                             polarity = NULL, verbose = 100, seed = 123) {
    cat("\n", paste(rep("=", 70), collapse = ""), "\n")
    cat("EJECUTANDO MODELO L1IDEAL\n")
    cat(paste(rep("=", 70), collapse = ""), "\n\n")

    cat("PARÁMETROS DEL MODELO:\n")
    cat(sprintf("   Dimensiones: %d\n", dimensions))
    cat(sprintf("   MCMC iteraciones: %d\n", mcmc))
    cat(sprintf("   Thin: %d\n", thin))
    cat(sprintf("   Burnin: %d\n", burnin))
    cat(sprintf("   Votos mínimos: %d\n", minvotes))
    cat(sprintf("   LOP: %.2f\n", lop))
    cat(sprintf("   Seed: %d\n", seed))

    # Determinar polarity automáticamente si no se proporciona
    if (is.null(polarity)) {
        cat("\nDeterminando polaridad automáticamente...\n")
        # Usar los primeros legisladores como referencia
        polarity <- c(1, 2)
        cat(sprintf("   Polaridad establecida: c(%s)\n", paste(polarity, collapse = ",")))
    }

    cat("\nIniciando estimación (esto puede tomar varios minutos)...\n\n")

    start_time <- Sys.time()

    res <- l1ideal(
        rc,
        dimensions = dimensions,
        mcmc = mcmc,
        thin = thin,
        burnin = burnin,
        minvotes = minvotes,
        lop = lop,
        polarity = polarity,
        verbose = verbose,
        seed = seed
    )

    end_time <- Sys.time()
    tiempo_total <- as.numeric(difftime(end_time, start_time, units = "secs"))

    cat("\nMODELO L1IDEAL EJECUTADO EXITOSAMENTE!\n")
    cat(sprintf(
        "Tiempo total: %.2f segundos (%.2f minutos)\n",
        tiempo_total, tiempo_total / 60
    ))

    return(list(
        resultado = res,
        tiempo = tiempo_total
    ))
}

# =============================================================================
# FUNCIÓN 6: VISUALIZAR RESULTADOS
# =============================================================================

visualizar_resultados_reales <- function(res, legis_data) {
    cat("\n", paste(rep("=", 70), collapse = ""), "\n")
    cat("GENERANDO VISUALIZACIONES\n")
    cat(paste(rep("=", 70), collapse = ""), "\n\n")

    # Extraer posiciones promedio
    est_pos_1d <- apply(res$resultado$legislators[[1]], 2, mean)
    est_pos_2d <- if (length(res$resultado$legislators) > 1) {
        apply(res$resultado$legislators[[2]], 2, mean)
    } else {
        NULL
    }

    weight_mean <- mean(res$resultado$weight)

    # Preparar dataframe
    plot_df <- data.frame(
        id = names(est_pos_1d),
        dim1 = est_pos_1d,
        stringsAsFactors = FALSE
    )

    if (!is.null(est_pos_2d)) {
        plot_df$dim2 <- est_pos_2d
    }

    # Agregar información de partidos
    plot_df <- merge(plot_df, legis_data[, c("id", "nombre", "partido")],
        by = "id", all.x = TRUE
    )

    # Gráfico 1: Espacio ideológico 2D
    if (!is.null(est_pos_2d)) {
        cat("Creando gráfico del espacio ideológico 2D...\n")

        # Paleta de colores distinguibles (colores primarios y vibrantes)
        # Asignar colores específicos a partidos principales
        colores_partidos <- c(
            "UDI" = "#0000FF", # Azul fuerte (derecha)
            "RN" = "#00BFFF", # Azul claro (centro-derecha)
            "EVOP" = "#87CEEB", # Azul cielo (centro-derecha liberal)
            "PS" = "#FF0000", # Rojo (izquierda)
            "PC" = "#8B0000", # Rojo oscuro (izquierda)
            "PPD" = "#FF6347", # Rojo tomate (centro-izquierda)
            "DC" = "#FF8C00", # Naranja (centro)
            "PRad" = "#FFA500", # Naranja claro (centro-izquierda)
            "RD" = "#32CD32", # Verde (izquierda joven)
            "CS" = "#00FF00", # Verde brillante (centro)
            "PL" = "#9370DB", # Púrpura (liberal)
            "IND" = "#808080", # Gris (independientes)
            "COM" = "#DC143C", # Carmesí (comunista)
            "FRVS" = "#FF1493", # Rosa fuerte (Frente amplio)
            "PH" = "#00CED1", # Turquesa (humanista)
            "PEV" = "#228B22", # Verde bosque (ecologista)
            "PRep" = "#4169E1" # Azul real (republicano)
        )

        p1 <- ggplot(plot_df, aes(
            x = dim1 * weight_mean,
            y = dim2 * (1 - weight_mean),
            color = partido
        )) +
            geom_point(size = 3, alpha = 0.7) +
            scale_color_manual(
                values = colores_partidos,
                na.value = "#CCCCCC" # Gris claro para NA
            ) +
            theme_minimal() +
            labs(
                title = "Puntos Ideales de Legisladores (L1IDEAL)",
                subtitle = sprintf(
                    "Datos reales: %d legisladores | Weight: %.3f",
                    nrow(plot_df), weight_mean
                ),
                x = "Dimensión 1 (Económica)",
                y = "Dimensión 2 (Social)",
                color = "Partido"
            ) +
            theme(
                plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
                plot.subtitle = element_text(hjust = 0.5, size = 12),
                legend.position = "right"
            )

        print(p1)
    }

    # Gráfico 2: Trazas MCMC
    cat("Creando gráficos de convergencia MCMC...\n")

    mcmc_data <- data.frame(
        iteration = rep(1:length(res$resultado$beta), 2),
        value = c(as.numeric(res$resultado$beta), as.numeric(res$resultado$weight)),
        parameter = rep(c("Beta (Precisión)", "Weight (Peso Dim1)"),
            each = length(res$resultado$beta)
        )
    )

    p2 <- ggplot(mcmc_data, aes(x = iteration, y = value)) +
        geom_line(alpha = 0.8, color = "steelblue") +
        facet_wrap(~parameter, scales = "free_y", ncol = 1) +
        theme_minimal() +
        labs(
            title = "Convergencia de Parámetros MCMC",
            x = "Iteración",
            y = "Valor"
        ) +
        theme(
            plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
            strip.text = element_text(size = 12, face = "bold")
        )

    print(p2)

    # Guardar gráficos en el directorio de salida
    output_dir <- file.path("data", "l1ideal", "output")
    if (!dir.exists(output_dir)) {
        dir.create(output_dir, recursive = TRUE)
    }

    cat("\nGuardando gráficos...\n")

    # Guardar gráfico 2D si existe
    if (!is.null(est_pos_2d)) {
        ggsave(
            filename = file.path(output_dir, "l1ideal_espacio_ideologico_2D.png"),
            plot = p1,
            width = 12,
            height = 8,
            dpi = 300
        )
        cat("   l1ideal_espacio_ideologico_2D.png guardado\n")
    }

    # Guardar gráfico de convergencia
    ggsave(
        filename = file.path(output_dir, "l1ideal_convergencia_mcmc.png"),
        plot = p2,
        width = 10,
        height = 8,
        dpi = 300
    )
    cat("   l1ideal_convergencia_mcmc.png guardado\n")

    cat("Visualizaciones completadas\n")

    return(list(p1 = if (!is.null(est_pos_2d)) p1 else NULL, p2 = p2))
}

# =============================================================================
# FUNCIÓN 7: GUARDAR RESULTADOS
# =============================================================================

guardar_resultados <- function(res, datos, plots, filename = "l1ideal_resultados_reales.RData") {
    cat("\nGuardando resultados...\n")

    # Determinar directorio de salida relativo al proyecto
    # Asume que el script se ejecuta desde la raíz del proyecto
    output_dir <- file.path("data", "l1ideal", "output")

    # Crear directorio si no existe
    if (!dir.exists(output_dir)) {
        dir.create(output_dir, recursive = TRUE)
        cat(sprintf("   Directorio creado: %s\n", output_dir))
    }

    # Ruta completa del archivo
    filepath <- file.path(output_dir, filename)

    save(
        res,
        datos,
        plots,
        file = filepath
    )

    cat(sprintf("Resultados guardados en '%s'\n", filepath))
    cat(sprintf("   Para cargar: load('%s')\n", filepath))

    # Exportar coordenadas a CSV
    cat("\nExportando coordenadas a CSV...\n")

    # Extraer posiciones promedio
    est_pos_1d <- apply(res$resultado$legislators[[1]], 2, mean)
    est_pos_2d <- if (length(res$resultado$legislators) > 1) {
        apply(res$resultado$legislators[[2]], 2, mean)
    } else {
        NULL
    }

    # Crear dataframe con coordenadas
    coords_df <- data.frame(
        legislator_id = names(est_pos_1d),
        coord1D = est_pos_1d,
        stringsAsFactors = FALSE
    )

    if (!is.null(est_pos_2d)) {
        coords_df$coord2D <- est_pos_2d
    }

    # Agregar metadata de legisladores
    coords_df <- merge(coords_df, datos$legis_data[, c("id", "nombre", "partido")],
        by.x = "legislator_id", by.y = "id", all.x = TRUE
    )

    # Guardar CSV
    csv_path <- file.path(output_dir, "l1ideal_coordinates.csv")
    write.csv(coords_df, csv_path, row.names = FALSE)
    cat(sprintf("   Coordenadas exportadas: %s\n", csv_path))
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

ejecutar_analisis_completo <- function(
    mcmc = 100,
    dimensions = 2,
    minvotes = 20,
    filtro_votaciones = NULL) {
    cat("\n", paste(rep("=", 70), collapse = ""), "\n")
    cat("INICIANDO ANÁLISIS L1IDEAL CON DATOS REALES\n")
    cat(paste(rep("=", 70), collapse = ""), "\n")

    # 1. Conectar a MongoDB
    colecciones <- conectar_mongodb()

    # 2. Obtener IDs de votaciones
    votation_ids <- obtener_votation_ids(colecciones, filtro_votaciones)

    # 3. Construir matriz de votaciones
    datos <- construir_matriz_votos(colecciones, votation_ids)

    # 4. Crear objeto rollcall
    rc <- crear_rollcall(datos)

    # 5. Ejecutar l1ideal
    res <- ejecutar_l1ideal(
        rc,
        dimensions = dimensions,
        mcmc = mcmc,
        minvotes = minvotes
    )

    # 6. Visualizar resultados
    plots <- visualizar_resultados_reales(res, datos$legis_data)

    # 7. Guardar resultados
    guardar_resultados(res, datos, plots)

    # 8. Resumen final
    cat("\n", paste(rep("=", 70), collapse = ""), "\n")
    cat("ANÁLISIS COMPLETADO EXITOSAMENTE\n")
    cat(paste(rep("=", 70), collapse = ""), "\n\n")

    cat("RESUMEN DE RESULTADOS:\n")
    cat(sprintf("   Legisladores analizados: %d\n", ncol(res$resultado$legislators[[1]])))
    cat(sprintf("   Votaciones analizadas: %d\n", ncol(res$resultado$yea_positions[[1]])))
    cat(sprintf("   Dimensiones: %d\n", dimensions))
    cat(sprintf("   Tiempo de ejecución: %.2f minutos\n", res$tiempo / 60))
    cat(sprintf("   Beta promedio: %.3f\n", mean(res$resultado$beta)))
    cat(sprintf("   Weight promedio: %.3f\n", mean(res$resultado$weight)))

    # Cerrar conexiones
    colecciones$votos$disconnect()
    colecciones$parlamentarios$disconnect()
    colecciones$votaciones$disconnect()

    return(list(
        resultado = res,
        datos = datos,
        plots = plots
    ))
}

cat("\nFunciones de l1ideal_mongodb.R cargadas exitosamente\n")
cat("\nPara ejecutar el análisis completo:\n")
cat("   resultados <- ejecutar_analisis_completo(mcmc = 100, dimensions = 2)\n")
cat("\n")
