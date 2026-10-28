import os, requests
from flask import Flask, request
from PIL import Image, ImageDraw
from io import BytesIO

app = Flask(__name__)
VERIFY_TOKEN = "zapatos100"
PHONE_ID = os.getenv("PHONE_ID", "1429240156934262")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
BG_COLOR = (230, 230, 225)  # concreto clarito
GRAPH_URL = f"https://graph.facebook.com/v21.0/{PHONE_ID}"

def editar_foto_zapato(image_bytes):
    from rembg import remove
    img = Image.open(BytesIO(image_bytes)).convert("RGBA")
    sin_fondo = remove(img)
    bg = Image.new("RGBA", sin_fondo.size, BG_COLOR + (255,))
    final_rgba = Image.alpha_composite(bg, sin_fondo)
    final = final_rgba.convert("RGB")
    
    # Poner precio $5.000
    w, h = final.size
    draw = ImageDraw.Draw(final)
    # caja negra abajo
    box_h = int(h * 0.12)
    draw.rectangle([0, h - box_h, w, h], fill=(0,0,0))
    # texto - centrado
    try:
        # intenta con fuente grande
        draw.text((w*0.42, h - box_h + 10), "$5.000", fill=(255,255,255))
    except:
        draw.text((w*0.42, h - box_h + 10), "$5.000", fill=(255,255,255))
    
    buf = BytesIO()
    final.save(buf, format="JPEG", quality=92)
    buf.seek(0)
    return buf

def get_media_url(media_id):
    url = f"https://graph.facebook.com/v21.0/{media_id}"
    r = requests.get(url, headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"})
    return r.json().get("url")

def download_media(media_url):
    r = requests.get(media_url, headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"})
    return r.content

def send_image_back(to_number, image_buf):
    # 1. Subir imagen a WhatsApp
    files = {"file": ("zapato.jpg", image_buf, "image/jpeg")}
    data = {"type": "image/jpeg", "messaging_product": "whatsapp"}
    upload = requests.post(f"{GRAPH_URL}/media", headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"}, files=files, data=data)
    media_id = upload.json().get("id")
    if not media_id:
        print("Error upload:", upload.text)
        return
    
    # 2. Enviar mensaje con imagen
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "image",
        "image": {"id": media_id, "caption": "Listo ✅ Fondo concreto + $5.000"}
    }
    r = requests.post(f"{GRAPH_URL}/messages", headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}, json=payload)
    print("Enviado:", r.text)

@app.route("/")
def home():
    return "Bot Zapatos 100 - WhatsApp Activo", 200

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print(data)
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" in entry:
            msg = entry["messages"][0]
            from_number = msg["from"]
            if msg.get("type") == "image":
                media_id = msg["image"]["id"]
                print(f"Foto recibida de {from_number}, id {media_id}")
                media_url = get_media_url(media_id)
                img_bytes = download_media(media_url)
                editado = editar_foto_zapato(img_bytes)
                send_image_back(from_number, editado)
    except Exception as e:
        print("Error:", e)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
