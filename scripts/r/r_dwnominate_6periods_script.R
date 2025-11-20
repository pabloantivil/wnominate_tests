# DW-NOMINATE Analysis - 6 Political Periods
# 55º Período Legislativo (2018-2022)
# Divided based on major Chilean political events
# Generated automatically

cat("\n")
cat("===============================================\n")
cat("  DW-NOMINATE - 6 Political Periods          \n")
cat("  55º PL (2018-2022) - Chile                 \n")
cat("===============================================\n")
cat("\n")

# Install required packages
if (!require(pscl)) {
  cat("📦 Installing pscl...\n")
  install.packages("pscl")
}
if (!require(dplyr)) {
  cat("📦 Installing dplyr...\n")
  install.packages("dplyr")
}
if (!require(dwnominate)) {
  cat("📦 Installing dwnominate...\n")
  install.packages("remotes")
  remotes::install_github("wmay/dwnominate")
}

library(pscl)
library(dplyr)
library(dwnominate)

cat("\n✅ All packages loaded\n\n")

# Load metadata
legislator_meta <- read.csv("../../data/dwnominate_6periods/input/legislator_metadata.csv")
vote_meta <- read.csv("../../data/dwnominate_6periods/input/vote_metadata.csv")

cat("📊 Metadata loaded:\n")
cat("   Legislators: ", nrow(legislator_meta), "\n")
cat("   Votes: ", nrow(vote_meta), "\n\n")

cat("📅 Loading 6 political periods...\n\n")

# Storage for rollcall objects
rc_list <- list()

# PERIOD 1: Inicio PL - Primera Mitad
# Marzo 2018 - Septiembre 2018 (Pre-Estallido, Parte 1)
# Context: Inicio del gobierno de Sebastián Piñera (2º mandato)
votes_p1a <- read.csv("../../data/dwnominate_6periods/input/votes_matrix_p1a.csv", row.names = 1)
votes_mat_p1a <- as.matrix(votes_p1a)

period_legislators_p1a <- rownames(votes_mat_p1a)
legis_data_p1a <- data.frame(
  legislator_id = as.integer(period_legislators_p1a),
  row.names = period_legislators_p1a,
  stringsAsFactors = FALSE
)
legis_data_p1a <- legis_data_p1a %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = "legislator_id"
  )
legis_data_p1a$party <- ifelse(is.na(legis_data_p1a$partido), "IND", legis_data_p1a$partido)
rownames(legis_data_p1a) <- period_legislators_p1a

rc_p1a <- rollcall(
  data = votes_mat_p1a,
  yea = 1,
  nay = 0,
  missing = NA,
  notInLegis = 9,
  legis.names = rownames(votes_mat_p1a),
  vote.names = colnames(votes_mat_p1a),
  desc = "Inicio PL - Primera Mitad",
  legis.data = legis_data_p1a
)
cat(
  "✅ Inicio PL - Primera Mitad: ", nrow(rc_p1a$votes), " legislators x ",
  ncol(rc_p1a$votes), " votes\n"
)
rc_list[[1]] <- rc_p1a

# PERIOD 2: Inicio PL - Segunda Mitad
# Octubre 2018 - Octubre 2019 (Pre-Estallido, Parte 2)
# Context: Período previo al estallido social
votes_p1b <- read.csv("../../data/dwnominate_6periods/input/votes_matrix_p1b.csv", row.names = 1)
votes_mat_p1b <- as.matrix(votes_p1b)

period_legislators_p1b <- rownames(votes_mat_p1b)
legis_data_p1b <- data.frame(
  legislator_id = as.integer(period_legislators_p1b),
  row.names = period_legislators_p1b,
  stringsAsFactors = FALSE
)
legis_data_p1b <- legis_data_p1b %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = "legislator_id"
  )
legis_data_p1b$party <- ifelse(is.na(legis_data_p1b$partido), "IND", legis_data_p1b$partido)
rownames(legis_data_p1b) <- period_legislators_p1b

rc_p1b <- rollcall(
  data = votes_mat_p1b,
  yea = 1,
  nay = 0,
  missing = NA,
  notInLegis = 9,
  legis.names = rownames(votes_mat_p1b),
  vote.names = colnames(votes_mat_p1b),
  desc = "Inicio PL - Segunda Mitad",
  legis.data = legis_data_p1b
)
cat(
  "✅ Inicio PL - Segunda Mitad: ", nrow(rc_p1b$votes), " legislators x ",
  ncol(rc_p1b$votes), " votes\n"
)
rc_list[[2]] <- rc_p1b

# PERIOD 3: Estallido Social - Primera Mitad
# Octubre 2019 - Abril 2020 (Estallido y COVID-19)
# Context: Estallido social y llegada de la pandemia
votes_p2a <- read.csv("../../data/dwnominate_6periods/input/votes_matrix_p2a.csv", row.names = 1)
votes_mat_p2a <- as.matrix(votes_p2a)

period_legislators_p2a <- rownames(votes_mat_p2a)
legis_data_p2a <- data.frame(
  legislator_id = as.integer(period_legislators_p2a),
  row.names = period_legislators_p2a,
  stringsAsFactors = FALSE
)
legis_data_p2a <- legis_data_p2a %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = "legislator_id"
  )
legis_data_p2a$party <- ifelse(is.na(legis_data_p2a$partido), "IND", legis_data_p2a$partido)
rownames(legis_data_p2a) <- period_legislators_p2a

rc_p2a <- rollcall(
  data = votes_mat_p2a,
  yea = 1,
  nay = 0,
  missing = NA,
  notInLegis = 9,
  legis.names = rownames(votes_mat_p2a),
  vote.names = colnames(votes_mat_p2a),
  desc = "Estallido Social - Primera Mitad",
  legis.data = legis_data_p2a
)
cat(
  "✅ Estallido Social - Primera Mitad: ", nrow(rc_p2a$votes), " legislators x ",
  ncol(rc_p2a$votes), " votes\n"
)
rc_list[[3]] <- rc_p2a

# PERIOD 4: Estallido Social - Segunda Mitad
# Abril 2020 - Octubre 2020 (Pandemia y Acuerdo por la Paz)
# Context: Pandemia COVID-19 y preparación del plebiscito
votes_p2b <- read.csv("../../data/dwnominate_6periods/input/votes_matrix_p2b.csv", row.names = 1)
votes_mat_p2b <- as.matrix(votes_p2b)

period_legislators_p2b <- rownames(votes_mat_p2b)
legis_data_p2b <- data.frame(
  legislator_id = as.integer(period_legislators_p2b),
  row.names = period_legislators_p2b,
  stringsAsFactors = FALSE
)
legis_data_p2b <- legis_data_p2b %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = "legislator_id"
  )
legis_data_p2b$party <- ifelse(is.na(legis_data_p2b$partido), "IND", legis_data_p2b$partido)
rownames(legis_data_p2b) <- period_legislators_p2b

rc_p2b <- rollcall(
  data = votes_mat_p2b,
  yea = 1,
  nay = 0,
  missing = NA,
  notInLegis = 9,
  legis.names = rownames(votes_mat_p2b),
  vote.names = colnames(votes_mat_p2b),
  desc = "Estallido Social - Segunda Mitad",
  legis.data = legis_data_p2b
)
cat(
  "✅ Estallido Social - Segunda Mitad: ", nrow(rc_p2b$votes), " legislators x ",
  ncol(rc_p2b$votes), " votes\n"
)
rc_list[[4]] <- rc_p2b

# PERIOD 5: Post-Plebiscito - Primera Mitad
# Octubre 2020 - Agosto 2021 (Constitución y Elecciones)
# Context: Plebiscito aprueba nueva constitución, Convención Constituyente
votes_p3a <- read.csv("../../data/dwnominate_6periods/input/votes_matrix_p3a.csv", row.names = 1)
votes_mat_p3a <- as.matrix(votes_p3a)

period_legislators_p3a <- rownames(votes_mat_p3a)
legis_data_p3a <- data.frame(
  legislator_id = as.integer(period_legislators_p3a),
  row.names = period_legislators_p3a,
  stringsAsFactors = FALSE
)
legis_data_p3a <- legis_data_p3a %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = "legislator_id"
  )
legis_data_p3a$party <- ifelse(is.na(legis_data_p3a$partido), "IND", legis_data_p3a$partido)
rownames(legis_data_p3a) <- period_legislators_p3a

rc_p3a <- rollcall(
  data = votes_mat_p3a,
  yea = 1,
  nay = 0,
  missing = NA,
  notInLegis = 9,
  legis.names = rownames(votes_mat_p3a),
  vote.names = colnames(votes_mat_p3a),
  desc = "Post-Plebiscito - Primera Mitad",
  legis.data = legis_data_p3a
)
cat(
  "✅ Post-Plebiscito - Primera Mitad: ", nrow(rc_p3a$votes), " legislators x ",
  ncol(rc_p3a$votes), " votes\n"
)
rc_list[[5]] <- rc_p3a

# PERIOD 6: Post-Plebiscito - Segunda Mitad
# Agosto 2021 - Marzo 2022 (Elecciones Presidenciales)
# Context: Elecciones presidenciales y fin del período legislativo
votes_p3b <- read.csv("../../data/dwnominate_6periods/input/votes_matrix_p3b.csv", row.names = 1)
votes_mat_p3b <- as.matrix(votes_p3b)

period_legislators_p3b <- rownames(votes_mat_p3b)
legis_data_p3b <- data.frame(
  legislator_id = as.integer(period_legislators_p3b),
  row.names = period_legislators_p3b,
  stringsAsFactors = FALSE
)
legis_data_p3b <- legis_data_p3b %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = "legislator_id"
  )
legis_data_p3b$party <- ifelse(is.na(legis_data_p3b$partido), "IND", legis_data_p3b$partido)
rownames(legis_data_p3b) <- period_legislators_p3b

rc_p3b <- rollcall(
  data = votes_mat_p3b,
  yea = 1,
  nay = 0,
  missing = NA,
  notInLegis = 9,
  legis.names = rownames(votes_mat_p3b),
  vote.names = colnames(votes_mat_p3b),
  desc = "Post-Plebiscito - Segunda Mitad",
  legis.data = legis_data_p3b
)
cat(
  "✅ Post-Plebiscito - Segunda Mitad: ", nrow(rc_p3b$votes), " legislators x ",
  ncol(rc_p3b$votes), " votes\n"
)
rc_list[[6]] <- rc_p3b



cat("\n✅ All 6 periods loaded successfully\n")
cat("📋 Rollcall list contains ", length(rc_list), " periods\n\n")

# Set polarity anchors
cat("🎯 Setting polarity anchors...\n")

# Find legislators in ALL periods
all_period_legislators <- list()
for (i in 1:6) {
  all_period_legislators[[i]] <- rownames(rc_list[[i]]$votes)
}

common_legislators <- Reduce(intersect, all_period_legislators)
cat("   Legislators in ALL 6 periods: ", length(common_legislators), "\n")

# Chilean political spectrum anchors
left_parties <- c("PC", "PS")
right_parties <- c("UDI", "RN")

left_legislators <- legislator_meta$legislator_id[legislator_meta$partido %in% left_parties]
right_legislators <- legislator_meta$legislator_id[legislator_meta$partido %in% right_parties]

# Find left-wing legislator in common set
left_in_common <- left_legislators[as.character(left_legislators) %in% common_legislators]

if (length(left_in_common) > 0) {
  polarity_anchor <- as.character(left_in_common[1])
  anchor_info <- legislator_meta[legislator_meta$legislator_id == as.integer(polarity_anchor), ]
  cat(
    "   Polarity anchor: ", polarity_anchor, " (",
    anchor_info$partido[1], " - ", anchor_info$nombres[1], ")\n\n"
  )
} else {
  polarity_anchor <- common_legislators[1]
  cat("   Fallback polarity anchor: ", polarity_anchor, "\n\n")
}

cat("🚀 Running DW-NOMINATE (6 periods)...\n")
cat("   This may take several minutes.\n\n")

# Run DW-NOMINATE
dw_result <- dwnominate(
  rc_list,
  id = "legislator_id",
  dims = 2,
  model = 1, # Linear change over time
  polarity = polarity_anchor,
  minvotes = 10, # Reducido para períodos más cortos
  lop = 0.025, # Lopsided vote threshold (2.5%)
  niter = 20, # Aumentado de 4 a 20 para mejor convergencia
  beta = 5.9539,
  w = 0.3463,
  verbose = TRUE
)

cat("\n✅ DW-NOMINATE estimation complete!\n\n")

# Print summary
cat("\n=== DW-NOMINATE RESULTS ===\n")
print(summary(dw_result))

# Extract coordinates
legislators <- dw_result$legislators %>%
  rename(
    legislator = ID,
    period = session
  ) %>%
  mutate(legislator = as.integer(legislator))

# Add metadata
legislators <- legislators %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = c("legislator" = "legislator_id")
  )

# Create output directory
output_dir <- "../../data/dwnominate_6periods/output"
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# Save combined results
cat("\n💾 Saving results...\n")
write.csv(legislators, file.path(output_dir, "dwnominate_coordinates_all_periods.csv"), row.names = FALSE)
cat("   ✅ dwnominate_coordinates_all_periods.csv\n")

# Save period-specific files
cat("\n💾 Saving period-specific coordinates...\n")
for (i in 1:6) {
  period_coords <- legislators %>%
    filter(period == i) %>%
    select(legislator, period, coord1D, coord2D, se1D, se2D, nombres, partido, region, distrito)

  period_id <- c("P1a", "P1b", "P2a", "P2b", "P3a", "P3b")[i]
  output_file <- file.path(output_dir, paste0("coordinates_", period_id, "_6periods.csv"))
  write.csv(period_coords, output_file, row.names = FALSE)
  cat("   ✅ ", basename(output_file), " (", nrow(period_coords), " legislators)\n")
}

# Save bill parameters
cat("\n💾 Saving bill parameters...\n")
write.csv(dw_result$rollcalls, file.path(output_dir, "dwnominate_bill_parameters.csv"), row.names = FALSE)
cat("   ✅ dwnominate_bill_parameters.csv\n")

# Create visualization
cat("\n📊 Creating visualization...\n")
results_dir <- "../../results"
if (!dir.exists(results_dir)) {
  dir.create(results_dir, recursive = TRUE)
}

png(file.path(results_dir, "dwnominate_6periods.png"), width = 1200, height = 800, res = 150)
plot(dw_result)
title(main = "DW-NOMINATE - 6 Political Periods\n55º PL Chile (2018-2022)", line = 0.5)
dev.off()
cat("   ✅ dwnominate_6periods.png\n")

# Summary
cat("\n=== ANALYSIS COMPLETE ===\n")
cat("Legislators analyzed: ", length(unique(legislators$legislator)), "\n")
cat("Total periods: 6\n")
cat("Model: Linear (model=1)\n")
cat("Dimensions: 2\n")

cat("\n✅ Analysis complete!\n")
cat("📂 Output: data/dwnominate_6periods/output/\n")
cat("💡 Next: Run correct_polarity_dwnominate_6periods.R\n\n")
