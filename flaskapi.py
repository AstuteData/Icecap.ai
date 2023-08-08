from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin
import getexistingresearch
import loginauth
import registration
import companyResearch
import checkDatabase
import loadCompanies
import json
import returnList
import tasks
import nltk
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


@app.route('/registration', methods=['POST'])
def register():
    registeruserdata = request.get_json()
    registerresponse = registration.registeruser(registeruserdata)
    return registerresponse


@app.route('/login', methods=['POST'])
def login():
    loginuserdata = request.get_json()
    loginResponse = loginauth.loginauth(loginuserdata)
    return loginResponse


@app.route('/researchstatuscheck', methods=['POST', 'GET'])
def check_research_status():
    response = loadCompanies.load_researched_data()
    y = json.loads(response)
    return y


@app.route('/companyresearch', methods=['POST'])
def get_existing_research():
    if request.method == 'POST':
        companyid = request.get_json()
        response = getexistingresearch.getresearch(companyid)
        return response


@app.route('/companyinfo', methods=['POST'])
def get_company_info():
    if request.method == 'POST':
        companyid = request.get_json()
        response = getexistingresearch.getresearch(companyid)
        return response


if __name__ == '__main__':
    app.run()
