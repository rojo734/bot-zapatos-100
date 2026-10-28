import os
from flask import Flask, request, jsonify
from PIL import Image, ImageOps
import requests
from io import BytesIO

app = Flask(__name__)

# Fondo concreto claro que usas para los 100 zapatos
BG_COLOR = (230, 230, 225)

def procesar_imagen_con_fondo_concreto(imagen_bytes):
    # Importamos rembg aqui adentro para que Render inicie rapido
    from rembg import remove
    import numpy as np

    input_img = Image.open(BytesIO(imagen_bytes)).convert("RGBA")
    # Quita fondo
    output_rgba = remove(input_img)
    
    # Crear fondo concreto
    bg = Image.new("RGBA", output_rgba.size, BG_COLOR + (255,))
    # Pegar zapato sobre concreto
    final = Image.alpha_composite(bg, output_rgba)
    final = final.convert("RGB")
    
    # Agregar texto de precio $5.000
    # (si quieres, lo dejamos sin texto por ahora para que sea mas rapido)
    
    buf = BytesIO()
    final.save(buf, format="JPEG", quality=90)
    buf.seek(0)
    return buf

@app.route("/")
def home():
    return "Bot de Zapatos 100 - Activo - Fondo Concreto + $5k", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verificacion de Meta
        if request.args.get("hub.verify_token") == os.getenv("VERIFY_TOKEN", "zapatos100"):
            return request.args.get("hub.challenge")
        return "Error token", 403
    
    # POST - llega foto de WhatsApp
    data = request.get_json()
    try:
        # Aqui va tu logica de WhatsApp
        # Por ahora solo respondemos OK para que Render marque Live
        print("Mensaje recibido:", data)
    except Exception as e:
        print(e)
    
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
