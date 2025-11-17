#!/usr/bin/env python
"""
CSV DW-NOMINATE Graphing Module

This module provides visualization tools for DW-NOMINATE results from R analysis.
It can plot individual periods or show the dynamic evolution of ideal points over time.

Usage:
    # Plot a single period:
    python csv_dwnominate_graph.py --period --labels P1 --csv-file data/dwnominate/output/dwnominate_coordinates_p1.csv  --output results/dwnominate_p1_coordinates.png
    
    # Plot evolution across all periods:
    python src/csv_dwnominate_graph.py --evolution --csv-dir data/dwnominate/output --output results/dwnominate_evolution.png
    
    # Compare specific periods:
    python src/csv_dwnominate_graph.py --compare --labels P1 P5 --csv-dir data/dwnominate/output --output results/dwnominate_p1_vs_p5.png
"""

import os
import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, List, Optional
import glob


def create_party_colors_for_chile() -> Dict[str, str]:
    """
    Define color mapping for Chilean political parties.

    Returns:
        Dictionary mapping party codes to colors
    """
    return {
        # Left-wing parties
        "PC": "#FF0000",           # Communist Party (Red)
        "PS": "#E60026",           # Socialist Party (Deep Red)
        "PPD": "#FF6600",          # Party for Democracy (Orange)
        "FRVS": "#FF3366",         # Broad Front (Pink-Red)
        "RD": "#00CC66",           # Democratic Revolution (Green)
        "CS": "#66CC00",           # Social Convergence (Light Green)
        "PH": "#FF00CC",           # Humanist Party (Magenta)

        # Center parties
        "DC": "#0066FF",           # Christian Democrat (Blue)
        "PR": "#3399FF",           # Radical Party (Light Blue)
        "PL": "#0099CC",           # Liberal Party (Cyan)

        # Right-wing parties
        "RN": "#000080",           # National Renewal (Navy Blue)
        "UDI": "#800000",          # Independent Democratic Union (Maroon)
        "EVOP": "#CC6600",         # Evolve (Brown)
        "PRI": "#996633",          # Regional Independent Party (Brown)

        # Independents and others
        "IND": "#808080",          # Independent (Gray)
        "IND-UDI": "#A00000",      # Independent leaning UDI (Dark Red)
        "IND-RN": "#000060",       # Independent leaning RN (Dark Blue)

        # Default
        "Default": "#CCCCCC"       # Unknown parties (Light Gray)
    }


def load_dwnominate_period(csv_file: str) -> pd.DataFrame:
    """
    Load DW-NOMINATE coordinates for a single period from CSV file.

    Args:
        csv_file: Path to CSV file with columns: legislator_id, coord1D, coord2D, period, partido, nombres

    Returns:
        DataFrame with legislator coordinates
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    df = pd.read_csv(csv_file)

    # Handle both 'legislator' and 'legislator_id' column names
    if 'legislator' in df.columns and 'legislator_id' not in df.columns:
        df['legislator_id'] = df['legislator']

    # Verify required columns
    required_cols = ['legislator_id', 'coord1D', 'coord2D']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in CSV: {missing_cols}")

    return df


def load_all_periods(csv_dir: str) -> Dict[str, pd.DataFrame]:
    """
    Load DW-NOMINATE coordinates for all periods from a directory.

    Args:
        csv_dir: Directory containing dwnominate_coordinates_p*.csv files

    Returns:
        Dictionary mapping period IDs to DataFrames
    """
    # First try to find corrected files (pattern for 6 periods)
    period_files = glob.glob(os.path.join(
        csv_dir, "coordinates_P*_6periods_corrected.csv"))

    # If no 6-period corrected files, try original 6-period files
    if not period_files:
        period_files = glob.glob(os.path.join(
            csv_dir, "coordinates_P*_6periods.csv"))

    # If still no files, try bootstrap pattern (corrected)
    if not period_files:
        period_files = glob.glob(os.path.join(
            csv_dir, "coordinates_P*_bootstrap_corrected.csv"))

    # If still no files, try bootstrap pattern (original)
    if not period_files:
        period_files = glob.glob(os.path.join(
            csv_dir, "coordinates_P*_bootstrap.csv"))

    # If still no files, try corrected 5-period pattern
    if not period_files:
        period_files = glob.glob(os.path.join(
            csv_dir, "dwnominate_coordinates_p*_corrected.csv"))

    # If still no corrected files, use original 5-period files
    if not period_files:
        period_files = glob.glob(os.path.join(
            csv_dir, "dwnominate_coordinates_p*.csv"))

    if not period_files:
        raise FileNotFoundError(
            f"No DW-NOMINATE coordinate files found in {csv_dir}")

    periods = {}
    for filepath in sorted(period_files):
        # Extract period ID from filename
        basename = os.path.basename(filepath)

        # Handle different filename patterns
        if "coordinates_P" in basename:
            # Pattern: coordinates_P1_6periods_corrected.csv -> P1
            period_id = basename.split("_")[1]  # Gets "P1"
        else:
            # Pattern: dwnominate_coordinates_p1.csv -> P1
            period_id = basename.replace(
                "dwnominate_coordinates_", "").replace("_corrected.csv", "").replace(".csv", "").upper()

        df = load_dwnominate_period(filepath)
        periods[period_id] = df
        print(f"📂 Loaded {period_id}: {len(df)} legislators")

    return periods


def plot_single_period(csv_file: str, output_file: Optional[str] = None,
                       show_labels: bool = False, title: Optional[str] = None):
    """
    Plot DW-NOMINATE coordinates for a single period.

    Args:
        csv_file: Path to CSV coordinates file
        output_file: Optional path to save plot image
        show_labels: Whether to show legislator labels on plot
        title: Plot title (auto-generated if None)
    """
    df = load_dwnominate_period(csv_file)

    # Extract period from dataframe or filename
    if 'period' in df.columns and not df['period'].isna().all():
        period_name = df['period'].iloc[0]
    else:
        basename = os.path.basename(csv_file)
        period_name = basename.replace(
            "dwnominate_coordinates_", "").replace(".csv", "").upper()

    if title is None:
        title = f"DW-NOMINATE Map - Period {period_name}"

    # Create party color mapping
    party_colors = create_party_colors_for_chile()

    # Create the plot
    plt.figure(figsize=(12, 8))

    # Plot each legislator
    for _, row in df.iterrows():
        x = row['coord1D']
        y = row['coord2D']
        party = row.get('partido', '')
        color = party_colors.get(party, party_colors["Default"])

        plt.scatter(x, y, c=color, s=60, alpha=0.7,
                    edgecolors='black', linewidth=0.5)

        if show_labels and 'nombres' in row:
            label = f"{row['nombres']} ({party})" if party else row['nombres']
            plt.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points',
                         fontsize=7, alpha=0.8)

    # Add axes lines
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)

    # Add adaptive circle boundary based on data range
    # Calculate the maximum absolute coordinate value
    x_vals = df['coord1D'].values
    y_vals = df['coord2D'].values
    max_coord = max(abs(x_vals).max(), abs(y_vals).max())

    # Use at least 1.0, but expand if data goes beyond
    circle_radius = max(1.0, max_coord * 1.1)  # 10% margin

    theta = np.linspace(0, 2*np.pi, 100)
    circle_x = circle_radius * np.cos(theta)
    circle_y = circle_radius * np.sin(theta)
    plt.plot(circle_x, circle_y, color='red', linestyle='--', alpha=0.5, linewidth=2,
             label=f'Boundary Circle (r={circle_radius:.2f})')

    # Formatting
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel('First Dimension (Economic: Left ← → Right)', fontsize=12)
    plt.ylabel('Second Dimension (Social Issues)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.3)

    # Create legend for parties
    unique_parties = df['partido'].dropna(
    ).unique() if 'partido' in df.columns else []

    legend_elements = []
    for party in sorted(unique_parties):
        if party in party_colors:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                              markerfacecolor=party_colors[party],
                                              markersize=8, label=party))

    if legend_elements:
        plt.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5),
                   fontsize=10, framealpha=0.8)

    # Set axis limits symmetrically around origin with margin
    max_abs_coord = max(abs(x_vals).max(), abs(y_vals).max())
    axis_limit = max_abs_coord * 1.15  # 15% margin
    plt.xlim(-axis_limit, axis_limit)
    plt.ylim(-axis_limit, axis_limit)

    # Ensure square aspect ratio for circular plot
    plt.gca().set_aspect('equal', adjustable='box')

    plt.tight_layout()

    if output_file:
        # Asegurar que el directorio existe
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        abs_path = os.path.abspath(output_file)
        plt.savefig(abs_path, dpi=300, bbox_inches='tight')
        print(f"📊 Gráfico guardado en: {abs_path}")
    else:
        plt.show()


def plot_evolution(csv_dir: str, output_file: Optional[str] = None,
                   legislators_to_track: Optional[List[str]] = None):
    """
    Plot the evolution of legislator ideal points across all periods.

    Args:
        csv_dir: Directory containing period CSV files
        output_file: Optional path to save plot image
        legislators_to_track: Optional list of legislator IDs to highlight
    """
    periods = load_all_periods(csv_dir)

    if len(periods) < 2:
        raise ValueError("Need at least 2 periods to show evolution")

    party_colors = create_party_colors_for_chile()

    # Create figure with subplots for each period
    n_periods = len(periods)
    fig, axes = plt.subplots(1, n_periods, figsize=(6*n_periods, 6))

    if n_periods == 1:
        axes = [axes]

    sorted_periods = sorted(periods.keys())

    # Track specific legislators across periods if specified
    if legislators_to_track:
        legislator_positions = {leg_id: [] for leg_id in legislators_to_track}

    for i, period_id in enumerate(sorted_periods):
        ax = axes[i]
        df = periods[period_id]

        # Plot all legislators
        for _, row in df.iterrows():
            x = row['coord1D']
            y = row['coord2D']
            party = row.get('partido', '')
            color = party_colors.get(party, party_colors["Default"])

            alpha = 0.7
            size = 60

            # Highlight tracked legislators
            if legislators_to_track and str(row['legislator_id']) in legislators_to_track:
                alpha = 1.0
                size = 100
                legislator_positions[str(row['legislator_id'])].append(
                    (period_id, x, y))

            ax.scatter(x, y, c=color, s=size, alpha=alpha,
                       edgecolors='black', linewidth=0.5)

        # Formatting
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)

        # Adaptive circle boundary for this period
        period_x = df['coord1D'].values
        period_y = df['coord2D'].values
        period_max = max(abs(period_x).max(), abs(period_y).max())
        period_radius = max(1.0, period_max * 1.1)

        theta = np.linspace(0, 2*np.pi, 100)
        circle_x = period_radius * np.cos(theta)
        circle_y = period_radius * np.sin(theta)
        ax.plot(circle_x, circle_y, color='red',
                linestyle='--', alpha=0.3, linewidth=1)

        ax.set_title(f'Period {period_id}', fontsize=14, fontweight='bold')
        ax.set_xlabel('First Dimension', fontsize=10)
        if i == 0:
            ax.set_ylabel('Second Dimension', fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.3)

        # Set symmetric limits
        axis_lim = period_radius * 1.15
        ax.set_xlim(-axis_lim, axis_lim)
        ax.set_ylim(-axis_lim, axis_lim)
        ax.set_aspect('equal', adjustable='box')

    # Add overall title
    fig.suptitle('DW-NOMINATE Evolution Across Periods\nChilean Congress 55th Legislative Period (2018-2022)',
                 fontsize=16, fontweight='bold')

    plt.tight_layout()

    if output_file:
        # Asegurar que el directorio existe
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        abs_path = os.path.abspath(output_file)
        plt.savefig(abs_path, dpi=300, bbox_inches='tight')
        print(f"📊 Gráfico de evolución guardado en: {abs_path}")
    else:
        plt.show()

    # If tracking specific legislators, print their movement
    if legislators_to_track and legislator_positions:
        print("\n📈 Movimiento de Legisladores:")
        for leg_id, positions in legislator_positions.items():
            if positions:
                print(f"\n   Legislador {leg_id}:")
                for period_id, x, y in positions:
                    print(f"      {period_id}: ({x:.3f}, {y:.3f})")


def compare_periods(csv_dir: str, period1: str, period2: str,
                    output_file: Optional[str] = None, show_labels: bool = False):
    """
    Create side-by-side comparison of two periods.

    Args:
        csv_dir: Directory containing period CSV files
        period1: First period ID (e.g., "P1")
        period2: Second period ID (e.g., "P5")
        output_file: Optional path to save plot image
        show_labels: Whether to show legislator names on the plot
    """
    periods = load_all_periods(csv_dir)

    if period1 not in periods:
        raise ValueError(f"Period {period1} not found")
    if period2 not in periods:
        raise ValueError(f"Period {period2} not found")

    df1 = periods[period1]
    df2 = periods[period2]

    party_colors = create_party_colors_for_chile()

    # Create figure with more space for legend
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

    # Calculate adaptive radius for both periods
    all_coords = pd.concat(
        [df1[['coord1D', 'coord2D']], df2[['coord1D', 'coord2D']]])
    max_coord = max(abs(all_coords['coord1D']).max(),
                    abs(all_coords['coord2D']).max())
    circle_radius = max(1.0, max_coord * 1.1)
    axis_limit = circle_radius * 1.15

    # Plot period 1
    for _, row in df1.iterrows():
        x = row['coord1D']
        y = row['coord2D']
        party = row.get('partido', '')
        color = party_colors.get(party, party_colors["Default"])
        ax1.scatter(x, y, c=color, s=80, alpha=0.7,
                    edgecolors='black', linewidth=0.5)

        # Add labels if requested
        if show_labels and 'nombres' in row:
            # Split name to show only first name and last name
            nombres = str(row['nombres'])
            name_parts = nombres.split()
            if len(name_parts) >= 2:
                short_name = f"{name_parts[0]} {name_parts[-1]}"
            else:
                short_name = nombres

            ax1.annotate(short_name, (x, y),
                         xytext=(3, 3), textcoords='offset points',
                         fontsize=6, alpha=0.8,
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                   edgecolor='gray', alpha=0.7))

    ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax1.axvline(x=0, color='k', linestyle='-', alpha=0.3)

    # Add adaptive circle to ax1
    theta = np.linspace(0, 2*np.pi, 100)
    circle_x = circle_radius * np.cos(theta)
    circle_y = circle_radius * np.sin(theta)
    ax1.plot(circle_x, circle_y, color='red',
             linestyle='--', alpha=0.4, linewidth=1.5)

    ax1.set_title(f'Period {period1} (2018)', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Primera Dimensión (Izquierda ← → Derecha)', fontsize=12)
    ax1.set_ylabel('Segunda Dimensión', fontsize=12)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim(-axis_limit, axis_limit)
    ax1.set_ylim(-axis_limit, axis_limit)
    ax1.set_aspect('equal', adjustable='box')

    # Plot period 2
    for _, row in df2.iterrows():
        x = row['coord1D']
        y = row['coord2D']
        party = row.get('partido', '')
        color = party_colors.get(party, party_colors["Default"])
        ax2.scatter(x, y, c=color, s=80, alpha=0.7,
                    edgecolors='black', linewidth=0.5)

        # Add labels if requested
        if show_labels and 'nombres' in row:
            nombres = str(row['nombres'])
            name_parts = nombres.split()
            if len(name_parts) >= 2:
                short_name = f"{name_parts[0]} {name_parts[-1]}"
            else:
                short_name = nombres

            ax2.annotate(short_name, (x, y),
                         xytext=(3, 3), textcoords='offset points',
                         fontsize=6, alpha=0.8,
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                   edgecolor='gray', alpha=0.7))

    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax2.axvline(x=0, color='k', linestyle='-', alpha=0.3)

    # Add adaptive circle to ax2
    ax2.plot(circle_x, circle_y, color='red',
             linestyle='--', alpha=0.4, linewidth=1.5)

    ax2.set_title(f'Period {period2} (2021)', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Primera Dimensión (Izquierda ← → Derecha)', fontsize=12)
    ax2.set_ylabel('Segunda Dimensión', fontsize=12)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlim(-axis_limit, axis_limit)
    ax2.set_ylim(-axis_limit, axis_limit)
    ax2.set_aspect('equal', adjustable='box')

    # Create comprehensive party legend
    # Get all unique parties from both periods
    all_parties = set()
    if 'partido' in df1.columns:
        all_parties.update(df1['partido'].dropna().unique())
    if 'partido' in df2.columns:
        all_parties.update(df2['partido'].dropna().unique())

    # Create legend with party colors and descriptions
    legend_elements = []
    party_descriptions = {
        'PC': 'PC - Partido Comunista',
        'PS': 'PS - Partido Socialista',
        'PPD': 'PPD - Partido por la Democracia',
        'RD': 'RD - Revolución Democrática',
        'FRVS': 'FRVS - Frente Amplio',
        'DC': 'DC - Democracia Cristiana',
        'PRad': 'PRad - Partido Radical',
        'PL': 'PL - Partido Liberal',
        'RN': 'RN - Renovación Nacional',
        'UDI': 'UDI - Unión Demócrata Independiente',
        'EVOP': 'EVOP - Evolución Política',
        'IND': 'IND - Independiente',
        'PH': 'PH - Partido Humanista',
        'PEV': 'PEV - Partido Ecologista Verde',
        'COM': 'COM - Comunes',
        'PRO': 'PRO - Partido Progresista'
    }

    for party in sorted(all_parties):
        if party and party in party_colors:
            label = party_descriptions.get(party, party)
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                              markerfacecolor=party_colors[party],
                                              markeredgecolor='black',
                                              markersize=10, label=label))

    # Add legend below the plots
    fig.legend(handles=legend_elements,
               loc='lower center',
               bbox_to_anchor=(0.5, -0.05),
               ncol=4,
               fontsize=10,
               framealpha=0.9,
               title='Partidos Políticos',
               title_fontsize=12)

    fig.suptitle(f'Comparación DW-NOMINATE: {period1} (2018) vs {period2} (2021)\nCongreso Chileno - 55° Período Legislativo',
                 fontsize=18, fontweight='bold')

    plt.tight_layout(rect=[0, 0.05, 1, 0.96])

    if output_file:
        # Asegurar que el directorio existe
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        abs_path = os.path.abspath(output_file)
        plt.savefig(abs_path, dpi=300, bbox_inches='tight')
        print(f"📊 Gráfico de comparación guardado en: {abs_path}")
    else:
        plt.show()


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Plot DW-NOMINATE coordinates from CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--csv-file',
        type=str,
        help='Path to CSV file with DW-NOMINATE coordinates for single period'
    )

    parser.add_argument(
        '--csv-dir',
        type=str,
        help='Directory containing multiple period CSV files'
    )

    parser.add_argument(
        '--period',
        type=str,
        help='Period ID for single period plot (e.g., P1, P2, ...)'
    )

    parser.add_argument(
        '--evolution',
        action='store_true',
        help='Plot evolution across all periods (requires --csv-dir)'
    )

    parser.add_argument(
        '--compare',
        nargs=2,
        metavar=('PERIOD1', 'PERIOD2'),
        help='Compare two specific periods (requires --csv-dir)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Path to save the plot image (if not specified, shows the plot)'
    )

    parser.add_argument(
        '--labels',
        action='store_true',
        help='Show legislator labels on the plot'
    )

    parser.add_argument(
        '--title',
        type=str,
        help='Custom title for the plot'
    )

    args = parser.parse_args()

    try:
        if args.evolution:
            # Plot evolution across all periods
            if not args.csv_dir:
                print("❌ Error: --csv-dir required for --evolution")
                return 1

            plot_evolution(args.csv_dir, args.output)

        elif args.compare:
            # Compare two periods
            if not args.csv_dir:
                print("❌ Error: --csv-dir required for --compare")
                return 1

            period1, period2 = args.compare
            compare_periods(args.csv_dir, period1.upper(),
                            period2.upper(), args.output, args.labels)

        elif args.csv_file:
            # Plot single period from file
            plot_single_period(args.csv_file, args.output,
                               args.labels, args.title)

        elif args.csv_dir and args.period:
            # Plot single period from directory
            period_file = os.path.join(
                args.csv_dir, f"dwnominate_coordinates_{args.period.lower()}.csv")
            plot_single_period(period_file, args.output,
                               args.labels, args.title)

        else:
            print("❌ Error: Must specify either:")
            print("   1. --csv-file for single period plot")
            print("   2. --csv-dir and --period for single period plot")
            print("   3. --csv-dir and --evolution for evolution plot")
            print("   4. --csv-dir and --compare PERIOD1 PERIOD2 for comparison")
            parser.print_help()
            return 1

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
