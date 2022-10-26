import smtplib
from unittest import result
from flask import Flask, render_template, jsonify, request, session, redirect ,url_for, flash
from bson.objectid import ObjectId #str인 _id를 obj로 변환
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from datetime import datetime
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "week0Blue3"

client = MongoClient('mongodb+srv://test:sparta@cluster0.cbhgxgw.mongodb.net/?retryWrites=true&w=majority')
db = client.week0  # 'week0'라는 이름의 db를 만들거나 사용합니다.


board=[{"id":1, "name":"a", "meal":"b","hCounter":5,"time":"오후5시"},
       {"id":2, "name":"c", "meal":"cc","hCounter":2,"time":"오후2시"}]


@app.route('/loginform')
def loginform():
    return render_template('loginform.html')
    
@app.route('/logout')
def boot():
    session.pop('id',None)
    return redirect(url_for('loginform'))

@app.route('/main')
def goMain():
    return redirect(url_for('main', page_idx = 1))

@app.route('/main/<page_idx>', methods=['POST','GET'] )
def main(page_idx=1):
    #session.pop('id',None)
    sess_check() #세션체크 메소드
    sess_id = session['id'] #세션 체크
    
    kw = ""
    searchType =  ""

    if request.method == "POST":
        kw = request.form['search_kw'] 
        searchType = request.form['searchType']

    if kw is not None and kw != "":
        if searchType is not None and searchType != "":
            board_list = list(db.board.find({searchType : {"$regex" : kw}}))
        else:
            board_list = list(db.board.find({"$or" :[{"title":{"$regex" : kw}}, {"comment":{"$regex" : kw}}, {"writer": {"$regex" : kw}}]}))
    else:
        board_list = list(db.board.find({}))
    
    paging_data={
                "currentPage":int(page_idx),
                "pageCount":4,
                "dataperPage":8,
                "totalData":len(board_list),
                "pageGroup":int(page_idx)//4+1,
                "last": (int(page_idx)//4+1)*4
                }
    
    if paging_data['last'] > paging_data['totalData']//paging_data['dataperPage']+1:
        paging_data['last']=paging_data['totalData']//paging_data['dataperPage']+1

    page_board=board_list[(((int(page_idx)-1)*8+1))-1 : (int(page_idx)*8)]
    
    return render_template("main.html", board_list=page_board, id = sess_id, paging=paging_data)


@app.route('/boardView/<board_id>')
def boardView(board_id):
    if sess_check() == False:
        return redirect(url_for('loginform')) #세션체크
    sess_id = session['id']

    obj_id = ObjectId(board_id)
    result = db.board.find_one({'_id' : obj_id})
    join_list = obj_decode(list(db.join.find({'board_id' : obj_id}).sort("reg_date",-1)))

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
    join_count = len(list(db.join.find({"board_id" : obj_id})))
    print(join_count)

    btn_color = ""
    btn_text = ""
    btn_route = ""
    disabled = ""

    if join_check:
        btn_color = "btn btn-danger"
        btn_text = "취소하기 " + str(join_count) + "/" + str(result['people'])
        btn_route = "/join_delete"
    else:
        btn_color = "btn btn-primary"
        btn_text = "참여하기 " + str(join_count) + "/" + str(result['people'])
        btn_route = "/join_put"
        if join_count >= int(result['people']) or datetime.now() > datetime.strptime(result['date'] + " " + result['time'], '%Y-%m-%d %H:%M'):
            disabled = "disabled"
            btn_color = "btn btn-primary"
            btn_text = "참여불가 " + str(join_count) + "/" + str(result['people'])

    if result['delivery'] == "true":
        delivery = "배달가능"
    else:
        delivery = "배달불가"


    comment_list = obj_decode(list(db.comment.find({'board_id' : obj_id})))


    return render_template('boardView.html',id = sess_id,result = result, join_list = join_list, btn_color = btn_color, btn_text = btn_text, btn_route = btn_route, comment_list = comment_list, join_count = join_count,disabled = disabled, delivery = delivery)

@app.route('/join_put', methods=['POST'])
def join_put():
    if sess_check() == False:
        return redirect(url_for('loginform')) #세션체크
    sess_id = session['id']
    receive_board_id = ObjectId(request.form['board_id'])

    insert_input = {'user_id' : sess_id, 'board_id' : receive_board_id, 'reg_date' : datetime.now()}
    db.join.insert_one(insert_input)

    return redirect(url_for('boardView', board_id = str(receive_board_id)))

@app.route('/join_delete', methods=['POST'])
def join_delete():
    if sess_check() == False:
        return redirect(url_for('loginform')) #세션체크
    sess_id = session['id']
    receive_board_id = ObjectId(request.form['board_id'])

    delete_input = {'user_id' : sess_id, 'board_id' : receive_board_id}
    db.join.delete_many(delete_input)

    return redirect(url_for('boardView', board_id = str(receive_board_id)))

@app.route('/comment_put', methods=['POST'])
def comment_put():
    if sess_check() == False:
        return redirect(url_for('loginform')) #세션체크
    sess_id = session['id']
    receive_board_id = ObjectId(request.form['board_id'])
    receive_comment = request.form['comment']

    insert_input = {'user_id' : sess_id, 'board_id' : receive_board_id, 'comment' : receive_comment}
    db.comment.insert_one(insert_input)

    return redirect(url_for('boardView', board_id = str(receive_board_id)))

@app.route('/comment_delete/<comment_id>/<board_id>')
def comment_delete(comment_id,board_id):
    if sess_check() == False:
        return redirect(url_for('loginform')) #세션체크
    sess_id = session['id']
    receive_comment_id = ObjectId(comment_id)

    delete_input = {'user_id' : sess_id, '_id' : receive_comment_id}
    db.comment.delete_many(delete_input)

    return redirect(url_for('boardView', board_id = board_id))


@app.route('/go_create_page',  methods=['POST'])
def go_create_page():
    if sess_check() == False:
        return redirect(url_for('loginform')) #세션체크
    sess_id = session['id']

    resList = list(db.restaurant.find({}))

    return render_template('create.html',resList = resList)

@app.route('/getResInfo',  methods=['POST'])
def getResInfo():
    if sess_check() == False:
        return redirect(url_for('loginform')) #세션체크
    sess_id = session['id']

    receive_obj_id = ObjectId(request.form['obj_id'])
    result = obj_decode(list(db.restaurant.find({'_id' : receive_obj_id})))
    print(result)

    return jsonify({'result': 'success', 'info': result})

@app.route('/login',  methods=['POST','GET'])
def login():
    receive_id = request.form['id']  # 클라이언트로부터 id 받는 부분
    receive_password = request.form['password']  # 클라이언트로부터 password 받는 부분

    result = db.users.find_one({'id' : receive_id, 'password' : receive_password},{'_id' : False, 'id' : True}) #id와 pw가 일치하는 값 찾기

    if result == None: #일치하는 값이 없을 경우
        flash("일치하는 ID와 PW의 조합이 없습니다. 다시 입력하세요!")
        return render_template('loginform.html')
    else:  #일치하는 값이 있으면
        session['id'] = result['id'] #세션에 아이디로 정보 저장
        return redirect(url_for('main', page_idx=1)) #메인페이지로 이동

@app.route('/register',  methods=['POST','GET'])
def register():
    if request.method == 'POST':
        receive_name = request.form['name']  # 클라이언트로부터 name 받는 부분
        receive_phone = request.form['phone']  # 클라이언트로부터 phone 받는 부분
        receive_email = request.form['email']  # 클라이언트로부터 email 받는 부분
        receive_id = request.form['id'].lower()  # 클라이언트로부터 id 받는 부분
        receive_password = request.form['password']  # 클라이언트로부터 password 받는 부분
        receive_password_check = request.form['password-check']  # 클라이언트로부터 password-check 받는 부분

        if receive_password != receive_password_check:
            flash("The passwords do not match, please re-enter the password!")
            return render_template('register.html')
        elif db.users.find_one({'id' : receive_id}) is not None:
            flash("The ID entered already exists!")
            return render_template('register.html')
        elif len(receive_password) < 8:
            flash("Password has to be at least 8 characters!")
            return render_template('register.html')
        else:  #조건이 전부 만족한 경우
            flash("Your account has been created!")
            db.users.insert_one({'id' : receive_id, 'password' : receive_password, 'name': receive_name, 'phone': receive_phone, 'email': receive_email})
            return render_template('loginform.html')
    else:
        return render_template('register.html')

@app.route('/findId',  methods=['POST','GET'])
def findId():
    if request.method == 'POST':
        receive_name = request.form['name']
        receive_email = request.form['email']
        
        user_email_db = db.users.find_one({'email': receive_email})
        print(user_email_db)
        if user_email_db is not None:
            user_email = user_email_db['email']
            user_name = user_email_db['name']
            user_id = user_email_db['id']

            if user_name == receive_name:
                print('passed')
            else:
                flash("Entered name and email does not match!")
                return render_template('findId.html')
        else:
            flash("Enter a valid email address!")
            return render_template('findId.html')

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login('swlee6507@gmail.com', 'uxbdbhjxwybunsng')

        # text = input("enter a string to convert into ascii values:")
        # ascii_values = []
        # for character in text:
        #     ascii_values.append(ord(character))
        # print(ascii_values)

        # 보낼 메시지 설정
        msg = MIMEText('Your ID is: ' + user_id)
        msg['Subject'] = 'Your ID'

        s.sendmail("swlee6507@gmail.com", user_email, msg.as_string())
        s.quit()
        flash("Your ID has been sent to the given email address!")
        
        return render_template('loginform.html')
    else:
        return render_template('findId.html')

@app.route('/findPw',  methods=['POST','GET'])
def findPw():
    if request.method == 'POST':
        receive_id = request.form['id']
        receive_email = request.form['email']

        user_email_db = db.users.find_one({'email': receive_email})

        if user_email_db is not None:
            user_email = user_email_db['email']
            user_password = user_email_db['password']
            user_id = user_email_db['id']

            if user_id == receive_id:
                print('passed')
            else:
                flash("Entered ID and email does not match!")
                return render_template('findId.html')
        else:
            flash("Enter a valid email address!")
            return render_template('findId.html')

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login('swlee6507@gmail.com', 'uxbdbhjxwybunsng')

        # 보낼 메시지 설정
        msg = MIMEText('Your PW is: ' + user_password)
        msg['Subject'] = 'Your PW'

        s.sendmail("swlee6507@gmail.com", user_email, msg.as_string())
        s.quit()
        
        flash("Your PW has been sent to the given email address!")
                
        return render_template('loginform.html')
    else:
        return render_template('findPw.html')


def sess_check():
    if 'id' not in session: #없으면 로그인 페이지로
        return False
    else:
        return True

def obj_decode(list):
    results = []
    for doc in list:
        doc['_id'] = str(doc['_id'])
        results.append(doc)
    return results
    
@app.route('/create', methods=['POST'])
def create_room():
    if sess_check() == False:
        return redirect(url_for('loginform')) #세션체크
    sess_id = session['id']

    title_receive = request.form['title']
    date_receive = request.form['date']
    time_receive = request.form['time']
    people_receive = request.form['people']    
    comment_receive = request.form['comment']

    rest_name = request.form['rest_name']
    rest_img = request.form['rest_img']
    rest_addr = request.form['rest_addr']
    get_delivery = request.form.get('delivery')

    if get_delivery == None:
        delivery = "false"
    else:
        delivery = "true"

    print(delivery)
    # delivery = "false"
    # if request.form['delivery']:
    #     delivery = "true"
 

    insert_input = {
                    'title' : title_receive, 'date' : date_receive, 'time' : time_receive, 'people' : people_receive, 
                    'comment' : comment_receive, 'reg_date' : datetime.now(), 'writer' : sess_id, 'res_name' : rest_name,
                    'rest_img' : rest_img, 'rest_addr' : rest_addr , 'delivery' : delivery
                    }

    result = db.board.insert_one(insert_input).inserted_id
    getId = db.board.find_one(result)

    insert_input = {'user_id' : sess_id, 'board_id' : result}
    db.join.insert_one(insert_input)
    
    return redirect(url_for('boardView', board_id = str(getId['_id'])))

@app.route('/board_delete', methods=['POST'])
def board_delete():
    if sess_check() == False:
        return redirect(url_for('loginform')) #세션체크
    sess_id = session['id']
    receive_board_id = ObjectId(request.form['board_id'])

    delete_input = {'_id' : receive_board_id}
    db.board.delete_one(delete_input)

    return redirect(url_for('goMain'))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)