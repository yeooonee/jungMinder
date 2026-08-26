from flask import Flask, render_template
from api.login import *
from api.card import *
from api.review import *

from pymongo import MongoClient

from api.file import file_bp # 파일 위치에 맞게 임포트
app.register_blueprint(file_bp)

client = MongoClient('localhost',27017)
db = client.dbjungminder

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)