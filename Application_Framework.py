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
    sql = "select consign_id from consigns where user_id='%s' and time='%s'" % (user_id, time)
    result = Cursor.execute(sql)
    if result:
        consign_id = Cursor.fetchall()[0]
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
        return u'你没有登录'


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
        sql = "select user_id from users where username='%s' and password='%s'" % \
              (username, password)
        result = cursor.execute(sql)
        if result:
            user_id = cursor.fetchall()[0]
            session["user_id"] = user_id
            session["username"] = username
            # 储存用户名和密码进入session
            # session["username"] = username
            # session["password"] = password
            cursor.close()
            if check:
                session.permanent = True
            return jsonify({
                "status": 21,
                "message": "用户{}登录成功！".format(username)
            }), 200
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
        sql = """INSERT INTO users(username,password)
                     VALUES ('%s', '%s')""" % (username, password)
        try:
            cursor.execute(sql)
            db.commit()
            return jsonify({
                "status": 11,
                "message": "用户{}添加成功！".format(username)
            }), 200
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
        pass
    else:
        cursor = db.cursor()
        # form
        consign_name = request.form.get('consign_name')
        desc = request.form.get('desc')
        contact = request.form.get('contact')
        partition = request.form.get('partition')
        user_id = session.get('user_id')
        username = session.get('username')
        time = datetime()
        if not consign_name or not desc:
            cursor.close()
            return jsonify({
                "status": "4error1",
                "message": "提交信息有误！"
            })
        sql = """INSERT INTO consigns(user_id,username,consign_name,desc,time,contact,partition)
                             VALUES ('%s', '%s', '%s', '%s', '%s','%s','%s')""" \
              % (user_id, username, consign_name, desc, time, contact, partition)
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


# 个人中心跳转
@app.route('/home', methods=["GET"])
@login_require
def home_index():
    return redirect(url_for('home', user_id=session.get('user_id')))


# 个人中心
@app.route('/home/<user_id>', methods=["GET"])
@login_require
def home(user_id):
    return u"{}'s home".format(user_id)


# 历史接单跳转
@app.route('/history/', methods=["GET"])
@login_require
def history_index():
    return redirect(url_for('history', user_id=session.get('user_id')))


# 历史接单
@app.route('/history/<user_id>', methods=["GET"])
@login_require
def history(user_id):
    cursor = db.cursor()
    sql = "select comsign_name,desc,time from consigns where user_id='%s'" \
          % (user_id)
    cursor.execute(sql)
    comsigns = cursor.fetchall()
    sql = "select comsign_name,desc,time from comments where user_id='%s'" \
          % (user_id)
    cursor.execute(sql)
    comments = cursor.fetchall()
    # 返回一个网页
    return ''


if (__name__ == '__main__'):
    app.run(debug=True, port=5000, host='0.0.0.0')
