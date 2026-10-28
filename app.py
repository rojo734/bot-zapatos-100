import os
from flask import Flask, request

app = Flask(__name__)
VERIFY_TOKEN = "zapatos100"

@app.route("/")
def home():
    return "Bot Zapatos 100 Activo", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        print(f"Verificando: mode={mode} token={token}")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK VERIFICADO!")
            return challenge, 200
        else:
            return "Token no coincide", 403

    if request.method == "POST":
        data = request.get_json()
        print("Mensaje recibido:", data)
        return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
