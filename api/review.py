from flask import Blueprint, Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
import boto3
from ref.config import Config
from PIL import Image
from ref.database import db
from bson.objectid import ObjectId
from datetime import datetime
import json

# app.py 와 연결
review_bp = Blueprint('review', __name__, url_prefix='/review')


def sm2_algorithm(quality: int, repetitions: int, previous_interval: int, easiness_factor: float):
    # quality 사용자 평가 점수 (쉬움 : 5, 보통: 4, 어려움: 1)
    # repetitions 연속 성공 횟수
    # interval 이전 복습 간격
    # easiness_factor 쉬움 계수 
    
    # 쉬움, 보통
    if quality >= 4: 
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(previous_interval * easiness_factor)
            # 10 * 
        repetitions += 1
    
    # 어려움
    else :
        repetitions = 0
        interval = 1
    
    # EF 공식 (기존의 EF와 사용자 평가 점수를 통해 재계산)
    easiness_factor = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    # EF 는 1.3 이 최솟값
    if easiness_factor < 1.3 :
        easiness_factor = 1.3
        
    return repetitions, interval, round(easiness_factor,2)

    # jsonify({'result':'success',
    #                 'repetitions':repetitions, 
    #                 'interval':interval, 
    #                 'easiness_factor':round(easiness_factor,2)})



# 복습완료 API
@review_bp.route('/complete', methods=['POST'])
def review_complete():
    studylog_id = request.form['studylogId']
    quality = request.form['quality'] # 쉬움 easy, 보통 good , 어려움 hard
    review_date = request.form['reviewDate']
    
    # 날짜 변환
    date_format = "%Y-%m-%d"
    date_object = datetime.strptime(review_date, date_format)
    
    # 사용자 평가 지표 숫자로 변환
    if quality == 'easy':
        quality = 5
    elif quality == 'good':
        quality = 4
    else :
        quality = 1
    
    # db 에서 검색
    studylog = db.studylogs.find_one({'_id':ObjectId(studylog_id)})
    
    # id 검색하여 이전 값 가져오기 
    prv_repetitions = studylog['repetitions']
    prv_interval = studylog['interval']
    prv_easiness_factor = studylog['easiness_factor']
    
    # SM-2 알고리즘 조회
    result = sm2_algorithm(quality, prv_repetitions, prv_interval, prv_easiness_factor)

    repetitions = result[0]
    interval = result[1]
    easiness_factor = result[2]
    
    # DB에 알고리즘 값 업데이트
    db.studylogs.update_one({'_id':ObjectId(studylog_id)},
                            {'$set':{'repetitions':repetitions, 
                                     'interval':interval, 
                                     'easiness_factor':easiness_factor,
                                     'review_date':date_object}})
    
    return jsonify({'result':"success", 'msg':'복습주기가 업데이트 되었습니다!'}) 


# 복습주기 된 학습기록 노출
@review_bp.route('/list', methods=['GET'])
def review_studylog_list():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # select _id, title from studylogs s 
    # where s.review_date + s.interval > today mongodb
    results = list(db.studylogs.aggregate([
        {"$addFields":{
            "review_date_chk": {
                "$add" : ["$review_date", {"$multiply": ["$interval", 86400000]}]
            }
        }},
        {"$match": {
            "review_date_chk": {"$lte":today}
        }},
        {"$sort": { "review_date_chk": 1}}
    ]))
        
    for n in results:
        n['_id'] = str(n['_id'])
 
    return jsonify({'result':'success', 'reveiw_studylogs':results})