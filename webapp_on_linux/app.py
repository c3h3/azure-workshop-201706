import os
APP_ID  = os.environ.get("APP_ID", "AzureWorkshop201706")
APP_HOST  = os.environ.get("APP_HOST", "0.0.0.0")
APP_PORT  = os.environ.get("APP_PORT", 5000)
DEBUG  = [True, False][int(os.environ.get("DEBUG", 0))]
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://")
DB = os.environ.get("DB", "az")

try:
    from local_settings import *
except:
    pass

from flask import Flask, request, abort, render_template, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient

mcli = MongoClient(MONGODB_URI)
db = mcli[DB]

sample_data = [{"text":"Hello! Flask!"}, 
               {"text":"Flask is awesome!"}, 
               {"text":"Flask is the best!"}]
    
if db.messages.find().count() == 0:
    for raw in sample_data:
        db.messages.insert(raw)

@app.route('/')
def index():
    return render_template("home.html",
        title = 'Home',
        app_id = APP_ID,
        data = db.messages.find())


@app.route('/submit', methods=['POST'])
def submit():
    raw = {"text":request.form['message']}
    db.messages.insert(raw)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.debug = DEBUG
    app.run(host=APP_HOST, port=APP_PORT)