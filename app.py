
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

print(username)
print(password)
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

    statisticsCollection = db["statistics"]

    statsData = statisticsCollection.find()

    for item in statsData:
        if(item['type'] == "US"):
            latestData['usCases14Day'] = item['cases_14_days_change']
        
    return json.dumps(latestData)

@app.route('/graphData')
def grabGraphData():
    db = client["TwitterVisual"]
    daily_real_data_us_collection = db["daily_real_data_us"]
    new_cases_data = daily_real_data_us_collection.find()

    dataArr = []

    for data in new_cases_data:

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
    

    tweetArr = []
    
    for data in new_cases_data:

        #some db entries are missing some key pairs
        try:
            tweetArr.append({
                "date": data['date'],
                "new_tweets": data['new_tweets_count'],
                "tweets_7_average": data['cases_7_average'],
                "tweets_14_average": data['cases_14_average'],
                "total_tweets": data['total_tweets_count'],
                "positive_tweets_ratio":data['positive_tweets_ratio'],
                "weekly_new_cases_per10m":data['weekly_new_cases_per10m']
            })
        except:
            print("Keyerror finding cases_7_average in grabGraphData:")
            # print(data)

    tweetArr.sort(key=lambda x: x["date"])

    db = client["TwitterVisual"]

    daily_positive_tweet_count_collection = db["us_map"]
    
    new_cases_data = daily_positive_tweet_count_collection.find()


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
 
@app.route('/graphData1')
def grabGraphData1():

    db = client["TwitterVisual"]
    
    daily_real_data_us_collection = db["daily_all_tweets_count"]
    
    new_cases_data = daily_real_data_us_collection.find()
    
    dataArr = []
    
    for data in new_cases_data:
        
        #some db entries are missing some key pairs

        try:
            dataArr.append({
                "date": data['date'],
                "new_tweets_count": data['new_tweets_count'],
                "total_tweets_count": data['total_tweets_count'],
                "tweets_14_average": data['tweets_14_average'],
                "tweets_7_average": data['tweets_7_average']
            })
        except:
            print("Keyerror finding cases_7_average in:")
            # print(data)


    sorted_dataArr = sorted(dataArr, key=lambda x: x["date"])

    return json.dumps(sorted_dataArr)

@app.route('/tableData')
def getTableData():
    db = client["TwitterVisual"]
    statistics_collection = db["statistics"]
    daily_positive_tweets_count_collection = db["daily_positive_tweets_count"]
    usMapCollection = db["us_map"]
    
    # Process data for US map collection
    usDataArr = []
    for item in usMapCollection.find().sort([("_id", pymongo.DESCENDING)]):
        temp_state_item = {"data": []}
        for key, value in item.items():
            if key == 'state':
                temp_state_item['state'] = value
            elif key not in ["_id", "state", "total_count"]:
                temp_state_item['data'].append((key, value))
        temp_state_item['data'] = sorted(temp_state_item['data'], key=lambda x: x[0], reverse=True)[:14]
        temp_state_item['data'] = list(reversed(list(temp_state_item['data'])))
        usDataArr.append(temp_state_item)
    
    # Process data for 14-day graph
    latestDailyPositiveTweetsCount = list(daily_positive_tweets_count_collection.find().sort(
        "_id", pymongo.DESCENDING))
    us14DayGraphData = {"labels": [], "data": []}
    count = 0
    for item in latestDailyPositiveTweetsCount:
        #some entries have less data or are missing important key pairs
        try:
            us14DayGraphData['labels'].append(item['date'])
            us14DayGraphData['data'].append([item['date'],item['cases_14_average']])
            count+=1
        except:
            print("Issue at GRABTABLEDATA, missing key value 'cases_14_average'")
            # print(item)
        if count == 14:
            break

    # Process data for state table 
    latestStatisticsData = statistics_collection.find()
    stateArr = []
    for counter, item in enumerate(latestStatisticsData):
        print(item)
        stateData = {"state": item['type']}
        # Update the state data with the matching data from US map, using the state value
        matching_data = next((x["data"] for x in usDataArr if x["state"] == stateData["state"]), [])
        stateData['cases_14_days_change'] = {
            "percentage": item.get('cases_14_days_change', 'N/A'),
            "14DayData": {
                "labels": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
                "data": matching_data
            } if counter > 0 else {
                "labels": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
                "data": us14DayGraphData['data'] 
            }
        }
        

        #US Data is missing some entries
        
        try:
            stateData['weekly_new_cases_per10m'] = item.get('weekly_new_cases_per10m',
                                                       latestDailyPositiveTweetsCount[0]['weekly_new_cases_per10m'] if counter == 0 else 'N/A')
        except:
            print("Key error when getting data, key: weekly_new_cases_per10m")
            stateData['weekly_new_cases_per10m'] = "N/A"
        stateData['cases_7_sum'] = item.get('cases_7_sum', 'N/A')
        stateData['positivity'] = item.get('positivity', 'N/A')
        stateArr.append(stateData)

    return json.dumps(stateArr)

@app.route('/mapData')
def getMapData():
    db = client["TwitterVisual"]
    usd_map_collection = db["us_map"]
    map_data = usd_map_collection.find()
    stateDataArr = []
    for item in map_data:
        state_data = {
            "state":item['state'],
            "positive":item['total_count']
        }
        stateDataArr.append(state_data)

    return json.dumps(stateDataArr)

@app.route('/wordCloudData')
def getWordCloudData():
    
    db = client["TwitterVisual"]
    
    word_cloud_collection = db["word_cloud"]
    
    word_data = word_cloud_collection.find()
    
    wordDataArr = []
    
    for item in word_data:
        word_data = {
            "name":item['word'],
            "weight":item['frequency']
        }
        wordDataArr.append(word_data)
    
    return json.dumps(wordDataArr)

if __name__ == '__main__':
    app.run(port=5001)
    
