from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


@app.route('/test', methods=['GET'])
def welcome():
    if request.method == "GET":
        return {'message': 'Complete',
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
