
import json
import os

from dotenv import load_dotenv
import pymongo
import urllib.parse
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)



load_dotenv()

pw = os.getenv("PASSWORD")
usr = os.getenv("USERNAME")

username = urllib.parse.quote_plus(str(usr))
password = urllib.parse.quote_plus(str(pw))

client = pymongo.MongoClient("mongodb://" + username + ":" + password + "@covlab.tech:57017/TwitterVisual")



@cross_origin()
@app.route('/', methods=['GET'])
def home():
    return "<h1>Covlab</h1>"

@app.route('/latest', methods=['GET'])
def latest():
    db = client["TwitterVisual"]
    daily_real_data_us_collection = db["daily_real_data_us"]
    latestData = daily_real_data_us_collection.find().sort([("_id", -1)]).limit(1)[0]
    latestData['_id'] = str(latestData['_id'])
    return json.dumps(latestData)
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

    daily_positive_tweet_count_collection = db["us_map"]
    
    new_cases_data = daily_positive_tweet_count_collection.find()

    print(new_cases_data)
    counter = 0


    stateDataArr = []
    pastData = []

    for data in new_cases_data:
        for key in data:
            if key != 'state' and key != '_id' and key != 'total_count':
                pastData.append({str(key): data[key]})  # convert key to string
        stateData = {
            str(data['state']): {  # convert state name to string
                "total_count": data['total_count'],
                "past_data": list(pastData)  # use pastData directly since it's already a list
            }
        }        
        stateDataArr.append(stateData)
        pastData.clear()

    dataObj = [dataArr,tweetArr,stateDataArr]

    #json data is  not serializeable
    return json.dumps(dataObj)
 

if __name__ == '__main__':
    app.run(port=5001)
    
