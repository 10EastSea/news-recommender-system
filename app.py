from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
import math


''' Initial Setting '''
app = Flask(__name__)

myclient = MongoClient("mongodb://localhost:27017/") 
db = myclient["news_recsys"]
collection = db["news"]


''' Data '''
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
        
        news = news_data_formating(news)
        results.append(news)
    return results

def category_smoothing(category):
    if category in ["news", "middleeast", "northamerica"]: category = "news"
    elif category in ["lifestyle", "foodanddrink", "health", "kids"]: category = "life"
    elif category in ["entertainment", "video", "tv", "music", "movies", "games"]: category = "entertainment"
    return category

def news_data_formating(news):
    news['category'] = category_smoothing(news['category'])
    news['body'] = ''.join(news['body'])
    return news


''' Routing '''
@app.route("/")
def news_home():
    page = request.args.get("page", type=int, default=1)
    limit = 10
    
    # all news setting
    all_news_list = cursor_to_list(collection.find({}).skip((page - 1) * limit).limit(limit))
    all_news_count = 101527 # collection.find({}).count() 혹은 collection.estimated_document_count()
    last_page_num = math.ceil(all_news_count / limit) # 마지막 page number
    
    # block setting
    block_size = 10 # 한 페이지에 표시할 block size
    block_num = int((page - 1) / block_size) # 현재 block number
    block_start = (block_size * block_num) + 1 # 현재 block의 맨 첫번째 page number
    block_end = block_start + (block_size - 1) # 현재 block의 맨 마지막 page number
    
    # recommended news setting
    rec_news_list = news_list[:10]
    
    return render_template("index.html", rec_news_list=rec_news_list, all_news_list=all_news_list, page=page, limit=limit, last_page_num=last_page_num, block_start=block_start, block_end=block_end)

@app.route("/detail/<news_id>")
def news_detail(news_id):
    # detail new setting
    news = collection.find_one({"id": news_id})
    news = news_data_formating(news)
    
    # recommended news setting
    rec_news_list = news_list[:10]
    
    return render_template("detail.html", news=news, rec_news_list=rec_news_list)

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


''' main '''
if __name__ == "__main__":
    # data setting
    news_list = cursor_to_list(collection.find().limit(50))
    
    # app runing
    app.run(host='0.0.0.0', port=5000, debug=True)