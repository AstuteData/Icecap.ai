import os
import threading
import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin
import register
import login
import companyResearch
import checkDatabase
import loadCompanies
import json
import returnList
import tasks
import nltk
import requests
nltk.download('punkt')

app = Flask(__name__)
cors = CORS(app)


@app.route('/beginresearch', methods=['POST'])
def welcome():
    jsonstring = request.get_json()
    tasks.researchworker.delay(jsonstring)
    return "Sent to worker"


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


@app.route('/enrichedcompanylist', methods=['GET'])
def retrieveenrichedlist():
    response = returnList.load_database()
    y = json.loads(response)
    return y


@app.route('/register', methods=['POST', 'GET'])
def register():
    registeruserdata = request.get_json()
    registerResponse = register.register(registeruserdata)
    return registerResponse


@app.route('/login', methods=['POST', 'GET'])
def login():
    loginuserdata = request.get_json()
    loginResponse = login.login(loginuserdata)
    return loginResponse



if __name__ == '__main__':
    app.run()
