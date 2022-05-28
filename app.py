from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/test/method", methods=["GET", "POST"])
def method():
    if request.method == "GET": return "GET으로 전달"
    elif request.method == "POST": return "POST로 전달"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)