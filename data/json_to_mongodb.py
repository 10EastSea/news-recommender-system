from pymongo import MongoClient
import json

myclient = MongoClient("mongodb://localhost:27017/") 
db = myclient["news_recsys"]
collection = db["news"]

for c in range(11):
    with open("news_data_%d.json" % c, "r") as f:
        json_arr = json.load(f)
        
        if isinstance(json_arr, list): collection.insert_many(json_arr)
        else: collection.insert_one(json_arr)