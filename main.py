from flask import Flask
import pymongo
import urllib.parse
import json
from flask_cors import CORS
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app,resources={r"/*": {"origins": "*"}})

load_dotenv()

pw = os.getenv("PASSWORD")
usr = os.getenv("USERNAME")


username = urllib.parse.quote_plus(usr)
password = urllib.parse.quote_plus(pw)

client = pymongo.MongoClient("mongodb://" + username + ":" + password +
                             "@covlab.tech:57017/TwitterVisual")

@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Covlab API'


@app.route('/graphData')
def grabGraphData():


    db = client["TwitterVisual"]
    daily_real_data_us_collection = db["daily_real_data_us"]
    new_cases_data = daily_real_data_us_collection.find()
    counter = 0

    dataArr = []
    for data in new_cases_data:
        counter += 1

        dataArr.append({
            "date": data['date'],
            "new_cases": data['new_cases'],
            "cases_7_average": data['cases_7_average'],
            "cases_14_average": data['cases_14_average'],
            "total_cases": data['total_cases']
        })


    db = client["TwitterVisual"]

    daily_positive_tweet_count_collection = db["daily_positive_tweets_count"]
    
    new_cases_data = daily_positive_tweet_count_collection.find()
    
    counter = 0

    tweetArr = []
    
    for data in new_cases_data:
        counter += 1


        tweetArr.append({
            "date": data['date'],
            "new_tweets": data['new_tweets_count'],
            "tweets_7_average": data['cases_7_average'],
            "tweets_14_average": data['cases_14_average'],
            "total_tweets": data['total_tweets_count'],
            "positive_tweets_ratio":data['positive_tweets_ratio'],
            "weekly_new_cases_per1k":data['weekly_new_cases_per1k']
        })

    tweetArr.sort(key=lambda x: x["date"])

    db = client["TwitterVisual"]

    daily_positive_tweet_count_collection = db["states_statistics"]
    
    new_cases_data = daily_positive_tweet_count_collection.find()

    for data in new_cases_data:
            print(data)

    dataObj = [dataArr,tweetArr]

    #json data is  not serializeable
    return json.dumps(dataObj)
 
# main driver function
if __name__ == '__main__':
 
    app.run()



    
