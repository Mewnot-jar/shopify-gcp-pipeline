import os
import requests
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE=os.environ["SHOPIFY_STORE"]
CLIENT_ID=os.environ["SHOPIFY_CLIENT_ID"]
CLIENTE_SECRET=os.environ["SHOPIFY_CLIENT_SECRET"]

BASE_URL=f"https://{SHOPIFY_STORE}.myshopify.com"
TOKEN_URL=f"{BASE_URL}/admin/oauth/access_token"

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

ACCESS_TOKEN=response.json()["access_token"]
GRAPHQL_URL=f"{BASE_URL}/admin/api/2026-07/graphql.json"


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

resp_productos = requests.post(
    GRAPHQL_URL,
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Shopify-Access-Token": ACCESS_TOKEN,
    },
    json={"query": query},
    timeout=30,
)

print("Status code:", resp_productos.status_code)
print(resp_productos.json())