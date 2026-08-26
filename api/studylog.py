from flask import Blueprint, Flask, render_template, request, jsonify
from pymongo import MongoClient
from ref.database import db
from datetime import datetime

# app.py 와 연결
studylogs_bp = Blueprint('studylogs', __name__, url_prefix='/studylogs')

# 1. 이미지를 받아 static/uploads 폴더에 저장하고 파일명을 리턴하는 라우터
@studylogs_bp.route('/upload', methods=['POST'])
def studylogs_image_upload():
    if 'files' not in request.files:
        return jsonify({'result': 'fail', 'msg': '전송된 파일이 없습니다.'}), 400
    
    file = request.files['files']
    
    if file.filename == '':
        return jsonify({'result': 'fail', 'msg': '선택된 파일이 없습니다.'}), 400

    # 파일명 충돌을 막기 위해 타임스탬프 접두사 추가
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{timestamp}_{file.filename}"
    
    # uploads 폴더 자동 생성
    upload_folder = os.path.join('static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # 실제 서버 경로에 파일 저장
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    return jsonify({
        'result': 'success',
        'filename': filename
    })

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
        'easiness_factor': 2.5
    }
    
    db.studylogs.insert_one(studylogs)
    
    return jsonify({
    'result': 'success', 
    'msg': '학습일지가 성공적으로 저장되었습니다!'
})
