# DW-NOMINATE Analysis Script - 6 Períodos Semestrales (2019-2021)
# Análisis con 6 períodos divididos por semestre

cat("\n")
cat("===============================================\n")
cat("  DW-NOMINATE Analysis - Chilean Congress     \n")
cat("  6 Períodos Semestrales (2019-2021)          \n")
cat("===============================================\n")
cat("\n")

# Instalar paquetes requeridos si no están instalados
if (!require(pscl)) {
    cat("📦 Instalando paquete pscl...\n")
    install.packages("pscl")
}
if (!require(dplyr)) {
    cat("📦 Instalando paquete dplyr...\n")
    install.packages("dplyr")
}
if (!require(dwnominate)) {
    cat("📦 Instalando paquete dwnominate...\n")
    install.packages("remotes")
    remotes::install_github("wmay/dwnominate")
}

library(pscl)
library(dplyr)
library(dwnominate)

cat("\n✅ Todos los paquetes cargados exitosamente\n\n")

# Cargar metadata desde data/dwnominate_6periods/input
legislator_meta <- read.csv("../../data/dwnominate_6periods/input/legislator_metadata.csv")

cat("📊 Metadata cargada:\n")
cat("   Legisladores: ", nrow(legislator_meta), "\n\n")

cat("📅 Cargando matrices de votos para cada período...\n\n")

# Almacenamiento para objetos rollcall
rc_list <- list()

# PERÍODO 1: 2019 Semestre 1
votes_p1 <- read.csv("../../data/dwnominate_6periods/input/P1_votes_matrix.csv", row.names = 1)
votes_mat_p1 <- as.matrix(votes_p1)

period_legislators_p1 <- rownames(votes_mat_p1)
legis_data_p1 <- data.frame(
    legislator_id = as.integer(period_legislators_p1),
    row.names = period_legislators_p1,
    stringsAsFactors = FALSE
)
legis_data_p1 <- legis_data_p1 %>%
    left_join(
        legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
        by = "legislator_id"
    )
legis_data_p1$party <- ifelse(is.na(legis_data_p1$partido), "IND", legis_data_p1$partido)
rownames(legis_data_p1) <- period_legislators_p1

rc_p1 <- rollcall(
    data = votes_mat_p1,
    yea = 1,
    nay = 0,
    missing = NA,
    notInLegis = 9,
    legis.names = rownames(votes_mat_p1),
    vote.names = colnames(votes_mat_p1),
    desc = "2019 Semestre 1",
    legis.data = legis_data_p1
)
cat(
    "✅ 2019 Semestre 1: ", nrow(rc_p1$votes), " legisladores x ",
    ncol(rc_p1$votes), " votaciones\n"
)
rc_list[[1]] <- rc_p1

# PERÍODO 2: 2019 Semestre 2
votes_p2 <- read.csv("../../data/dwnominate_6periods/input/P2_votes_matrix.csv", row.names = 1)
votes_mat_p2 <- as.matrix(votes_p2)

period_legislators_p2 <- rownames(votes_mat_p2)
legis_data_p2 <- data.frame(
    legislator_id = as.integer(period_legislators_p2),
    row.names = period_legislators_p2,
    stringsAsFactors = FALSE
)
legis_data_p2 <- legis_data_p2 %>%
    left_join(
        legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
        by = "legislator_id"
    )
legis_data_p2$party <- ifelse(is.na(legis_data_p2$partido), "IND", legis_data_p2$partido)
rownames(legis_data_p2) <- period_legislators_p2

rc_p2 <- rollcall(
    data = votes_mat_p2,
    yea = 1,
    nay = 0,
    missing = NA,
    notInLegis = 9,
    legis.names = rownames(votes_mat_p2),
    vote.names = colnames(votes_mat_p2),
    desc = "2019 Semestre 2",
    legis.data = legis_data_p2
)
cat(
    "✅ 2019 Semestre 2: ", nrow(rc_p2$votes), " legisladores x ",
    ncol(rc_p2$votes), " votaciones\n"
)
rc_list[[2]] <- rc_p2

# PERÍODO 3: 2020 Semestre 1
votes_p3 <- read.csv("../../data/dwnominate_6periods/input/P3_votes_matrix.csv", row.names = 1)
votes_mat_p3 <- as.matrix(votes_p3)

period_legislators_p3 <- rownames(votes_mat_p3)
legis_data_p3 <- data.frame(
    legislator_id = as.integer(period_legislators_p3),
    row.names = period_legislators_p3,
    stringsAsFactors = FALSE
)
legis_data_p3 <- legis_data_p3 %>%
    left_join(
        legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
        by = "legislator_id"
    )
legis_data_p3$party <- ifelse(is.na(legis_data_p3$partido), "IND", legis_data_p3$partido)
rownames(legis_data_p3) <- period_legislators_p3

rc_p3 <- rollcall(
    data = votes_mat_p3,
    yea = 1,
    nay = 0,
    missing = NA,
    notInLegis = 9,
    legis.names = rownames(votes_mat_p3),
    vote.names = colnames(votes_mat_p3),
    desc = "2020 Semestre 1",
    legis.data = legis_data_p3
)
cat(
    "✅ 2020 Semestre 1: ", nrow(rc_p3$votes), " legisladores x ",
    ncol(rc_p3$votes), " votaciones\n"
)
rc_list[[3]] <- rc_p3

# PERÍODO 4: 2020 Semestre 2
votes_p4 <- read.csv("../../data/dwnominate_6periods/input/P4_votes_matrix.csv", row.names = 1)
votes_mat_p4 <- as.matrix(votes_p4)

period_legislators_p4 <- rownames(votes_mat_p4)
legis_data_p4 <- data.frame(
    legislator_id = as.integer(period_legislators_p4),
    row.names = period_legislators_p4,
    stringsAsFactors = FALSE
)
legis_data_p4 <- legis_data_p4 %>%
    left_join(
        legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
        by = "legislator_id"
    )
legis_data_p4$party <- ifelse(is.na(legis_data_p4$partido), "IND", legis_data_p4$partido)
rownames(legis_data_p4) <- period_legislators_p4

rc_p4 <- rollcall(
    data = votes_mat_p4,
    yea = 1,
    nay = 0,
    missing = NA,
    notInLegis = 9,
    legis.names = rownames(votes_mat_p4),
    vote.names = colnames(votes_mat_p4),
    desc = "2020 Semestre 2",
    legis.data = legis_data_p4
)
cat(
    "✅ 2020 Semestre 2: ", nrow(rc_p4$votes), " legisladores x ",
    ncol(rc_p4$votes), " votaciones\n"
)
rc_list[[4]] <- rc_p4

# PERÍODO 5: 2021 Semestre 1
votes_p5 <- read.csv("../../data/dwnominate_6periods/input/P5_votes_matrix.csv", row.names = 1)
votes_mat_p5 <- as.matrix(votes_p5)

period_legislators_p5 <- rownames(votes_mat_p5)
legis_data_p5 <- data.frame(
    legislator_id = as.integer(period_legislators_p5),
    row.names = period_legislators_p5,
    stringsAsFactors = FALSE
)
legis_data_p5 <- legis_data_p5 %>%
    left_join(
        legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
        by = "legislator_id"
    )
legis_data_p5$party <- ifelse(is.na(legis_data_p5$partido), "IND", legis_data_p5$partido)
rownames(legis_data_p5) <- period_legislators_p5

rc_p5 <- rollcall(
    data = votes_mat_p5,
    yea = 1,
    nay = 0,
    missing = NA,
    notInLegis = 9,
    legis.names = rownames(votes_mat_p5),
    vote.names = colnames(votes_mat_p5),
    desc = "2021 Semestre 1",
    legis.data = legis_data_p5
)
cat(
    "✅ 2021 Semestre 1: ", nrow(rc_p5$votes), " legisladores x ",
    ncol(rc_p5$votes), " votaciones\n"
)
rc_list[[5]] <- rc_p5

# PERÍODO 6: 2021 Semestre 2
votes_p6 <- read.csv("../../data/dwnominate_6periods/input/P6_votes_matrix.csv", row.names = 1)
votes_mat_p6 <- as.matrix(votes_p6)

period_legislators_p6 <- rownames(votes_mat_p6)
legis_data_p6 <- data.frame(
    legislator_id = as.integer(period_legislators_p6),
    row.names = period_legislators_p6,
    stringsAsFactors = FALSE
)
legis_data_p6 <- legis_data_p6 %>%
    left_join(
        legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
        by = "legislator_id"
    )
legis_data_p6$party <- ifelse(is.na(legis_data_p6$partido), "IND", legis_data_p6$partido)
rownames(legis_data_p6) <- period_legislators_p6

rc_p6 <- rollcall(
    data = votes_mat_p6,
    yea = 1,
    nay = 0,
    missing = NA,
    notInLegis = 9,
    legis.names = rownames(votes_mat_p6),
    vote.names = colnames(votes_mat_p6),
    desc = "2021 Semestre 2",
    legis.data = legis_data_p6
)
cat(
    "✅ 2021 Semestre 2: ", nrow(rc_p6$votes), " legisladores x ",
    ncol(rc_p6$votes), " votaciones\n"
)
rc_list[[6]] <- rc_p6

cat("\n")
cat("===============================================\n")
cat("  Ejecutando DW-NOMINATE                      \n")
cat("===============================================\n")
cat("\n")

# Obtener lista de legisladores comunes en todos los períodos
common_legislators <- character(0)
if (length(rc_list) > 0) {
  # Obtener legisladores del primer período
  common_legislators <- as.character(rc_list[[1]]$legis.data$legislator_id)
  
  # Intersectar con legisladores de cada período subsiguiente
  for (i in 2:length(rc_list)) {
    period_legislators <- as.character(rc_list[[i]]$legis.data$legislator_id)
    common_legislators <- intersect(common_legislators, period_legislators)
  }
}

cat("📋 Legisladores comunes en todos los períodos: ", length(common_legislators), "\n\n")

# Definir partidos de izquierda y derecha
right_parties <- c("UDI", "RN")
left_parties <- c("PC", "PS")

left_legislators <- legislator_meta$legislator_id[legislator_meta$partido %in% left_parties]
right_legislators <- legislator_meta$legislator_id[legislator_meta$partido %in% right_parties]

# Buscar legislador de izquierda en el conjunto común
left_in_common <- left_legislators[as.character(left_legislators) %in% common_legislators]

if (length(left_in_common) > 0) {
  polarity_anchor <- as.character(left_in_common[1])
  anchor_info <- legislator_meta[legislator_meta$legislator_id == as.integer(polarity_anchor), ]
  cat(
    "🎯 Anclaje de polaridad: ", polarity_anchor, " (",
    anchor_info$partido[1], " - ", anchor_info$nombres[1], ")\n\n"
  )
} else {
  # Fallback: usar el primer legislador común
  polarity_anchor <- common_legislators[1]
  cat("   ⚠️  Usando anclaje alternativo: ", polarity_anchor, "\n\n")
}

cat("⚙️  Parámetros:\n")
cat("   • Dimensiones: 2\n")
cat("   • Modelo: 1 (linear)\n")
cat("   • lop: 0.001 (filtro de votaciones lopsided)\n")
cat("   • minvotes: 1\n")
cat("   • Períodos: 6\n")
cat("   • Polarity: ", polarity_anchor, " (primera dimensión)\n\n")

cat("🔄 Ejecutando algoritmo DW-NOMINATE...\n")
cat("   (esto puede tomar varios minutos)\n\n")

# Ejecutar DW-NOMINATE con parámetros correctos
dw_result <- dwnominate(
  rc_list,
  id = "legislator_id",  # CRÍTICO: identificador único de legisladores
  dims = 2,              # 2 dimensiones
  model = 1,             # Linear change over time
  polarity = polarity_anchor,  # STRING del ID del legislador ancla
  minvotes = 1,          # Mínimo de votos para incluir legislador
  lop = 0.001,           # Lopsided vote threshold (muy permisivo)
  niter = 4,             # 4 iteraciones (usualmente suficiente)
  beta = 5.9539,         # Parámetro de error espacial (default)
  w = 0.3463,            # Peso segunda dimensión (default)
  verbose = TRUE
    )

cat("\n✅ DW-NOMINATE completado exitosamente!\n\n")

# Mostrar resumen
cat("\n=== RESUMEN DE RESULTADOS DW-NOMINATE ===\n")
print(summary(dw_result))

# Extraer coordenadas de legisladores
legislators <- dw_result$legislators

# Renombrar columnas para que coincidan con nuestra nomenclatura
legislators <- legislators %>%
  rename(
    legislator = ID,
    period = session
  ) %>%
  mutate(
    legislator = as.integer(legislator)
  )

# Agregar metadata
legislators <- legislators %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = c("legislator" = "legislator_id")
  )

# Guardar resultados
cat("\n💾 Guardando coordenadas para todos los períodos combinados...\n")

# Crear directorio de salida si no existe
output_dir <- "../../data/dwnominate_6periods/output"
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

write.csv(legislators, file.path(output_dir, "dwnominate_coordinates_all_periods_6p.csv"), row.names = FALSE)
cat("   ✅ dwnominate_coordinates_all_periods_6p.csv (", nrow(legislators), " filas)\n")

# Guardar archivos específicos por período
cat("\n💾 Guardando coordenadas para cada período...\n")
for (i in 1:6) {
  period_coords <- legislators %>%
    filter(period == i) %>%
    select(legislator, period, coord1D, coord2D, se1D, se2D, nombres, partido, region, distrito)

  output_file <- file.path(output_dir, paste0("coordinates_P", i, "_6periods.csv"))
  write.csv(period_coords, output_file, row.names = FALSE)
  cat("   ✅ ", basename(output_file), " (", nrow(period_coords), " legisladores)\n")
}

# Guardar parámetros de votaciones
cat("\n💾 Guardando parámetros de votaciones...\n")
write.csv(dw_result$rollcalls, file.path(output_dir, "dwnominate_bill_parameters_6periods.csv"), row.names = FALSE)
cat("   ✅ dwnominate_bill_parameters_6periods.csv\n")

# Guardar objeto completo R
saveRDS(dw_result, file.path(output_dir, "dw_nominate_result_6periods.rds"))
cat("   ✅ dw_nominate_result_6periods.rds (objeto R completo)\n")

# Guardar información del modelo
cat("\n💾 Guardando información del modelo...\n")
model_info <- data.frame(
  parameter = c("Dimensions", "Model", "Beta", "Weight_Dim2", "Periods", "Total_Legislators", "Total_Votes"),
  value = c(
    dw_result$dimensions,
    1,  # linear model
    dw_result$beta,
    dw_result$weights[2],
    length(rc_list),
    nrow(legislators) / length(rc_list),  # Legisladores por período
    ncol(rc_list[[1]]$votes) + ncol(rc_list[[2]]$votes) + ncol(rc_list[[3]]$votes) + 
      ncol(rc_list[[4]]$votes) + ncol(rc_list[[5]]$votes) + ncol(rc_list[[6]]$votes)
  )
)

write.csv(
  model_info,
  file.path(output_dir, "model_info_6periods.csv"),
  row.names = FALSE
)
cat("   ✅ model_info_6periods.csv\n")

# Crear visualización
cat("\n📊 Creando visualización...\n")

# Crear directorio de resultados si no existe
results_dir <- "../../results"
if (!dir.exists(results_dir)) {
  dir.create(results_dir, recursive = TRUE)
}

png(file.path(results_dir, "dwnominate_results_6periods.png"), width = 1200, height = 800, res = 150)
plot(dw_result)
dev.off()

cat("   ✅ dwnominate_results_6periods.png\n")

# Estadísticas resumen
cat("\n=== RESUMEN DEL ANÁLISIS ===\n")
cat("Total de legisladores: ", nrow(dw_result$legislators), "\n")
cat("Total de períodos: ", length(rc_list), "\n")
cat("Tipo de modelo: Linear (model=1)\n")
cat("Dimensiones: 2\n")
cat("Iteraciones: 4\n")

cat("\n")
cat("===============================================\n")
cat("  ANÁLISIS COMPLETADO                         \n")
cat("===============================================\n")
cat("\n")

cat("📁 Archivos generados en:", output_dir, "\n")
cat("   • dw_nominate_result_6periods.rds (objeto R completo)\n")
cat("   • dwnominate_coordinates_all_periods_6p.csv (todos los períodos)\n")
cat("   • coordinates_P1_6periods.csv ... P6_6periods.csv (por período)\n")
cat("   • dwnominate_bill_parameters_6periods.csv (parámetros de votaciones)\n")
cat("   • model_info_6periods.csv (información del modelo)\n")

cat("\n📊 Parámetros del modelo:\n")
cat("   • Beta:", round(dw_result$beta, 4), "\n")
cat("   • Peso Dim 2:", round(dw_result$weights[2], 4), "\n")
cat("   • Dimensiones:", dw_result$dimensions, "\n")

cat("\n🚀 SIGUIENTE PASO:\n")
cat("   1. Corregir polaridad (si es necesario):\n")
cat("      Rscript correct_polarity_dwnominate_6periods.R\n")
cat("   2. Generar visualizaciones:\n")
cat("      python ../../src/csv_dwnominate_graph_6periods.py\n")

cat("\n")
cat("===============================================\n\n")
