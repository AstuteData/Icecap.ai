import os
import threading
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin
import companyResearch
import checkDatabase
import loadCompanies
import articleResearch
import json
import requests

app = Flask(__name__)
cors = CORS(app)


class MyWorker():
    def __init__(self, message):
        self.message = message
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        logging.info(f'run MyWorker with parameter {self.message}')


@app.route('/beginresearch', methods=['POST'])
def welcome():
    jsonstring = request.get_json()
    MyWorker(articleResearch.prep_article_data(jsonstring))
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
    companyResearch.upload_list(importrequest)
    return "complete"


@app.route('/companylist', methods=['GET'])
def retrievecompanylist():
    response = loadCompanies.load_database()
    y = json.loads(response)
    return y


if __name__ == '__main__':
    app.run()
