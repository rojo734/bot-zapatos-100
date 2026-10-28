import os, requests
from flask import Flask, request
from PIL import Image
from io import BytesIO

app = Flask(__name__)
VERIFY_TOKEN = "zapatos100"
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")

BG_COLOR = (230, 230, 225)  # Tu concreto clarito

@app.route("/")
def home():
    return "Bot Zapatos 100 Activo - Fondo Concreto", 200

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Error", 403

@app.route("/webhook", methods=["POST"])
def incoming():
    data = request.get_json()
    print(data)
    try:
        # Aqui llega la foto de WhatsApp
        # Por ahora solo confirmamos que llegó
        # Luego agregamos la lógica de descargar y editar
        if "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    msg = change.get("value", {}).get("messages", [])
                    if msg and msg[0].get("image"):
                        print("FOTO DE ZAPATO RECIBIDA!")
    except Exception as e:
        print(e)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
