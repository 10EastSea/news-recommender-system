from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient


app = Flask(__name__)

myclient = MongoClient("mongodb://localhost:27017/") 
db = myclient["news_recsys"]
collection = db["news"]

news_list = []
def cursor_to_list(mongodb_results):
    results = []
    for item in mongodb_results:
        news = {"id":None, "category":None, "title":None, "url":None, "nid":None, "body":None}
        
        news['id'] = item['id']
        news['category'] = item['category']
        news['title'] = item['title']
        news['url'] = item['url']
        news['nid'] = item['nid']
        news['body'] = item['body']
        
        results.append(news)
    return results


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
    if request.method == "GET": return jsonify(news_list)
    elif request.method == "POST": return "POST로 전달"

    
if __name__ == "__main__":
    # set data
    news_list = cursor_to_list(collection.find().limit(50))
    
    # run app
    app.run(host='0.0.0.0', port=5000, debug=True)