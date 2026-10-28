import os, requests
from flask import Flask, request
from io import BytesIO
from PIL import Image, ImageDraw
import random
try:
    from rembg import remove
    HAS_REMBG=True
except:
    HAS_REMBG=False

app=Flask(__name__)
VERIFY_TOKEN=os.getenv("VERIFY_TOKEN","botzapatos100")
WHATSAPP_TOKEN=os.getenv("WHATSAPP_TOKEN","")
PHONE_NUMBER_ID="1429240156934262"
processed_count={"count":0}

def create_concrete_background(size):
    w,h=size
    base=Image.new('RGB',size,(205,200,195))
    draw=ImageDraw.Draw(base)
    for _ in range(8000):
        x=random.randint(0,w-1)
        y=random.randint(0,h-1)
        shade=random.randint(-15,15)
        c=205+shade
        draw.point((x,y),fill=(c,c-2,c-5))
    return base

def process_shoe_image(image_bytes):
    img=Image.open(BytesIO(image_bytes)).convert("RGBA")
    if HAS_REMBG:
        img_no_bg=remove(img)
        if isinstance(img_no_bg,bytes):
            img_no_bg=Image.open(BytesIO(img_no_bg)).convert("RGBA")
    else:
        img_no_bg=img
    w,h=img_no_bg.size
    bg_size=(int(w*1.1),int(h*1.1))
    concrete=create_concrete_background(bg_size)
    x_offset=(bg_size[0]-w)//2
    y_offset=(bg_size[1]-h)//2-20
    concrete.paste(img_no_bg,(x_offset,y_offset),img_no_bg)
    final=concrete.convert("RGB")
    buf=BytesIO()
    final.save(buf,format='JPEG',quality=92)
    buf.seek(0)
    return buf

def send_whatsapp_image(to,image_buffer,caption=""):
    url_upload=f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/media"
    files={'file':('zapato.jpg',image_buffer,'image/jpeg')}
    data={'messaging_product':'whatsapp','type':'image/jpeg'}
    headers={'Authorization':f'Bearer {WHATSAPP_TOKEN}'}
    r=requests.post(url_upload,headers=headers,files=files,data=data)
    media_id=r.json().get('id')
    url_send=f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    payload={"messaging_product":"whatsapp","to":to,"type":"image","image":{"id":media_id,"caption":caption}}
    requests.post(url_send,headers=headers,json=payload)

def send_text(to,text):
    url=f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers={'Authorization':f'Bearer {WHATSAPP_TOKEN}','Content-Type':'application/json'}
    payload={"messaging_product":"whatsapp","to":to,"type":"text","text":{"body":text}}
    requests.post(url,headers=headers,json=payload)

@app.route("/",methods=["GET"])
def home():
    return f"Bot Live! {processed_count['count']}/100",200

@app.route("/webhook",methods=["GET"])
def verify():
    if request.args.get("hub.verify_token")==VERIFY_TOKEN:
        return request.args.get("hub.challenge"),200
    return "fail",403

@app.route("/webhook",methods=["POST"])
def webhook():
    data=request.get_json()
    try:
        value=data['entry'][0]['changes'][0]['value']
        if 'messages' not in value: return "OK",200
        msg=value['messages'][0]
        from_number=msg['from']
        if msg['type']=='image':
            send_text(from_number,f"Recibida {processed_count['count']+1}/100 procesando...")
            image_id=msg['image']['id']
            headers={'Authorization':f'Bearer {WHATSAPP_TOKEN}'}
            r=requests.get(f"https://graph.facebook.com/v20.0/{image_id}",headers=headers)
            image_url=r.json().get('url')
            r_img=requests.get(image_url,headers=headers)
            processed=process_shoe_image(r_img.content)
            processed_count["count"]+=1
            caption=f"Listo {processed_count['count']}/100 Fondo Concreto +$5.000"
            send_whatsapp_image(from_number,processed,caption)
    except Exception as e:
        print(e)
    return "OK",200

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
