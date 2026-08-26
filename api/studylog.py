from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
from ref.database import db
from bson.objectid import ObjectId
from api.file import img_presigned_url
from bs4 import BeautifulSoup
import re
import os

# app.py와 연결되는 블루프린트 설정
studylogs_bp = Blueprint('studylogs', __name__, url_prefix='/studylogs')

# 1. 새 글쓰기 페이지 렌더링 (GET /studylogs/create)
@studylogs_bp.route('/create', methods=['GET'])
def studylogs_create_page():
    user_name = session.get('user_name', '사용자')
    return render_template('studylogcreate.html', user_name=user_name, studylog=None)

# 2. 이미지 업로드 라우터 (POST /studylogs/upload)
@studylogs_bp.route('/upload', methods=['POST'])
def studylogs_image_upload():
    if 'files' not in request.files:
        return jsonify({'result': 'fail', 'msg': '전송된 파일이 없습니다.'}), 400
    
    file = request.files['files']
    
    if file.filename == '':
        return jsonify({'result': 'fail', 'msg': '선택된 파일이 없습니다.'}), 400

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{timestamp}_{file.filename}"
    
    upload_folder = os.path.join('static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    return jsonify({
        'result': 'success',
        'filename': filename
    })

# 3. studylog 생성 라우터 (POST /studylogs/create)
@studylogs_bp.route('/create', methods=['POST'])
def studylogs_create():
    title = request.form.get('title')
    content = request.form.get('content')
    reg_id = session.get('user_id', request.form.get('regId', 'anonymous'))
    
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

# 4. 하단 카드 리스트 노출 및 페이징/검색 라우터 (GET /studylogs/list)
@studylogs_bp.route('/list', methods=['GET'])
def studylog_list():
    page = int(request.args.get('page', 1))
    searchword = request.args.get('searchword', '').strip()
    items_per_page = 2  # 페이지당 보여줄 카드 개수
    
    query = {}
    if searchword:
        query = {
            "$or": [
                {"title": {"$regex": searchword, "$options": "i"}},
                {"content": {"$regex": searchword, "$options": "i"}}
            ]
        }
    
    total_count = db.studylogs.count_documents(query)
    skip_count = (page - 1) * items_per_page
    
    studylogs = list(db.studylogs.find(query).skip(skip_count).limit(items_per_page))
    for n in studylogs:
        n['_id'] = str(n['_id'])
        
    return jsonify({
        'result': 'success', 
        'studylogs': studylogs,
        'total_count': total_count,
        'current_page': page
    })

# 5. 학습일지 상세 조회 (SSR 렌더링)
@studylogs_bp.route('/lookup', methods=['GET'])
def studylogs_view():
    studylog_id = request.args.get('id')
    user_id = session.get('user_id')

    studylog = db.studylogs.find_one({
        '_id': ObjectId(studylog_id)
    })

    if studylog is None:
        return '학습일지를 찾을 수 없습니다.', 404

    # content 내 이미지 태그 가공 (Presigned URL 적용 등)
    content = studylog['content']
    soup = BeautifulSoup(content, 'html.parser')
    images = soup.find_all(name='img')

    for n in images:
        filename = n.get('alt', '')
        if filename:
            new_img_url = img_presigned_url(filename)
            n.attrs.update({'src': new_img_url})

    content = str(soup).replace('&amp;', '&')
    studylog['content'] = content
    studylog['_id'] = str(studylog['_id'])

    user_name = session.get('user_name', '사용자')

    return render_template('studylog_view.html', studylog=studylog, user_name=user_name)