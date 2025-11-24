"""
Visualización de trayectorias temporales de partidos políticos
W-NOMINATE para 3 períodos del 55º Periodo Legislativo (2018-2022):
- P1: 11/03/2018 - 18/10/2019 (Inicio PL → Estallido Social)
- P2: 18/10/2019 - 25/10/2020 (Estallido Social → Plebiscito 2020)
- P3: 25/10/2020 - 10/03/2022 (Plebiscito 2020 → Fin PL)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuración de estilo
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.3)

# Definir períodos
periodos = ['p1', 'p2', 'p3']
nombres_periodos = [
    'P1\n11/03/2018 - 18/10/2019\n(Inicio → Estallido)',
    'P2\n18/10/2019 - 25/10/2020\n(Estallido → Plebiscito)',
    'P3\n25/10/2020 - 10/03/2022\n(Plebiscito → Fin PL)'
]

nombres_periodos_cortos = ['P1\nInicio→Estallido',
                           'P2\nEstallido→Plebiscito', 'P3\nPlebiscito→Fin']

# Colores por partido
colores_partidos = {
    'PC': '#FF0000',      # Rojo intenso
    'COM': '#CC0000',     # Rojo oscuro
    'PH': '#FF6B6B',      # Rojo claro
    'PS': '#E74C3C',      # Rojo anaranjado
    'PRad': '#F39C12',    # Naranja
    'PRO': '#F1C40F',     # Amarillo
    'RD': '#9B59B6',      # Púrpura
    'PPD': '#3498DB',     # Azul claro
    'PL': '#5DADE2',      # Azul cielo
    'DC': '#27AE60',      # Verde
    'IND': '#95A5A6',     # Gris
    'FRVS': '#7F8C8D',    # Gris oscuro
    'PEV': '#2ECC71',     # Verde claro
    'UDI': '#1A1A1A',     # Negro
    'RN': '#34495E',      # Azul oscuro
    'EVOP': '#8E44AD'     # Púrpura oscuro
}

# Directorio de datos
data_dir = Path('data/wnominate_3periods/output')
results_dir = Path('results')
results_dir.mkdir(exist_ok=True)

print("=" * 70)
print("VISUALIZACIÓN DE TRAYECTORIAS W-NOMINATE (3 PERÍODOS 55º PL)")
print("=" * 70)

# Cargar datos de todos los períodos
datos_periodos = []

for periodo in periodos:
    archivo = data_dir / f'wnominate_coordinates_{periodo}_corrected.csv'

    if not archivo.exists():
        print(f"⚠️  Archivo no encontrado: {archivo}")
        continue

    df = pd.read_csv(archivo)
    df['periodo'] = periodo
    datos_periodos.append(df)
    print(f"✅ {periodo.upper()}: {len(df)} legisladores cargados")

# Combinar todos los datos
df_todos = pd.concat(datos_periodos, ignore_index=True)

print(f"\nTotal de observaciones: {len(df_todos)}")
print(f"Partidos únicos: {df_todos['party'].nunique()}")
print(f"Períodos: {len(periodos)}\n")

# Calcular centroides por partido y período
centroides = df_todos.groupby(['periodo', 'party']).agg({
    'coord1D': 'mean',
    'coord2D': 'mean',
    'legislator_id': 'count'
}).reset_index()

centroides.rename(columns={'legislator_id': 'n_legisladores'}, inplace=True)

print("Centroides calculados:")
print(centroides.head(10))
print(f"\nTotal de centroides: {len(centroides)}")

# Filtrar partidos con al menos 3 observaciones en al menos un período
partidos_significativos = centroides[centroides['n_legisladores'] >= 3]['party'].unique(
)
print(
    f"\nPartidos con >= 3 legisladores en al menos un período: {len(partidos_significativos)}")
print(f"   {', '.join(sorted(partidos_significativos))}")

centroides_filtrados = centroides[centroides['party'].isin(
    partidos_significativos)]

# ============================================================================
# VISUALIZACIÓN 1: Trayectorias con flechas y etiquetas de partido
# ============================================================================

print("\n" + "=" * 70)
print("GENERANDO VISUALIZACIÓN 1: Trayectorias con flechas y etiquetas")
print("=" * 70)

fig, ax = plt.subplots(figsize=(16, 12))

for partido in sorted(partidos_significativos):
    df_partido = centroides_filtrados[centroides_filtrados['party'] == partido].copy(
    )

    # Ordenar por período
    df_partido['orden'] = df_partido['periodo'].map(
        {p: i for i, p in enumerate(periodos)})
    df_partido = df_partido.sort_values('orden')

    if len(df_partido) < 2:
        continue

    color = colores_partidos.get(partido, '#808080')

    # Obtener coordenadas
    coords = df_partido[['coord1D', 'coord2D']].values

    # Dibujar línea de trayectoria
    ax.plot(coords[:, 0], coords[:, 1],
            color=color, linewidth=2.5, alpha=0.4, linestyle='-', zorder=1)

    # Dibujar flechas entre períodos consecutivos
    for i in range(len(coords) - 1):
        x1, y1 = coords[i]
        x2, y2 = coords[i + 1]

        # Calcular punto medio para la flecha
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        # Dibujar flecha desde punto medio
        dx = x2 - x1
        dy = y2 - y1

        ax.annotate('', xy=(x2, y2), xytext=(mid_x, mid_y),
                    arrowprops=dict(arrowstyle='->', color=color,
                                    lw=3, alpha=0.8, mutation_scale=20),
                    zorder=5)

    # Marcar posiciones con círculos numerados
    for idx, (orden, row) in enumerate(df_partido.iterrows()):
        periodo_num = row['orden'] + 1
        ax.scatter(row['coord1D'], row['coord2D'],
                   color=color, s=250, alpha=0.9,
                   edgecolors='white', linewidth=2.5, zorder=10)
        ax.text(row['coord1D'], row['coord2D'], str(periodo_num),
                ha='center', va='center', fontsize=11,
                fontweight='bold', color='white', zorder=11)

    # Etiqueta del partido en posición final
    x_final, y_final = coords[-1]
    ax.text(x_final, y_final + 0.08, partido,
            ha='center', va='bottom', fontsize=11, fontweight='bold',
            color=color,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor=color, linewidth=2, alpha=0.9),
            zorder=12)

# Configuración del gráfico
ax.axhline(y=0, color='gray', linestyle='--', linewidth=1.2, alpha=0.6)
ax.axvline(x=0, color='gray', linestyle='--', linewidth=1.2, alpha=0.6)

ax.set_xlabel('Dimensión 1 (Económica: Izquierda ← → Derecha)',
              fontsize=14, fontweight='bold')
ax.set_ylabel('Dimensión 2 (Social/Coalición)',
              fontsize=14, fontweight='bold')
ax.set_title('Trayectorias de Partidos Políticos en el 55º Periodo Legislativo (2018-2022)\n' +
             'W-NOMINATE - 3 Períodos: Estallido Social y Plebiscito 2020',
             fontsize=16, fontweight='bold', pad=20)

# Añadir leyenda de períodos
legend_text = "Períodos:\n1️⃣ P1: Inicio → Estallido Social (11/03/2018 - 18/10/2019)\n" + \
              "2️⃣ P2: Estallido → Plebiscito 2020 (18/10/2019 - 25/10/2020)\n" + \
              "3️⃣ P3: Plebiscito → Fin PL (25/10/2020 - 10/03/2022)"

ax.text(0.02, 0.98, legend_text,
        transform=ax.transAxes, fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
plt.tight_layout()

archivo_salida1 = results_dir / 'trayectorias_wnominate_3periods_flechas.png'
plt.savefig(archivo_salida1, dpi=300, bbox_inches='tight')
print(f"Guardado: {archivo_salida1}")
plt.close()

# ============================================================================
# VISUALIZACIÓN 2: Trayectorias con marcadores diferenciados (inicio/fin)
# ============================================================================

print("\n" + "=" * 70)
print("GENERANDO VISUALIZACIÓN 2: Inicio (○) → Final (■)")
print("=" * 70)

fig, ax = plt.subplots(figsize=(16, 12))

for partido in sorted(partidos_significativos):
    df_partido = centroides_filtrados[centroides_filtrados['party'] == partido].copy(
    )

    df_partido['orden'] = df_partido['periodo'].map(
        {p: i for i, p in enumerate(periodos)})
    df_partido = df_partido.sort_values('orden')

    if len(df_partido) < 2:
        continue

    color = colores_partidos.get(partido, '#808080')
    coords = df_partido[['coord1D', 'coord2D']].values

    # Línea de trayectoria
    ax.plot(coords[:, 0], coords[:, 1],
            color=color, linewidth=3, alpha=0.6, linestyle='-', zorder=1)

    # Flechas
    for i in range(len(coords) - 1):
        x1, y1 = coords[i]
        x2, y2 = coords[i + 1]

        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color,
                                    lw=3.5, alpha=0.9, mutation_scale=25),
                    zorder=5)

    # Marcar INICIO (círculo)
    ax.scatter(coords[0, 0], coords[0, 1],
               color=color, s=350, alpha=0.95, marker='o',
               edgecolors='white', linewidth=3, zorder=10)

    # Marcar posiciones intermedias (círculos pequeños)
    if len(coords) > 2:
        for i in range(1, len(coords) - 1):
            ax.scatter(coords[i, 0], coords[i, 1],
                       color=color, s=200, alpha=0.9, marker='o',
                       edgecolors='white', linewidth=2, zorder=10)

    # Marcar FINAL (cuadrado)
    ax.scatter(coords[-1, 0], coords[-1, 1],
               color=color, s=350, alpha=0.95, marker='s',
               edgecolors='white', linewidth=3, zorder=10)

    # Etiqueta del partido
    x_final, y_final = coords[-1]
    ax.text(x_final + 0.03, y_final, partido,
            ha='left', va='center', fontsize=12, fontweight='bold',
            color=color,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                      edgecolor=color, linewidth=2.5, alpha=0.95),
            zorder=12)

# Configuración
ax.axhline(y=0, color='gray', linestyle='--', linewidth=1.2, alpha=0.6)
ax.axvline(x=0, color='gray', linestyle='--', linewidth=1.2, alpha=0.6)

ax.set_xlabel('Dimensión 1 (Económica: Izquierda ← → Derecha)',
              fontsize=14, fontweight='bold')
ax.set_ylabel('Dimensión 2 (Social/Coalición)',
              fontsize=14, fontweight='bold')
ax.set_title('Evolución de Posiciones Ideológicas: 55º Periodo Legislativo\n' +
             '⚫ Inicio (P1) → Trayectoria → ⬛ Final (P3)',
             fontsize=16, fontweight='bold', pad=20)

# Leyenda de períodos
legend_text = "Leyenda:\n⚫ P1: 11/03/2018 - 18/10/2019\n" + \
              "   ↓ Estallido Social\n" + \
              "● P2: 18/10/2019 - 25/10/2020\n" + \
              "   ↓ Plebiscito 2020\n" + \
              "⬛ P3: 25/10/2020 - 10/03/2022"

ax.text(0.02, 0.98, legend_text,
        transform=ax.transAxes, fontsize=11,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='#E8F4F8', alpha=0.9,
                  edgecolor='#2C3E50', linewidth=2))

ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
plt.tight_layout()

archivo_salida2 = results_dir / 'trayectorias_wnominate_3periods_inicio_fin.png'
plt.savefig(archivo_salida2, dpi=300, bbox_inches='tight')
print(f"Guardado: {archivo_salida2}")
plt.close()

# ============================================================================
# VISUALIZACIÓN 3: Análisis de cambios direccionales
# ============================================================================

print("\n" + "=" * 70)
print("ANÁLISIS DE CAMBIOS DIRECCIONALES")
print("=" * 70)

cambios_direccion = []

for partido in sorted(partidos_significativos):
    df_partido = centroides_filtrados[centroides_filtrados['party'] == partido].copy(
    )
    df_partido['orden'] = df_partido['periodo'].map(
        {p: i for i, p in enumerate(periodos)})
    df_partido = df_partido.sort_values('orden')

    if len(df_partido) != 3:  # Necesitamos los 3 períodos
        continue

    coords = df_partido[['coord1D', 'coord2D']].values

    # Vector P1 → P2
    v1 = coords[1] - coords[0]
    # Vector P2 → P3
    v2 = coords[2] - coords[1]

    # Calcular ángulo entre vectores
    norma_v1 = np.linalg.norm(v1)
    norma_v2 = np.linalg.norm(v2)

    if norma_v1 > 0.01 and norma_v2 > 0.01:
        cos_angulo = np.dot(v1, v2) / (norma_v1 * norma_v2)
        cos_angulo = np.clip(cos_angulo, -1, 1)
        angulo_grados = np.degrees(np.arccos(cos_angulo))

        # Calcular magnitudes de movimiento
        distancia_p1_p2 = norma_v1
        distancia_p2_p3 = norma_v2

        cambios_direccion.append({
            'partido': partido,
            'angulo_cambio': angulo_grados,
            'distancia_P1_P2': distancia_p1_p2,
            'distancia_P2_P3': distancia_p2_p3,
            'movimiento_total': distancia_p1_p2 + distancia_p2_p3,
            'cambio_significativo': angulo_grados > 45
        })

df_cambios = pd.DataFrame(cambios_direccion)

if len(df_cambios) > 0:
    print(f"\nPartidos analizados: {len(df_cambios)}")
    print(
        f"Cambios significativos (>45°): {df_cambios['cambio_significativo'].sum()}")

    df_cambios_ordenado = df_cambios.sort_values(
        'angulo_cambio', ascending=False)

    print("\nRANKING DE CAMBIOS DIRECCIONALES:")
    print(df_cambios_ordenado[['partido', 'angulo_cambio',
          'movimiento_total', 'cambio_significativo']].to_string(index=False))

    # Guardar análisis
    archivo_cambios = results_dir / 'analisis_cambios_direccionales_3periods.csv'
    df_cambios_ordenado.to_csv(archivo_cambios, index=False)
    print(f"\nAnálisis guardado: {archivo_cambios}")

# ============================================================================
# TABLAS RESUMEN
# ============================================================================

print("\n" + "=" * 70)
print("GENERANDO TABLAS RESUMEN")
print("=" * 70)

# Tabla pivot coord1D
pivot_coord1D = centroides_filtrados.pivot(
    index='party',
    columns='periodo',
    values='coord1D'
).round(3)

# Tabla pivot coord2D
pivot_coord2D = centroides_filtrados.pivot(
    index='party',
    columns='periodo',
    values='coord2D'
).round(3)

# Guardar
archivo_coord1D = results_dir / 'posiciones_coord1D_3periods.csv'
archivo_coord2D = results_dir / 'posiciones_coord2D_3periods.csv'

pivot_coord1D.to_csv(archivo_coord1D)
pivot_coord2D.to_csv(archivo_coord2D)

print(f"Posiciones coord1D guardadas: {archivo_coord1D}")
print(f"Posiciones coord2D guardadas: {archivo_coord2D}")

