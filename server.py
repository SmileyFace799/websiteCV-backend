from datetime import datetime as dt
from flask import Flask, jsonify, request
from flask_cors import CORS
from waitress import serve
from portalocker import portalocker, LOCK_EX
import json

# Create a Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": [
        "http://localhost:5173",
        "https://smiley-face.no/websiteCV"
    ],
    "allow_headers": ["X-API-key"]
}})

DEBUG = True

def check_valid(key: str) -> bool:
    if not key: return False

    keyIsValid = False
    forRemoval = []
    with open("secretData/keys.json", "r+") as keysFile:
        portalocker.lock(keysFile, LOCK_EX)
        try:
            keys = json.load(keysFile)
            i = 0
            while not keyIsValid and i < len(keys):
                if (dt.now() >= dt.fromisoformat(keys[i]["expiry"])):
                    forRemoval.insert(0, i)
                else:
                    keyIsValid = key == keys[i]["key"]
                i += 1
        finally:
            portalocker.unlock(keysFile)

    if forRemoval:
        for i in forRemoval:
            keys.pop(i)
        with open("secretData/keys.json", "w") as keysFile:
            portalocker.lock(keysFile, LOCK_EX)
            try:
                json.dump(keys, keysFile, indent=4)
            finally:
                portalocker.unlock(keysFile)
    
    return keyIsValid

@app.route('/assertValid', methods=['GET'])
def assert_valid():
    return jsonify(result={"valid": check_valid(request.headers.get("X-API-key"))})

@app.route('/confidential', methods=['GET'])
def confidential():
    response = (jsonify({'error': 'Unauthorized'}), 401)
    if check_valid(request.headers.get("X-API-key")):
        with open("secretData/lang.json", "r") as f:
            response = jsonify(result=json.load(f))
    return response

if __name__ == '__main__':
    if DEBUG:
        app.run(debug=True)
    else:
        serve(app, host='0.0.0.0', port=8000)