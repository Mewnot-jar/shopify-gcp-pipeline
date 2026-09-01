import os
import requests
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE=os.environ["SHOPIFY_STORE"]
CLIENT_ID=os.environ["SHOPIFY_CLIENT_ID"]
CLIENTE_SECRET=os.environ["SHOPIFY_CLIENT_SECRET"]

BASE_URL=f"https://{SHOPIFY_STORE}.myshopify.com"
TOKEN_URL=f"{BASE_URL}/admin/oauth/access_token"
GRAPHQL_URL=f"{BASE_URL}/admin/api/2026-07/graphql.json"

def get_access_token() -> str:
    response = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENTE_SECRET,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["access_token"]

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
if __name__ == "__main__":
    query = """
    {
        products(first: 5){
            edges {
                node{
                    id
                    title
                    status
                }
            }
        }
    }
    """
    resultado = shopify_graphql_query(query)
    print(resultado)