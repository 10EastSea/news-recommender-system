# news-recommender-system

## Install
- MongoDB
- pip
  - Flask
  - pymongo
  - google-images-download

## Set Up
### Data Setting
1. MongoDB 설치 후에, `news_recsys` database를 만들고, `news` collection 생성

https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/

2. `/data`에 들어가서, `json_to_mongodb.py` 실행
### Pip Install
- `pip install Flask` 실행
- `pip install pymongo` 실행
- `pip install git+https://github.com/Joeclinton1/google-images-download.git` 실행
- `pip install recommenders` 실행
- `pip install tensorflow` 실행

### Run
- `mongod` 서버 실행
- `python app.py` 실행

## Site
https://news-recommender-system.run.goorm.io/
