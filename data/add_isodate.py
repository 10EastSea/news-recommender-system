import datetime
from dateutil.parser import parse
from pymongo import MongoClient

myclient = MongoClient("mongodb://localhost:27017/") # 실행시 포트 수정
db = myclient["news_recsys"]
collection = db["news"]

news_list = collection.find()
for news in news_list:
    news_id = news['id']
    news_date = news['date']
    collection.update_one({'id': news_id}, {"$set": {'isodate': parse(news_date)}})