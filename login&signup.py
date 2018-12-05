﻿# coding=utf-8
from flask import Flask, request, render_template, redirect, jsonify, json, make_response, session, url_for
from flask_cors import CORS
import os
from datetime import timedelta
from decorators import login_require
# mysql
import pymysql

db = pymysql.connect("localhost", "user", "user", "db1")

# #sqllite3
# import sqlite3
# db = sqlite3.connect('sql.db',check_same_thread = False)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
CORS(app, resources=r'/*')
CORS(app, supports_credentials=True)


@app.route('/')
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
        username = request.form.get('name')
        password = request.form.get('password')
        check = request.form.get('checkbox')
        # json
        # data = json.loads(request.get_data())
        # username = data['name']
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
        sql = "select * from users where name='%s' and password='%s'" % (username, password)
        result = cursor.execute(sql)
        if result:
            user_id = cursor.fetchall()[0][0]
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
        username = request.form.get('name')
        password = request.form.get('password1')
        password1 = request.form.get('password2')
        # json
        # data = json.loads(request.get_data())
        # username = data['name']
        # password = data['password1']
        # password1 = data['password2']
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
        sql = "select * from users where name='%s'" % (username)
        result = cursor.execute(sql)
        if result:
            cursor.close()
            return jsonify({
                "status": "1error3",
                "message": "用户已存在！"
            })
        # 创建用户
        sql = """INSERT INTO users(name,password)
                     VALUES ('%s', '%s')""" % (username, password)
        try:
            cursor.execute(sql)
            db.commit()
            cursor.close()
            return jsonify({
                "status": 11,
                "message": "用户{}添加成功！".format(username)
            }), 200
        except:
            cursor.close()
            return jsonify({
                "status": "1error4",
                "message": "添加错误！"
            })


# 退出
@app.route('/logout', methods=["GET"])
def logout():
    session.clear()  # 删除所有session
    return redirect(url_for('index'))


# 发布委托
@app.route('/entrust', methods=["POST", "GET"])
@login_require
def entrust():
    if (request.method == 'GET'):
        pass
    else:
        pass


# 个人中心跳转
@app.route('/home', methods=["GET"])
@login_require
def home_index():
    return redirect('/home/{}'.format(session.get('user_id')))


# 个人中心
@app.route('/home/<user_id>', methods=["GET"])
@login_require
def home(user_id):
    return u"{}'s home".format(user_id)


# 历史接单跳转
@app.route('/history/', methods=["GET"])
@login_require
def history_index():
    return redirect('/history/{}'.format(session.get('user_id')))


# 历史接单
@app.route('/history/<user_id>', methods=["GET"])
@login_require
def history(user_id):
    return u"{}' history".format(user_id)


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
