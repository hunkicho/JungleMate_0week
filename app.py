from flask import Flask, render_template, jsonify, request, session

from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

app = Flask(__name__)
app.secret_key = "week0Blue3"

client = MongoClient('localhost', 27017)  
db = client.week0  # 'week0'라는 이름의 db를 만들거나 사용합니다.

@app.route('/loginform')
def loginform():
    return render_template('loginform.html')

@app.route('/main')
def main():
    #session.pop('id',None)
    sess_check() #세션체크 메소드
    sess_id = session['id'] #세션 체크

    return render_template('main.html',id = sess_id)

@app.route('/login',  methods=['POST','GET'])
def login():
    receive_id = request.form['id']  # 클라이언트로부터 id 받는 부분
    receive_password = request.form['password']  # 클라이언트로부터 password 받는 부분

    print(receive_id)

    result = db.users.find_one({'id' : receive_id, 'password' : receive_password},{'_id' : False, 'id' : True}) #id와 pw가 일치하는 값 찾기

    if result == None: #일치하는 값이 없을 경우
        print("실패")
        return render_template('loginform.html')
    else:
        print("성공")  #일치하는 값이 있으면
        session['id'] = result['id'] #세션에 아이디로 정보 저장
        return main() #메인페이지로 이동
        

def sess_check():
    sess_id = session['id'] #세션값 가져오기
    if sess_id == "": #없으면 로그인 페이지로
        return render_template('loginform.html')
    else:
        return "1"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)