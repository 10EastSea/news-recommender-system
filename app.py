from flask import Flask, request, render_template, jsonify, session
from pymongo import MongoClient
from google_images_download import google_images_download
import math
import os


''' Initial Setting '''
app = Flask(__name__)

myclient = MongoClient("mongodb://localhost:27017/") 
db = myclient["news_recsys"]
collection = db["news"]


''' Data '''
ALL_CNT = 101527
NEWS_CNT = 30478 + 2 + 1
SPORTS_CNT = 32020
LIFE_CNT = 4570 + 4418 + 2929 + 104
FINANCE_CNT = 5916
TRAVEL_CNT = 4955
ENTERTAINMENT_CNT = 837 + 4569 + 1323 + 1263 + 815 + 1
WEATHER_CNT = 4255
AUTOS_CNT = 3071

news_list = []
tmp_category, tmp_category_list = None, []
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

def news_data_formating(news):
    news['category'] = category_smoothing(news['category'])
    news['body'] = ''.join(news['body'])
    return news

def category_smoothing(category):
    if category in ["news", "middleeast", "northamerica"]: category = "news"
    elif category in ["lifestyle", "foodanddrink", "health", "kids"]: category = "life"
    elif category in ["entertainment", "video", "tv", "music", "movies", "games"]: category = "entertainment"
    return category

def category_desmoothing(category):
    categorys = []
    if category == "news": categorys = [{"category": "news"}, {"category": "middleeast"}, {"category": "northamerica"}]
    elif category == "sports": categorys = [{"category": "sports"}]
    elif category == "life": categorys = [{"category": "lifestyle"}, {"category": "foodanddrink"}, {"category": "health"}, {"category": "kids"}]
    elif category == "finance": categorys = [{"category": "finance"}]
    elif category == "travel": categorys = [{"category": "travel"}]
    elif category == "entertainment": categorys = [{"category": "entertainment"}, {"category": "video"}, {"category": "tv"}, {"category": "music"}, {"category": "movies"}, {"category": "games"}]
    elif category == "weather": categorys = [{"category": "weather"}]
    elif category == "autos": categorys = [{"category": "autos"}]
    return categorys

def category_count(category):
    count = 0
    if category == "news": count = NEWS_CNT
    elif category == "sports": count = SPORTS_CNT
    elif category == "life": count = LIFE_CNT
    elif category == "finance": count = FINANCE_CNT
    elif category == "travel": count = TRAVEL_CNT
    elif category == "entertainment": count = ENTERTAINMENT_CNT
    elif category == "weather": count = WEATHER_CNT
    elif category == "autos": count = AUTOS_CNT
    return count


''' Image '''
def download_img(news):
    response = google_images_download.googleimagesdownload()
    keywords = news["title"].replace(",","")
    arguments = {"keywords": keywords, "limit": 1, "output_directory": "static/img", "no_directory": True, "prefix": news["id"]}
    paths = response.download(arguments)

def get_img_path(news):
    file_list = os.listdir('static/img')
    img_path = "/static/img/default.png"
    
    is_already_in = False
    for f in file_list:
        if news["id"] in f:
            img_path = "/static/img/" + f
            is_already_in = True
            break
    
    if not is_already_in:
        download_img(news)
        file_list = os.listdir('static/img')
        for f in file_list:
            if news["id"] in f:
                img_path = "/static/img/" + f
                is_already_in = True
                break
        
    return img_path

def get_img_paths(news_list):
    img_paths = []
    for news in news_list: img_paths.append(get_img_path(news))
    return img_paths


''' Routing '''
@app.route("/")
def news_home():
    page = request.args.get("page", type=int, default=1)
    limit = 10
    
    # all news setting
    all_news_list = cursor_to_list(collection.find({}).skip((page - 1) * limit).limit(limit))
    all_news_count = ALL_CNT # collection.estimated_document_count()
    last_page_num = math.ceil(all_news_count / limit) # 마지막 page number
    
    # block setting
    block_size = 5 # 한 페이지에 표시할 block size
    block_num = int((page - 1) / block_size) # 현재 block number
    block_start = (block_size * block_num) + 1 # 현재 block의 맨 첫번째 page number
    block_end = block_start + (block_size - 1) # 현재 block의 맨 마지막 page number
    
    # recommended news setting
    rec_news_list = news_list[:10] # !!impression 추천 적용
    img_paths = get_img_paths(rec_news_list)
    
    return render_template("index.html", rec_news_list=rec_news_list, img_paths=img_paths, all_news_list=all_news_list, page=page, limit=limit, last_page_num=last_page_num, block_start=block_start, block_end=block_end)

@app.route("/detail/<news_id>")
def news_detail(news_id):
    # detail new setting
    news = collection.find_one({"id": news_id})
    news = news_data_formating(news)
    
    # get img path
    img_path = get_img_path(news)
    
    # recommended news setting
    rec_news_list = news_list[:10] # !!해당 뉴스 기반 추천 적용
    
    return render_template("detail.html", news=news, img_path=img_path, rec_news_list=rec_news_list)

@app.route("/category/<category>")
def news_category(category):
    global tmp_category
    global tmp_category_list
    
    page = request.args.get("page", type=int, default=1)
    limit = 10
    
    # all news setting
    all_news_list = cursor_to_list(collection.find({"$or": category_desmoothing(category)}).skip((page - 1) * limit).limit(limit))
    all_news_count = category_count(category)
    last_page_num = math.ceil(all_news_count / limit) # 마지막 page number
    
    # block setting
    block_size = 5 # 한 페이지에 표시할 block size
    block_num = int((page - 1) / block_size) # 현재 block number
    block_start = (block_size * block_num) + 1 # 현재 block의 맨 첫번째 page number
    block_end = block_start + (block_size - 1) # 현재 block의 맨 마지막 page number
    
    # recommended news setting
    rec_news_list = []
    if tmp_category is None or tmp_category != category: # 같은 카테고리 내에서 이동하는 경우가 아닌경우
        tmp_category = category
        tmp_category_list = all_news_list[:10]
    rec_news_list = tmp_category_list[:10] # !!카테고리 별 추천 적용
    img_paths = get_img_paths(rec_news_list)
    
    return render_template("category.html", category=category, rec_news_list=rec_news_list, img_paths=img_paths, all_news_list=all_news_list, page=page, limit=limit, last_page_num=last_page_num, block_start=block_start, block_end=block_end)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route("/test/method", methods=["GET", "POST"])
def method():
    if request.method == "GET": return jsonify(news_list)
    elif request.method == "POST": return "POST로 전달"

@app.after_request
def save_response(r):
    if request.method == 'POST':
        return r

    if request.endpoint == 'static':
        return r

    
    
    history = session.get('history', [])
    print(history)
    
    
    if history:
        # 새로 고침 시
        if (history[-1][0] == request.endpoint and
                history[-1][1] == request.view_args):
            return r

    history.append([
        request.endpoint,
        request.view_args,
        r.status_code
    ])
    
    session['history'] = history[-5:]
    return r

app.secret_key = 'secretkey'

''' main '''
if __name__ == "__main__":
    news_list = cursor_to_list(collection.find().limit(10))
    app.run(host='0.0.0.0', port=5000, debug=True)