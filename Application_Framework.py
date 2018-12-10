# coding=utf-8
from flask import Flask, request, render_template, redirect, jsonify, json, make_response, session, url_for, \
    send_from_directory, abort
from flask_cors import CORS
import os, time, sched
from datetime import timedelta, datetime
from decorators import login_require
from func import random_name
# mysql
import pymysql

db = pymysql.connect("localhost", "user", "user", "db1")

# #sqllite3
# import sqlite3
# db = sqlite3.connect('sql.db',check_same_thread = False)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app, resources=r'/*')
CORS(app, supports_credentials=True)
basedir = os.path.abspath(os.path.dirname(__file__))


# 一些函数
# 查找consign_id
def get_consign_id(user_id, time):
    Cursor = db.cursor()
    sql = "select consign_id from consigns where user_id='%s' and `time`='%s'" % (user_id, time)
    result = Cursor.execute(sql)
    if result:
        consign_id = Cursor.fetchall()[0][0]
        Cursor.close()
        return consign_id
    else:
        Cursor.close()
        print("consign_id查找失败")
        return -1


# 定时访问数据库用
@app.route('/R9CXjrcx9vNvG8NepiyY13et')
def timing():
    Cursor_ = db.cursor()
    sql = "select * from users"
    Cursor_.execute(sql)
    Cursor_.close()


@app.route('/', methods=["GET"])
def index():
    if session.get('user_id'):
        return u'欢迎你：{}'.format(session.get('username'))
    else:
        return render_template('homepage.html')


# 用户登录
@app.route('/login', methods=["POST", "GET"])
def login():
    if (request.method == 'GET'):
        return render_template('login.html')
    else:
        cursor = db.cursor()
        # #form
        username = request.form.get('username')
        password = request.form.get('password')
        check = request.form.get('checkbox')
        # json
        # data = json.loads(request.get_data())
        # username = data['username']
        # password = data['password']
        # check = data['checkbox']
        # 检查是否存在用户名和密码
        if not username or not password:
            cursor.close()
            return jsonify({
                "status": "2error1",
                "message": "提交信息有误！"
            })
        # 登录
        sql = "select user_id from users where username='%s' and `password`='%s'" % \
              (username, password)
        result = cursor.execute(sql)
        if result:
            user_id = cursor.fetchall()[0][0]
            # 储存user_id,用户名进入session
            session["user_id"] = user_id
            session["username"] = username
            cursor.close()
            if check:
                session.permanent = True
            return redirect(url_for('index'))
        else:
            cursor.close()
            return jsonify({
                "status": "2error2",
                "message": "用户名或密码错误！"
            })


# 用户注册
@app.route('/signup', methods=["POST", "GET"])
def signup():
    if (request.method == 'GET'):
        return render_template('signup.html')
    else:
        cursor = db.cursor()
        #  form
        username = request.form.get('username')
        password = request.form.get('password')
        password1 = request.form.get('password')
        # json
        # data = json.loads(request.get_data())
        # username = data['username']
        # password = data['password']
        # password1 = data['password1']
        # 检查是否有用户名和密码
        if not username or not password:
            cursor.close()
            return jsonify({
                "status": "1error1",
                "message": "提交信息有误！"
            })
        # 检查是否两次密码是否相同
        if (password != password1):
            return jsonify({
                "status": "1error2",
                "message": "两次密码不相同！"
            })
        # 检查用户是否已经存在
        sql = "select * from users where username='%s'" % (username)
        result = cursor.execute(sql)
        if result:
            cursor.close()
            return jsonify({
                "status": "1error3",
                "message": "用户已存在！"
            })
        # 创建用户
        sql = """INSERT INTO users(username,`password`)
                     VALUES ('%s', '%s')""" % (username, password)
        try:
            cursor.execute(sql)
            db.commit()
            return redirect(url_for('index'))
        except:
            db.rollback()
            return jsonify({
                "status": "1error4",
                "message": "添加错误！"
            })
        finally:
            cursor.close()


# 退出
@app.route('/logout', methods=["GET"])
def logout():
    session.clear()  # 删除所有session
    return redirect(url_for('index'))


# 发布委托
@app.route('/consign', methods=["POST", "GET"])
@login_require
def consign():
    if (request.method == 'GET'):
        return render_template('consign.html')
    else:
        cursor = db.cursor()
        # form
        consign_name = request.form.get('consign_name')
        desc = request.form.get('desc')
        contact = request.form.get('contact')
        partition = request.form.get('partition')
        user_id = session.get('user_id')
        username = session.get('username')
        print(user_id)
        if not consign_name or not desc:
            cursor.close()
            return jsonify({
                "status": "4error1",
                "message": "提交信息有误！"
            })
        sql = """INSERT INTO consigns(user_id,username,consign_name,`desc`,`time`,contact,`partition`)
                             VALUES ('%s', '%s','%s','%s', NOW(),'%s','%s');""" \
              % (user_id, username, consign_name, desc, contact, partition)
        try:
            cursor.execute(sql)
            db.commit()
            consign_id = get_consign_id(user_id, time)
            return redirect(url_for('consign_page', consign_id=consign_id))
        except:
            db.rollback()
            return jsonify({
                "status": "4error2",
                "message": "添加错误！"
            })
        finally:
            cursor.close()


# 委托详情（未做完）
@app.route('/consign/<consign_id>', methods=["GET"])
@login_require
def consign_page(consign_id):
    cursor = db.cursor()
    sql = "select * from consigns where consign_id='%s'" % (consign_id)
    result = cursor.execute(sql)
    if result:
        pass
    else:
        abort(404)


# 委托删除
@app.route('/consign/delete', methods=["POST"])
@login_require
def consign_delete():
    cursor = db.cursor()
    consign_id = request.form.get('consign_id')
    username = session.get('username')
    sql = "select * from consigns where consign_id='%s' and username='%s'" \
          % (consign_id, username)
    result = cursor.execute(sql)
    if result:
        sql = "delete from consigns where consign_id='%s' and username='%s'" \
              % (consign_id, username)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            return jsonify({
                "status": "6error2",
                "message": "删除错误！"
            })
        finally:
            cursor.close()
    else:
        cursor.close()
        return jsonify({
            "status": "6error1",
            "message": "委托不存在！"
        })


# 委托状态变更（是否已完成）
@app.route('/consign/finish', methods=["POST"])
@login_require
def finish_change():
    cursor = db.cursor()
    consign_id = request.form.get('consign_id')
    finish = request.form.get('finish')
    username = session.get('username')
    sql = "select * from consigns where consign_id='%s' and username='%s'" \
          % (consign_id, username)
    result = cursor.execute(sql)
    if result:
        sql = "update consigns set finished = '%s' where consign_id='%s' and username='%s'" \
              % (finish, consign_id, username)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            return jsonify({
                "status": "7error2",
                "message": "变更状态错误！"
            })
        finally:
            cursor.close()
    else:
        cursor.close()
        return jsonify({
            "status": "7error1",
            "message": "委托不存在！"
        })


# 个人中心(未完成）
@app.route('/home', methods=["GET"])
@login_require
def home():
    cursor = db.cursor()
    username = session.get('username')
    user_id = session.get('user_id')
    # 发布的委托
    sql = "select * from consigns where username='%s'" \
          % (username)
    cursor.execute(sql)
    consigns = cursor.fetchall()
    Consigns = {}
    for consign in consigns:
        cache = {}
        cache['consign_name'] = consign[3]
        cache['desc'] = consign[4]
        cache['time'] = consign[5]
        cache['contact'] = consign[6]
        cache['partition'] = consign[7]
        cache['finished'] = consign[8]
        Consigns += cache
    # 收藏
    sql = "select * from collects where username='%s'" \
          % (username)
    cursor.execute(sql)
    collects = cursor.fetchall()
    Collects = {}
    for collect in collects:
        pass
    return u"{}'s home".format(user_id)


# 收藏（未完成）
@app.route('/collect', methods=["GET"])
@login_require
def collect():
    cursor = db.cursor()
    user_id = session.get("user_id")
    sql = "select comsign_name,`desc`,`time` from consigns where user_id='%s'" \
          % (user_id)
    cursor.execute(sql)
    comsigns = cursor.fetchall()
    cursor.close()
    # 返回一个网页
    return ''


# 搜索功能
@app.route('/search/<search_str>', methods=["GET"])
@login_require
def search(search_str):
    cursor = db.cursor()
    search_str = str(search_str)
    search_list = search_str.split()
    outer = []
    for char in search_list:
        sql = "select * from tr where `name` like '%{}%'".format(char)
        # sql = "select * from consigns where `consign_name` like '%{}%'".format(char)
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            if result[0] not in outer:
                outer += result
    cursor.close()
    # print(outer)
    # outer即是搜索结果
    return ""


if (__name__ == '__main__'):
    app.run(debug=True, port=5000, host='0.0.0.0')
