# Чек Парсер — Анализатор чеков с веб-ссылок

## 📌 Описание

Приложение на Flask для парсинга чеков с веб-ссылок (например, с сайта nrs.kz). 
Оно извлекает данные о товарах, категоризирует их с помощью локальной LLM-модели (Ollama), 
группирует по регионам и выводит сводную статистику.

## 📂 Структура проекта

```bash
project/
├── app.py                 # Flask-приложение
├── parser.py              # Логика парсинга чеков и анализа
├── templates/
│   └── index.html         # HTML-интерфейс (Jinja2)
├── static/                # (опционально) CSS/JS
├── ollama_helper.py       # Определение категории через локальную LLM (Ollama)
├── egov_api.py            # Получение данных по БИН из eGov API
├── requirements.txt       # Зависимости
└── README.md              # Документация (вы здесь)
```

## 🚀 Как запустить

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Убедитесь, что установлен Chrome и драйвер ChromeDriver.

3. Запустите Flask:

```bash
python app.py
```

4. Перейдите в браузере: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## ✅ Как пользоваться

- Вставьте ссылки на чеки в текстовое поле (по одной в строке).
- Нажмите "Анализировать".
- Вы увидите:
  - Общую статистику по категориям
  - Сводку по регионам/городам
  - Статистику по категориям в каждом регионе
  - Возможность свернуть/развернуть список товаров

## 🧠 Как это работает технически

### Связь компонентов

- `app.py` — точка входа, обрабатывает POST-запросы, вызывает `parse_multiple_checks` из `parser.py` и передаёт результат в `index.html`.
- `parser.py`:
  - Использует `Selenium + BeautifulSoup` для получения данных с чеков.
  - Выделяет метаинформацию (БИН, дата, адрес и т.д.).
  - Обращается к `egov_api.py`, чтобы по БИН получить регион и название компании.
  - Классифицирует товар через `ollama_helper.py` с помощью локальной LLM (например, `phi3:mini`).
  - Считает статистику и группирует по регионам и категориям.
- `index.html` (на Jinja2) отображает данные в минималистичном дизайне:
  - Общая таблица
  - Разделение по регионам
  - Раскрывающиеся списки товаров

## 🔧 Настройки

- Можно легко адаптировать под другие страны, сайты, категории.
- Расширяемо: можно добавить авторизацию, сохранение в БД, выгрузку в Excel.

## 📎 Пример формата ссылок

```


## 📞 Контакты

Автор: ms

---

_Этот проект создан как локальное решение для анализа чеков с использованием современных инструментов: Flask, Selenium, Ollama и eGov API._