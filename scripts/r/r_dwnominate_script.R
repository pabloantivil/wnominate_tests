# DW-NOMINATE Analysis Script for Chilean Congressional Data (5 PERIODS)
# Analyzes ideological changes across FIVE political periods (P1-P5)
# This allows using MODEL 1 (linear change) which requires 5+ periods

# =============================================================================
# INSTALLATION & SETUP
# =============================================================================

# Install required packages if not already installed
if (!require(pscl)) install.packages("pscl")
if (!require(dplyr)) install.packages("dplyr")
if (!require(ggplot2)) install.packages("ggplot2")
if (!require(tidyr)) install.packages("tidyr")

# Install dwnominate from GitHub (requires Rtools on Windows, gfortran on Mac/Linux)
if (!require(dwnominate)) {
    if (!require(remotes)) install.packages("remotes")
    remotes::install_github("wmay/dwnominate")
}

library(pscl)
library(dwnominate)
library(dplyr)
library(ggplot2)
library(tidyr)

# =============================================================================
# LOAD DATA FOR FIVE PERIODS
# =============================================================================

cat("\n=== LOADING DATA FOR DW-NOMINATE (5 PERIODS) ===\n")

# Load legislator metadata (shared across all periods)
legislator_meta <- read.csv("legislator_metadata.csv")
cat("✅ Loaded metadata for", nrow(legislator_meta), "legislators\n")

# Load period-specific data
periods <- c("p1", "p2", "p3", "p4", "p5")
period_names <- c(
    "Período 1",
    "Período 2",
    "Período 3 (Estallido)",
    "Período 4 (Pandemia)",
    "Período 5 (Post-Plebiscito)"
)
period_dates <- c(
    "2018-03-11 to 2018-11-01",
    "2018-11-01 to 2019-06-20",
    "2019-06-20 to 2020-02-10",
    "2020-02-10 to 2020-10-01",
    "2020-10-01 to 2022-03-10"
)

# Storage for rollcall objects
rc_list <- list()

for (i in 1:length(periods)) {
    period <- periods[i]
    period_name <- period_names[i]

    cat(sprintf("\n📂 Loading Period %d (%s)...\n", i, period_name))

    # Load votes matrix for this period
    votes_matrix_file <- sprintf("votes_matrix_%s.csv", period)

    if (!file.exists(votes_matrix_file)) {
        cat(sprintf("❌ ERROR: File not found: %s\n", votes_matrix_file))
        cat("   Please run prepare_dwnominate_5periods.py first!\n")
        stop("Missing data files")
    }

    votes_matrix <- read.csv(votes_matrix_file, row.names = 1)
    votes_mat <- as.matrix(votes_matrix)

    cat(sprintf("   Dimensions: %d legislators x %d votes\n", nrow(votes_mat), ncol(votes_mat)))

    # Load vote metadata for this period
    vote_meta_file <- sprintf("vote_metadata_%s.csv", period)
    vote_meta <- read.csv(vote_meta_file)

    # Create legislator data frame with metadata
    period_legislators <- rownames(votes_mat)
    legis_data <- data.frame(
        legislator_id = as.integer(period_legislators),
        row.names = period_legislators,
        stringsAsFactors = FALSE
    )

    # Add party information from metadata
    legis_data <- legis_data %>%
        left_join(
            legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
            by = "legislator_id"
        )

    # Create 'party' column for rollcall() function
    # Use partido (Spanish) but create party (English) column as well
    # Fill missing values with "IND" to avoid errors
    legis_data$party <- ifelse(is.na(legis_data$partido), "IND", legis_data$partido)

    # Ensure row names are preserved
    rownames(legis_data) <- period_legislators

    # Create rollcall object for this period
    rc <- rollcall(
        data = votes_mat,
        yea = 1, # "Sí" votes
        nay = 0, # "No" votes
        missing = NA, # True missing
        notInLegis = 9, # Abstentions, absences, etc.
        legis.names = rownames(votes_mat),
        vote.names = colnames(votes_mat),
        desc = sprintf("Chilean Congressional Votes - Period %d (%s)", i, period_name),
        legis.data = legis_data,
        vote.data = vote_meta
    )

    # Add to list
    rc_list[[i]] <- rc

    cat(sprintf("   ✅ Created rollcall object for Period %d\n", i))
}

cat("\n=== ROLLCALL OBJECTS CREATED ===\n")
cat(sprintf("Total periods: %d\n", length(rc_list)))

# Print summaries
for (i in 1:length(rc_list)) {
    cat(sprintf("\nPeriod %d (%s, %s):\n", i, period_names[i], period_dates[i]))
    print(summary(rc_list[[i]]))
}

# =============================================================================
# POLARITY ANCHOR SELECTION
# =============================================================================

cat("\n=== POLARITY ANCHOR SELECTION ===\n")

# Find legislators present in ALL periods for consistent polarity
# Extract legislator IDs from each period
all_period_legislators <- list()
for (i in 1:5) {
    all_period_legislators[[i]] <- rownames(rc_list[[i]]$votes)
}

# Find legislators in all periods
common_legislators <- Reduce(intersect, all_period_legislators)
cat(sprintf("Legislators present in ALL 5 periods: %d\n", length(common_legislators)))

# Find polarity anchor from common legislators
# We want a left-wing anchor (PC or PS) who appears in all periods
if ("partido" %in% colnames(legislator_meta)) {
    cat("\nSearching for polarity anchor (left-wing party member in all periods)...\n")

    # Left-wing parties (should have POSITIVE coordinates in Chilean spectrum)
    left_parties <- c("PC", "PS", "PPD")

    # Find left-wing legislators in common set
    left_legislators <- legislator_meta$legislator_id[
        legislator_meta$legislator_id %in% common_legislators &
            legislator_meta$partido %in% left_parties
    ]

    if (length(left_legislators) > 0) {
        # Use first left-wing legislator as anchor
        polarity_anchor <- as.character(left_legislators[1])
        anchor_info <- legislator_meta[legislator_meta$legislator_id == polarity_anchor, ]

        cat(sprintf(
            "✅ Polarity anchor: %s (%s, %s)\n",
            polarity_anchor,
            anchor_info$nombres,
            anchor_info$partido
        ))
        cat("   This legislator will have a POSITIVE coordinate on Dimension 1\n")
        cat("   (Economic dimension: Left=Positive, Right=Negative in Chilean context)\n")
    } else {
        # Fallback: use first common legislator
        polarity_anchor <- common_legislators[1]
        cat(sprintf("⚠️  Using fallback polarity anchor: %s\n", polarity_anchor))
    }
} else {
    # No party data, use first common legislator
    polarity_anchor <- common_legislators[1]
    cat(sprintf("⚠️  No party data available. Using legislator: %s\n", polarity_anchor))
}

# =============================================================================
# RUN DW-NOMINATE WITH MODEL 1 (LINEAR)
# =============================================================================

cat("\n=== RUNNING DW-NOMINATE ===\n")
cat("This may take several minutes...\n\n")

# With 5 periods, we can use model=1 (linear change over time)!
# This is the recommended model for DW-NOMINATE

cat("Running DW-NOMINATE with MODEL 1 (Linear change)...\n")
cat("✅ With 5 periods, we can use the linear model to detect trends!\n\n")

dw_result <- dwnominate(
    rc_list = rc_list,
    id = "legislator_id", # Column in legis.data with unique IDs
    dims = 2, # 2 dimensions
    model = 1, # Linear change over time ⭐ NOW ENABLED
    niter = 4, # Number of iterations (4 is usually sufficient)
    polarity = polarity_anchor, # Polarity anchor
    verbose = TRUE # Show progress
)

cat("\n=== DW-NOMINATE RESULTS ===\n")
print(summary(dw_result))

# =============================================================================
# EXTRACT AND SAVE RESULTS
# =============================================================================

cat("\n=== EXTRACTING RESULTS ===\n")

# Extract legislator coordinates (includes all periods)
legislators <- dw_result$legislators

cat(sprintf("DW-NOMINATE results: %d rows (legislator-period combinations)\n", nrow(legislators)))
cat(sprintf("Legislator metadata: %d unique legislators\n", nrow(legislator_meta)))

# First, let's check the actual column names in the legislators dataframe
cat("\nColumn names in legislators dataframe:\n")
print(names(legislators))

# Rename columns to match our expected names
# DW-NOMINATE returns: ID, session, party, name, coord1D, coord2D, etc.
legislators <- legislators %>%
    rename(
        legislator = ID, # Legislator ID
        period = session # Time period (1-5)
    ) %>%
    mutate(
        legislator = as.integer(legislator) # Convert to integer for join
    )

cat("✅ Renamed 'ID' → 'legislator' and 'session' → 'period'\n")
cat("✅ Converted 'legislator' to integer for joining\n")

# Add metadata - use left_join to preserve all DW-NOMINATE results
# Note: DW-NOMINATE already includes a 'party' column, but we want full metadata
legislators <- legislators %>%
    left_join(
        legislator_meta %>% select(legislator_id, partido, nombres, region, distrito),
        by = c("legislator" = "legislator_id")
    )

# Check for missing metadata
missing_meta <- sum(is.na(legislators$partido))
if (missing_meta > 0) {
    cat(sprintf("⚠️  Warning: %d legislator-period entries missing metadata\n", missing_meta))
}

# Save full results
write.csv(legislators, "dwnominate_5p_coordinates_all_periods.csv", row.names = FALSE)
cat("💾 Saved: dwnominate_5p_coordinates_all_periods.csv\n")

# Save rollcall results
rollcalls <- dw_result$rollcalls
write.csv(rollcalls, "dwnominate_5p_bill_parameters.csv", row.names = FALSE)
cat("💾 Saved: dwnominate_5p_bill_parameters.csv\n")

# Create period-specific coordinate files for easier analysis
for (i in 1:5) {
    period_coords <- legislators %>%
        filter(period == i) %>%
        select(legislator, period, coord1D, coord2D, se1D, se2D, nombres, partido, region, distrito)

    filename <- sprintf("dwnominate_5p_coordinates_p%d.csv", i)
    write.csv(period_coords, filename, row.names = FALSE)
    cat(sprintf("💾 Saved: %s (%d legislators)\n", filename, nrow(period_coords)))
}

# =============================================================================
# ANALYZE IDEOLOGICAL CHANGES
# =============================================================================

cat("\n=== ANALYZING IDEOLOGICAL CHANGES ===\n")

# For legislators present in all 5 periods, calculate shifts
legislators_wide <- legislators %>%
    filter(legislator %in% common_legislators) %>%
    select(legislator, period, coord1D, coord2D, partido, nombres) %>%
    tidyr::pivot_wider(
        id_cols = c(legislator, partido, nombres),
        names_from = period,
        values_from = c(coord1D, coord2D),
        names_prefix = "P"
    )

# Calculate changes across different time spans
legislators_wide <- legislators_wide %>%
    mutate(
        # Sequential changes
        shift_P1_P2 = coord1D_P2 - coord1D_P1,
        shift_P2_P3 = coord1D_P3 - coord1D_P2, # Into Estallido Social
        shift_P3_P4 = coord1D_P4 - coord1D_P3, # Estallido to Pandemia
        shift_P4_P5 = coord1D_P5 - coord1D_P4, # Pandemia to Post-Plebiscito

        # Major period changes
        shift_P1_P3 = coord1D_P3 - coord1D_P1, # Pre-Estallido to Estallido
        shift_P3_P5 = coord1D_P5 - coord1D_P3, # Estallido to Post-Plebiscito
        shift_P1_P5 = coord1D_P5 - coord1D_P1, # Total change

        abs_shift_total = abs(shift_P1_P5)
    )

# Save shifts analysis
write.csv(legislators_wide, "dwnominate_5p_ideological_shifts.csv", row.names = FALSE)
cat("💾 Saved: dwnominate_5p_ideological_shifts.csv\n")

# Find legislators with largest shifts
cat("\nLegislators with LARGEST ideological shifts (Dimension 1, P1→P5):\n")
top_shifters <- legislators_wide %>%
    arrange(desc(abs_shift_total)) %>%
    head(10) %>%
    select(nombres, partido, coord1D_P1, coord1D_P5, shift_P1_P5)

print(top_shifters)

# Average shift by party
cat("\nAverage ideological shift by party (P1→P5):\n")
party_shifts <- legislators_wide %>%
    group_by(partido) %>%
    summarize(
        n = n(),
        avg_shift = mean(shift_P1_P5, na.rm = TRUE),
        sd_shift = sd(shift_P1_P5, na.rm = TRUE)
    ) %>%
    arrange(desc(abs(avg_shift)))

print(party_shifts)

# Analyze trend: Are movements linear?
cat("\nChecking for LINEAR trends in ideological movement:\n")
cat("If movements are linear, shifts should be consistent across periods.\n\n")

avg_sequential_shifts <- legislators_wide %>%
    summarize(
        avg_P1_P2 = mean(shift_P1_P2, na.rm = TRUE),
        avg_P2_P3 = mean(shift_P2_P3, na.rm = TRUE),
        avg_P3_P4 = mean(shift_P3_P4, na.rm = TRUE),
        avg_P4_P5 = mean(shift_P4_P5, na.rm = TRUE)
    )

print(avg_sequential_shifts)

# =============================================================================
# VISUALIZATIONS
# =============================================================================

cat("\n=== CREATING VISUALIZATIONS ===\n")

# 1. Standard DW-NOMINATE plot
cat("Creating standard DW-NOMINATE plot...\n")
png("dwnominate_5p_map_standard.png", width = 14, height = 10, units = "in", res = 300)
plot(dw_result, main = "Chilean Congressional DW-NOMINATE Map (5 Periods)")
dev.off()
cat("💾 Saved: dwnominate_5p_map_standard.png\n")

# 2. Separate plots for each period
for (i in 1:5) {
    period_data <- legislators %>% filter(period == i)

    p <- ggplot(period_data, aes(x = coord1D, y = coord2D, color = partido)) +
        geom_point(alpha = 0.7, size = 3) +
        geom_hline(yintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.7) +
        geom_vline(xintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.7) +
        labs(
            title = sprintf("Period %d: %s (%s)", i, period_names[i], period_dates[i]),
            x = "First Dimension (Economic: Left ← → Right)",
            y = "Second Dimension",
            color = "Party"
        ) +
        theme_minimal() +
        theme(
            legend.position = "bottom",
            plot.title = element_text(hjust = 0.5, size = 14, face = "bold")
        ) +
        xlim(-1, 1) +
        ylim(-1, 1) # Keep scale consistent

    filename <- sprintf("dwnominate_5p_map_period_%d.png", i)
    ggsave(filename, p, width = 10, height = 8, dpi = 300)
    cat(sprintf("💾 Saved: %s\n", filename))
}

# 3. Trajectory plot (show how legislators move over time)
cat("\nCreating ideological trajectory plot (5 periods)...\n")

# Get legislators with large total shifts
sample_legislators <- legislators_wide %>%
    arrange(desc(abs_shift_total)) %>%
    head(15) %>% # Top 15 shifters
    pull(legislator)

trajectory_data <- legislators %>%
    filter(legislator %in% sample_legislators) %>%
    arrange(legislator, period)

p_trajectory <- ggplot(trajectory_data, aes(x = coord1D, y = coord2D, group = legislator, color = partido)) +
    geom_path(arrow = arrow(length = unit(0.2, "cm")), alpha = 0.6, size = 0.8) +
    geom_point(aes(shape = as.factor(period)), size = 3, alpha = 0.8) +
    geom_hline(yintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.5) +
    geom_vline(xintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.5) +
    labs(
        title = "Ideological Trajectories: Top 15 Legislators with Largest Shifts",
        subtitle = "Arrows show movement from P1 → P2 → P3 → P4 → P5",
        x = "First Dimension (Economic: Left ← → Right)",
        y = "Second Dimension",
        color = "Party",
        shape = "Period"
    ) +
    scale_shape_manual(values = c(16, 17, 18, 15, 8), labels = c("P1", "P2", "P3", "P4", "P5")) +
    theme_minimal() +
    theme(
        legend.position = "right",
        plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
        plot.subtitle = element_text(hjust = 0.5, size = 10)
    ) +
    xlim(-1, 1) +
    ylim(-1, 1)

ggsave("dwnominate_5p_trajectories.png", p_trajectory, width = 14, height = 9, dpi = 300)
cat("💾 Saved: dwnominate_5p_trajectories.png\n")

# 4. Time series plot: Average coordinate by period
cat("\nCreating time series plot...\n")

time_series_data <- legislators %>%
    filter(legislator %in% common_legislators) %>%
    group_by(period, partido) %>% # Use 'partido' which is now in legislators after join
    summarize(
        mean_coord1D = mean(coord1D, na.rm = TRUE),
        se_coord1D = sd(coord1D, na.rm = TRUE) / sqrt(n()),
        .groups = "drop"
    )

p_timeseries <- ggplot(time_series_data, aes(x = period, y = mean_coord1D, color = partido, group = partido)) +
    geom_line(size = 1.2, alpha = 0.8) +
    geom_point(size = 3) +
    geom_errorbar(aes(ymin = mean_coord1D - se_coord1D, ymax = mean_coord1D + se_coord1D), width = 0.1) +
    labs(
        title = "Ideological Movement by Party (5 Periods)",
        subtitle = "Average Dimension 1 coordinate ± SE",
        x = "Period",
        y = "Average Coordinate (Left ← → Right)",
        color = "Party"
    ) +
    scale_x_continuous(breaks = 1:5, labels = c("P1", "P2", "P3\n(Estallido)", "P4\n(Pandemia)", "P5\n(Post-Pleb)")) +
    theme_minimal() +
    theme(
        legend.position = "right",
        plot.title = element_text(hjust = 0.5, size = 14, face = "bold")
    )

ggsave("dwnominate_5p_timeseries_by_party.png", p_timeseries, width = 12, height = 7, dpi = 300)
cat("💾 Saved: dwnominate_5p_timeseries_by_party.png\n")

# 5. Shift distribution histogram
p_shifts <- ggplot(legislators_wide, aes(x = shift_P1_P5)) +
    geom_histogram(bins = 30, fill = "steelblue", alpha = 0.7) +
    geom_vline(xintercept = 0, color = "red", linetype = "dashed", size = 1) +
    labs(
        title = "Distribution of Ideological Shifts (P1 to P5)",
        subtitle = sprintf("n = %d legislators present in all periods", nrow(legislators_wide)),
        x = "Change in Dimension 1 Coordinate (Positive = Shift Right)",
        y = "Count"
    ) +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5, size = 14, face = "bold"))

ggsave("dwnominate_5p_shift_distribution.png", p_shifts, width = 10, height = 6, dpi = 300)
cat("💾 Saved: dwnominate_5p_shift_distribution.png\n")

# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

cat("\n=== SUMMARY STATISTICS ===\n")

# Overall polarization by period
polarization <- legislators %>%
    group_by(period) %>%
    summarize(
        n = n(),
        mean_coord1D = mean(coord1D, na.rm = TRUE),
        sd_coord1D = sd(coord1D, na.rm = TRUE),
        mean_coord2D = mean(coord2D, na.rm = TRUE),
        sd_coord2D = sd(coord2D, na.rm = TRUE),
        polarization = sd(coord1D, na.rm = TRUE) # SD as measure of polarization
    )

cat("\nPolarization by period (SD of Dimension 1):\n")
print(polarization)

# Check polarization trends
cat("\n📊 Polarization Trends:\n")
for (i in 2:5) {
    if (polarization$polarization[i] > polarization$polarization[i - 1]) {
        cat(sprintf(
            "  P%d → P%d: INCREASED (%.4f → %.4f)\n",
            i - 1, i, polarization$polarization[i - 1], polarization$polarization[i]
        ))
    } else {
        cat(sprintf(
            "  P%d → P%d: DECREASED (%.4f → %.4f)\n",
            i - 1, i, polarization$polarization[i - 1], polarization$polarization[i]
        ))
    }
}

# =============================================================================
# FINAL SUMMARY
# =============================================================================

cat("\n", rep("=", 70), "\n", sep = "")
cat("DW-NOMINATE ANALYSIS COMPLETE (5 PERIODS, LINEAR MODEL)\n")
cat(rep("=", 70), "\n", sep = "")

cat("\n📊 Results Summary:\n")
cat(sprintf("  - Total legislators analyzed: %d\n", length(unique(legislators$legislator))))
cat(sprintf("  - Legislators in all 5 periods: %d\n", length(common_legislators)))
cat(sprintf("  - Average ideological shift (P1→P5): %.4f\n", mean(legislators_wide$shift_P1_P5, na.rm = TRUE)))
cat(sprintf("  - Max absolute shift: %.4f\n", max(legislators_wide$abs_shift_total, na.rm = TRUE)))

cat("\n💾 Files created:\n")
cat("  Coordinates:\n")
cat("    - dwnominate_5p_coordinates_all_periods.csv\n")
for (i in 1:5) {
    cat(sprintf("    - dwnominate_5p_coordinates_p%d.csv\n", i))
}
cat("  Analysis:\n")
cat("    - dwnominate_5p_ideological_shifts.csv\n")
cat("    - dwnominate_5p_bill_parameters.csv\n")
cat("  Visualizations:\n")
cat("    - dwnominate_5p_map_standard.png\n")
for (i in 1:5) {
    cat(sprintf("    - dwnominate_5p_map_period_%d.png\n", i))
}
cat("    - dwnominate_5p_trajectories.png\n")
cat("    - dwnominate_5p_timeseries_by_party.png\n")
cat("    - dwnominate_5p_shift_distribution.png\n")

cat("\n📖 Key Findings to Explore:\n")
cat("  1. Review ideological shifts during Estallido Social (P2→P3)\n")
cat("  2. Analyze impact of COVID-19 pandemic (P3→P4)\n")
cat("  3. Examine post-Plebiscito changes (P4→P5)\n")
cat("  4. Identify legislators with consistent linear trends\n")
cat("  5. Compare party-level movements across periods\n")

cat("\n✅ Analysis complete with LINEAR MODEL (model=1)!\n\n")
