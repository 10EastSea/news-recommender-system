# tasks.py
from celery import Celery
from pymongo import MongoClient
import time

myclient = MongoClient("mongodb://localhost:27017/")
db = myclient["news_recsys"]
collection = db["news"]

BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
app = Celery('tasks', broker=BROKER_URL, backend=CELERY_RESULT_BACKEND)

@app.task
def get_today_news_list(today):
    time.sleep(5)
    return collection.find({"date": today})