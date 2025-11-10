# Correct the polarity of DW-NOMINATE coordinates
# This script flips the first dimension to match Chilean political spectrum conventions
# Handles multiple periods (P1-P5)

library(dplyr)

cat("\n")
cat("===============================================\n")
cat("  DW-NOMINATE Polarity Correction             \n")
cat("  Chilean Congress - 5 Periods                \n")
cat("===============================================\n")
cat("\n")

cat("🔄 Correcting DW-NOMINATE coordinate polarity...\n\n")

# Define paths
input_dir <- "../../data/dwnominate/output"
output_dir <- "../../data/dwnominate/output"
results_dir <- "../../results"

# Create output directories if they don't exist
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}
if (!dir.exists(results_dir)) {
  dir.create(results_dir, recursive = TRUE)
}

# Function to correct a single period file
correct_period_file <- function(period_num) {
  input_file <- file.path(input_dir, paste0("dwnominate_coordinates_p", period_num, ".csv"))
  output_file <- file.path(output_dir, paste0("dwnominate_coordinates_p", period_num, "_corrected.csv"))

  if (!file.exists(input_file)) {
    cat(sprintf("⚠️  Period %d file not found: %s\n", period_num, input_file))
    return(NULL)
  }

  # Load the original coordinates
  coords_original <- read.csv(input_file)

  cat(sprintf("📂 Period P%d: Loaded %d legislators\n", period_num, nrow(coords_original)))

  # Show current distribution by party on first dimension
  if ("partido" %in% colnames(coords_original)) {
    party_stats <- coords_original %>%
      group_by(partido) %>%
      summarise(
        count = n(),
        mean_coord1D = round(mean(coord1D, na.rm = TRUE), 3),
        .groups = "drop"
      ) %>%
      arrange(mean_coord1D)

    # Show specific examples
    ps_mean <- mean(coords_original$coord1D[coords_original$partido == "PS"], na.rm = TRUE)
    udi_mean <- mean(coords_original$coord1D[coords_original$partido == "UDI"], na.rm = TRUE)

    cat(sprintf("   Current: PS (left) = %.3f, UDI (right) = %.3f\n", ps_mean, udi_mean))
  }

  # Apply the correction: flip first dimension
  coords_corrected <- coords_original
  coords_corrected$coord1D <- -coords_corrected$coord1D

  # Show corrected distribution
  if ("partido" %in% colnames(coords_corrected)) {
    ps_mean_corrected <- mean(coords_corrected$coord1D[coords_corrected$partido == "PS"], na.rm = TRUE)
    udi_mean_corrected <- mean(coords_corrected$coord1D[coords_corrected$partido == "UDI"], na.rm = TRUE)

    cat(sprintf(
      "   Corrected: PS (left) = %.3f ✓, UDI (right) = %.3f ✓\n",
      ps_mean_corrected, udi_mean_corrected
    ))
  }

  # Save the corrected coordinates
  write.csv(coords_corrected, output_file, row.names = FALSE)
  cat(sprintf("   ✅ Saved: %s\n\n", basename(output_file)))

  return(coords_corrected)
}

# Process all 5 periods
cat("📅 Processing individual period files...\n\n")
all_corrected <- list()
for (i in 1:5) {
  corrected <- correct_period_file(i)
  if (!is.null(corrected)) {
    all_corrected[[i]] <- corrected
  }
}

# Now correct the combined file
cat("\n📊 Processing combined file (all periods)...\n")
combined_file <- file.path(input_dir, "dwnominate_coordinates_all_periods.csv")

if (file.exists(combined_file)) {
  coords_all_original <- read.csv(combined_file)

  cat(sprintf(
    "   Loaded %d total observations (%d legislators × 5 periods)\n",
    nrow(coords_all_original), nrow(coords_all_original) / 5
  ))

  # Show distribution across all periods
  if ("partido" %in% colnames(coords_all_original)) {
    cat("\n   Current distribution (all periods combined):\n")
    party_stats_all <- coords_all_original %>%
      group_by(partido) %>%
      summarise(
        count = n(),
        mean_coord1D = round(mean(coord1D, na.rm = TRUE), 3),
        .groups = "drop"
      ) %>%
      arrange(mean_coord1D) %>%
      head(10)

    print(party_stats_all)
  }

  # Apply correction
  coords_all_corrected <- coords_all_original
  coords_all_corrected$coord1D <- -coords_all_corrected$coord1D

  # Show corrected distribution
  if ("partido" %in% colnames(coords_all_corrected)) {
    cat("\n   Corrected distribution (all periods combined):\n")
    party_stats_corrected <- coords_all_corrected %>%
      group_by(partido) %>%
      summarise(
        count = n(),
        mean_coord1D = round(mean(coord1D, na.rm = TRUE), 3),
        .groups = "drop"
      ) %>%
      arrange(mean_coord1D) %>%
      head(10)

    print(party_stats_corrected)
  }

  # Save corrected combined file
  write.csv(coords_all_corrected, file.path(output_dir, "dwnominate_coordinates_all_periods_corrected.csv"),
    row.names = FALSE
  )
  cat("\n   ✅ Saved: dwnominate_coordinates_all_periods_corrected.csv\n")
}

# Create visualization comparing before and after
cat("\n📈 Creating comparison visualizations...\n")

if (require(ggplot2)) {
  # Plot for Period 5 (2021) - before and after
  if (!is.null(all_corrected[[5]])) {
    coords_p5_original <- read.csv(file.path(input_dir, "dwnominate_coordinates_p5.csv"))
    coords_p5_corrected <- all_corrected[[5]]

    coords_p5_original$version <- "Original (Incorrect)"
    coords_p5_corrected$version <- "Corrected"
    coords_p5_combined <- rbind(coords_p5_original, coords_p5_corrected)

    p_comparison <- ggplot(coords_p5_combined, aes(x = coord1D, y = coord2D, color = partido)) +
      geom_point(alpha = 0.7, size = 2.5) +
      facet_wrap(~version, ncol = 2) +
      labs(
        title = "DW-NOMINATE Polarity Correction - Period P5 (2021)",
        subtitle = "Before vs After: First Dimension Flipped",
        x = "First Dimension (Economic: Left ← → Right)",
        y = "Second Dimension (Social Issues)",
        color = "Party"
      ) +
      geom_hline(yintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.5) +
      geom_vline(xintercept = 0, color = "gray50", linestyle = "dashed", alpha = 0.5) +
      theme_minimal() +
      theme(
        legend.position = "bottom",
        plot.title = element_text(size = 14, face = "bold"),
        plot.subtitle = element_text(size = 11)
      ) +
      annotate("text",
        x = -0.8, y = -0.9, label = "Left\n(PS, PC)",
        size = 3, color = "gray30", fontface = "italic"
      ) +
      annotate("text",
        x = 0.8, y = 0.9, label = "Right\n(UDI, RN)",
        size = 3, color = "gray30", fontface = "italic"
      )

    ggsave(file.path(results_dir, "dwnominate_polarity_comparison_p5.png"), p_comparison,
      width = 14, height = 7, dpi = 300
    )
    cat("   ✅ Saved: dwnominate_polarity_comparison_p5.png\n")

    # Also create evolution plot with corrected coordinates
    if (length(all_corrected) == 5) {
      coords_evolution <- bind_rows(all_corrected, .id = "period")
      coords_evolution$period <- paste0("P", coords_evolution$period)
      coords_evolution$period <- factor(coords_evolution$period,
        levels = c("P1", "P2", "P3", "P4", "P5")
      )

      p_evolution <- ggplot(coords_evolution, aes(x = coord1D, y = coord2D, color = partido)) +
        geom_point(alpha = 0.6, size = 2) +
        facet_wrap(~period, ncol = 5) +
        labs(
          title = "DW-NOMINATE Evolution with Corrected Polarity",
          subtitle = "Chilean Congress 55th Legislative Period (2018-2022)",
          x = "First Dimension (Economic: Left ← → Right)",
          y = "Second Dimension",
          color = "Party"
        ) +
        geom_hline(yintercept = 0, color = "gray50", linetype = "dashed", alpha = 0.5) +
        geom_vline(xintercept = 0, color = "gray50", linestyle = "dashed", alpha = 0.5) +
        theme_minimal() +
        theme(
          legend.position = "bottom",
          plot.title = element_text(size = 14, face = "bold"),
          plot.subtitle = element_text(size = 11),
          axis.text = element_text(size = 8)
        )

      ggsave(file.path(results_dir, "dwnominate_evolution_corrected.png"), p_evolution,
        width = 20, height = 5, dpi = 300
      )
      cat("   ✅ Saved: dwnominate_evolution_corrected.png\n")
    }
  }
} else {
  cat("   ⚠️  ggplot2 not installed, skipping visualizations\n")
  cat("   Install with: install.packages('ggplot2')\n")
}

# Summary
cat("\n")
cat("===============================================\n")
cat("  ✅ Polarity Correction Complete!            \n")
cat("===============================================\n")
cat("\n")

cat("📂 Files created:\n")
cat("   • dwnominate_coordinates_p1_corrected.csv through p5_corrected.csv\n")
cat("   • dwnominate_coordinates_all_periods_corrected.csv\n")
cat("   • dwnominate_polarity_comparison_p5.png (if ggplot2 available)\n")
cat("   • dwnominate_evolution_corrected.png (if ggplot2 available)\n")
cat("\n")

cat("🎯 Correction applied:\n")
cat("   • First dimension flipped: coord1D = -coord1D\n")
cat("   • Left-wing parties (PC, PS) are now NEGATIVE (left side)\n")
cat("   • Right-wing parties (UDI, RN) are now POSITIVE (right side)\n")
cat("   • This matches the standard political spectrum convention\n")
cat("\n")

cat("💡 Next steps:\n")
cat("   1. Use the *_corrected.csv files for your analysis\n")
cat("   2. Re-run csv_dwnominate_graph.py with corrected files:\n")
cat("      python src/csv_dwnominate_graph.py --csv-file data/dwnominate/output/dwnominate_coordinates_p5_corrected.csv --output results/dwnominate_map_corrected.png\n")
cat("\n")
