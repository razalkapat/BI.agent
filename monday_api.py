import requests
from config import MONDAY_API_KEY

MONDAY_URL = "https://api.monday.com/v2"


def monday_query(query: str) -> dict:
    headers = {
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json",
        "API-Version": "2024-01"
    }
    response = requests.post(
        MONDAY_URL,
        json={"query": query},
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def get_column_titles(board_id: str) -> dict:
    query = '{ boards(ids: [' + str(board_id) + ']) { columns { id title } } }'
    result = monday_query(query)
    try:
        columns = result["data"]["boards"][0]["columns"]
        return {col["id"]: col["title"] for col in columns}
    except (KeyError, IndexError):
        return {}


def get_board_items(board_id: str, limit: int = 500) -> list:
    col_map = get_column_titles(board_id)
    query = '{ boards(ids: [' + str(board_id) + ']) { name items_page(limit: ' + str(limit) + ') { items { id name column_values { id text value } } } } }'
    result = monday_query(query)
    try:
        items = result["data"]["boards"][0]["items_page"]["items"]
        for item in items:
            item["_col_map"] = col_map
        return items
    except (KeyError, IndexError):
        return []


def normalize_item(item: dict) -> dict:
    col_map = item.get("_col_map", {})
    normalized = {"name": item.get("name", "Unknown")}
    for col in item.get("column_values", []):
        col_id = col.get("id", "unknown")
        key = col_map.get(col_id, col_id).strip()
        text = col.get("text", "") or ""
        if text.strip() in ["", "null", "None", "-", "N/A", "n/a"]:
            text = None
        normalized[key] = text
    return normalized


def safe_float(value) -> float:
    if value is None:
        return 0.0
    try:
        cleaned = (
            str(value)
            .replace(",", "")
            .replace("₹", "")
            .replace("$", "")
            .replace(" ", "")
            .strip()
        )
        return float(cleaned) if cleaned else 0.0
    except (ValueError, TypeError):
        return 0.0
