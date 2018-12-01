from flask import Flask, request, render_template, redirect

app = Flask(__name__)


@app.route('/')
def index():
    return "欢迎来到首页"

@app.route('/login', methods=['GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_():
    username = request.form.get('uname')
    userpassword = request.form.get('upwd')
    if username == 'admin' and userpassword == 'admin':
        return "OK"
    else:
        return "REFUSE"
if __name__ == '__main__':
    app.run()
