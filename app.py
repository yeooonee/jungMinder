from flask import Flask
from api.login import *
from api.card import *
from api.review import *


app = Flask(___name___)

@app.route('/')
def home():
    return 'This is home!'

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)