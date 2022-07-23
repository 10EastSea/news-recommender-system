from flask import Flask, request, render_template, jsonify, session
from pymongo import MongoClient
from google_images_download import google_images_download
from dateutil.parser import parse
# from celery import Celery
# from tasks import get_today_news_list
import math
import os
import datetime


''' Initial Setting '''
app = Flask(__name__)
app.secret_key = 'secretkey' # 세션을 위해 필요한 값
# app.config.update(
#     CELERY_BROKER_URL='redis://localhost:6379',
#     CELERY_RESULT_BACKEND='redis://localhost:6379'
# ) # 비동기 처리를 위해 redis 서버와 celery task에 필요한 설정

myclient = MongoClient("mongodb://localhost:27017/") # 실행시 포트 수정
db = myclient["news_recsys"]
collection = db["news"]

# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)


''' Data '''
TODAY = "2019-11-11"

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
        news = {"id":None, "date":None, "category":None, "title":None, "url":None, "nid":None, "body":None, "hits":None}
        
        news['id'] = item['id']
        news['date'] = item['date']
        news['category'] = item['category']
        news['title'] = item['title']
        news['url'] = item['url']
        news['nid'] = item['nid']
        news['body'] = item['body']
        news['hits'] = item['hits']
        
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

def sort_hits(news_list):
    print(news_list[:10])


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


# ''' Async '''
# @celery.task
# def tasks(today):
#     time.sleep(5)
#     return collection.find({"date": today})


''' Routing '''
@app.route("/")
def news_home():
    global news_list
    
    page = request.args.get("page", type=int, default=1)
    limit = 10
    
    # all news setting
    all_news_list = cursor_to_list(collection.find({"isodate": {"$lte": parse(TODAY)}}).skip((page - 1) * limit).limit(limit)) # find({"date": TODAY}) -> find()
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
    global news_list
    
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
    global news_list
    global tmp_category
    global tmp_category_list
    
    page = request.args.get("page", type=int, default=1)
    limit = 10
    
    # all news setting
    all_news_list = cursor_to_list(collection.find({"isodate": {"$lte": parse(TODAY)}, "$or": category_desmoothing(category)}).skip((page - 1) * limit).limit(limit)) # find({"date": TODAY}) -> find()
    all_news_count = category_count(category)
    last_page_num = math.ceil(all_news_count / limit) # 마지막 page number
    
    # block setting
    block_size = 5 # 한 페이지에 표시할 block size
    block_num = int((page - 1) / block_size) # 현재 block number
    block_start = (block_size * block_num) + 1 # 현재 block의 맨 첫번째 page number
    block_end = block_start + (block_size - 1) # 현재 block의 맨 마지막 page number
    
    # recommended news setting
    if tmp_category is None or tmp_category != category: # 같은 카테고리 내에서 이동하는 경우가 아닌경우
        tmp_category = category
        tmp_category_list = []
        for news in news_list:
            if news['category'] == category: tmp_category_list.append(news)
            if len(tmp_category_list) == 10: break
    
    rec_news_list = tmp_category_list[:10] # !!카테고리 별 추천 적용
    img_paths = get_img_paths(rec_news_list)
    
    return render_template("category.html", category=category, rec_news_list=rec_news_list, img_paths=img_paths, all_news_list=all_news_list, page=page, limit=limit, last_page_num=last_page_num, block_start=block_start, block_end=block_end)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route("/test/method", methods=["GET", "POST"])
def test_method():
    if request.method == "GET": return jsonify(news_list)
    elif request.method == "POST": return "POST로 전달"
    
# @app.route("/test/async")
# def test_async():
#     task = tasks.delay(TODAY)
#     return jsonify({'id': task.id})
#     # print(tmp_today_news_list)
#     # return jsonify(tmp_today_news_list)

# 동작 안함 ㅋㅋ;;
# @app.route("/session/clear", methods=["POST"])
# def session_clear():
#     if request.method == "POST":
#         if request.args.get('clear', default=False) == "True":
#             print('clear!')
#             session.clear()
#         return "POST로 전달"

@app.after_request
def save_response(r):
    if request.method == 'POST':
        return r

    if request.endpoint == 'static':
        return r
    
    history = session.get('history', [])
    
    if history:
        # 새로 고침 시
        if (history[-1][0] == request.endpoint and
                history[-1][1] == request.view_args):
            return r

    if request.view_args is not None:
        if request.view_args.get('news_id') is not None:
            news_id = request.view_args.get('news_id')
            if news_id not in history:
                history.append(news_id)
                # add_to_user_history(news_id)
                print(history)

    #TODO: hist size 찾아서 넣기
    session['history'] = history[-5:]
    return r

''' main '''
if __name__ == "__main__":
    # set cnt data
    ALL_CNT = len(cursor_to_list(collection.find({"isodate": {"$lte": parse(TODAY)}})))
    NEWS_CNT = len(cursor_to_list(collection.find({"isodate": {"$lte": parse(TODAY)}, "$or": [{"category": "news"}, {"category": "middleeast"}, {"category": "northamerica"}]})))
    SPORTS_CNT = len(cursor_to_list(collection.find({"isodate": {"$lte": parse(TODAY)}, "$or": [{"category": "sports"}]})))
    LIFE_CNT = len(cursor_to_list(collection.find({"isodate": {"$lte": parse(TODAY)}, "$or": [{"category": "lifestyle"}, {"category": "foodanddrink"}, {"category": "health"}, {"category": "kids"}]})))
    FINANCE_CNT = len(cursor_to_list(collection.find({"isodate": {"$lte": parse(TODAY)}, "$or": [{"category": "finance"}]})))
    TRAVEL_CNT = len(cursor_to_list(collection.find({"isodate": {"$lte": parse(TODAY)}, "$or": [{"category": "travel"}]})))
    ENTERTAINMENT_CNT = len(cursor_to_list(collection.find({"isodate": {"$lte": parse(TODAY)}, "$or": [{"category": "entertainment"}, {"category": "video"}, {"category": "tv"}, {"category": "music"}, {"category": "movies"}, {"category": "games"}]})))
    WEATHER_CNT = len(cursor_to_list(collection.find({"isodate": {"$lte": parse(TODAY)}, "$or": [{"category": "weather"}]})))
    AUTOS_CNT = len(cursor_to_list(collection.find({"isodate": {"$lte": parse(TODAY)}, "$or": [{"category": "autos"}]})))
    print("\nALL_CNT", ALL_CNT)
    print("NEWS_CNT", NEWS_CNT)
    print("SPORTS_CNT", SPORTS_CNT)
    print("LIFE_CNT", LIFE_CNT)
    print("FINANCE_CNT", FINANCE_CNT)
    print("TRAVEL_CNT", TRAVEL_CNT)
    print("ENTERTAINMENT_CNT", ENTERTAINMENT_CNT)
    print("WEATHER_CNT", WEATHER_CNT)
    print("AUTOS_CNT", AUTOS_CNT)
    
    
    # get today's news
    news_list = cursor_to_list(collection.find({"date": TODAY}))
    news_list = sorted(news_list, key=lambda x: x['hits'], reverse=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True) # 실행시 포트 수정