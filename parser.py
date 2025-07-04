from ollama_helper import get_category_ollama
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re

def extract_float(text):
    match = re.search(r"[\d,]+(?:\.\d+)?", text)
    return float(match.group(0).replace(',', '.')) if match else 0.0

def parse_check(url):
    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    items = soup.select("div.ticket-columns.ticket-items")
    if not items:
        return []

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
        except Exception as e:
            continue
    return result

def parse_multiple_checks(urls):
    all_products = []
    stats = {}

    for url in urls:
        products = parse_check(url)
        all_products.extend(products)
        for p in products:
            amount = extract_float(p["total"])
            stats[p["category"]] = stats.get(p["category"], 0) + amount
    return all_products, stats
