from flask import Blueprint, Flask, render_template, request, jsonify
from pymongo import MongoClient

# app.py 와 연결
studylogs_bp = Blueprint('studylogs', __name__, url_prefix='/studylogs')

client = MongoClient('localhost',27017)
db = client.dbjungminder

@studylogs_bp.route('/create', methods=['POST'])
def studylogs_create():
    # title = request.form['title']
    # content = request.form['content']
    
    studylogs = {
        'title' : "test",
        'content' : "test"
    }
    
    db.studylogs.insert_one(studylogs)
    
    return jsonify({'result':'success'})