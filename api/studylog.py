from flask import Blueprint, Flask, render_template, request, jsonify, session
from pymongo import MongoClient
from ref.database import db
from datetime import datetime
# 문자열을 MongoDB의 ObjectId로 변환
from bson import ObjectId
import os
from api.file import img_presigned_url
from bs4 import BeautifulSoup

# app.py 와 연결
studylogs_bp = Blueprint('studylogs', __name__, url_prefix='/studylogs')



# studylog 생성
@studylogs_bp.route('/create', methods=['POST'])
def studylogs_create():
    title = request.form['title']
    content = request.form['content']
    reg_id = session.get('user_id')
        
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

# studylog 조회
@studylogs_bp.route('/view/<id>', methods=['GET'])
def studylogs_view(id):
    user_id = session['user_id']

    studylog = db.studylogs.find_one({
        '_id': ObjectId(id),
        'reg_id': user_id
    })
    
    # content img intercept
    content = studylog['content']
    
    soup = BeautifulSoup(content, 'html.parser')
    image = soup.find_all(name='img')
    
    # 이미지 태그 배열 돌기 
    for n in image:
        filename = n['alt']
        new_img_url = img_presigned_url(filename)
        print(new_img_url)
        n.attrs.update({'src':new_img_url})
        
    
    
    content = str(soup).replace('&amp;', '&')
    print(content)
    
    studylog['content'] = content
        
    if studylog is None:
        return '학습일지를 찾을 수 없습니다.', 404

    #ssr
    return render_template(
        'studylog_view.html',
        studylog=studylog
    )
