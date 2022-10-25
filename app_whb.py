from lib2to3.pgen2 import token
from flask import Flask, render_template, jsonify, request, session,make_response
import jwt
from datetime import datetime, timedelta
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = "kcKaoo4Md-riOdVU"

client = MongoClient('mongodb+srv://test:<password>@cluster0.cbhgxgw.mongodb.net/?retryWrites=true&w=majority')  ##
db = client.week0  # 'week0'라는 이름의 db를 만들거나 사용합니다.

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('loginform.html')
    else: 
        return 'Logged in currently!'

@app.route('/login', methods=['POST', 'GET'])
def login():
    receive_id = request.form['id']  # 클라이언트로부터 id 받는 부분
    receive_password = request.form['password']  # 클라이언트로부터 password 받는 부분

    result = db.users.find_one({'id' : receive_id, 'password' : receive_password},{'_id' : False, 'id' : True}) #id와 pw가 일치하는 값 찾기
    
    if result: # 성공
        print("성공")
        session['logged_in'] = True

        token = jwt.encode({
            'user': request.form['username'],
            # don't foget to wrap it in str function, otherwise it won't work [ i struggled with this one! ]
            'expiration': str(datetime.utcnow() + timedelta(seconds=60))
        },
            app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('utf-8')})
    else:
        print("실패")
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "Authentication Failed "'})

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        tocken=request.args.get('token')
        if not token:
            return jsonify({'Alert!': 'token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return decorated



if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)