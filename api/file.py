from flask import Blueprint, Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
import boto3
from ref.config import Config
from PIL import Image
from ref.database import db

# app.py 와 연결
file_bp = Blueprint('file', __name__, url_prefix='/file')

s3 = boto3.client(service_name='s3', 
                  region_name = Config.S3_REGION,
                  aws_access_key_id = Config.ACCESS_KEY,
                  aws_secret_access_key = Config.SECRET_KEY,
                  )


# 이미지 저장 (S3 서버에 업로드)
@file_bp.route('/upload', methods=['POST'])
def file_upload():
    file = request.files['image']
    
    # 이미지 용량 검사
    content_length = request.content_length
    if content_length and content_length > 5 * 1024 * 1024 :
        return {'error':'업로드 실패: 파일 크기는 최대 5MB까지 지원합니다.'}, 413
    
    # 이미지 타입 검사
    file_type = os.path.splitext(file.filename)[1] # 기존 파일 타입 추출
    if file_type not in ('.jpg','.png','.jpeg'):
        return {'error': file_type + '은 지원하는 이미지 파일이 아닙니다.'}, 500

    # 파일명 변경
    current_time = datetime.now()
    new_file_name = current_time.isoformat().replace(':','_')+file_type
    file.filename = new_file_name

    # S3 업로드
    s3 = boto3.client('s3', aws_access_key_id = Config.ACCESS_KEY,aws_secret_access_key = Config.SECRET_KEY)
    try:
        s3.upload_fileobj(file, Config.S3_BUCKET, file.filename, ExtraArgs={'ContentType':file.content_type})
    except Exception as e:
        return {'error':str(e)}, 500
    
    img_url = new_file_name
    return jsonify({'result':'success','img_url':img_url})


# 이미지 읽어오기
@file_bp.route('/read', methods=['POST'])
def image_read():
    filename = request.form['image']
    
    # s3 = boto3.client('s3',
    #                   aws_access_key_id = Config.ACCESS_KEY, 
    #                   aws_secret_access_key = Config.SECRET_KEY, 
    #                   region_name = Config.S3_REGION)
    # response = s3.get_object(Bucket=Config.S3_BUCKET, Key=filename)
    # location = s3.get_bucket_location(Bucket=Config.S3_BUCKET)["LocationConstraint"]
    
    # 임시 전체 허용 경로
    try:
        url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': Config.S3_BUCKET, 'Key': filename},
        ExpiresIn=3600  # 1시간 유효
        )
    except Exception as e :
        return {'error':str(e)},500
    
    # img = Image.open(response['Body'])
    # return f"https://{Config.S3_BUCKET}.s3.{location}.amazonaws.com/{filename}"
    return url
    
    
@file_bp.route('/multiupload', methods=['POST'])
def multi_file_upload():
    file = request.files['image']
    
    print(file)
    
    # 이미지 용량 검사
    content_length = request.content_length
    if content_length and content_length > 5 * 1024 * 1024 :
        return {'error':'업로드 실패: 파일 크기는 최대 5MB까지 지원합니다.'}, 413
    
    # 이미지 타입 검사
    file_type = os.path.splitext(file.filename)[1] # 기존 파일 타입 추출
    if file_type not in ('.jpg','.png','.jpeg'):
        return {'error': file_type + '은 지원하는 이미지 파일이 아닙니다.'}, 500

    # 파일명 변경
    current_time = datetime.now()
    new_file_name = current_time.isoformat().replace(':','_')+file_type
    file.filename = new_file_name

    # S3 업로드
    s3 = boto3.client('s3', aws_access_key_id = Config.ACCESS_KEY,aws_secret_access_key = Config.SECRET_KEY)
    try:
        s3.upload_fileobj(file, Config.S3_BUCKET, file.filename, ExtraArgs={'ContentType':file.content_type})
    except Exception as e:
        return {'error':str(e)}, 500
    
    img_url = new_file_name
    return jsonify({'result':'success','img_url':img_url})