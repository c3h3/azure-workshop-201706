import os
APP_ID  = os.environ.get("APP_ID", "AzureWorkshop201706")
APP_HOST  = os.environ.get("APP_HOST", "0.0.0.0")
APP_PORT  = int(os.environ.get("APP_PORT", 80))
DEBUG  = [True, False][int(os.environ.get("DEBUG", 0))]
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://")
DB = os.environ.get("DB", "az")

# Variables about linebot
CHANNEL_SECRET  = os.environ.get("CHANNEL_SECRET", "")
ChHANNEL_ACCESS_TOKEN = os.environ.get("ChHANNEL_ACCESS_TOKEN", "")

# Variables about linebot
AZURE_STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT", "")
AZURE_STORAGE_ACCOUNT_KEY = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY", "")

try:
    from local_settings import *
except:
    pass

from flask import Flask, request, abort, render_template

app = Flask(__name__)

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)

handler = WebhookHandler(CHANNEL_SECRET)
line_bot_api = LineBotApi(ChHANNEL_ACCESS_TOKEN)


from azure.storage.blob import BlockBlobService
service = BlockBlobService(account_name=AZURE_STORAGE_ACCOUNT,
                           account_key=AZURE_STORAGE_ACCOUNT_KEY)

service.create_container(APP_ID)
con = list(filter(lambda con:con.name == APP_ID,service.list_containers()))[0]

from pymongo import MongoClient

mcli = MongoClient(MONGODB_URI)
db = mcli[DB]

import datetime, hashlib, json
from datetime import datetime

@app.route('/')
def index():
    return render_template("home.html",
        title = 'Home',
        app_id = APP_ID)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)  # default
def handle_text_message(event):  # default
    my_line_id = event.source.sender_id

    if event.type == "message":
        msg = event.message.text  # message from user
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Your line id is {line_id}. Your message is: {msg}".format(line_id=my_line_id,msg=msg)))


@handler.add(MessageEvent, message=ImageMessage)  # default
def handle_image_message(event):  # default
    my_line_id = event.source.sender_id
    save_event(db, APP_ID, my_line_id, event)

    if event.type == "message":
        save_message(db, APP_ID, my_line_id, event.message)
        retrieve_image_message(APP_ID, line_bot_api,service,con,event.message.id)

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Recieve ImageMessage!"))

def save_message(db, app_id, user_id, message):
    try:
        data = {}
        hash_data = {"appId": app_id, "userId": user_id}
        data["uid"] = hashlib.sha256(json.dumps(hash_data,sort_keys=True).encode("utf-8")).hexdigest()
        data["message"] = json.loads(str(message))
        data["createAt"] = datetime.utcnow()
        db.messages.insert(data)
        print("CALL save_message SUCCESSFULLY")
    except Exception as e:
        print(e)

def save_event(db, app_id, user_id, event):
    try:
        data = {}
        hash_data = {"appId": app_id, "userId": user_id}
        data["uid"] = hashlib.sha256(json.dumps(hash_data,sort_keys=True).encode("utf-8")).hexdigest()
        data["event"] = json.loads(str(event))
        data["createAt"] = datetime.utcnow()
        db.eventsLog.insert(data)
        print("CALL save_message SUCCESSFULLY")
    except Exception as e:
        print(e)

def retrieve_image_message(app_id, line_bot_api, service, con, message_id):
    message = line_bot_api.get_message_content(message_id)
    message_type = message.content_type.split("/")[-1].split("-")[-1]
    message_file = "{message_id}.{ftype}".format(message_id=message_id, ftype=message_type)
    with open(message_file, "wb") as wf:
        wf.write(message.content)

    content_type = "image"

    service.create_blob_from_path(
        con.name,
        "{type}/{file}".format(type=content_type, file=message_file),
        message_file,
        content_settings=ContentSettings(content_type=message.content_type)
    )

    return "https://pyladiesbot.blob.core.windows.net/{APP_ID}/{type}/{MESSAGE_FILE}".format(APP_ID=app_id,
                                                                                             type=content_type,
                                                                                             MESSAGE_FILE=message_file)

if __name__ == "__main__":
    app.debug = DEBUG
    app.run(host=APP_HOST, port=APP_PORT)