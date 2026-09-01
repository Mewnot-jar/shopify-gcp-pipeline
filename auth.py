import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_STORE=os.environ["SHOPIFY_STORE"]
CLIENT_ID=os.environ["SHOPIFY_CLIENT_ID"]
CLIENTE_SECRET=os.environ["SHOPIFY_CLIENT_SECRET"]

BASE_URL=f"https://{SHOPIFY_STORE}.myshopify.com"
TOKEN_URL=f"{BASE_URL}/admin/oauth/access_token"
GRAPHQL_URL=f"{BASE_URL}/admin/api/2026-07/graphql.json"

_token_cache = {"access_token": None, "expires_at": 0}

def get_access_token() -> str:

    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["access_token"]

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
    payload = response.json()
    _token_cache["access_token"] = payload["access_token"]
    _token_cache["expires_at"] = time.time() + payload.get("expires_in", 86400)
    return _token_cache["access_token"]

