import requests
import os
import json
from datetime import date
from auth import GRAPHQL_URL, get_access_token

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

def guardar_como_json(datos: list[dict], nombre_entidad: str) -> str:

    os.makedirs("data/raw", exist_ok=True)

    fecha = date.today().isoformat()
    nombre_archivo = f"data/raw/{nombre_entidad}_{fecha}.json"

    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)

    print(f"Guardado: {nombre_archivo} ({len(datos)} registros)")
    return nombre_archivo