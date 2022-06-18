from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def news_home():
    return render_template("index.html")

@app.route("/detail/<news_id>")
def news_detail(news_id):
    return render_template("detail.html")

@app.route("/category/<category_name>")
def news_category(category_name):
    return render_template("category.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/test/method", methods=["GET", "POST"])
def method():
    if request.method == "GET": return "GET으로 전달"
    elif request.method == "POST": return "POST로 전달"

    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)