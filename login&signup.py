from flask import Flask, request, render_template, redirect, jsonify, json
#mysql
import pymysql
db = pymysql.connect("localhost","user","user","db1" )

# #sqllite3
# import sqlite3
# db = sqlite3.connect('sql.db',check_same_thread = False)
# db.row_factory = "dict_factory"



app = Flask(__name__)

@app.route('/')
def index():
    return "欢迎来到首页"

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

#用户登录
@app.route('/login', methods=['POST'])
def login_():
    cursor = db.cursor()
    username = request.form.get('name')
    userpassword = request.form.get('password')
    if not username or not userpassword:
        cursor.close()
        return jsonify({
                "status": 0,
                "message": "提交信息有误！"
             }), 400
    sql = "select * from users where name='%s' and password='%s'" % (username, userpassword)
    result = cursor.execute(sql)
    if result:
        cursor.close()
        return jsonify({
            "status": 1,
            "message": "用户{}登录成功！".format(username)
        }), 200
    else:
        cursor.close()
        return jsonify({
            "status": 0,
            "message": "用户名或密码错误！".format(username)
        })



@app.route('/signup', methods=['GET'])
def signup():
    return render_template('login.html')


#用户注册
@app.route('/signup', methods=['POST'])
def signup_():
    cursor = db.cursor()
    username = request.form.get('name')
    userpassword = request.form.get('password')
    if not username or not userpassword:
        cursor.close()
        return jsonify({
                "status": 0,
                "message": "提交信息有误！"
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
    #创建用户
    sql = """INSERT INTO users(name,password)
             VALUES ('%s', '%s')"""%(username,userpassword)
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

if __name__ == '__main__':
    app.run()
