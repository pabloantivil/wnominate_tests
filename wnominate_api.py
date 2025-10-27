#!/usr/bin/env python
"""
W-NOMINATE API Module

Este módulo consolida la funcionalidad de los archivos test_update_nominate.py y 
generar_payload.py, proporcionando una única interfaz para generar cálculos de W-NOMINATE 
basados ​​en una lista de ID de votación. Se conecta directamente a MongoDB, obtiene los datos 
necesarios, genera el payload en memoria y ejecuta el cálculo de W-NOMINATE.
Este módulo está diseñado para ser llamado desde una API de Golang en un entorno Dockerizado.
"""

from pynominate.nominate import update_nominate
import os
import sys
import json
import argparse
import hashlib
import datetime
import numpy as np
import pymongo
from typing import List, Dict, Any, Optional, Union

# Asegúrese de que Pynominate esté en la ruta
sys.path.append('.')

# Configuración: cambie esta única variable para cambiar los nombres de las bases de datos
DEFAULT_DB_NAME = "database_example"


def get_mongodb_connection() -> pymongo.MongoClient:
    """
    Conéctese a MongoDB y gestione entornos de desarrollo y producción.
    En desarrollo, se conecta al host local.
    En producción (Docker), se conecta al contenedor de MongoDB.

    Returns:
        pymongo.MongoClient: A MongoDB client instance
    """
    # Comprobar la variable de entorno (se puede configurar en Docker)
    mongo_url = os.environ.get('MONGODB_URL', 'mongodb://localhost:27017/')
    # default_mongo_url = 'mongodb://localhost:27017/'
    # Para el entorno Docker, utilice el nombre del servicio si está disponible
    if os.environ.get('DOCKER_ENV') == 'true':
        mongo_url = os.environ.get(
            'MONGODB_URL', 'mongodb://database_example-mongodb:27017/')

    print(f"Intentando conectar a MongoDB en: {mongo_url}")
    print(f"Variables de entorno:")
    print(f"  MONGODB_URL: {os.environ.get('MONGODB_URL', 'NO CONFIGURADO')}")
    print(f"  DOCKER_ENV: {os.environ.get('DOCKER_ENV', 'NO CONFIGURADO')}")

    try:
        client = pymongo.MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        # Probar la conexión
        client.admin.command('ping')
        print(f"Conexión exitosa a MongoDB")
        return client
    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        raise


def generate_vote_hash(votation_ids: List[int], calculation_params: Optional[Dict[str, Any]] = None) -> str:
    """
    Generar un hash estable para un conjunto de identificadores de votación y parámetros de cálculo.

    Args:
        votation_ids: Lista de IDS de votación
        calculation_params: Parámetros de cálculo opcionales para incluir en el hash

    Returns:
        SHA256 hash string para la combinación
    """
    # Ordenar los ID de votación para garantizar un orden coherente
    sorted_ids = sorted(votation_ids)

    # Crear cadena de entrada para el hash
    hash_input = ",".join(map(str, sorted_ids))

    # Incluir parámetros de cálculo si se proporcionan
    if calculation_params:
        # Ordenar parámetros para un hash coherente
        sorted_params = sorted(calculation_params.items())
        params_str = ",".join(f"{k}:{v}" for k, v in sorted_params)
        hash_input += f"|{params_str}"

    # Generar hash SHA256
    hash_object = hashlib.sha256(hash_input.encode('utf-8'))
    return hash_object.hexdigest()


def store_wnominate_result(
    result_hash: str,
    votation_ids: List[int],
    calculation_params: Dict[str, Any],
    results: Dict[str, Any],
    db_name: str = DEFAULT_DB_NAME
) -> bool:
    """
    Almacenar los resultados del cálculo W-NOMINATE en MongoDB.

    Args:
        result_hash: El hash que identifica este cálculo
        votation_ids: Lista de IDs de votación utilizados
        calculation_params: Parámetros utilizados para el cálculo
        results: Los resultados del cálculo W-NOMINATE
        db_name: Nombre de la base de datos MongoDB

    Returns:
        Verdadero si se almacenó correctamente, falso en caso contrario
    """
    try:
        client = get_mongodb_connection()
        db = client[db_name]
        results_collection = db["dwnominate_calculations"]

        # Preparar el documento para su almacenamiento.
        result_document = {
            "result_hash": result_hash,
            # Almacenar ordenado para mayor consistencia
            "votation_ids": sorted(votation_ids),
            "votation_count": len(votation_ids),
            "calculation_params": calculation_params,
            "results": results,
            "created_at": datetime.datetime.utcnow(),
            "last_accessed": datetime.datetime.utcnow(),
            "access_count": 1
        }

        # Almacenar el resultado
        results_collection.insert_one(result_document)
        print(f"Resultado almacenado con hash: {result_hash}")
        return True

    except Exception as e:
        print(f"Error al almacenar resultado: {e}")
        return False


def create_wnominate_indexes(db_name: str = DEFAULT_DB_NAME) -> None:
    """
    Crear índices para la colección dwnominate_calculations para lograr un rendimiento óptimo.

    Args:
        db_name: Nombre de la base de datos MongoDB
    """
    try:
        client = get_mongodb_connection()
        db = client[db_name]
        results_collection = db["dwnominate_calculations"]

        # Crear índices
        results_collection.create_index("result_hash", unique=True)
        results_collection.create_index("created_at")
        results_collection.create_index("votation_count")
        results_collection.create_index("last_accessed")

        print("Índices creados para la colección dwnominate_calculations")

    except Exception as e:
        print(f"Error al crear índices: {e}")


def cleanup_old_results(
    days_old: int = 30,
    db_name: str = DEFAULT_DB_NAME
) -> int:
    """
    Limpia los antiguos resultados de W-NOMINATE a los que no se ha accedido recientemente.

    Args:
        days_old: Eliminar resultados más antiguos que este número de días
        db_name: Nombre de la base de datos MongoDB

    Returns:
        Número de resultados eliminados
    """
    try:
        client = get_mongodb_connection()
        db = client[db_name]
        results_collection = db["dwnominate_calculations"]

        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_old)

        result = results_collection.delete_many({
            "last_accessed": {"$lt": cutoff_date}
        })

        print(f"Se limpiaron {result.deleted_count} resultados antiguos")
        return result.deleted_count

    except Exception as e:
        print(f"Error al limpiar resultados: {e}")
        return 0


def generate_payload(votation_ids: List[int], db_name: str = DEFAULT_DB_NAME) -> Dict[str, Any]:
    """
    Generar un payload para el cálculo de W-NOMINATE basado en una lista de IDs de votación.

    Args:
        votation_ids: Lista de IDs de votación para incluir en el payload
        db_name: Nombre de la base de datos MongoDB a la que conectarse

    Returns:
        Diccionario que contiene la carga útil generada
    """
    # Conectar a MongoDB
    try:
        client = get_mongodb_connection()
        print(f"Cliente MongoDB creado exitosamente")

        db = client[db_name]
        print(f"Conectado a la base de datos: {db_name}")

        # Probar conexión a la base de datos
        try:
            # Listar colecciones para verificar conexión
            collections = db.list_collection_names()
            print(f"Colecciones disponibles: {collections}")
        except Exception as e:
            print(f"Error al listar colecciones: {e}")
            raise

    except Exception as e:
        print(f"Error al conectar a MongoDB: {e}")
        raise

    votos_diputados = db["VotosDiputados"]
    parlamentarios = db["parlamentarios"]
    votaciones = db["votaciones"]

    print(f"Orden original de IDs de votación: {votation_ids}")

    # Probar acceso a colecciones y existencia de datos
    try:
        # Contar documentos en cada colección
        votos_count = votos_diputados.count_documents({})
        parlamentarios_count = parlamentarios.count_documents({})
        votaciones_count = votaciones.count_documents({})

        print(f"Conteo de documentos en colecciones:")
        print(f"  VotosDiputados: {votos_count}")
        print(f"  parlamentarios: {parlamentarios_count}")
        print(f"  votaciones: {votaciones_count}")

        # Verificar si existen IDs de votación específicos
        votaciones_exist = votaciones.count_documents(
            {"id": {"$in": votation_ids}})
        print(
            f"  votaciones que coinciden con IDs {votation_ids}: {votaciones_exist}")

        if votaciones_exist == 0:
            print(
                f"ADVERTENCIA: No se encontraron votaciones para los IDs {votation_ids}")
            # Intentar encontrar algunos IDs de votación de ejemplo
            sample_votaciones = list(votaciones.find({}, {"id": 1}).limit(5))
            sample_ids = [v.get("id") for v in sample_votaciones]
            print(
                f"IDs de votación de muestra en la base de datos: {sample_ids}")

    except Exception as e:
        print(f"Error al verificar colecciones: {e}")
        raise

    # Obtener todos los parlamentarios
    try:
        todos_diputados = list(parlamentarios.find())
        print(f"Se encontraron {len(todos_diputados)} parlamentarios")
        if len(todos_diputados) == 0:
            print("ADVERTENCIA: No se encontraron parlamentarios en la base de datos")
    except Exception as e:
        print(f"Error al obtener parlamentarios: {e}")
        raise

    # Obtener votaciones solicitadas
    try:
        # Intentar con IDs tanto enteros como cadenas en caso de discrepancia de tipo de dato
        votaciones_list = list(votaciones.find({"id": {"$in": votation_ids}}))
        print(
            f"Se encontraron {len(votaciones_list)} votaciones para IDs enteros {votation_ids}")

        if len(votaciones_list) == 0:
            # Intentar con IDs como cadenas
            string_ids = [str(id) for id in votation_ids]
            votaciones_list = list(
                votaciones.find({"id": {"$in": string_ids}}))
            print(
                f"Se encontraron {len(votaciones_list)} votaciones para IDs de cadena {string_ids}")

        if len(votaciones_list) == 0:
            print(
                f"ERROR: No se encontraron votaciones para los IDs especificados: {votation_ids}")
            # Verificar qué hay realmente en la colección de votaciones
            print("Verificando estructura de la colección votaciones...")
            sample_votacion = votaciones.find_one()
            if sample_votacion:
                print(
                    f"Claves del documento de votación de muestra: {list(sample_votacion.keys())}")
                print(
                    f"Campo ID de votación de muestra: {sample_votacion.get('id', 'NO ENCONTRADO')}")
                print(
                    f"Tipo de ID de votación de muestra: {type(sample_votacion.get('id'))}")
            else:
                print("No se encontraron documentos en la colección votaciones")
            raise ValueError(
                f"No se encontraron votaciones para los IDs: {votation_ids}")

    except Exception as e:
        print(f"Error al obtener votaciones: {e}")
        raise

    # Ordenar votaciones por fecha si está disponible
    if votaciones_list and all('fecha' in v for v in votaciones_list):
        votaciones_list.sort(key=lambda x: x['fecha'])
        print(
            f"Votaciones ordenadas por fecha: {[v['id'] for v in votaciones_list]}")
    else:
        # Si las fechas no están disponibles, intentar preservar el orden original
        votation_id_to_index = {id: i for i, id in enumerate(votation_ids)}
        votaciones_list.sort(
            key=lambda x: votation_id_to_index.get(x.get('id', 0), 999999))
        print(
            f"Orden original preservado: {[v['id'] for v in votaciones_list]}")

    # Inicializar estructura del payload
    payload = {
        'votes': [],
        'memberwise': [],
        'idpt': {},
        'bp': {},
        'bw': {'b': 8.8633, 'w': 0.4619}  # Valores por defecto
    }

    votos_por_diputado = {}

    # Procesar cada votación
    print(f"Procesando votaciones en este orden:")
    for idx, votacion in enumerate(votaciones_list):
        vot_id = votacion["id"]
        print(f"  {idx+1}. ID: {vot_id}" +
              (f", Fecha: {votacion.get('fecha', 'N/A')}" if 'fecha' in votacion else ""))
        voto_doc = votos_diputados.find_one({"id": vot_id})

        if not voto_doc:
            print(
                f"Advertencia: No se encontraron datos de voto para el ID de votación {vot_id}")
            continue

        detalle = voto_doc.get("detalle", {})
        votos = []

        # Procesar votos para cada parlamentario
        for diputado in todos_diputados:
            dip_id_str = str(diputado.get("id"))
            miembro = f"M{dip_id_str}"

            # Obtener voto si existe; de lo contrario abstención/ausente (2)
            voto_original = detalle.get(dip_id_str, 2)
            voto_mapeado = mapear_voto(voto_original)
            votos.append((voto_mapeado, miembro))

            # Agregar a memberwise
            if miembro not in votos_por_diputado:
                votos_por_diputado[miembro] = []
            votos_por_diputado[miembro].append((voto_mapeado, f"V{vot_id}"))

            # Inicializar idpt si no existe todavía
            if miembro not in payload['idpt']:
                # Usar inicialización aleatoria similar a R W-NOMINATE
                # R usa inicios aleatorios sofisticados, usaremos valores aleatorios pequeños dentro del círculo unitario
                import random
                import math

                # Generar punto aleatorio dentro del círculo unitario (similar al enfoque de R)
                angle = random.uniform(0, 2 * math.pi)
                # Comenzar más cerca del centro pero no en el origen
                radius = random.uniform(0.1, 0.5)

                payload['idpt'][miembro] = [
                    radius * math.cos(angle),  # coordenada x
                    radius * math.sin(angle)   # coordenada y
                ]

        # Agregar votación al payload
        payload['votes'].append({
            'id': f"V{vot_id}",
            'update': True,
            'votes': votos
        })

        # Establecer parámetro bp
        payload['bp'][f"V{vot_id}"] = [
            0.0, 0.0, 0.1, 0.1]  # Valores por defecto

    # Verificar el orden en el payload final
    payload_votation_order = [int(v['id'][1:]) for v in payload['votes']]
    print(f"Orden de votaciones en el payload final: {payload_votation_order}")

    # Construir memberwise
    for member_id, votos in votos_por_diputado.items():
        payload['memberwise'].append({
            'icpsr': member_id,
            'update': True,
            'votes': votos
        })

    return payload


def mapear_voto(valor: int) -> int:
    """
    Asignar valores de votos originales al formato W-NOMINATE.
    ASIGNACIÓN CORREGIDA (coincide con el formato R W-NOMINATE):
    - 1 (Yes) → 1 (Yea)
    - 0 (No) → 0 (Nay)  
    - Other (Abstention/Absent) → 9 (Not in legislature)

    Args:
        valor: Valor de voto original

    Returns:
        Mapped vote value: 1 (Yes), 0 (No), 9 (Abstention/Absent)
    """
    if valor == 1:
        return 1   # Yes
    elif valor == 0:
        return 0   # No (CORREGIDO: era -1, lo que causaba violaciones del círculo unitario)
    else:
        # Abstention or Absent (CORREGIDO: era 0, ahora coincide con el notInLegis de R)
        return 9


def apply_polarity_correction(
    results: Dict[str, Any],
    db_name: str = DEFAULT_DB_NAME
) -> Dict[str, Any]:
    """
    Aplicar corrección de polaridad a los resultados de W-NOMINATE según las posiciones conocidas de los partidos.
    Esto imita el parámetro "polaridad" de la función wnominate() de R.

    Args:
        results: Resultados brutos de W-NOMINATE
        db_name: Nombre de la base de datos para la búsqueda de partidos

    Returns:
        Resultados con polaridad corregida
    """
    if 'idpt' not in results:
        print("⚠️  No se encontraron puntos ideales para corrección de polaridad")
        return results

    print("🔄 Aplicando corrección de polaridad basada en posiciones de partidos chilenos...")

    try:
        # Conectar a MongoDB para obtener información de partidos
        client = get_mongodb_connection()
        db = client[db_name]
        parlamentarios = db["parlamentarios"]

        # Definir posiciones esperadas de partidos (espectro político chileno)
        left_wing_parties = ["PC", "PS", "PPD", "RD", "PH",
                             "COM", "PEV"]  # Deberían ser negativos (izquierda)
        # Deberían ser positivos (derecha)
        right_wing_parties = ["UDI", "RN", "EVOP"]

        # Calcular coordenadas medias para cada partido
        party_means = {}
        party_counts = {}

        for member_id, member_data in results['idpt'].items():
            if isinstance(member_data, dict) and 'idpt' in member_data:
                coords = member_data['idpt']
            else:
                coords = member_data

            if len(coords) >= 2:  # Asegurar que tenemos ambas dimensiones
                # Buscar partido para este miembro
                numeric_id = int(member_id) if str(
                    member_id).isdigit() else None
                if numeric_id:
                    parlamentario = parlamentarios.find_one({"id": numeric_id})
                    if parlamentario and "periodo" in parlamentario:
                        # Extraer partido de la estructura periodo anidada
                        for periodo in parlamentario["periodo"]:
                            if "partido" in periodo:
                                party = periodo["partido"]
                                if party not in party_means:
                                    party_means[party] = [0.0, 0.0]
                                    party_counts[party] = 0

                                # Primera dimensión
                                party_means[party][0] += coords[0]
                                # Segunda dimensión
                                party_means[party][1] += coords[1]
                                party_counts[party] += 1
                                break  # Usar el primer partido válido encontrado

        # Calcular coordenadas promedio por partido
        for party in party_means:
            if party_counts[party] > 0:
                party_means[party][0] /= party_counts[party]
                party_means[party][1] /= party_counts[party]

        print(f"📊 Coordenadas de partidos antes de la corrección:")
        for party, coords in party_means.items():
            print(
                f"   {party}: dim1={coords[0]:.3f}, dim2={coords[1]:.3f} (n={party_counts[party]})")

        # Determinar si necesitamos invertir dimensiones
        flip_dim1 = False
        flip_dim2 = False

        # Verificar primera dimensión: izquierda debería ser negativa, derecha debería ser positiva
        left_mean_dim1 = np.mean([party_means[p][0]
                                 for p in left_wing_parties if p in party_means])
        right_mean_dim1 = np.mean([party_means[p][0]
                                  for p in right_wing_parties if p in party_means])

        if not np.isnan(left_mean_dim1) and not np.isnan(right_mean_dim1):
            if left_mean_dim1 > right_mean_dim1:  # Izquierda es más positiva que derecha
                flip_dim1 = True
                print(
                    f"🔄 Invirtiendo primera dimensión: promedio izquierda ({left_mean_dim1:.3f}) > promedio derecha ({right_mean_dim1:.3f})")

        # Para la segunda dimensión, podemos usar una heurística más simple o posiciones en temas sociales
        # Por ahora, asumiremos orientación estándar a menos que detectemos que se necesita un cambio claro

        # Aplicar correcciones a todas las coordenadas
        if flip_dim1 or flip_dim2:
            corrected_results = results.copy()

            for member_id, member_data in corrected_results['idpt'].items():
                if isinstance(member_data, dict) and 'idpt' in member_data:
                    coords = member_data['idpt']
                    if flip_dim1:
                        coords[0] = -coords[0]
                    if flip_dim2:
                        coords[1] = -coords[1]
                else:
                    # Manejar formato de coordenadas directas
                    if flip_dim1:
                        member_data[0] = -member_data[0]
                    if flip_dim2:
                        member_data[1] = -member_data[1]

            print(
                f"✅ Corrección de polaridad aplicada: inversión_dim1={flip_dim1}, inversión_dim2={flip_dim2}")
            return corrected_results
        else:
            print(
                "✅ No se necesita corrección de polaridad - la orientación parece correcta")
            return results

    except Exception as e:
        print(f"⚠️  Error en corrección de polaridad: {e}")
        print("   Devolviendo resultados originales sin corrección")
        return results


def find_polarity_anchors(
    votation_ids: List[int],
    db_name: str = DEFAULT_DB_NAME
) -> Dict[str, List[float]]:
    """
    Encuentrar legisladores extremos para utilizar como anclas de polaridad, imitando el parámetro de polaridad de R W-NOMINATE.

    Args:
        votation_ids: Lista de IDs de votación para analizar
        db_name: Nombre de la base de datos

    Returns:
        Dict que asigna los identificadores de legisladores a sus coordenadas de anclaje
    """
    print("🔍 Buscando anclajes de polaridad basados en partidos políticos chilenos...")

    try:
        client = get_mongodb_connection()
        db = client[db_name]
        parlamentarios = db["parlamentarios"]

        # Definir partidos extremos en la política chilena
        # Partidos comunistas (más de izquierda)
        left_extreme_parties = ["PC", "COM"]
        # Unión Demócrata Independiente (más de derecha)
        right_extreme_parties = ["UDI"]

        # Encontrar legisladores de partidos extremos
        left_anchor = None
        right_anchor = None

        # Buscar anclaje de izquierda
        for party in left_extreme_parties:
            cursor = parlamentarios.find({
                "periodo.partido": party
            }).limit(5)  # Obtener algunos candidatos

            for parlamentario in cursor:
                member_id = str(parlamentario["id"])
                # Asegurarse de que estén en nuestros datos
                if member_id not in [str(vid) for vid in votation_ids]:
                    continue
                left_anchor = member_id
                print(
                    f"📍 Anclaje izquierdo encontrado: {parlamentario.get('nombre', 'Desconocido')} (ID: {member_id}, Partido: {party})")
                break
            if left_anchor:
                break

        # Buscar anclaje de derecha
        for party in right_extreme_parties:
            cursor = parlamentarios.find({
                "periodo.partido": party
            }).limit(5)

            for parlamentario in cursor:
                member_id = str(parlamentario["id"])
                if member_id not in [str(vid) for vid in votation_ids]:
                    continue
                right_anchor = member_id
                print(
                    f"📍 Anclaje derecho encontrado: {parlamentario.get('nombre', 'Desconocido')} (ID: {member_id}, Partido: {party})")
                break
            if right_anchor:
                break

        # Establecer coordenadas de anclaje (siguiendo la convención W-NOMINATE)
        anchors = {}
        if left_anchor:
            # Extremo izquierdo en primera dimensión
            anchors[left_anchor] = [-0.8, 0.0]
        if right_anchor:
            # Extremo derecho en primera dimensión
            anchors[right_anchor] = [0.8, 0.0]

        print(
            f"✅ Anclajes de polaridad configurados: {len(anchors)} anclajes establecidos")
        return anchors

    except Exception as e:
        print(f"⚠️  Error al buscar anclajes de polaridad: {e}")
        return {}


def run_wnominate(
    payload: Dict[str, Any],
    maxiter: int = 30,
    cores: int = 1,
    xtol: float = 1e-4,
    update: List[str] = None,
    add_meta: List[str] = None,
    polarity_anchors: Dict[str, List[float]] = None,
    db_name: str = DEFAULT_DB_NAME
) -> Dict[str, Any]:
    """
    Runnear el cálculo W-NOMINATE con la carga útil proporcionada.

    Args:
        payload: Datos de carga útil para el cálculo de W-NOMINATE
        maxiter: Número máximo de iteraciones
        cores: Número de núcleos de CPU a utilizar
        xtol: Tolerancia de convergencia
        update: Lista de parámetros para actualizar
        add_meta: Metadatos adicionales para incluir
        polarity_anchors: Dict que asigna los identificadores de legisladores a sus coordenadas de anclaje
        db_name: Nombre de la base de datos para la búsqueda de anclajes

    Returns:
        Dict que contiene los resultados del cálculo W-NOMINATE
    """
    if update is None:
        update = ["bp", "idpt", "bw"]

    if add_meta is None:
        add_meta = []

    # Si no se proporcionan anclajes, detectarlos automáticamente
    if polarity_anchors is None:
        print("🎯 Detectando anclajes de polaridad automáticamente...")
        member_ids = [str(m['icpsr']) for m in payload.get('memberwise', [])]
        polarity_anchors = find_polarity_anchors_from_members(
            member_ids, db_name)

    # Aplicar anclajes de polaridad al payload
    if polarity_anchors:
        print(f"🔒 Aplicando {len(polarity_anchors)} anclajes de polaridad...")
        for member_id, coords in polarity_anchors.items():
            if member_id in payload['idpt']:
                payload['idpt'][member_id] = coords
                print(f"   {member_id} → [{coords[0]:.2f}, {coords[1]:.2f}]")

        # Marcar miembros anclados como no actualizables durante la optimización
        for member in payload.get('memberwise', []):
            if str(member['icpsr']) in polarity_anchors:
                # No actualizar coordenadas de anclaje
                member['update'] = False
                print(f"🔒 Anclaje bloqueado: {member['icpsr']}")

    # Convierte listas en carga útil en matrices numpy cuando sea necesario
    processed_payload = {
        "votes": payload["votes"],
        "memberwise": payload["memberwise"],
        "idpt": {k: np.array(v) for k, v in payload["idpt"].items()},
        "bp": {k: np.array(v) for k, v in payload["bp"].items()},
        "bw": {
            "b": float(payload["bw"]["b"]),
            "w": float(payload["bw"]["w"])
        }
    }

    # Ejecutar el cálculo W-NOMINATE
    result = update_nominate(
        processed_payload,
        maxiter=maxiter,
        cores=cores,
        update=update,
        xtol=xtol,
        add_meta=add_meta
    )

    return result


def find_polarity_anchors_from_members(
    member_ids: List[str],
    db_name: str = DEFAULT_DB_NAME
) -> Dict[str, List[float]]:
    """
    Encuentre anclajes de polaridad en una lista de ID de miembros.

    Args:
        member_ids: Lista de ID de miembros para buscar
        db_name: Nombre de la base de datos

    Returns:
        Dict que asigna los ID de miembros a sus coordenadas de anclaje
    """
    try:
        client = get_mongodb_connection()
        db = client[db_name]
        parlamentarios = db["parlamentarios"]

        # Definir partidos extremos
        left_extreme_parties = ["PC", "COM"]
        right_extreme_parties = ["UDI"]

        anchors = {}

        # Encontrar anclajes de los miembros disponibles
        for member_id in member_ids:
            try:
                # Manejar formatos 'M1000' y '1000'
                numeric_id = int(member_id.replace('M', '')) if member_id.startswith(
                    'M') else int(member_id)
                parlamentario = parlamentarios.find_one({"id": numeric_id})

                if parlamentario and "periodo" in parlamentario:
                    for periodo in parlamentario["periodo"]:
                        if "partido" in periodo:
                            party = periodo["partido"]

                            # Verificar anclaje de izquierda
                            if party in left_extreme_parties and len([k for k in anchors.keys() if anchors[k][0] < 0]) == 0:
                                anchors[member_id] = [-0.8, 0.0]
                                print(
                                    f"📍 Anclaje izquierdo: {parlamentario.get('nombre', member_id)} ({party})")

                            # Verificar anclaje de derecha
                            elif party in right_extreme_parties and len([k for k in anchors.keys() if anchors[k][0] > 0]) == 0:
                                anchors[member_id] = [0.8, 0.0]
                                print(
                                    f"📍 Anclaje derecho: {parlamentario.get('nombre', member_id)} ({party})")

                            break

            except (ValueError, TypeError):
                continue

            # Detener una vez que tengamos ambos anclajes
            if len(anchors) >= 2:
                break

        return anchors

    except Exception as e:
        print(f"⚠️  Error al buscar anclajes de los miembros: {e}")
        return {}


def format_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formatee los resultados de update_nominate para un uso limpio de la API.
    Convierte matrices numpy en listas, elimina prefijos y garantiza una estructura serializable en JSON.

    Args:
        results: Resultados de update_nominate

    Returns:
        Dict contiene resultados con formato limpio y listos para la serialización JSON
    """
    formatted = {}

    # Proceso idpt (coordenadas de cada parlamentario)
    # Eliminar el prefijo 'M' y almacenar identificaciones de congresistas limpias con una estructura simplificada
    if 'idpt' in results:
        formatted['idpt'] = {}
        for member_id, member_data in results['idpt'].items():
            # Remover el prefijo 'M' para obtener la identificación de congresista limpia
            clean_id = member_id[1:] if member_id.startswith(
                'M') else member_id

            # Extraer coordenadas de la estructura anidada
            if isinstance(member_data, dict) and 'idpt' in member_data:
                # Manejar estructura anidada: {"idpt": [x, y], "meta": {...}}
                coords = member_data['idpt']
            else:
                # Manejar estructura de coordenadas directa: [x, y]
                coords = member_data

            # Convertir matrices numpy en listas y crea una estructura limpia
            if isinstance(coords, np.ndarray):
                coords_list = coords.tolist()
            else:
                coords_list = coords if isinstance(coords, list) else [coords]

            # Almacenar como estructura xcoord, ycoord
            if len(coords_list) >= 2:
                formatted['idpt'][clean_id] = {
                    "xcoord": coords_list[0],
                    "ycoord": coords_list[1]
                }
            else:
                # Respaldo en caso de estructura inesperada
                formatted['idpt'][clean_id] = {
                    "xcoord": coords_list[0] if len(coords_list) > 0 else 0.0,
                    "ycoord": 0.0
                }

    # Proceso bp (parámetros del proyecto de ley para cada votación)
    # Eliminar el prefijo 'V' y almacenar identificaciones de votación limpias
    if 'bp' in results:
        formatted['bp'] = {}
        for vote_id, params in results['bp'].items():
            # Eliminar el prefijo 'V' para obtener la identificación de votación limpia
            clean_vote_id = vote_id[1:] if vote_id.startswith('V') else vote_id

            if isinstance(params, np.ndarray):
                formatted['bp'][clean_vote_id] = params.tolist()
            else:
                formatted['bp'][clean_vote_id] = params

    # Agregar parámetros globales (b y w)
    if 'bw' in results:
        formatted['bw'] = results['bw']

    # Agregar metadatos si están presentes
    if 'meta' in results:
        formatted['meta'] = results['meta']

    return formatted


def get_congressman_details(congressman_ids: List[str], db_name: str = DEFAULT_DB_NAME) -> Dict[str, Dict[str, Any]]:
    """
   Obtenga los detalles del congresista para las identificaciones proporcionadas de la colección parlamentarios.

    Args:
        congressman_ids: Lista de identificaciones de congresistas (como cadenas)
        db_name: Nombre de la base de datos de MongoDB

    Returns:
        Dict que asigna la identificación del congresista a sus datos
    """
    client = get_mongodb_connection()
    db = client[db_name]
    parlamentarios = db["parlamentarios"]

    # Convertir IDs a enteros para la consulta de MongoDB
    int_ids = [int(id) for id in congressman_ids]

    # Obtener detalles del congresista
    congressmen = parlamentarios.find({"id": {"$in": int_ids}})

    details = {}
    for congressman in congressmen:
        details[str(congressman["id"])] = {
            "id": congressman["id"],
            "nombre": congressman.get("nombre", ""),
            "apellido": congressman.get("apellido", ""),
            "partido": congressman.get("partido", ""),
            "periodo": congressman.get("periodo", ""),
            # Agregar cualquier otro campo que necesite
        }

    return details


def get_votation_details(votation_ids: List[str], db_name: str = DEFAULT_DB_NAME) -> Dict[str, Dict[str, Any]]:
    """
    Obtener detalles de votación para los ID dados de la colección votaciones.

    Args:
        votation_ids: Lista de IDs de votación (como cadenas)
        db_name: Nombre de la base de datos de MongoDB

    Returns:
        Dict que asigna la ID de votación a sus detalles
    """
    client = get_mongodb_connection()
    db = client[db_name]
    votaciones = db["votaciones"]

    # Convertir IDs en números enteros para consultas de MongoDB
    int_ids = [int(id) for id in votation_ids]

    # Obtener detalles de votación
    votations = votaciones.find({"id": {"$in": int_ids}})

    details = {}
    for votation in votations:
        details[str(votation["id"])] = {
            "id": votation["id"],
            "nombre": votation.get("nombre", ""),
            "boletin": votation.get("boletin", ""),
            "fecha": votation.get("fecha", ""),
            "descripcion": votation.get("descripcion", ""),
            # Agregar cualquier otro campo que necesite
        }

    return details


def calculate_wnominate_with_provided_hash(
    votation_ids: List[int],
    result_hash: str,
    db_name: str = DEFAULT_DB_NAME,
    maxiter: int = 30,
    cores: int = 1,
    xtol: float = 1e-4
) -> Dict[str, Any]:
    """
    Calcula W-NOMINATE con un hash proporcionado previamente (llamado desde la API de Go). 
    Esto omite la generación del hash y la comprobación de caché, ya que Go ya lo hacía.

    Args:
        votation_ids: Lista de IDs de votación para incluir en el cálculo
        result_hash: Hash pre-generado para este cálculo
        db_name: Nombre de la base de datos de MongoDB
        maxiter: Número máximo de iteraciones
        cores: Número de núcleos de CPU a utilizar
        xtol: Tolerancia de convergencia

    Returns:
        Dict que contiene:
        - 'result_hash': El hash proporcionado
        - 'cached': Siempre False (ya que Go ya verificó la caché)
        - 'results': Los resultados del cálculo W-NOMINATE
    """
    print(f"Usando hash proporcionado: {result_hash}")
    print("Realizando cálculo DW-NOMINATE (caché ya verificado por API Go)...")

    # Preparar parámetros de cálculo para almacenamiento
    calculation_params = {
        'maxiter': maxiter,
        'cores': cores,
        'xtol': xtol,
        'db_name': db_name
    }

    # Realizar el cálculo
    results = calculate_wnominate(
        votation_ids=votation_ids,
        db_name=db_name,
        maxiter=maxiter,
        cores=cores,
        xtol=xtol
    )

    # Almacenar los resultados con el hash proporcionado
    storage_success = store_wnominate_result(
        result_hash=result_hash,
        votation_ids=votation_ids,
        calculation_params=calculation_params,
        results=results,
        db_name=db_name
    )

    if not storage_success:
        print("Advertencia: Error al almacenar resultados en la base de datos")

    return {
        'result_hash': result_hash,
        'cached': False,
        'results': results
    }


def calculate_wnominate(
    votation_ids: List[int],
    db_name: str = DEFAULT_DB_NAME,
    maxiter: int = 30,
    cores: int = 1,
    xtol: float = 1e-4
) -> Dict[str, Any]:
    """
    Función de extremo a extremo para calcular W-NOMINATE para una lista dada de IDs de votación.

    Args:
        votation_ids: Lista de IDs de votación para incluir en el cálculo
        db_name: Nombre de la base de datos de MongoDB
        maxiter: Número máximo de iteraciones
        cores: Número de núcleos de CPU a utilizar
        xtol: Tolerancia de convergencia

    Returns:
        Dict que contiene los resultados del cálculo W-NOMINATE
    """
    # Generar payload a partir de datos de MongoDB
    payload = generate_payload(votation_ids, db_name)

    # Ejecutar cálculo W-NOMINATE
    results = run_wnominate(
        payload,
        maxiter=maxiter,
        cores=cores,
        xtol=xtol
    )

    # Formatear resultados para consumo de API
    formatted_results = format_results(results)

    return formatted_results


def save_results_to_file(results: Dict[str, Any], output_file: str) -> None:
    """
    Guardar los resultados en un archivo JSON.

    Args:
        results: Resultados para guardar
        output_file: Ruta al archivo de salida
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def parse_arguments():
    """
    Analizar argumentos de la línea de comandos.

    Returns:
        Argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description='Calcular W-NOMINATE para un conjunto de IDs de votación')

    parser.add_argument(
        '--votation-ids',
        type=int,
        nargs='+',
        required=True,
        help='Lista de IDs de votación para incluir en el cálculo'
    )

    parser.add_argument(
        '--db-name',
        type=str,
        default=DEFAULT_DB_NAME,
        help='Nombre de la base de datos de MongoDB'
    )

    parser.add_argument(
        '--maxiter',
        type=int,
        default=10,
        help='Número máximo de iteraciones'
    )

    parser.add_argument(
        '--cores',
        type=int,
        default=1,
        help='Número de núcleos de CPU a utilizar'
    )

    parser.add_argument(
        '--xtol',
        type=float,
        default=1e-4,
        help='Tolerancia de convergencia'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Ruta al archivo JSON de salida (si no se especifica, se imprime en stdout)'
    )
    parser.add_argument(
        '--force-recalculate',
        action='store_true',
        help='Forzar el recálculo incluso si existe un resultado en caché'
    )

    parser.add_argument(
        '--cleanup-days',
        type=int,
        help='Eliminar resultados más antiguos que este número de días'
    )

    parser.add_argument(
        '--create-indexes',
        action='store_true',
        help='Crear índices en la base de datos para un rendimiento óptimo'
    )

    parser.add_argument(
        '--include-details',
        action='store_true',
        help='Incluir detalles del congresista y de la votación en la salida'
    )

    parser.add_argument(
        '--result-hash',
        type=str,
        help='Hash pre-generado para este cálculo (omite la generación de hash)'
    )

    return parser.parse_args()


def main():
    """
    Función principal para el uso de CLI.
    """
    args = parse_arguments()

    try:
        # Manejar primero las operaciones de servicios públicos
        if args.create_indexes:
            create_wnominate_indexes(args.db_name)
            return

        if args.cleanup_days:
            cleanup_old_results(args.cleanup_days, args.db_name)
            return

        # Calcular W-NOMINATE con almacenamiento
        if args.result_hash:
            # Utilice el hash proporcionado (llamado desde la API de Go con un hash generado previamente)
            calculation_result = calculate_wnominate_with_provided_hash(
                votation_ids=args.votation_ids,
                result_hash=args.result_hash,
                db_name=args.db_name,
                maxiter=args.maxiter,
                cores=args.cores,
                xtol=args.xtol
            )
        else:
            # Generar hash internamente (modo legado)
            calculation_result = calculate_wnominate_with_storage(
                votation_ids=args.votation_ids,
                db_name=args.db_name,
                maxiter=args.maxiter,
                cores=args.cores,
                xtol=args.xtol,
                force_recalculate=args.force_recalculate
            )

        # Preparar salida
        output_data = {
            'result_hash': calculation_result['result_hash'],
            'cached': calculation_result['cached'],
            'results': calculation_result['results']
        }

        # Enriquecer con detalles si se solicita
        if args.include_details:
            output_data['results'] = create_enriched_result(
                output_data['results'],
                include_details=True,
                db_name=args.db_name
            )

        # Guardar o imprimir resultados
        if args.output:
            save_results_to_file(output_data, args.output)
            print(f"Resultados guardados en {args.output}")
        else:
            print(json.dumps(output_data, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
