from flask import Flask, request
from flask_cors import CORS
import tasks
import json

app = Flask(__name__)
cors = CORS(app)


@app.route('/login', methods=['POST'])
def login():
    login_data = request.get_json()
    print("Sent to worker")
    tasks.loginworker.delay(login_data)


@app.route('/register', methods=['POST'])
def register():
    registration_data = request.get_json()
    print("Sent to worker")
    tasks.registrationworker.delay(registration_data)


@app.route('/research', methods=['POST'])
def research():
    upload_data = request.get_json()
    print("Sent to worker")
    tasks.researchworker.delay(upload_data)


if __name__ == '__main__':
    app.run()
