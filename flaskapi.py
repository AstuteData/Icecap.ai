from flask import Flask, request, jsonify
from flask_cors import CORS
import tasks
from main.core_platform.login import loginauth, registration
import json

app = Flask(__name__)
cors = CORS(app)


@app.route('/login', methods=['POST'])
def login():
    login_data = request.get_json()
    print("Sent to worker")
    response = loginauth.login(login_data)
    return jsonify(response)


@app.route('/register', methods=['POST'])
def register():
    registration_data = request.get_json()
    print("Sent to worker")
    response = registration.register(registration_data)
    print('flask')
    print(response)
    return jsonify(response)


@app.route('/research', methods=['GET', 'POST'])
def research():
    upload_data = request.get_json()
    print("Sent to worker")
    response = tasks.researchworker.delay(upload_data)


if __name__ == '__main__':
    app.run()
