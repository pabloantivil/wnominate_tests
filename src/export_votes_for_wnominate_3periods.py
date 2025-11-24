"""
Script para dividir las votaciones del 55º PL en 3 períodos según eventos políticos:
- P1: 11/03/2018 - 18/10/2019 (Inicio PL hasta Estallido Social)
- P2: 18/10/2019 - 25/10/2020 (Estallido Social hasta Plebiscito 2020)
- P3: 25/10/2020 - 10/03/2022 (Plebiscito 2020 hasta Fin PL)
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("DIVISIÓN DE VOTACIONES EN 3 PERÍODOS (55º PL)")
print("=" * 70)

# Directorios
input_dir = Path('data/wnominate/input')
output_dir = Path('data/wnominate_3periods/input')
output_dir.mkdir(parents=True, exist_ok=True)

# Cargar datos
print("\nCargando datos...")
votes_matrix = pd.read_csv(input_dir / 'votes_matrix.csv', index_col=0)
vote_metadata = pd.read_csv(input_dir / 'vote_metadata.csv')
legislator_metadata = pd.read_csv(input_dir / 'legislator_metadata.csv')

print(
    f"Matriz de votos: {votes_matrix.shape[0]} legisladores × {votes_matrix.shape[1]} votaciones")
print(f"Metadata de votaciones: {len(vote_metadata)} registros")
print(f"Metadata de legisladores: {len(legislator_metadata)} registros")

# Convertir fechas
vote_metadata['fecha'] = pd.to_datetime(vote_metadata['fecha'])

print(f"\nRango de fechas:")
print(f"   Inicio: {vote_metadata['fecha'].min()}")
print(f"   Fin: {vote_metadata['fecha'].max()}")

# Definir límites de períodos
fecha_estallido = datetime(2019, 10, 18)
fecha_plebiscito = datetime(2020, 10, 25)

# Clasificar votaciones por período
vote_metadata['periodo'] = 'P3'  # Por defecto P3
vote_metadata.loc[vote_metadata['fecha'] < fecha_estallido, 'periodo'] = 'P1'
vote_metadata.loc[(vote_metadata['fecha'] >= fecha_estallido) &
                  (vote_metadata['fecha'] < fecha_plebiscito), 'periodo'] = 'P2'

# Resumen por período
print("\nDistribución de votaciones por período:")
for periodo in ['P1', 'P2', 'P3']:
    df_periodo = vote_metadata[vote_metadata['periodo'] == periodo]
    print(f"\n{periodo}:")
    print(f"   Votaciones: {len(df_periodo)}")
    print(f"   Fecha inicio: {df_periodo['fecha'].min()}")
    print(f"   Fecha fin: {df_periodo['fecha'].max()}")
    print(
        f"   Duración: {(df_periodo['fecha'].max() - df_periodo['fecha'].min()).days} días")

# Verificar que vote_id coincida con columnas de votes_matrix
vote_ids_metadata = set(vote_metadata['vote_id'].astype(str))
vote_ids_matrix = set(votes_matrix.columns)

print(f"\nVerificación de coherencia:")
print(f"   Vote IDs en metadata: {len(vote_ids_metadata)}")
print(f"   Vote IDs en matriz: {len(vote_ids_matrix)}")
print(f"   Coincidencias: {len(vote_ids_metadata & vote_ids_matrix)}")

# Exportar matrices por período
print("\n" + "=" * 70)
print("EXPORTANDO MATRICES POR PERÍODO")
print("=" * 70)

for periodo in ['P1', 'P2', 'P3']:
    print(f"\nProcesando {periodo}...")

    # Obtener vote_ids del período
    vote_ids_periodo = vote_metadata[vote_metadata['periodo']
                                     == periodo]['vote_id'].astype(str).tolist()

    # Filtrar columnas que existen en votes_matrix
    vote_ids_disponibles = [
        vid for vid in vote_ids_periodo if vid in votes_matrix.columns]

    if len(vote_ids_disponibles) == 0:
        print(f" {periodo}: No hay votaciones disponibles en la matriz")
        continue

    # Extraer submatriz
    votes_periodo = votes_matrix[vote_ids_disponibles].copy()

    # Filtrar legisladores con suficientes votos
    votos_validos_por_legislador = (votes_periodo != 9).sum(axis=1)
    legisladores_activos = votos_validos_por_legislador >= 20

    votes_periodo_filtrado = votes_periodo[legisladores_activos]

    print(f"   Votaciones: {len(vote_ids_disponibles)}")
    print(f"   Legisladores originales: {len(votes_periodo)}")
    print(
        f"   Legisladores filtrados (≥20 votos): {len(votes_periodo_filtrado)}")

    # Guardar matriz
    archivo_matriz = output_dir / f'votes_matrix_{periodo.lower()}.csv'
    votes_periodo_filtrado.to_csv(archivo_matriz)
    print(f"Guardado: {archivo_matriz}")

    # Guardar metadata de votaciones del período
    vote_meta_periodo = vote_metadata[vote_metadata['vote_id'].astype(
        str).isin(vote_ids_disponibles)]
    archivo_vote_meta = output_dir / f'vote_metadata_{periodo.lower()}.csv'
    vote_meta_periodo.to_csv(archivo_vote_meta, index=False)
    print(f"Guardado: {archivo_vote_meta}")

# Copiar metadata de legisladores (es la misma para todos los períodos)
legislator_metadata.to_csv(output_dir / 'legislator_metadata.csv', index=False)
print(f"\nMetadata de legisladores copiada")
print(f"\nArchivos generados en: {output_dir}/")
print("  - votes_matrix_p1.csv")
print("  - votes_matrix_p2.csv")
print("  - votes_matrix_p3.csv")
print("  - vote_metadata_p1.csv")
print("  - vote_metadata_p2.csv")
print("  - vote_metadata_p3.csv")
print("  - legislator_metadata.csv")

print("\nSiguiente paso: Ejecutar r_wnominate_3periods_script.R")
