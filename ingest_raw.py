import os
import json
import hashlib
import base64
from google.cloud import storage

GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]

def guardar_como_json(datos: list[dict], nombre_entidad: str, fecha: str) -> str:
    os.makedirs("data/raw", exist_ok=True)

    nombre_archivo = f"data/raw/{nombre_entidad}_{fecha}.json"

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        for registro in datos:
            linea = json.dumps(registro, ensure_ascii=False)
            archivo.write(linea + "\n")

    print(f"Guardado: {nombre_archivo} ({len(datos)} registros)")
    return nombre_archivo

def calcular_md5_local(ruta_local: str) -> str:
    hash_md5 = hashlib.md5()
    with open(ruta_local, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(8192), b""):
            hash_md5.update(bloque)
    return base64.b64encode(hash_md5.digest()).decode("utf-8")

def bucket_existe() -> bool:
    cliente = storage.Client(project=GCP_PROJECT_ID)
    bucket = cliente.bucket(GCS_BUCKET_NAME)
    return bucket.exists()

def listar_archivos(prefijo: str = "") -> list[str]:
    cliente = storage.Client(project=GCP_PROJECT_ID)
    blobs = cliente.list_blobs(GCS_BUCKET_NAME, prefix=prefijo)
    return [blob.name for blob in blobs]

def subir_a_gcs(ruta_local: str, nombre_entidad: str, fecha: str) -> str:
    nombre_archivo = os.path.basename(ruta_local)
    ruta_en_bucket = f"{nombre_entidad}/{fecha}/{nombre_archivo}"
    gs = f"gs://{GCS_BUCKET_NAME}/{ruta_en_bucket}"

    cliente = storage.Client(project=GCP_PROJECT_ID)
    bucket = cliente.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(ruta_en_bucket)

    if not blob.exists():
        blob.upload_from_filename(ruta_local)
        print(f"[NUEVO] {gs}")
        return gs, "nuevo"

    blob.reload()
    hash_remoto = blob.md5_hash
    hash_local = calcular_md5_local(ruta_local)

    if hash_local == hash_remoto:
        print(f"[SIN CAMBIOS] {gs}")
        return gs, "sin_cambios"

    blob.upload_from_filename(ruta_local)
    print(f"[ACTUALIZADO] {gs}")
    return gs, "actualizado"