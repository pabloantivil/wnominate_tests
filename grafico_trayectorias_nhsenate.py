"""
Visualización de Trayectorias Temporales DW-NOMINATE
Dataset: nhsenate con modelo cúbico (model = 3)
Muestra la evolución de centroides de partidos a través de 21 sesiones
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle

print("="*80)
print("GRAFICANDO TRAYECTORIAS DW-NOMINATE - Dataset nhsenate")
print("="*80)

# Cargar coordenadas exportadas desde R
df = pd.read_csv('scripts/r/output_nhsenate/nhsenate_coordinates_model3.csv')

print("\nColumnas disponibles:")
print(df.columns.tolist())
print("\nPrimeras filas:")
print(df.head())

# Identificar columnas de coordenadas
coord1_col = 'coord1D' if 'coord1D' in df.columns else 'dim1'
coord2_col = 'coord2D' if 'coord2D' in df.columns else 'dim2'

# Identificar columna de sesión/congreso
session_col = 'congress' if 'congress' in df.columns else 'session'

# Identificar columna de partido
party_col = 'party' if 'party' in df.columns else 'partido'

print(f"\nUsando columnas:")
print(f"  - Sesión: {session_col}")
print(f"  - Partido: {party_col}")
print(f"  - Coord 1D: {coord1_col}")
print(f"  - Coord 2D: {coord2_col}")

# Calcular centroides por partido y sesión
partidos = sorted(df[party_col].unique())
sesiones = sorted(df[session_col].unique())

print(f"\n{len(partidos)} partidos encontrados: {partidos}")
print(f"{len(sesiones)} sesiones encontradas")

# Calcular medias por partido y sesión
trayectorias = []

for partido in partidos:
    for sesion in sesiones:
        subset = df[(df[party_col] == partido) & (df[session_col] == sesion)]
        
        if len(subset) > 0:
            trayectorias.append({
                'partido': partido,
                'sesion': sesion,
                'coord1D_mean': subset[coord1_col].mean(),
                'coord2D_mean': subset[coord2_col].mean(),
                'n_legislators': len(subset)
            })

df_tray = pd.DataFrame(trayectorias)

print(f"\n{len(df_tray)} puntos de trayectoria calculados")
print("\nPrimeros puntos de trayectoria:")
print(df_tray.head(10))

# Definir colores para cada partido
party_colors = {
    'Democrat': '#0015BC',
    'Republican': '#E81B23', 
    'Federalist': '#C19A6B',
    'Democratic Republican': '#228B22',
    'Whig': '#F0C862',
    'Anti-Administration': '#8B4513',
    'Pro-Administration': '#4682B4',
}

# Asignar colores automáticos para partidos no definidos
available_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                   '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788']
color_idx = 0
for partido in partidos:
    if partido not in party_colors:
        party_colors[partido] = available_colors[color_idx % len(available_colors)]
        color_idx += 1

# ============================================================================
# GRÁFICO 1: Trayectorias con líneas y puntos
# ============================================================================
print("\nGenerando gráfico de trayectorias...")

fig, ax = plt.subplots(figsize=(16, 10))

for partido in partidos:
    data = df_tray[df_tray['partido'] == partido].sort_values('sesion')
    
    if len(data) >= 2:
        x = data['coord1D_mean'].values
        y = data['coord2D_mean'].values
        
        color = party_colors.get(partido, '#808080')
        
        # Dibujar línea de trayectoria
        ax.plot(x, y, marker='o', linewidth=2.5, markersize=8,
                alpha=0.7, color=color, label=partido)
        
        # Etiqueta en el punto final
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
                                alpha=0.8),
                       color=color)

# Configurar ejes
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)

ax.set_xlabel('Dimensión 1 (Liberal ← → Conservador)', 
              fontsize=14, fontweight='bold')
ax.set_ylabel('Dimensión 2', 
              fontsize=14, fontweight='bold')
ax.set_title('Trayectorias Temporales de Partidos - DW-NOMINATE (Modelo Cúbico)\nDataset: New Hampshire Senate (21 sesiones)',
             fontsize=16, fontweight='bold', pad=20)

ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1),
          ncol=1, fontsize=10, framealpha=0.9,
          title='Partido', title_fontsize=11)

plt.tight_layout()
plt.savefig('scripts/r/output_nhsenate/trayectorias_nhsenate_model3.png',
            dpi=300, bbox_inches='tight')
print("✓ Gráfico guardado: scripts/r/output_nhsenate/trayectorias_nhsenate_model3.png")
plt.show()

# ============================================================================
# GRÁFICO 2: Trayectorias en Círculo Unitario
# ============================================================================
print("\nGenerando gráfico de trayectorias en círculo unitario...")

fig, ax = plt.subplots(figsize=(12, 12))

# Dibujar círculo unitario
circle = Circle((0, 0), 1, fill=False, edgecolor='black', 
                linewidth=2, linestyle='-', alpha=0.6)
ax.add_patch(circle)

# Dibujar círculos concéntricos para referencia
for radius in [0.25, 0.5, 0.75]:
    circle_ref = Circle((0, 0), radius, fill=False, edgecolor='gray',
                       linewidth=0.5, linestyle=':', alpha=0.3)
    ax.add_patch(circle_ref)

# Dibujar trayectorias de partidos
for partido in partidos:
    data = df_tray[df_tray['partido'] == partido].sort_values('sesion')
    
    if len(data) >= 2:
        x = data['coord1D_mean'].values
        y = data['coord2D_mean'].values
        
        color = party_colors.get(partido, '#808080')
        
        # Dibujar línea de trayectoria
        ax.plot(x, y, marker='o', linewidth=2.5, markersize=8,
                alpha=0.7, color=color, label=partido, zorder=3)
        
        # Marcar punto inicial con círculo
        ax.plot(x[0], y[0], 'o', markersize=12,
               color=color, alpha=0.5, zorder=4,
               markeredgecolor='black', markeredgewidth=1.5)
        
        # Marcar punto final con cuadrado
        ax.plot(x[-1], y[-1], 's', markersize=12,
               color=color, alpha=0.9, zorder=4,
               markeredgecolor='black', markeredgewidth=1.5)
        
        # Etiqueta en el punto final
        if len(x) > 0:
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
                                alpha=0.9),
                       color=color,
                       zorder=5)

# Configurar ejes
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1.5, zorder=1)
ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, linewidth=1.5, zorder=1)
ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8, zorder=0)

# Configurar límites y aspecto
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.set_aspect('equal', adjustable='box')

ax.set_xlabel('Dimensión 1 (Liberal ← → Conservador)',
              fontsize=14, fontweight='bold')
ax.set_ylabel('Dimensión 2',
              fontsize=14, fontweight='bold')
ax.set_title('Trayectorias en Círculo Unitario - DW-NOMINATE (Modelo Cúbico)\nDataset: New Hampshire Senate',
             fontsize=16, fontweight='bold', pad=20)

# Leyenda personalizada
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
           markersize=12, markeredgecolor='black', markeredgewidth=1.5,
           label=f'Inicio (Sesión {sesiones[0]})'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='gray',
           markersize=12, markeredgecolor='black', markeredgewidth=1.5,
           label=f'Final (Sesión {sesiones[-1]})'),
    Line2D([0], [0], color='gray', linewidth=2.5,
           label='Trayectoria temporal')
]

# Añadir partidos a la leyenda
ax.legend(handles=legend_elements, loc='upper left',
          bbox_to_anchor=(1.02, 1), ncol=1, fontsize=11, 
          framealpha=0.9, title='Símbolos', title_fontsize=12)

# Crear segunda leyenda para partidos
from matplotlib.patches import Patch
party_patches = [Patch(facecolor=party_colors.get(p, '#808080'), 
                       edgecolor='black', label=p) for p in partidos]
ax2 = ax.twinx()
ax2.set_yticks([])
ax2.legend(handles=party_patches, loc='lower left',
          bbox_to_anchor=(1.02, 0), ncol=1, fontsize=10,
          framealpha=0.9, title='Partidos', title_fontsize=11)

plt.tight_layout()
plt.savefig('scripts/r/output_nhsenate/trayectorias_circulo_unitario_model3.png',
            dpi=300, bbox_inches='tight')
print("✓ Gráfico de círculo unitario guardado: scripts/r/output_nhsenate/trayectorias_circulo_unitario_model3.png")
plt.show()

print("\n" + "="*80)
print("ANÁLISIS COMPLETADO")
print("="*80)
print(f"\nArchivos generados:")
print("  1. scripts/r/output_nhsenate/trayectorias_nhsenate_model3.png")
print("  2. scripts/r/output_nhsenate/trayectorias_circulo_unitario_model3.png")
print("\nEstadísticas:")
print(f"  - Partidos analizados: {len(partidos)}")
print(f"  - Sesiones: {len(sesiones)}")
print(f"  - Modelo usado: Cúbico (polynomial degree 3)")
print(f"  - Total puntos de trayectoria: {len(df_tray)}")