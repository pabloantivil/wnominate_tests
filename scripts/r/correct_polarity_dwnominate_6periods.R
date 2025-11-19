# Correct Polarity for DW-NOMINATE - 6 Political Periods
# 55º Período Legislativo (2018-2022)
#
# Este script invierte las coordenadas para alinear con la convención política chilena:
# 
# PRIMERA DIMENSIÓN (coord1D - Eje Económico):
# - Izquierda (PC, PS) = valores NEGATIVOS (-)
# - Derecha (UDI, RN) = valores POSITIVOS (+)
#
# SEGUNDA DIMENSIÓN (coord2D - Eje Social/Valórico):
# - UDI (derecha conservadora) = valores NEGATIVOS (-) → abajo
# - RN (derecha liberal) = valores POSITIVOS (+) → arriba

cat("\n")
cat("=======================================================\n")
cat("  Corrección de Polaridad - DW-NOMINATE (6 Períodos) \n")
cat("  55º PL (2018-2022) - Chile                         \n")
cat("=======================================================\n")
cat("\n")

library(dplyr)

# Definición de partidos
left_parties <- c("PC", "PS", "FA", "RD")
right_parties <- c("UDI", "RN", "EVOP")
center_parties <- c("DC", "PPD", "PR")

cat("📊 Partidos definidos:\n")
cat("   Izquierda: ", paste(left_parties, collapse = ", "), "\n")
cat("   Derecha: ", paste(right_parties, collapse = ", "), "\n")
cat("   Centro: ", paste(center_parties, collapse = ", "), "\n\n")

# Directorios
input_dir <- "../../data/dwnominate_6periods/output"
output_dir <- input_dir # Guardar en el mismo directorio con sufijo '_corrected'

cat("📂 Input directory: ", input_dir, "\n")
cat("💾 Output directory: ", output_dir, "\n\n")

# Archivos a procesar
period_files <- c(
    "coordinates_P1a_6periods.csv",
    "coordinates_P1b_6periods.csv",
    "coordinates_P2a_6periods.csv",
    "coordinates_P2b_6periods.csv",
    "coordinates_P3a_6periods.csv",
    "coordinates_P3b_6periods.csv",
    "dwnominate_coordinates_all_periods.csv"
)

period_names <- c(
    "P1a - Inicio PL (Primera Mitad)",
    "P1b - Inicio PL (Segunda Mitad)",
    "P2a - Estallido Social (Primera Mitad)",
    "P2b - Estallido Social (Segunda Mitad)",
    "P3a - Post-Plebiscito (Primera Mitad)",
    "P3b - Post-Plebiscito (Segunda Mitad)",
    "Todos los períodos (combinado)"
)

cat("📋 Archivos a procesar: ", length(period_files), "\n\n")

# Función para verificar y corregir polaridad
correct_polarity <- function(coords_df, period_name) {
    cat("====================================\n")
    cat("Procesando: ", period_name, "\n")
    cat("====================================\n")

    if (nrow(coords_df) == 0) {
        cat("⚠️  Archivo vacío, saltando...\n\n")
        return(NULL)
    }

    # Verificar columnas necesarias
    if (!"coord1D" %in% names(coords_df)) {
        cat("❌ Error: columna 'coord1D' no encontrada\n\n")
        return(NULL)
    }

    if (!"partido" %in% names(coords_df)) {
        cat("⚠️  Advertencia: columna 'partido' no encontrada, se omitirá validación\n")
    }

    # Estadísticas antes de corregir
    cat("\n📊 Estadísticas ANTES de corrección:\n")
    cat(
        "   coord1D - Media: ", round(mean(coords_df$coord1D, na.rm = TRUE), 4),
        " | SD: ", round(sd(coords_df$coord1D, na.rm = TRUE), 4), "\n"
    )
    cat(
        "   coord1D - Min: ", round(min(coords_df$coord1D, na.rm = TRUE), 4),
        " | Max: ", round(max(coords_df$coord1D, na.rm = TRUE), 4), "\n"
    )

    # Validar orientación actual con partidos de referencia
    needs_correction <- FALSE

    if ("partido" %in% names(coords_df)) {
        # Obtener promedios por partido
        party_means <- coords_df %>%
            filter(!is.na(partido) & !is.na(coord1D)) %>%
            group_by(partido) %>%
            summarize(
                mean_coord1D = mean(coord1D),
                n = n(),
                .groups = "drop"
            ) %>%
            arrange(mean_coord1D)

        cat("\n📈 Promedio coord1D por partido:\n")
        for (i in 1:nrow(party_means)) {
            party <- party_means$partido[i]
            mean_val <- party_means$mean_coord1D[i]
            n <- party_means$n[i]

            # Identificar posición política
            position <- if (party %in% left_parties) {
                "← Izquierda"
            } else if (party %in% right_parties) {
                "→ Derecha"
            } else if (party %in% center_parties) {
                "⊙ Centro"
            } else {
                "? Otro"
            }

            cat("   ", party, ": ", round(mean_val, 4),
                " (n=", n, ") ", position, "\n",
                sep = ""
            )
        }

        # Determinar si necesita corrección
        left_mean <- mean(
            coords_df$coord1D[coords_df$partido %in% left_parties],
            na.rm = TRUE
        )
        right_mean <- mean(
            coords_df$coord1D[coords_df$partido %in% right_parties],
            na.rm = TRUE
        )

        if (!is.nan(left_mean) && !is.nan(right_mean)) {
            cat("\n🔍 Verificando orientación:\n")
            cat("   Promedio IZQUIERDA (", paste(left_parties, collapse = ", "), "): ",
                round(left_mean, 4), "\n",
                sep = ""
            )
            cat("   Promedio DERECHA (", paste(right_parties, collapse = ", "), "): ",
                round(right_mean, 4), "\n",
                sep = ""
            )

            if (left_mean > right_mean) {
                cat("   ❌ INCORRECTA: Izquierda está a la DERECHA numérica\n")
                cat("   ✅ SE REQUIERE INVERSIÓN (coord1D *= -1)\n")
                needs_correction <- TRUE
            } else {
                cat("   ✅ CORRECTA: Izquierda está a la IZQUIERDA numérica\n")
                cat("   ℹ️  NO se requiere corrección\n")
                needs_correction <- FALSE
            }
        } else {
            cat("\n⚠️  No se pudieron calcular promedios de referencia\n")
            cat("   Asumiendo que SE REQUIERE corrección (por defecto)\n")
            needs_correction <- TRUE
        }
    } else {
        cat("\n⚠️  No hay datos de partido disponibles\n")
        cat("   Asumiendo que SE REQUIERE corrección (por defecto)\n")
        needs_correction <- TRUE
    }

    # Aplicar corrección si es necesaria
    if (needs_correction) {
        cat("\n🔄 Invirtiendo coord1D (multiplicando por -1)...\n")
        coords_df$coord1D <- -coords_df$coord1D

        # Estadísticas después de corregir
        cat("\n📊 Estadísticas DESPUÉS de corrección:\n")
        cat(
            "   coord1D - Media: ", round(mean(coords_df$coord1D, na.rm = TRUE), 4),
            " | SD: ", round(sd(coords_df$coord1D, na.rm = TRUE), 4), "\n"
        )
        cat(
            "   coord1D - Min: ", round(min(coords_df$coord1D, na.rm = TRUE), 4),
            " | Max: ", round(max(coords_df$coord1D, na.rm = TRUE), 4), "\n"
        )

        # Verificar nuevamente
        if ("partido" %in% names(coords_df)) {
            left_mean_new <- mean(
                coords_df$coord1D[coords_df$partido %in% left_parties],
                na.rm = TRUE
            )
            right_mean_new <- mean(
                coords_df$coord1D[coords_df$partido %in% right_parties],
                na.rm = TRUE
            )

            cat("\n✅ Verificación post-corrección coord1D:\n")
            cat("   Promedio IZQUIERDA: ", round(left_mean_new, 4), "\n", sep = "")
            cat("   Promedio DERECHA: ", round(right_mean_new, 4), "\n", sep = "")

            if (left_mean_new < right_mean_new) {
                cat("   ✅ POLARIDAD CORRECTA: Izquierda (-) < Derecha (+)\n")
            } else {
                cat("   ⚠️  ADVERTENCIA: Polaridad aún puede estar incorrecta\n")
            }
        }
    } else {
        cat("\n✅ No se realizó corrección de coord1D (polaridad ya era correcta)\n")
    }

    # ===========================================================================
    # CORRECCIÓN DE SEGUNDA DIMENSIÓN (coord2D)
    # ===========================================================================
    # La segunda dimensión en el contexto chileno refleja posiciones sociales/valóricas:
    # - UDI (conservadora) debería estar ABAJO (valores negativos)
    # - RN (más liberal) debería estar ARRIBA (valores positivos)
    
    needs_correction_2d <- FALSE
    
    if ("partido" %in% names(coords_df) && "coord2D" %in% names(coords_df)) {
        cat("🔍 Verificando orientación de SEGUNDA DIMENSIÓN (coord2D)...\n")
        
        # Calcular promedios de coord2D para UDI y RN
        udi_mean_2d <- mean(
            coords_df$coord2D[coords_df$partido == "UDI"],
            na.rm = TRUE
        )
        rn_mean_2d <- mean(
            coords_df$coord2D[coords_df$partido == "RN"],
            na.rm = TRUE
        )
        
        cat("\n📊 Promedio coord2D por partido (derecha):\n")
        cat("   UDI (conservadora): ", round(udi_mean_2d, 4), "\n", sep = "")
        cat("   RN (liberal):       ", round(rn_mean_2d, 4), "\n", sep = "")
        
        # Determinar si necesita inversión
        # Esperamos: UDI < 0 (abajo), RN > 0 (arriba)
        if (!is.nan(udi_mean_2d) && !is.nan(rn_mean_2d)) {
            cat("\n🔍 Verificando orientación coord2D:\n")
            
            if (udi_mean_2d > 0 && rn_mean_2d < 0) {
                # UDI está arriba y RN abajo → INVERTIDO
                cat("   ❌ INCORRECTA: UDI está ARRIBA (positivo) y RN está ABAJO (negativo)\n")
                cat("   ✅ SE REQUIERE INVERSIÓN (coord2D *= -1)\n")
                needs_correction_2d <- TRUE
            } else if (udi_mean_2d < 0 && rn_mean_2d > 0) {
                # UDI está abajo y RN arriba → CORRECTO
                cat("   ✅ CORRECTA: UDI está ABAJO (negativo) y RN está ARRIBA (positivo)\n")
                cat("   ℹ️  NO se requiere corrección de coord2D\n")
                needs_correction_2d <- FALSE
            } else {
                # Casos ambiguos (ambos positivos o ambos negativos)
                cat("   ⚠️  AMBIGUO: UDI=", round(udi_mean_2d, 3), ", RN=", round(rn_mean_2d, 3), "\n", sep = "")
                
                # Si UDI es más positivo que RN, necesita inversión
                if (udi_mean_2d > rn_mean_2d) {
                    cat("   🔄 UDI está más ARRIBA que RN → SE REQUIERE INVERSIÓN\n")
                    needs_correction_2d <- TRUE
                } else {
                    cat("   ✅ UDI está más ABAJO que RN → NO se requiere corrección\n")
                    needs_correction_2d <- FALSE
                }
            }
        } else {
            cat("\n⚠️  No se pudieron calcular promedios de coord2D\n")
            cat("   NO se corregirá coord2D (mantener valores originales)\n")
            needs_correction_2d <- FALSE
        }
        
        # Aplicar corrección de coord2D si es necesaria
        if (needs_correction_2d) {
            cat("\n🔄 Invirtiendo coord2D (multiplicando por -1)...\n")
            coords_df$coord2D <- -coords_df$coord2D
            
            # Verificar post-corrección
            udi_mean_2d_new <- mean(
                coords_df$coord2D[coords_df$partido == "UDI"],
                na.rm = TRUE
            )
            rn_mean_2d_new <- mean(
                coords_df$coord2D[coords_df$partido == "RN"],
                na.rm = TRUE
            )
            
            cat("\n✅ Verificación post-corrección coord2D:\n")
            cat("   UDI (conservadora): ", round(udi_mean_2d_new, 4), " (esperado: negativo)\n", sep = "")
            cat("   RN (liberal):       ", round(rn_mean_2d_new, 4), " (esperado: positivo)\n", sep = "")
            
            if (udi_mean_2d_new < 0 && rn_mean_2d_new > 0) {
                cat("   ✅ POLARIDAD coord2D CORRECTA\n")
            } else {
                cat("   ⚠️  ADVERTENCIA: coord2D aún puede estar incorrecta\n")
            }
        } else {
            cat("\n✅ No se realizó corrección de coord2D\n")
        }
    }

    cat("\n")

    return(coords_df)
}

# Procesar cada archivo
cat("🚀 Iniciando corrección de polaridad...\n\n")

results <- list()

for (i in seq_along(period_files)) {
    file_name <- period_files[i]
    period_name <- period_names[i]

    input_path <- file.path(input_dir, file_name)

    # Verificar existencia
    if (!file.exists(input_path)) {
        cat("⚠️  Archivo no encontrado: ", file_name, "\n")
        cat("   Saltando...\n\n")
        next
    }

    # Leer datos
    coords <- read.csv(input_path, stringsAsFactors = FALSE)

    # Corregir polaridad
    coords_corrected <- correct_polarity(coords, period_name)

    if (!is.null(coords_corrected)) {
        # Generar nombre de archivo corregido
        if (grepl("_corrected", file_name)) {
            output_name <- file_name # Ya tiene sufijo
        } else {
            output_name <- sub("\\.csv$", "_corrected.csv", file_name)
        }

        output_path <- file.path(output_dir, output_name)

        # Guardar
        write.csv(coords_corrected, output_path, row.names = FALSE)
        cat("💾 Guardado: ", output_name, "\n\n")

        results[[file_name]] <- list(
            input = input_path,
            output = output_path,
            rows = nrow(coords_corrected),
            corrected = TRUE
        )
    }
}

# Resumen final
cat("\n")
cat("=======================================================\n")
cat("  CORRECCIÓN COMPLETADA                              \n")
cat("=======================================================\n")
cat("\n")

cat("📋 Archivos procesados: ", length(results), "/", length(period_files), "\n")

for (file_name in names(results)) {
    res <- results[[file_name]]
    cat("   ✅ ", file_name, " → ", basename(res$output),
        " (", res$rows, " filas)\n",
        sep = ""
    )
}

cat("\n📂 Output directory: ", output_dir, "\n")
cat("\n✅ ¡Corrección de polaridad completada!\n")
cat("💡 Los archivos corregidos tienen el sufijo '_corrected'\n")
cat("\n📏 Convenciones aplicadas:\n")
cat("   • Primera Dimensión (coord1D): Izquierda (-) < Centro (0) < Derecha (+)\n")
cat("   • Segunda Dimensión (coord2D): UDI (abajo, -) < RN (arriba, +)\n\n")
