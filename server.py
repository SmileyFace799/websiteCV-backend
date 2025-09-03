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


# Define a route
@app.route('/confidential', methods=['GET'])
def confidential():
    request_key = request.headers.get("X-API-key")
    forRemoval = []
    response = (jsonify({'error': 'Unauthorized'}), 401)
    with open("secretData/keys.json", "r+") as keysFile:
        keyIsValid = False
        portalocker.lock(keysFile, LOCK_EX)
        try:
            keys = json.load(keysFile)
            i = 0
            while not keyIsValid and i < len(keys):
                if (dt.now() >= dt.fromisoformat(keys[i]["expiry"])):
                    forRemoval.insert(0, i)
                else:
                    keyIsValid = request_key == keys[i]["key"]
                i += 1
        finally:
            portalocker.unlock(keysFile)
            if keyIsValid:
                with open("secretData/lang.json", "r") as f:
                    response = jsonify(result=json.load(f))
    if forRemoval:
        with open("secretData/keys.json", "w") as keysFile:
            for i in forRemoval:
                keys.pop(i)
            keysFile.seek(0)
            json.dump(keys, keysFile, indent=4)
    return response

if __name__ == '__main__':
    if DEBUG:
        app.run(debug=True)
    else:
        serve(app, host='0.0.0.0', port=8000)