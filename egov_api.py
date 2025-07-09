# egov_api.py
import requests
import json
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

def extract_region_or_city(address):
    if not address:
        return "Не определено"

    address = address.lower()

    # Города республиканского значения
    cities = ['алматы', 'астана', 'шымкент']
    for city in cities:
        if city in address:
            return city.capitalize()

    # Области
    regions = [
        'алматинская', 'акмолинская', 'актюбинская', 'атырауская', 'восточно-казахстанская',
        'жамбылская', 'жетысуская', 'западно-казахстанская', 'карагандинская', 'костанайская',
        'кызылординская', 'мангыстауская', 'павлодарская', 'северо-казахстанская', 'туркестанская',
        'улытауская', 'абайская'
    ]

    for region in regions:
        if region in address:
            return region.capitalize() + " область"

    return "Не определено"

def get_company_info(bin_number):
    if not bin_number or len(bin_number) != 12:
        return None, None, "Не определено"  # <- Три значения!

    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"bin": bin_number}}
                ]
            }
        },
        "size": 1
    }

    source_json = json.dumps(query, ensure_ascii=False)
    source_encoded = urllib.parse.quote(source_json)

    url = f"https://data.egov.kz/api/v4/gbd_ul/v1?apiKey={API_KEY}&source={source_encoded}"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data:
            company = data[0]
            name = company.get("nameru")
            address = company.get("addressru")
            region = extract_region_or_city(address)
            return name, address, region
    except Exception as e:
        print(f"⚠️ Ошибка при получении данных по БИН: {e}")

    return None, None, "Не определено"  # <- Три значения!
