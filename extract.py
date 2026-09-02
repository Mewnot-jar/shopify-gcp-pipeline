import requests
import os
import json
from auth import GRAPHQL_URL, get_access_token
from google.cloud import storage

GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]

QUERY_PRODUCTOS = """
query ($cursor: String) {
    products(first: 50, after: $cursor) {
        edges {
            node {
                id
                title
                status
            }
        }
        pageInfo {
            hasNextPage
            endCursor
        }
    }
}
"""
QUERY_ORDENES = """
query ($cursor: String) {
    orders(first: 50, after: $cursor) {
        edges {
            node {
                id
                name
                createdAt
                displayFinancialStatus
                totalPriceSet {
                    shopMoney {
                        amount
                        currencyCode
                    }
                }
                customer {
                    id
                }
                lineItems(first: 10) {
                    edges {
                        node {
                            title
                            quantity
                        }
                    }
                }
            }
        }
        pageInfo {
            hasNextPage
            endCursor
        }
    }
}
"""
QUERY_CLIENTES = """
query ($cursor: String) {
    customers(first: 50, after: $cursor) {
        edges {
            node {
                id
                firstName
                lastName
                defaultEmailAddress {
                    emailAddress
                }
                createdAt
                numberOfOrders
                amountSpent {
                    amount
                    currencyCode
                }
                defaultAddress {
                    city
                    country
                }
                tags
            }
        }
        pageInfo {
            hasNextPage
            endCursor
        }
    }
}
"""

def shopify_graphql_query(query: str, variables: dict | None = None) -> dict:
    access_token = get_access_token()

    response = requests.post(
        GRAPHQL_URL,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Shopify-Access-Token": access_token,
        },
        json={"query": query, "variables": variables or {}},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    if "errors" in data:
        raise RuntimeError(f"Errores encontrados: {data["errors"]}")
    return data["data"]

def paginar_todos(query: str, nombre_entidad: str) -> list[dict]:
    todos_los_nodos = []
    cursor = None
    hay_siguiente_pagina = True

    while hay_siguiente_pagina:
        resultado = shopify_graphql_query(query, variables={"cursor":cursor})
        pagina = resultado[nombre_entidad]

        for edge in pagina["edges"]:
            todos_los_nodos.append(edge["node"])

        hay_siguiente_pagina = pagina["pageInfo"]["hasNextPage"]
        cursor = pagina["pageInfo"]["endCursor"]

        print(f"Pagina traida. Total acumulado: {len(todos_los_nodos)}")

    return todos_los_nodos

def guardar_como_json(datos: list[dict], nombre_entidad: str, fecha: str) -> str:

    os.makedirs("data/raw", exist_ok=True)

    nombre_archivo = f"data/raw/{nombre_entidad}_{fecha}.json"

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)

    print(f"Guardado: {nombre_archivo} ({len(datos)} registros)")
    return nombre_archivo

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

    archivos_existentes = listar_archivos(prefijo=f"{nombre_entidad}/{fecha}")

    if ruta_en_bucket in archivos_existentes:
        print(f"Ya existe, se omite subida: {gs}")
        return gs

    cliente = storage.Client(project=GCP_PROJECT_ID)
    bucket = cliente.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(ruta_en_bucket)
    blob.upload_from_filename(ruta_local)

    print(f"Subido a GCS: {gs}")
    return gs