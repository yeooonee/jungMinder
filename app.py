from flask import Flask, render_template
from api.login import *
from api.card import *
from api.review import *


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)