from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def home():
    text = { 'content': 'Welcome to your flask application !' } 
    return render_template("home.html",
        title = 'Home',
        text = text)

@app.route('/test')
def test():
    sample_data = [{"text":"Hello! Flask!"}, 
                   {"text":"Flask is awesome!"}, 
                   {"text":"Flask is the best!"}]
    return render_template("home.html",
        title = 'TEST',
        data = sample_data)


app.debug = True
if __name__ == "__main__":
    app.run()
