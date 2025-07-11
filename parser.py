from ollama_helper import get_category_ollama
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from egov_api import get_company_info
import time
import re
from collections import defaultdict


def extract_float(text):
    clean = text.replace('\xa0', '').replace(' ', '').replace(',', '.')
    match = re.search(r"\d+(?:\.\d+)?", clean)
    return float(match.group()) if match else 0.0


def parse_meta_info(soup):
    info_block = soup.select_one(".col-12")
    if not info_block:
        return {}

    info_texts = [div.get_text(strip=True) for div in info_block.find_all("div")]

    info = {
        "name": None, "bin": None, "kkm": None, "reg_number": None,
        "address": None, "cashier": None, "date": None, "fp": None,
    }

    for line in info_texts:
        lower = line.lower()

        if "товарищество" in line or "ип" in line:
            info["name"] = line
        elif any(key in line.upper() for key in ["ИИН/БИН", "ЖСН/БСН"]):
            match = re.search(r"(?:ИИН/БИН|ЖСН/БСН)\s*[:\s]*([0-9]{12})", line, re.IGNORECASE)
            if match:
                info["bin"] = match.group(1)
        elif "кассир" in lower:
            info["cashier"] = line.split(":", 1)[-1].strip()
        elif "ккм" in lower:
            info["kkm"] = line.split(":", 1)[-1].strip()
        elif "регистрационный номер" in lower:
            info["reg_number"] = line.split(":", 1)[-1].strip()
        elif "адрес" in lower:
            info["address"] = line.split(":", 1)[-1].strip()
        elif "фп" in lower:
            match = re.search(r"фп[:\s]*([0-9]+)", lower)
            if match:
                info["fp"] = match.group(1)
        elif "/" in line and ":" not in line and len(line.strip()) < 30:
            info["date"] = line.strip()

    return info


def parse_check(url):
    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
    finally:
        driver.quit()

    meta = parse_meta_info(soup)

    bin_value = meta.get("bin")
    org_name, org_address, region = None, None, None
    if bin_value:
        try:
            org_name, org_address, region = get_company_info(bin_value)
        except Exception as e:
            print(f"❌ Ошибка при получении данных по БИН: {e}")

    meta["org_name"] = org_name
    meta["org_address"] = org_address
    meta["region_or_city"] = region

    items = soup.select("div.ticket-columns.ticket-items")
    result = []

    for item in items:
        try:
            name = item.select_one(".product-name span").text.strip()
            qty = item.select(".text-center")[1].text.strip()
            total = item.select(".text-end")[1].text.strip()
            category = get_category_ollama(name)

            result.append({
                "name": name,
                "qty": qty,
                "total": total,
                "category": category
            })
        except Exception:
            continue

    return {"products": result, "meta": meta}


def parse_multiple_checks(urls, date_from=None, date_to=None):
    products_per_check = []
    all_products = []
    all_meta = []
    stats = {}
    grouped_by_region = {}
    total_by_category = defaultdict(float)

    for url in urls:
        check_data = parse_check(url)
        products = check_data["products"]
        meta = check_data["meta"]

        products_per_check.append(products)
        all_meta.append(meta)
        all_products.extend(products)

        region = meta.get("region_or_city") or "Не определено"

        if region not in grouped_by_region:
            grouped_by_region[region] = {
                "products": [],
                "stats": {"amount": 0.0, "count": 0},
                "meta": [],
                "category_stats": {}
            }

        grouped_by_region[region]["meta"].append(meta)

        for p in products:
            amount = extract_float(p["total"])
            qty = extract_float(p["qty"]) or 1
            cat = p["category"]

            if cat not in stats:
                stats[cat] = {"amount": 0.0, "count": 0}
            stats[cat]["amount"] += amount
            stats[cat]["count"] += int(qty)

            total_by_category[cat] += amount

            grouped_by_region[region]["products"].append(p)
            grouped_by_region[region]["stats"]["amount"] += amount
            grouped_by_region[region]["stats"]["count"] += int(qty)

            # новая статистика по категориям внутри региона
            region_cat_stats = grouped_by_region[region]["category_stats"]
            if cat not in region_cat_stats:
                region_cat_stats[cat] = {"amount": 0.0, "count": 0}
            region_cat_stats[cat]["amount"] += amount
            region_cat_stats[cat]["count"] += int(qty)


            date_str = meta.get("date")  # Пример: "31.05.2025 / 18:31"
            try:
                check_dt = datetime.strptime(date_str.split('/')[0].strip(), "%d.%m.%Y")
            except Exception:
                check_dt = None

            if date_from and check_dt and check_dt < date_from:
                continue
            if date_to and check_dt and check_dt > date_to:
                continue


    return products_per_check, stats, all_meta, grouped_by_region, total_by_category, all_products
