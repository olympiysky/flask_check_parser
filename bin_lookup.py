# bin_lookup.py
import requests
import json
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_company_info(bin_number):
    if not bin_number:
        return {"org_name": "—", "org_address": "—"}

    query = {
        "query": {
            "bool": {
                "must": [{"match": {"bin": bin_number}}]
            }
        },
        "size": 1
    }

    source_json = json.dumps(query, ensure_ascii=False)
    source_encoded = urllib.parse.quote(source_json)

    url = f"https://data.egov.kz/api/v4/gbd_ul/v1?apiKey={API_KEY}&source={source_encoded}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data:
            company = data[0]
            return {
                "org_name": company.get("nameru", "Нет названия"),
                "org_address": company.get("addressru", "Нет адреса")
            }
        else:
            return {
                "org_name": "Данные не найдены",
                "org_address": "—"
