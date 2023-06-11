from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)


@app.route('/test')
def welcome():
    test = "true"
    return jsonify({'bool': test})


if __name__ == '__main__':
    app.run()