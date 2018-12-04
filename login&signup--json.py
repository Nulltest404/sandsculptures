from flask import Flask, request, render_template, redirect, jsonify, json, make_response, session, url_for
import os
from datetime import timedelta
# mysql
import pymysql

db = pymysql.connect("192.168.1.101", "new", "new", "db1")

# #sqllite3
# import sqlite3
# db = sqlite3.connect('sql.db',check_same_thread = False)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

@app.route('/')
def index():
    print(session.get('username'))
    if session.get('username'):
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
        # # #form
        # username = request.form.get('name')
        # userpassword = request.form.get('password')
        # check = request.form.get('checkbox')
        # json
        data = json.loads(request.get_data())
        username = data['name']
        userpassword = data['password']
        # check = data['checkbox']
        # 检查是否存在用户名和密码
        if not username or not userpassword:
            cursor.close()
            return jsonify({
                "status": 0,
                "message": "提交信息有误！"
            }), 400
        # 登录
        sql = "select * from users where name='%s' and password='%s'" % (username, userpassword)
        result = cursor.execute(sql)
        pid = cursor.fetchall()[0][0]
        session["pid"] = pid
        if result:
            cursor.close()
            # 储存用户名和密码进入session
            if 1:
                session["username"] = username
                session["password"] = userpassword
            return jsonify({
                "status": 1,
                "message": "用户{}登录成功！".format(username)
            }), 200
        else:
            cursor.close()
            return jsonify({
                "status": 0,
                "message": "用户名或密码错误！"
            })


# 用户注册
@app.route('/signup', methods=["POST", "GET"])
def signup():
    if (request.method == 'GET'):
        return render_template('signup.html')
    else:
        cursor = db.cursor()
        # #  form
        # username = request.form.get('name')
        # userpassword = request.form.get('password1')
        # userpassword1 = request.form.get('password2')
        # json
        data = json.loads(request.get_data())
        username = data['name']
        userpassword = data['password']
        # userpassword1 = data['password2']
        # 检查是否有用户名和密码
        if not username or not userpassword:
            cursor.close()
            return jsonify({
                "status": 0,
                "message": "提交信息有误！"
            }), 400
        # 检查是否两次密码是否相同
        if (userpassword != userpassword1):
            return jsonify({
                "status": 0,
                "message": "两次密码不相同！"
            }), 400
        # 检查用户是否已经存在
        sql = "select * from users where name='%s'" % (username)
        result = cursor.execute(sql)
        if result:
            cursor.close()
            return jsonify({
                "status": 0,
                "message": "用户已存在！"
            })
        # 创建用户
        sql = """INSERT INTO users(name,password)
                     VALUES ('%s', '%s')""" % (username, userpassword)
        try:
            cursor.execute(sql)
            db.commit()
            cursor.close()
            return jsonify({
                "status": 1,
                "message": "用户{}添加成功！".format(username)
            }), 200
        except:
            cursor.close()
            return jsonify({
                "status": 0,
                "message": "添加错误！"
            })


# 退出
@app.route('/logout', methods=["GET"])
def logout():
    session.clear()  # 删除所有session
    return redirect(url_for('index'))


# 发布委托
@app.route('/entrust', methods=["POST", "GET"])
def entrust():
    # 判断是否登录
    if session.get('username'):
        return redirect(url_for('index'))

    if (request.method == 'GET'):
        pass
    else:
        pass


# 个人中心跳转
@app.route('/home', methods=["GET"])
def homeindex():
    # 判断是否登录
    if session.get('username'):
        return redirect(url_for('index'))
    else:
        return redirect('/home/{}'.format(session.get('pid')))


# 个人中心
@app.route('/home/<id>', methods=["GET"])
def home(id):
    # 判断是否登录
    if session.get('username'):
        return redirect(url_for('index'))
    else:
        return "{}'s home".format(id)


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
