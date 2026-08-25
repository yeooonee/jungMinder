from flask import Blueprint, Flask, render_template, request, jsonify
from pymongo import MongoClient
from ref.database import db

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
        'reg_id' : reg_dt,
        'mod_dt' : mod_dt
    }
    
    db.studylogs.insert_one(studylogs)
    
    return jsonify({'result':'success'})