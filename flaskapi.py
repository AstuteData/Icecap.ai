from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)


@app.route('/test', methods=[GET, POST])
def welcome():
    data = {'message': 'Complete'}
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
