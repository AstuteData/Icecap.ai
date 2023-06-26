import redis
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin
import companyResearch
import checkDatabase
import loadCompanies
import articleResearch
import json
import requests
from redis import Redis
from rq import Queue, Retry

app = Flask(__name__)
cors = CORS(app)
q = Queue(connection=Redis())
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis = redis.Redis(connection_pool=pool)

@app.route('/beginresearch', methods=['POST'])
def welcome():
    jsonstring = request.get_json()
    articleResearch.prep_article_data(jsonstring)
    return "complete"



@app.route('/tester', methods=['GET'])
def two():
    if request.method == "GET":
        return {'message': 'Alana',
                'method': request.method
                }


@app.route('/checkdatabase', methods=['GET'])
def rundbcheck():
    if request.method == "GET":
        response = checkDatabase.check_database()
        if response == True:
            return 'true'
        elif response == False:
            return 'false'


@app.route('/researchimport', methods=['POST'])
def csvimport():
    importrequest = request.get_json()
    q.enqueue(companyResearch.upload_list(importrequest), retry=Retry(max=3))
    return "complete"


@app.route('/companylist', methods=['GET'])
def retrievecompanylist():
    response = loadCompanies.load_database()
    y = json.loads(response)
    return y


if __name__ == '__main__':
    app.run()
