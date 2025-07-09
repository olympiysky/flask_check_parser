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
            stats, metas, grouped_by_region = parse_multiple_checks(urls)
            result = {
                "stats": stats,
                "meta": metas,
                "grouped_by_region": grouped_by_region
            }
        except Exception as e:
            error = f"Произошла ошибка: {str(e)}"

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
