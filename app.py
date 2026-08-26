from flask import Flask, render_template
from ref.config import Config
# api 파일 import
from api.login import *
from api.studylog import *
from api.review import *
from api.file import *

from ref.database import db

app = Flask(__name__)

# .env 내용 불러오기
app.config.from_object(Config)

#flask session용 비밀번호 암호화
app.secret_key = "test-secret-key"

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/studylogcreate')
def studylogcreate():
    return render_template('studylogcreate.html')

# api/*.py 등록
app.register_blueprint(login_bp)
app.register_blueprint(studylogs_bp)
app.register_blueprint(file_bp)
app.register_blueprint(review_bp)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
    
    
