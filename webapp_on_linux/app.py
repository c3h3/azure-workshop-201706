import os
APP_ID  = os.environ.get("APP_ID", "AzureWorkshop201706")
APP_HOST  = os.environ.get("APP_HOST", "0.0.0.0")
APP_PORT  = int(os.environ.get("APP_PORT", 80))
DEBUG  = [True, False][int(os.environ.get("DEBUG", 0))]

# Variables about linebot
CHANNEL_SECRET  = os.environ.get("CHANNEL_SECRET", "")
ChHANNEL_ACCESS_TOKEN = os.environ.get("ChHANNEL_ACCESS_TOKEN", "")

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
    MessageEvent, TextMessage, TextSendMessage
)

handler = WebhookHandler(CHANNEL_SECRET)
line_bot_api = LineBotApi(ChHANNEL_ACCESS_TOKEN)


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

if __name__ == "__main__":
    app.debug = DEBUG
    app.run(host=APP_HOST, port=APP_PORT)