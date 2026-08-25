from flask import Blueprint, Flask, render_template, request, jsonify

studylogs_bp = Blueprint('studylogs', __name__, url_prefix='/studylogs')

@studylogs_bp.route('/create', methods=['POST'])
def studylogs_create():
    title = request.form['title']
    content = request.form['content']
    
    logs = {
        'title' : title,
        'content' : content
        
    }
    
    return 0