from flask import Flask, request
from flask_cors import CORS
import tasks
import json

app = Flask(__name__)
cors = CORS(app)


@app.route('/research')
def research():
    upload_data = request.get_json()
    tasks.researchworker.delay(upload_data)
    return "Sent to worker"


if __name__ == '__main__':
    app.run()
