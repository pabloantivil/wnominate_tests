import pymongo
import pandas as pd
import numpy as np
import json
import os
import shutil
from typing import Dict, List, Tuple

def get_mongodb_connection():
    """Conexión a tu instancia de MongoDB"""
    return pymongo.MongoClient('mongodb://localhost:27017/')

def export_votes_for_r_wnominate(db_name: str = "name_database", output_dir: str = None):
    """
    Exportar votos de MongoDB a un formato compatible con R para el análisis de W-NOMINATE

    Crea:
    1. votes_matrix.csv - Matriz en formato amplio (legisladores x votos)
    2. legislator_metadata.csv - Información del legislador
    3. vote_metadata.csv - Información de voto/llamada nominal
    4. r_wnominate_script.R - Script de R listo para ejecutar
    """
    
    print(f"🔍 Exportando votos desde {db_name} para el análisis R W-NOMINATE...")
    
    client = get_mongodb_connection()
    db = client[db_name]
    
    # Si no se especifica output_dir, usar data/input
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'input')
    
    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)

    # 1. Obtener todos los parlamentarios primero
    print("📥 Obteniendo parlamentarios...")
    parlamentarios_cursor = db["parlamentarios"].find({}, {
        "id": 1,
        "nombre": 1,
        "apellidoP": 1,
        "apellidoM": 1,
        "periodo": 1,
        "distrito": 1,
        "_id": 0
    })
    
    parlamentarios_data = list(parlamentarios_cursor)
    print(f"✅ Encontrados {len(parlamentarios_data)} parlamentarios")
    
    if len(parlamentarios_data) == 0:
        print("❌ No se encontraron parlamentarios! Verifique el nombre de la colección y los datos.")
        return None
    
    # 2. Obtener metadatos de votaciones
    print("📥 Obteniendo metadatos de votaciones...")
    votaciones_cursor = db["votaciones"].find({}, {
        "id": 1,
        "fecha": 1,
        "nombre": 1,
        "boletin": 1,
        "_id": 0
    })
    
    votaciones_data = list(votaciones_cursor)
    print(f"✅ Encontradas {len(votaciones_data)} votaciones")
    
    if len(votaciones_data) == 0:
        print("❌ No se encontraron votaciones! Verifique el nombre de la colección y los datos.")
        return None
    
    # 3. Obtener datos de votos de la colección VotosDiputados (según la estructura de su API)
    print("📥 Obteniendo votos individuales de VotosDiputados...")
    
    votes_data = []
    processed_votations = 0
    
    for votacion in votaciones_data:
        vot_id = votacion.get("id")
        if vot_id is None:
            continue
            
        # Obtener detalles de las votaciones de la colección VotosDiputados
        voto_doc = db["VotosDiputados"].find_one({"id": vot_id})
        
        if voto_doc and "detalle" in voto_doc:
            detalle = voto_doc["detalle"]
            # Detalle debería ser un diccionario que asigne las identificaciones parlamentarias a los valores de los votos
            for parl_id, vote_value in detalle.items():
                votes_data.append({
                    'legislator_id': str(parl_id),
                    'vote_id': str(vot_id),
                    'vote': vote_value
                })
        
        processed_votations += 1
        if processed_votations % 1000 == 0:
            print(f"   Procesados {processed_votations}/{len(votaciones_data)} votaciones...")

    print(f"✅ Encontrados {len(votes_data)} registros de votos individuales")

    if len(votes_data) == 0:
        print("❌ No se encontraron datos de votos! Verifique su esquema de almacenamiento de votos.")
        print("Se esperaba: campo 'detalle' en la colección VotosDiputados")
        return None
    
    # Convertir a DataFrame
    df = pd.DataFrame(votes_data)
    
    # Comprobar qué valores de voto tenemos realmente
    print("📊 Valores de voto encontrados:", df['vote'].value_counts().head(10))
    
    # 4. Asignar códigos de votación a valores numéricos para W-NOMINATE
    print("📊 Conversión de códigos de votación al formato W-NOMINATE...")
    
    # Basado en la función mapear_voto de su API:
    # if valor == 1: return 1   # Si
    # elif valor == 0: return -1  # No  
    # else: return 0   # Abstencion, Ausente, Excusado, etc.
    
    vote_mapping = {
        1: 1,     # Si -> Yea (1)
        0: 0,     # No -> Nay (0)
        2: 9,     # Abstencion -> No en la legislatura (9)
        3: 9,     # Ausente -> No en la legislatura (9)
        4: 9,     # Excusado -> No en la legislatura (9)
        # Añade cualquier otro valor que encuentres
    }
    
    # Aplicar mapeo
    df['vote_numeric'] = df['vote'].map(vote_mapping)
    
    # Manejar cualquier valor no asignado
    unmapped = df[df['vote_numeric'].isna()]
    if len(unmapped) > 0:
        print(f"⚠️  Encontrado {len(unmapped)} valores de voto no asignados:")
        print(unmapped['vote'].value_counts())
        df['vote_numeric'] = df['vote_numeric'].fillna(9)  # por defecto a "no en la legislatura"

    # 5. Crear matriz en formato ancho (legisladores x votos)
    print("📊 Creando matriz legislador x voto...")
    
    # Pivotar a formato ancho
    vote_matrix = df.pivot_table(
        index='legislator_id',
        columns='vote_id', 
        values='vote_numeric',
        fill_value=9  # No en la legislatura para combinaciones faltantes
    )

    print(f"📏 Dimensiones de la matriz: {vote_matrix.shape[0]} legisladores x {vote_matrix.shape[1]} votos")

    # 6. Filtrar por legisladores y votos con datos suficientes
    # Eliminar a los legisladores con muy pocos votos
    min_votes_per_legislator = 20
    legislator_vote_counts = (vote_matrix != 9).sum(axis=1)
    active_legislators = legislator_vote_counts >= min_votes_per_legislator

    print(f"🧹 Filtrando: {active_legislators.sum()} legisladores con >= {min_votes_per_legislator} votos")

    # Eliminar votos con muy pocos participantes
    min_legislators_per_vote = 10
    vote_participation = (vote_matrix != 9).sum(axis=0)
    active_votes = vote_participation >= min_legislators_per_vote

    print(f"🧹 Filtrando: {active_votes.sum()} votos con >= {min_legislators_per_vote} participantes")

    # Aplicar filtros
    filtered_matrix = vote_matrix.loc[active_legislators, active_votes]

    print(f"📐 Matriz final: {filtered_matrix.shape[0]} legisladores x {filtered_matrix.shape[1]} votos")

    # 7. Ordenar los votos cronológicamente
    vote_ids_in_matrix = [int(vid) for vid in filtered_matrix.columns.tolist()]
    votaciones_filtered = [v for v in votaciones_data if v.get('id') in vote_ids_in_matrix]
    
    if votaciones_filtered and 'fecha' in votaciones_filtered[0]:
        # Ordenar por fecha
        votaciones_filtered.sort(key=lambda x: x.get('fecha', ''))
        chronological_order = [str(v['id']) for v in votaciones_filtered]
        
        # Reordenar columnas de matriz por fecha
        available_cols = [col for col in chronological_order if col in filtered_matrix.columns]
        if available_cols:
            filtered_matrix = filtered_matrix[available_cols]
            print(f"📅 Votos ordenados cronológicamente")

    # 8. Exportar archivos de datos
    print("💾 Exportando archivos de datos...")

    # Matriz de votos
    filtered_matrix.to_csv(f"{output_dir}/votes_matrix.csv")

    # Metadatos de legisladores
    active_legislator_ids = [int(lid) for lid in filtered_matrix.index.tolist()]
    legislator_metadata = []
    
    for parl in parlamentarios_data:
        if parl.get('id') in active_legislator_ids:
            # Extraer partido de la matriz de período (para el período 2018-2022)
            partido = ''
            if 'periodo' in parl and parl['periodo']:
                for periodo in parl['periodo']:
                    if 'partido' in periodo and periodo['partido']:
                        partido = str(periodo['partido']).strip()
                        break
            
            # Construir nombre completo
            nombre_completo = f"{parl.get('nombre', '')} {parl.get('apellidoP', '')} {parl.get('apellidoM', '')}".strip()

            # Obtener información de región/distrito
            region = ''
            distrito = ''
            if 'distrito' in parl and parl['distrito'] and isinstance(parl['distrito'], list) and len(parl['distrito']) > 0:
                distrito_info = parl['distrito'][0]
                region = distrito_info.get('region', '')
                distrito = distrito_info.get('distrito', '')
            
            legislator_metadata.append({
                'legislator_id': str(parl.get('id')),
                'id': parl.get('id'),
                'nombres': nombre_completo,
                'partido': partido,
                'region': region,
                'distrito': distrito
            })
    
    legislator_df = pd.DataFrame(legislator_metadata)
    legislator_df.to_csv(f"{output_dir}/legislator_metadata.csv", index=False)

    # Metadatos de votaciones
    vote_metadata = []
    for votacion in votaciones_filtered:
        if str(votacion.get('id')) in filtered_matrix.columns:
            vote_metadata.append({
                'vote_id': str(votacion.get('id')),
                'id': votacion.get('id'),
                'fecha': votacion.get('fecha', ''),
                'nombre': votacion.get('nombre', ''),
                'boletin': votacion.get('boletin', '')
            })
    
    vote_df = pd.DataFrame(vote_metadata)
    vote_df.to_csv(f"{output_dir}/vote_metadata.csv", index=False)
    
    # 9. Crear un script R para el análisis W-NOMINATE
    r_script = f'''
# Análisis W-NOMINATE con anclajes de polaridad adecuados
# Usando Amaro Labra (PC, extrema izquierda) y Enrique Van Rysselberghe (UDI, extrema derecha)

library(wnominate)

# Cargar los datos desde data/input
votes_matrix <- as.matrix(read.csv("../../data/input/votes_matrix.csv", row.names = 1))
legislator_metadata <- read.csv("../../data/input/legislator_metadata.csv")
vote_metadata <- read.csv("../../data/input/vote_metadata.csv")

# Relacionar los metadatos de la legisladora con la matriz de votos
vote_matrix_ids <- as.numeric(rownames(votes_matrix))
matched_metadata <- legislator_metadata[legislator_metadata$legislator_id %in% vote_matrix_ids, ]

# Reordenar los metadatos para que coincidan con el orden de la matriz de votos
matched_metadata <- matched_metadata[match(vote_matrix_ids, matched_metadata$legislator_id), ]

# Crear un objeto rollcall: permitirle utilizar códigos predeterminados
rc <- rollcall(votes_matrix)

cat("Resumen del conjunto de datos:\n")
cat("Legisladores:", nrow(votes_matrix), "\n")
cat("Votos:", ncol(votes_matrix), "\n")

# Definir anclajes de polaridad utilizando posiciones de fila
# Amaro Labra (1043, PC, extrema izquierda) debería ser negativo (izquierda) - posición 42
# Enrique Van Rysselberghe (959, UDI, extrema derecha) debería ser positivo (derecha) - posición 140
amaro_pos <- which(rownames(votes_matrix) == "1043")
enrique_pos <- which(rownames(votes_matrix) == "959")
polarity_anchors <- c(amaro_pos, enrique_pos) # posiciones para Amaro Labra y Van Rysselberghe

cat("\nUsando anclajes de polaridad:\n")
cat("Ancla izquierda (negativa): Posición", amaro_pos, "- Legislador 1043 (Amaro Labra, PC)\n")
cat("Ancla derecha (positiva): Posición", enrique_pos, "- Legislador 959 (Enrique Van Rysselberghe, UDI)\n")

# Ejecute W-NOMINATE con la especificación de polaridad adecuada
result <- wnominate(rc,
    dims = 2,
    trials = 3,
    polarity = polarity_anchors,
    verbose = TRUE
)

# Extraer coordenadas
coordinates <- result$legislators[, c("coord1D", "coord2D")]
# Agregar IDs de legisladores originales como nombres de fila
coordinates <- cbind(legislator_id = rownames(votes_matrix), coordinates)
rownames(coordinates) <- rownames(votes_matrix)

cat("\nResultados de W-NOMINATE con anclajes de polaridad:\n")
cat("Clasificación Correcta: ", result$fits[1], "%\n")
cat("APRE: ", result$fits[2], "\n")
cat("GMP: ", result$fits[3], "\n")

# Verificar que la polaridad es correcta (usar IDs de legisladores originales)
amaro_coords <- coordinates[rownames(coordinates) == "1043", c("coord1D", "coord2D")]
enrique_coords <- coordinates[rownames(coordinates) == "959", c("coord1D", "coord2D")]

# Convertir a vectores numéricos para una impresión adecuada
amaro_coord1D <- as.numeric(amaro_coords[1, "coord1D"])
amaro_coord2D <- as.numeric(amaro_coords[1, "coord2D"])
enrique_coord1D <- as.numeric(enrique_coords[1, "coord1D"])
enrique_coord2D <- as.numeric(enrique_coords[1, "coord2D"])

cat("\nVerificación de Polaridad:\n")
cat("Amaro Labra (PC, debería ser negativo):", amaro_coord1D, amaro_coord2D, "\n")
cat("Enrique Van Rysselberghe (UDI, debería ser positivo):", enrique_coord1D, enrique_coord2D, "\n")

# Guardar resultados con la orientación adecuada en data/output
coordinates_with_metadata <- merge(coordinates, legislator_metadata,
    by.x = "row.names", by.y = "legislator_id",
    all.x = TRUE
)
names(coordinates_with_metadata)[1] <- "legislator_id"

# Crear directorio de salida si no existe
output_dir <- "../../data/output"
if (!dir.exists(output_dir)) {{
    dir.create(output_dir, recursive = TRUE)
}}

write.csv(coordinates_with_metadata, file.path(output_dir, "wnominate_coordinates.csv"), row.names = FALSE)

cat("\nCoordenadas guardadas en:", file.path(output_dir, "wnominate_coordinates.csv"), "\n")

# Guardar parámetros de votación
write.csv(result$rollcalls, file.path(output_dir, "wnominate_bill_parameters.csv"), row.names = TRUE)

cat("Bill parameters guardados en:", file.path(output_dir, "wnominate_bill_parameters.csv"), "\n")
'''

    # Escriba el script R solo si no existe o cree una copia de seguridad
    # Guardar scripts R en scripts/r
    r_scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'r')
    os.makedirs(r_scripts_dir, exist_ok=True)
    
    r_script_path = os.path.join(r_scripts_dir, "r_wnominate_script.R")
    if os.path.exists(r_script_path):
        # Crear una copia de seguridad de un archivo existente
        backup_path = os.path.join(r_scripts_dir, "r_wnominate_script_backup.R")
        shutil.copy2(r_script_path, backup_path)
        print(f"📝 El script R ya existe. Copia de seguridad creada.: {backup_path}")
        print("📝 Manteniendo su script R existente con cualquier modificación manual.")
    else:
        # Escribir un nuevo script R
        with open(r_script_path, "w", encoding="utf-8") as f:
            f.write(r_script)
        print(f"📝 Se creó un nuevo script R: {r_script_path}")
    
    
    # 10. Crear script de comparación
    comparison_script = '''
# Comparar los resultados de R W-NOMINATE con los resultados de Python pynominate

# Cargar resultados de R  
r_coords <- read.csv("../../data/output/wnominate_coordinates.csv")

# Cargar resultados de Python (ajustar la ruta según sea necesario)
# python_file <- "../../data/output/all_votes_dwnominate.json"
# python_results <- jsonlite::fromJSON(python_file)

# TODO: Agregar el análisis de Procrustes para alinear los dos sistemas de coordenadas
# TODO: Calcular la correlación entre las coordenadas de R y Python
# TODO: Identificar discrepancias importantes

cat("Utilizar este script para comparar los resultados de R y Python después de ejecutar ambos análisis.\\n")
'''
    
    compare_script_path = os.path.join(r_scripts_dir, "compare_results.R")
    with open(compare_script_path, "w") as f:
        f.write(comparison_script)
    
    print(f"\n🎯 ¡Exportación completa!")
    print(f"   📁 Datos guardados en: {output_dir}/")
    print(f"      📄 votes_matrix.csv - {filtered_matrix.shape[0]}x{filtered_matrix.shape[1]} matriz de votos")
    print(f"      📄 legislator_metadata.csv - {len(legislator_metadata)} legisladores")
    print(f"      📄 vote_metadata.csv - {len(vote_metadata)} votos")
    print(f"   � Scripts R guardados en: {r_scripts_dir}/")
    print(f"      �📄 r_wnominate_script.R - Análisis R listo para ejecutar")
    print(f"      📄 compare_results.R - Para comparar resultados de R vs Python")
    
    print(f"\n🚀 Próximos pasos:")
    print(f"   1. cd {r_scripts_dir}")
    print(f"   2. Rscript r_wnominate_script.R")
    print(f"   3. Los resultados se guardarán en data/output/")
    print(f"   4. Comparar con resultados de pynominate")
    
    return {
        'matrix_shape': filtered_matrix.shape,
        'export_dir': output_dir,
        'vote_mapping': vote_mapping
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Exportar votos de MongoDB para análisis R W-NOMINATE")
    parser.add_argument("--db-name", default="database_example", help="Nombre de la base de datos MongoDB")
    parser.add_argument("--output-dir", default="r_wnominate_data", help="Directorio de salida")

    args = parser.parse_args()
    
    result = export_votes_for_r_wnominate(args.db_name, args.output_dir)
    print(f"\n✅ Exportación exitosa: {result}")