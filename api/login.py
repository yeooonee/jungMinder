from flask import Flask, render_template, request, jsonify, session
from pymongo import MongoClient

#비밀번호 해시화 및 검증 함수
from werkzeug.security import generate_password_hash, check_password_hash

client = MongoClient('localhost', 27017)
db = client.member

app = Flask(__name__, template_folder='../templates')

#세션 암호화 용도
app.secret_key = "test-secret-key"


@app.route('/')
def home():
   return render_template('login.html')

@app.route('/main')
def main():
   return render_template('main.html')


#회원가입
@app.route('/create-user')
def create_user():
   db.user.delete_many({"id": "test123"})
   #유저 정보 테스트용
   user = {
      "id": "test123",
      "pw": generate_password_hash("1234"),
      "name": "홍길동"
   }

   db.user.insert_one(user)

   return"사용자 생성 완료"

#로그인
@app.route('/login', methods=['POST'])
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

@app.route('/check-session')
def check_session():
   return jsonify({"user_id": session.get('user_id')})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)