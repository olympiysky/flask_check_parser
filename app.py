from flask import Flask, render_template, request
from parser import parse_multiple_checks

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        urls = request.form.get("urls", "").strip().splitlines()
        products, stats = parse_multiple_checks(urls)
        result = {"products": products, "stats": stats}
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
