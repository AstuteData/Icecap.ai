from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin
import companyResearch
import checkDatabase
import loadCompanies

app = Flask(__name__)
cors = CORS(app)


@app.route('/beginresearch', methods=['GET'])
def welcome():
    if request.method == "GET":
        companyResearch.upload_list()
        return {'message': 'Research complete',
                'method': request.method
                }


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
    rq = request.get_json()
    companyResearch.upload_list(rq)
    return "complete"


@app.route('/companylist', methods=['GET'])
def retrievecompanylist():
    response = loadCompanies.load_database()
    data = response.json()

    return data


if __name__ == '__main__':
    app.run()
