#此文件保存暂时无用的视图函数或其他函数
# coding=utf-8
from flask import Flask, request, render_template, redirect, jsonify, json, make_response, session, url_for, \
    send_from_directory
#############测试区#########################
# 上传图片
@app.route('/upload', methods=["POST", "GET"])
@login_require
def upload():
    if (request.method == 'GET'):
        pass
    else:
        username = session.get('username')
        photos = request.files.getlist('pic')
        dir_name = random_name()
        path = basedir + "/static/photo/" + username + dir_name
        try:
            for photo in photos:
                file_path = path + random_name(photo.filename)
                photo.save(file_path)
            return jsonify({
                "status": "1",
                "dir_name": dir_name,
                "message": "上传成功"
            })
        except:
            return jsonify({
                "status": "0",
                "dir_name": dir_name,
                "message": "未知错误"
            })


# 下载图片（准确说是查看）
@app.route('/download', methods=["POST", "GET"])
@login_require
def download():
    if (request.method == 'GET'):
        pass
    else:
        dir_name = request.form.get('dir_name')
        username = session.get('username')
        path = basedir + "/static/photo/" + username + dir_name
        photo_names = []
        for file in os.listdir(path):
            photo_names.append(file)
        return render_template('download.html', photo_names=photo_names, dir_name=dir_name, username=username)


@app.route('/est', methods=["GET"])
def est():
    photo_names = ['123.png']
    return render_template('download.html', photo_names=photo_names, dir_name='123', username='asd')


# 下载（查看）具体图片
@app.route('/get_photo/<username>/<dir_name>/<photo_name>', methods=["GET"])
# @login_require
def get_photo(username, dir_name, photo_name):
    if os.path.isfile(os.path.join("%s/static/photo/%s/%s" % (basedir, username, dir_name), photo_name)):
        return send_from_directory("%s/static/photo/%s/%s" % (basedir, username, dir_name), photo_name)
    # return send_from_directory("/static/photo/%s/%s"%(username,dir_name), photo_name, as_attachment=True)
    # if os.path.isfile(os.path.join('%s/static/photo/asd/123/' % (basedir), '123.png')):
    #     return send_from_directory('%s/static/photo/asd/123/' % (basedir), '123.png')
    else:
        # print('%s/static/photo/asd/123/' % (basedir))
        return "无话可说"
    # return send_from_directory("/static/photo/asd/123/", "123", as_attachment=True)


# 发布评论
@app.route('/consign/<consign_id>/comment', methods=["POST"])
@login_require
def comment(consign_id):
    cursor = db.cursor()
    # form
    desc = request.form.get('desc')
    user_id = session.get('user_id')
    username = session.get('username')
    time = datetime()
    if not desc:
        cursor.close()
        return jsonify({
            "status": "6error1",
            "message": "提交信息有误！"
        })
    sql = """INSERT INTO comments(consign_id,user_id,username,desc,time)
                                 VALUES ('%s', '%s', '%s', '%s', '%s')""" \
          % (consign_id, user_id, username, desc, time)
    try:
        cursor.execute(sql)
        db.commit()
        cursor.close()
        return redirect(url_for('consign_page', consign_id=consign_id))
    except:
        db.rollback()
        cursor.close()
        return jsonify({
            "status": "6error2",
            "message": "添加错误！"
        })

    # 历史接单
    @app.route('/history/<user_id>', methods=["GET"])
    @login_require
    def history(user_id):
        cursor = db.cursor()
        sql = "select comsign_name,`desc`,`time` from consigns where user_id='%s'" \
              % (user_id)
        cursor.execute(sql)
        comsigns = cursor.fetchall()

        # 评论不用做了
        # sql = "select comsign_name,`desc`,`time` from comments where user_id='%s'" \
        #       % (user_id)
        # cursor.execute(sql)
        # comments = cursor.fetchall()
        # 返回一个网页
        return ''