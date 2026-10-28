import os
from flask import Flask, request, send_file
from PIL import Image
from io import BytesIO

app = Flask(__name__)
VERIFY_TOKEN = "zapatos100"
BG_COLOR = (230, 230, 225)

def editar(imagen_bytes):
    from rembg import remove
    img = Image.open(BytesIO(imagen_bytes)).convert("RGBA")
    sin_fondo = remove(img)
    bg = Image.new("RGBA", sin_fondo.size, BG_COLOR + (255,))
    final = Image.alpha_composite(bg, sin_fondo).convert("RGB")
    buf = BytesIO()
    final.save(buf, format="JPEG", quality=92)
    buf.seek(0)
    return buf

@app.route("/")
def home():
    return '''
    <h2>Bot Zapatos 100 - Activo</h2>
    <p>Fondo concreto listo</p>
    <form action="/test" method="post" enctype="multipart/form-data">
    <input type="file" name="file"><button>Probar Fondo Concreto</button>
    </form>
    '''

@app.route("/test", methods=["POST"])
def test():
    file = request.files["file"]
    result = editar(file.read())
    return send_file(result, mimetype="image/jpeg")

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
