from flask import Flask, render_template
from ref.config import Config
# api 파일 import
from api.login import *
from api.studylog import *
from api.review import *
from api.file import *

from pymongo import MongoClient

from api.file import file_bp # 파일 위치에 맞게 임포트
app.register_blueprint(file_bp)

client = MongoClient('localhost',27017)
db = client.dbjungminder

app = Flask(__name__)

# .env 내용 불러오기
app.config.from_object(Config)

@app.route('/')
def home():
    return render_template('index.html')

# api/*.py 등록
app.register_blueprint(studylogs_bp)
app.register_blueprint(file_bp)




if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
    
    
