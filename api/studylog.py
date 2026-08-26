from flask import Blueprint, Flask, render_template, request, jsonify, session
from pymongo import MongoClient
from ref.database import db
from datetime import datetime
# 문자열을 MongoDB의 ObjectId로 변환
from bson import ObjectId
import os
from api.file import img_presigned_url
from bs4 import BeautifulSoup
import re

# app.py와 연결되는 블루프린트 설정 (url_prefix가 /studylogs 임)
studylogs_bp = Blueprint('studylogs', __name__, url_prefix='/studylogs')


# 페이지네이션 
def get_paginated_list(data, page=1, page_size=2):
    start = (page - 1) * page_size
    end = start + page_size
    return data[start:end]

# studylog 목록 조회
@studylogs_bp.route('/list', methods=['GET'])
def studylogs_list():
    page = request.args.get('page',1,type=int)
    
    # 검색어가 있을 때 검색조건 추가 
    query = {}
    if request.form.get('searchword'):
        searchword = request.form['searchword']
        query = {'$or': [
                    {'title':{"$regex":searchword}},
                    {'content':{"$regex":searchword}}
                ]
        }
    results = list(db.studylogs.find(query))
    
    print(results)
    
    for n in results:
        n['_id'] = str(n['_id'])
        
        # 태그 따로 빼기 
        content = n['content']
        tags = re.findall(r'#\S+', content)
        n['tags'] = tags     

    # 페이지네이션    
    paginated_results = get_paginated_list(results, page)
    print(paginated_results)
    
    return jsonify({'result':'success', 'results':paginated_results})

# 3. studylog 생성 라우터 (POST /studylogs/create)
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
    result = db.studylogs.insert_one(studylogs)
    
    return jsonify({
    'result': 'success', 
    'msg': '학습일지가 성공적으로 저장되었습니다!',
    #학습기록 최초 저장 이후 조회페이지로 가기 위해 _id 반환하기 위한 코드
    'id': str(result.inserted_id)
    })

# studylog 조회
@studylogs_bp.route('/view/<id>', methods=['GET'])
def studylogs_view(id):
    #테스트용으로 임의로 넣은 로그인정보
    #user_id = 'test1234'
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

# studylog 수정 화면
@studylogs_bp.route('/create/<id>', methods=['GET'])
def studylogs_create_edit(id):
    #테스트용으로 임의로 넣은 로그인정보
    #user_id = 'test1234'
    user_id = session['user_id']

    studylog = db.studylogs.find_one({
        '_id': ObjectId(id),
        'reg_id': user_id
    })

    if studylog is None:
        return '학습일지를 찾을 수 없습니다', 404

    return render_template(
        'studylogcreate.html',
        studylog=studylog
    )

# studylog 수정
@studylogs_bp.route('/update/<id>', methods=['POST'])
def studylogs_update(id):

    title = request.form['title']
    content = request.form['content']

    result = db.studylogs.update_one(
        {
            '_id': ObjectId(id)
        },
        {
            '$set': {
                'title': title,
                'content': content,
                'mod_dt': datetime.now()
            }
        }
    )

    if result.matched_count == 0:
        return jsonify({
            'result': 'fail',
            'msg': '학습일지를 찾을 수 없습니다.'
        })

    return jsonify({
        'result': 'success',
        'msg': '학습일지가 성공적으로 수정되었습니다.!',
        'id': str(id)
    })

# studylog 삭제
@studylogs_bp.route('/delete/<id>', methods=['POST'])
def studylogs_delete(id):
    #테스트용으로 임의로 넣은 로그인정보
    #user_id = 'test1234'
    user_id = session['user_id']

    result = db.studylogs.delete_one({
        '_id': ObjectId(id),
        'reg_id': user_id
    })

    if result.deleted_count == 0:
        return jsonify({
            'result': 'fail',
            'msg': '학습일지를 찾을 수 없습니다.'
        })

    return jsonify({
        'result': 'success',
        'msg': '학습일지가 삭제되었습니다.'
    })