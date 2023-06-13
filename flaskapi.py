from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin
import companyResearch

app = Flask(__name__)
cors = CORS(app)


@app.route('/test', methods=['GET'])
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


if __name__ == '__main__':
    app.run()
