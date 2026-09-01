import requests
from auth import GRAPHQL_URL, get_access_token

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