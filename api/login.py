from flask import Blueprint, render_template, request, jsonify, session
from pymongo import MongoClient

from ref.database import db

#비밀번호 해시화 및 검증 함수
from werkzeug.security import generate_password_hash, check_password_hash

login_bp = Blueprint('login', __name__)


@login_bp.route('/')
def home():
   return render_template('login.html')

@login_bp.route('/main')
def main():
   return render_template('main.html')

#회원가입
@login_bp.route('/signup', methods=['POST'])
def signup():
   print(request.form)

   #회원가입 정보 받기
   id = request.form['id']
   name = request.form['name']
   pw = request.form['pw']
   pw_confirm = request.form['pw_confirm']

   #비밀번호 중복확인
   if pw != pw_confirm:
      return jsonify({
         "result": "fail",
         "msg": "비밀번호가 일치하지 않습니다."
      })

    #비밀번호 해시하기
   pw = generate_password_hash(pw)

   user = {
       "id": id,
       "pw": pw,
       "name": name
    }
   db.user.insert_one(user)

   return jsonify({
      "result": "success",
      "msg": "회원가입이 완료되었습니다."
    })

#로그인
@login_bp.route('/login', methods=['POST'])
def login():
   id = request.form['id']
   pw = request.form['pw']

   user = db.user.find_one({"id": id})

   if user is None:
      return jsonify({
         "result": "fail",
         "msg": "존재하지 않는 아이디입니다."
      })

   if not check_password_hash(user["pw"], pw):
      return jsonify({
         "result": "fail",
         "msg": "비밀번호가 틀렸습니다."
      })

   session['user_id'] = id

   return jsonify({"result": "success"})

#아이디 중복확인
@login_bp.route('/check-id', methods=['POST'])
def check_id():
   id = request.form['id']

   user = db.user.find_one({"id": id})

   if user is None:
      return jsonify({
         "result": "success",
         "msg": "사용 가능한 아이디입니다."
      })
   else:
      return jsonify({
         "result": "fail",
         "msg": "중복된 아이디입니다."
      })

@login_bp.route('/check-session')
def check_session():
   return jsonify({"user_id": session.get('user_id')})