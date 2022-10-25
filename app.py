from unittest import result
from flask import Flask, render_template, jsonify, request, session, redirect ,url_for
from bson.objectid import ObjectId #str인 _id를 obj로 변환
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

@app.route('/boardView')
def boardView():
    sess_check() #세션체크 메소드
    sess_id = session['id'] #세션 체크
    print(sess_id)

    obj_id = ObjectId("635772aa45ab29b1239a8d8f")
    result = db.board.find_one({'_id' : obj_id})
    join_list = obj_decode(list(db.join.find({'board_id' : obj_id})))

    #db.users.insert_one({'name':'test2','phone':'010-2222-2222','email':'test2@gmail.com','id':'test2','password':'test2'})
    #db.users.insert_one({'name':'test3','phone':'010-3333-3333','email':'test3@gmail.com','id':'test3','password':'test3'})
    #db.users.insert_one({'name':'test4','phone':'010-4444-4444','email':'test4@gmail.com','id':'test4','password':'test4'})
    #db.join.insert_one({'user_id':'test4','board_id':obj_id})
    #db.join.insert_one({'user_id':'test3','board_id':obj_id})
    #db.comment.insert_one({'user_id' : 'test2', 'board_id' : obj_id, 'comment' : '안녕하세요 test2 입니다.'})
    #db.comment.insert_one({'user_id' : 'test3', 'board_id' : obj_id, 'comment' : '안녕하세요 test3 입니다.'})
    #db.comment.insert_one({'user_id' : 'test4', 'board_id' : obj_id, 'comment' : '안녕하세요 test4 입니다.'})
    #db.comment.insert_one({'user_id' : 'test1', 'board_id' : obj_id, 'comment' : '안녕하세요 test1 입니다.'})
    
    join_check = db.join.find_one({'board_id' : obj_id, 'user_id' : sess_id})

    btn_color = ""
    btn_text = ""
    btn_route = ""

    if join_check:
        btn_color = "btn btn-danger"
        btn_text = "취소하기"
        btn_route = "/join_delete"
    else:
        btn_color = "btn btn-primary"
        btn_text = "참여하기"
        btn_route = "/join_put"

    comment_list = obj_decode(list(db.comment.find({'board_id' : obj_id})))


    return render_template('boardview.html',id = sess_id,result = result, join_list = join_list, btn_color = btn_color, btn_text = btn_text, btn_route = btn_route, comment_list = comment_list)

@app.route('/join_put', methods=['POST'])
def join_put():
    sess_check() #세션체크 메소드
    sess_id = session['id'] #세션 체크
    receive_board_id = ObjectId(request.form['board_id'])

    insert_input = {'user_id' : sess_id, 'board_id' : receive_board_id}
    db.join.insert_one(insert_input)

    return redirect(url_for('boardView'))

@app.route('/join_delete', methods=['POST'])
def join_delete():
    sess_check() #세션체크 메소드
    sess_id = session['id'] #세션 체크
    receive_board_id = ObjectId(request.form['board_id'])

    delete_input = {'user_id' : sess_id, 'board_id' : receive_board_id}
    db.join.delete_many(delete_input)

    return redirect(url_for('boardView'))

@app.route('/comment_put', methods=['POST'])
def comment_put():
    sess_check() #세션체크 메소드
    sess_id = session['id'] #세션 체크
    receive_board_id = ObjectId(request.form['board_id'])
    receive_comment = request.form['comment']

    insert_input = {'user_id' : sess_id, 'board_id' : receive_board_id, 'comment' : receive_comment}
    db.comment.insert_one(insert_input)

    return redirect(url_for('boardView'))

@app.route('/comment_delete/<comment_id>')
def comment_delete(comment_id):
    sess_check() #세션체크 메소드
    sess_id = session['id'] #세션 체크
    receive_comment_id = ObjectId(comment_id)

    delete_input = {'user_id' : sess_id, '_id' : receive_comment_id}
    db.comment.delete_many(delete_input)

    return redirect(url_for('boardView'))


@app.route('/login',  methods=['POST','GET'])
def login():
    receive_id = request.form['id']  # 클라이언트로부터 id 받는 부분
    receive_password = request.form['password']  # 클라이언트로부터 password 받는 부분

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

def obj_decode(list):
    results = []
    for doc in list:
        doc['_id'] = str(doc['_id'])
        results.append(doc)
    return results


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)