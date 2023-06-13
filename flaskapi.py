from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/test', methods=['GET'])
@cross_origin()
def welcome():
    if request.method == "GET":
        return {'message': 'Complete',
                'method': request.method
                }


@app.route('/tester', methods=['GET'])
@cross_origin()
def two():
    if request.method == "GET":
        return {'message': 'Alana',
                'method': request.method
                }


if __name__ == '__main__':
    app.run()
