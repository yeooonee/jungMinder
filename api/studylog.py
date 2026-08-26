from flask import Blueprint, Flask, render_template, request, jsonify
from pymongo import MongoClient
from ref.database import db
from datetime import datetime

# app.py 와 연결
studylogs_bp = Blueprint('studylogs', __name__, url_prefix='/studylogs')

# studylog 생성
@studylogs_bp.route('/create', methods=['POST'])
def studylogs_create():
    title = request.form['title']
    content = request.form['content']
    reg_id = request.form['regId']
    reg_dt = request.form['regDt']
    mod_dt = request.form['modDt']
    
    studylogs = {
        'title' : title,
        'content' : content,
        'reg_id' : reg_id,
        'reg_dt' : datetime.now(),
        'mod_dt' : "",
        'repetitions' : 0,
        'interval': 1,
        'easiness_factor': 2.5,
        'review_date' : datetime.now()
    }
    
    db.studylogs.insert_one(studylogs)
    
    return jsonify({
    'result': 'success', 
    'msg': '학습일지가 성공적으로 저장되었습니다!'
})
