from flask import Flask, render_template
import json

app = Flask(__name__)


@app.route('/test')
def welcome():
    test = "true"
    res = json.dumps(test)
    return res

if __name__ == '__main__':
    app.run()