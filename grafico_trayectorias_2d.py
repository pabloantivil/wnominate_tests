"""
Visualización de Trayectorias Temporales en Espacio Bidimensional
Similar al gráfico del proyecto original, muestra la evolución de cada partido
en el mapa ideológico (coord1D vs coord2D) a través de los 6 períodos.
"""

from matplotlib.lines import Line2D
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("="*80)
print("GENERANDO GRÁFICO DE TRAYECTORIAS TEMPORALES (Espacio 2D)")
print("="*80)

# Cargar datos de los 6 períodos
periodos = ['P1a', 'P1b', 'P2a', 'P2b', 'P3a', 'P3b']
all_data = []

for periodo in periodos:
    df = pd.read_csv(
        f'data/dwnominate_6periods/output/coordinates_{periodo}_6periods_corrected.csv')
    df['periodo'] = periodo
    all_data.append(df)

combined_df = pd.concat(all_data, ignore_index=True)

# Calcular medias por partido y período
partidos = sorted(combined_df['partido'].unique())
trayectorias = []

for partido in partidos:
    for periodo in periodos:
        subset = combined_df[(combined_df['partido'] == partido) &
                             (combined_df['periodo'] == periodo)]

        if len(subset) > 0:
            trayectorias.append({
                'partido': partido,
                'periodo': periodo,
                'coord1D_mean': subset['coord1D'].mean(),
                'coord2D_mean': subset['coord2D'].mean(),
                'n': len(subset)
            })

df_tray = pd.DataFrame(trayectorias)

# Colores por partido (mismos que antes)
party_colors = {
    "PC": "#800026", "COM": "#E85D75", "PH": "#FC4E2A",
    "PS": "#FD793C", "PRad": "#9370DB", "PRO": "#FF69B4",
    "RD": "#FFB347", "PPD": "#87CEEB", "PL": "#20B2AA",
    "DC": "#FFFF00", "IND": "#00FF00", "FRVS": "#FBFF86",
    "PEV": "#32CD32", "UDI": "#00008B", "RN": "#4169E1",
    "EVOP": "#1E90FF"
}

# Crear figura
fig, ax = plt.subplots(figsize=(16, 10))

# Dibujar trayectorias para cada partido
for partido in partidos:
    data = df_tray[df_tray['partido'] == partido].sort_values('periodo')

    if len(data) >= 2:
        # Extraer coordenadas
        x = data['coord1D_mean'].values
        y = data['coord2D_mean'].values

        color = party_colors.get(partido, '#808080')

        # Dibujar línea de trayectoria
        ax.plot(x, y, marker='o', linewidth=2.5, markersize=8,
                alpha=0.7, color=color, label=partido)

        # Añadir etiquetas de partido en puntos específicos
        # Etiqueta en el último punto (P3b)
        if len(x) > 0:
            ax.annotate(partido,
                        xy=(x[-1], y[-1]),
                        xytext=(5, 5),
                        textcoords='offset points',
                        fontsize=9,
                        fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3',
                                  facecolor='white',
                                  edgecolor=color,
                                  alpha=0.7),
                        color=color)

# Configurar ejes y rejilla
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)

# Etiquetas y título
ax.set_xlabel('coord1D (Económica: Izquierda ← → Derecha)',
              fontsize=14, fontweight='bold')
ax.set_ylabel('coord2D (Social: Conservador ← → Progresista)',
              fontsize=14, fontweight='bold')
ax.set_title('Trayectorias Temporales de Partidos Políticos\nDW-NOMINATE 6 Períodos (P1a → P3b)',
             fontsize=16, fontweight='bold', pad=20)

# Añadir leyenda
ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1),
          ncol=1, fontsize=10, framealpha=0.9,
          title='Partido', title_fontsize=11)

# Añadir anotaciones de cuadrantes
ax.text(-0.95, 0.95, 'Izquierda\nProgresista',
        fontsize=10, ha='left', va='top',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
ax.text(0.95, 0.95, 'Derecha\nProgresista',
        fontsize=10, ha='right', va='top',
        bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.3))
ax.text(-0.95, -0.95, 'Izquierda\nConservador',
        fontsize=10, ha='left', va='bottom',
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
ax.text(0.95, -0.95, 'Derecha\nConservador',
        fontsize=10, ha='right', va='bottom',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.3))

# Ajustar límites
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)

plt.tight_layout()
plt.savefig('results/trayectorias_espacio2D_6periods_model1.png',
            dpi=300, bbox_inches='tight')
print("Gráfico guardado: results/trayectorias_espacio2D_6periods_model1.png")
plt.close()

# VERSIÓN 2: Más limpia, solo con flechas (similar a la imagen)
print("\nGenerando versión con flechas direccionales...")

fig, ax = plt.subplots(figsize=(16, 10))

for partido in partidos:
    data = df_tray[df_tray['partido'] == partido].sort_values('periodo')

    if len(data) >= 2:
        x = data['coord1D_mean'].values
        y = data['coord2D_mean'].values

        color = party_colors.get(partido, '#808080')

        # Dibujar línea con flechas
        for i in range(len(x) - 1):
            # Flecha entre períodos consecutivos
            ax.annotate('',
                        xy=(x[i+1], y[i+1]),
                        xytext=(x[i], y[i]),
                        arrowprops=dict(arrowstyle='->',
                                        color=color,
                                        lw=2.5,
                                        alpha=0.7))

        # Marcar punto inicial (P1a)
        ax.plot(x[0], y[0], 'o', markersize=10,
                color=color, alpha=0.7, zorder=5)

        # Marcar punto final (P3b) con etiqueta
        ax.plot(x[-1], y[-1], 's', markersize=10,
                color=color, alpha=0.9, zorder=5)

        # Etiqueta en punto final
        ax.annotate(partido,
                    xy=(x[-1], y[-1]),
                    xytext=(8, 8),
                    textcoords='offset points',
                    fontsize=10,
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.4',
                              facecolor='white',
                              edgecolor=color,
                              linewidth=2,
                              alpha=0.85),
                    color=color)

# Configurar ejes
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1.5)
ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, linewidth=1.5)
ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)

ax.set_xlabel('c1.mean.1 (Económica: Izquierda ← → Derecha)',
              fontsize=14, fontweight='bold')
ax.set_ylabel('c2.mean.1 (Social: Conservador ← → Progresista)',
              fontsize=14, fontweight='bold')
ax.set_title('Cambios Temporales en Posiciones Ideológicas de Partidos\nDW-NOMINATE 6 Períodos',
             fontsize=16, fontweight='bold', pad=20)

# Leyenda personalizada
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
           markersize=10, label='Inicio (P1a)'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='gray',
           markersize=10, label='Final (P3b)'),
    Line2D([0], [0], marker='>', color='gray', linestyle='-',
           markersize=8, linewidth=2, label='Dirección temporal')
]
ax.legend(handles=legend_elements, loc='upper left',
          fontsize=11, framealpha=0.9)

ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)

plt.tight_layout()
plt.savefig('results/trayectorias_flechas_6periods_model1.png',
            dpi=300, bbox_inches='tight')
print("Gráfico con flechas guardado: results/trayectorias_flechas_6periods_model1.png")
plt.close()