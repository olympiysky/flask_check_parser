import requests

def get_category_ollama(product_name: str) -> str:
    prompt = (
        f"Товар: «{product_name}».\n"
        "Определи категорию из списка: Сладости, Снеки, Хозтовары, Напитки, Продукты, Овощи, Фрукты, Мясо.\n"
        "Ответь только одним словом — названием категории на русском языке."
    )
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }, timeout=25)

        data = response.json()
        if "response" in data:
            result = data["response"].strip().split()[0]
            valid_categories = {"Сладости", "Снеки", "Хозтовары", "Напитки", "Продукты", "Овощи", "Фрукты", "Мясо"}
            return result if result in valid_categories else "Неизвестно"
    except Exception as e:
        print("❌ Ошибка Ollama:", e)
    return "Неизвестно"
