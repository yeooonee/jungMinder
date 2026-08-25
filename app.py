from flask import Flask, render_template
from api.login import *
from api.studylog import *
from api.review import *

from pymongo import MongoClient

client = MongoClient('localhost',27017)
db = client.dbjungminder

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# api/*.py 등록
app.register_blueprint(studylogs_bp)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
    
    
