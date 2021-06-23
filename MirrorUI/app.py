from logging import debug
from flask import Flask, render_template, request, jsonify
import requests
import pymysql
import time
import json

from scripts.weather import get_weather

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/update_weather', methods=['GET'])
def update_weather():
	'''
	Returns updated weather, called every 10 minutes
	'''
	currentWeather = get_weather()
	return jsonify({'result' : 'success', 'currentWeather' : currentWeather})

@app.route("/result/<serialnum>/<date>", methods=['POST', 'GET'])
def result(serialnum, date):
    user_conf = {}
    user_conf['serialnum'] = serialnum
    user_conf['date'] = date
    if request.method == 'POST':
        sql = "SELECT * FROM user_face  where machine_no = '{}' and date ='{}'".format(serialnum, date)
        rows = []
        while True:
            test_db = pymysql.connect(user='root', passwd='', host='', port=3306, db='', charset='UTF8')
            cursor = test_db.cursor(pymysql.cursors.DictCursor)
            cursor.execute("set names utf8")
            cursor.execute(sql)
            rows = cursor.fetchall()
            test_db.close()
            if rows:
                break
            time.sleep(5)
            print("not exist data")
        print("DONE")
        return rows[0]
    return render_template("loading.html", data = user_conf)

results = []
@app.route("/ai")
def ai_result():
    global results
    with open('scripts/data.json', 'r', encoding='utf-8') as f:
        data = f.read()
        results = json.loads(data)
    data={}
    for i in range(4):
        print()
        data[results[i]['item']] = {
            'num':results[i]['element1'],
            'pre':results[i]['element2'].split(',')
        }
    print(data)
    return render_template('resultspage1.html', data=data)

@app.route('/recommend')
def recommend_result():
    global results #/ai에서 받아온 데이터
    # with open('scripts/data.json', 'r', encoding='utf-8') as f:
    #     data = f.read()
    #     results = json.loads(data)
    if results[-1]['item'] == 'all_in_one':
        gender = 'm'
    else:
        gender = 'f'
    data={}
    for i in range(4,len(results)):
        data[results[i]['item']] = {
            'imgurl':results[i]['element1'],
            'price':results[i]['element2'],
            'name':results[i]['element3'],
        }
    return render_template('resultspage2.html', data=data, gender=gender)

if __name__ == '__main__':
    # app.run(debug=True)
	app.run(host="0.0.0.0",port=5000, debug=True)
