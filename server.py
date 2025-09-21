from datetime import datetime as dt
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from cheroot.wsgi import Server as WSGIServer
from cheroot.ssl.builtin import BuiltinSSLAdapter
from portalocker import portalocker, LOCK_EX
from os import _exit
from time import sleep
import json
import dateTmeStr

app = Flask(__name__)
ssl_adapter = None

with open("host_config.json", "r") as f:
    config = json.load(f)
    DEBUG = config["debug"]
    if not DEBUG and "ssl" in config and "cert" in config["ssl"] and config["ssl"]["cert"] and "key" in config["ssl"] and config["ssl"]["key"]:
        ssl_adapter = BuiltinSSLAdapter(
            certificate=config["ssl"]["cert"],
            private_key=config["ssl"]["key"]
        )

    CORS(app, resources={r"/*": {
        "origins": config["origins"]["debug" if DEBUG else "production"],
        "allow_headers": ["X-API-key"]
    }})

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
                if (dt.now() >= dateTmeStr.fromStr(keys[i]["expiry"])):
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

@app.route('/confidential/image/png', methods=['GET'])
def get_image():
    filename = request.args.get('name') + ".png"
    if check_valid(request.headers.get("X-API-key")):
        return send_from_directory('secretData/imgs', filename)

if __name__ == '__main__':
    if DEBUG:
        app.run(debug=True)
    else:
        print("Creating production server...")
        server = WSGIServer(
            bind_addr=('0.0.0.0', 8000),
            wsgi_app=app
        )
        print("Server created!")
        if ssl_adapter:
            print("Adding SSL...")
            server.ssl_adapter = ssl_adapter
            print("SSL added!")
        else:
            print("No SSL info found, SSL skipped")
        
        try:
            print("Starting production server...")
            server.start()
        except KeyboardInterrupt:
            print("Shutting down server...")
        finally:
            server.stop()
            sleep(1) # Give some time before the _exit()-signal is called
            print("Server stopped")
            _exit(0)
            