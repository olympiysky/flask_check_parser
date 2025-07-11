from flask import Flask, render_template, request
from parser import parse_multiple_checks

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        urls = request.form.get("urls", "").strip().splitlines()

        try:
            (
                products_per_check,
                stats,
                metas,
                grouped_by_region,
                category_stats_by_region,
                all_products
            ) = parse_multiple_checks(urls)

            # Общая статистика
            total_checks = len(metas)
            total_products = sum(stat["count"] for stat in stats.values())
            total_amount = sum(stat["amount"] for stat in stats.values())

            result = {
                "products": all_products,
                "stats": stats,
                "meta": metas,
                "grouped_by_region": grouped_by_region,
                "category_stats_by_region": category_stats_by_region,
                "total_checks": total_checks,
                "total_products": total_products,
                "total_amount": total_amount
            }

        except Exception as e:
            error = f"Произошла ошибка: {str(e)}"

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
