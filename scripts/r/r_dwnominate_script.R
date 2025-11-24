# DW-NOMINATE Analysis Script for Chilean Congressional Data
# 55th Legislative Period (2018-2022) divided into 5 periods
# Generated automatically from CSV files

cat("\n")
cat("===============================================\n")
cat("  DW-NOMINATE Analysis - Chilean Congress     \n")
cat("  55th Legislative Period (2018-2022)         \n")
cat("===============================================\n")
cat("\n")

# Install required packages if not already installed
if (!require(pscl)) {
  cat("Installing pscl package...\n")
  install.packages("pscl")
}
if (!require(dplyr)) {
  cat("Installing dplyr package...\n")
  install.packages("dplyr")
}
if (!require(dwnominate)) {
  cat("Installing dwnominate package...\n")
  install.packages("remotes")
  remotes::install_github("wmay/dwnominate")
}

library(pscl)
library(dplyr)
library(dwnominate)

cat("\nAll packages loaded successfully\n\n")

# Load metadata from data/dwnominate/input
legislator_meta <- read.csv("../../data/dwnominate/input/legislator_metadata.csv")
vote_meta <- read.csv("../../data/dwnominate/input/vote_metadata.csv")

cat("Metadata loaded:\n")
cat("   Legislators: ", nrow(legislator_meta), "\n")
cat("   Votes: ", nrow(vote_meta), "\n\n")

cat("Loading vote matrices for each period...\n\n")
# Storage for rollcall objects
rc_list <- list()

# PERIOD 1: Año 2018
votes_p1 <- read.csv("../../data/dwnominate/input/votes_matrix_p1.csv", row.names = 1)
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
  desc = "Año 2018",
  legis.data = legis_data_p1
)
cat(
  "Año 2018: ", nrow(rc_p1$votes), " legislators x ",
  ncol(rc_p1$votes), " votes\n"
)
rc_list[[1]] <- rc_p1

# PERIOD 2: Año 2019
votes_p2 <- read.csv("../../data/dwnominate/input/votes_matrix_p2.csv", row.names = 1)
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
  desc = "Año 2019",
  legis.data = legis_data_p2
)
cat(
  "Año 2019: ", nrow(rc_p2$votes), " legislators x ",
  ncol(rc_p2$votes), " votes\n"
)
rc_list[[2]] <- rc_p2

# PERIOD 3: 2020 Semestre 1
votes_p3 <- read.csv("../../data/dwnominate/input/votes_matrix_p3.csv", row.names = 1)
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
  "2020 Semestre 1: ", nrow(rc_p3$votes), " legislators x ",
  ncol(rc_p3$votes), " votes\n"
)
rc_list[[3]] <- rc_p3

# PERIOD 4: 2020 Semestre 2
votes_p4 <- read.csv("../../data/dwnominate/input/votes_matrix_p4.csv", row.names = 1)
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
  "2020 Semestre 2: ", nrow(rc_p4$votes), " legislators x ",
  ncol(rc_p4$votes), " votes\n"
)
rc_list[[4]] <- rc_p4

# PERIOD 5: Año 2021
votes_p5 <- read.csv("../../data/dwnominate/input/votes_matrix_p5.csv", row.names = 1)
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
  desc = "Año 2021",
  legis.data = legis_data_p5
)
cat(
  "Año 2021: ", nrow(rc_p5$votes), " legislators x ",
  ncol(rc_p5$votes), " votes\n"
)
rc_list[[5]] <- rc_p5


cat("\nAll periods loaded successfully\n\n")
cat("Rollcall list contains ", length(rc_list), " periods\n\n")

# Set polarity anchors based on Chilean political spectrum
cat("Setting polarity anchors...\n")

# Find legislators present in ALL periods for consistent polarity
all_period_legislators <- list()
for (i in 1:5) {
  all_period_legislators[[i]] <- rownames(rc_list[[i]]$votes)
}

common_legislators <- Reduce(intersect, all_period_legislators)
cat("   Legislators present in ALL 5 periods: ", length(common_legislators), "\n")

# For Chilean politics:
# Left-wing parties (should be negative): PC, PS
# Right-wing parties (should be positive): UDI, RN

right_parties <- c("UDI", "RN")
left_parties <- c("PC", "PS")

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
  # Fallback
  polarity_anchor <- common_legislators[1]
  cat("   Using fallback polarity anchor: ", polarity_anchor, "\n\n")
}

cat("Running DW-NOMINATE...\n")
cat("   This may take several minutes depending on data size.\n\n")

# Run DW-NOMINATE with id parameter
dw_result <- dwnominate(
  rc_list,
  id = "legislator_id", # CRÍTICO: identificador único de legisladores
  dims = 2, # 2 dimensions
  model = 1,
  polarity = polarity_anchor,
  minvotes = 5, # Minimum votes for a legislator to be included
  lop = 0.025, # Lopsided vote threshold (restaurado a valor estándar)
  niter = 4, # 4 iterations (usually sufficient)
  beta = 5.9539, # Spatial error parameter (default)
  w = 0.3463, # Second dimension weight (default)
  verbose = TRUE
)

cat("\nDW-NOMINATE estimation complete!\n\n")

# Print summary
cat("\n=== DW-NOMINATE RESULTS SUMMARY ===\n")
print(summary(dw_result))

# Extract legislator coordinates
legislators <- dw_result$legislators

# Rename columns to match our expected names
legislators <- legislators %>%
  rename(
    legislator = ID,
    period = session
  ) %>%
  mutate(
    legislator = as.integer(legislator)
  )

# Add metadata
legislators <- legislators %>%
  left_join(
    legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
    by = c("legislator" = "legislator_id")
  )

# Save full results
cat("\nSaving coordinates for all periods combined...\n")

# Crear directorio de salida si no existe
output_dir <- "../../data/dwnominate/output"
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

write.csv(legislators, file.path(output_dir, "dwnominate_coordinates_all_periods.csv"), row.names = FALSE)
cat(" dwnominate_coordinates_all_periods.csv (", nrow(legislators), " rows)\n")

# Save period-specific files
cat("\nSaving coordinates for each period...\n")
for (i in 1:5) {
  period_coords <- legislators %>%
    filter(period == i) %>%
    select(legislator, period, coord1D, coord2D, se1D, se2D, nombres, partido, region, distrito)

  output_file <- file.path(output_dir, paste0("dwnominate_coordinates_p", i, ".csv"))
  write.csv(period_coords, output_file, row.names = FALSE)
  cat("", basename(output_file), " (", nrow(period_coords), " legislators)\n")
}

# Also save bill/vote parameters
cat("\nSaving bill parameters...\n")
write.csv(dw_result$rollcalls, file.path(output_dir, "dwnominate_bill_parameters.csv"), row.names = FALSE)
cat("   dwnominate_bill_parameters.csv\n")

# Plot results
cat("\nCreating visualization...\n")

# Crear directorio de resultados si no existe
results_dir <- "../../results"
if (!dir.exists(results_dir)) {
  dir.create(results_dir, recursive = TRUE)
}

png(file.path(results_dir, "dwnominate_results.png"), width = 1200, height = 800, res = 150)
plot(dw_result)
dev.off()

cat("   dwnominate_results.png\n")
# Summary statistics
cat("\n=== ANALYSIS SUMMARY ===\n")
cat("Total legislators: ", nrow(dw_result$legislators), "\n")
cat("Total periods: ", length(rc_list), "\n")
cat("Model type: Linear (model=1)\n")
cat("Dimensions: 2\n")
cat("Iterations: 4\n")

cat("\nDW-NOMINATE analysis complete!\n\n")
cat("Output files:\n")
cat("   • dwnominate_coordinates_p1.csv through p5.csv (period-specific)\n")
cat("   • dwnominate_coordinates_all_periods.csv (combined)\n")
cat("   • dwnominate_bill_parameters.csv\n")
cat("   • dwnominate_results.png\n\n")
