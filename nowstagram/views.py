# -*- encoding=UTF-8 -*-

from nowstagram import app, db
from models import Image, User, Comment,Like,followers
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
import random, hashlib, json, uuid, os
from flask_login import login_user, logout_user, current_user, login_required
from qiniusdk import qiniu_upload_file

from tools.sql_connect_tools import SQLConnectTools



@app.route('/index/images/<int:page>/<int:per_page>/')
def index_images(page, per_page):
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=page, per_page=per_page, error_out=False)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        comments = []
        for i in range(0, min(2, len(image.comments))):
            comment = image.comments[i]
            comments.append({'username':comment.user.username,
                             'user_id':comment.user_id,
                             'content':comment.content})
        imgvo = {'id': image.id,
                 'url': image.url,
                 'comment_count': len(image.comments),
                 'user_id': image.user_id,
                 'head_url':image.user.head_url,
                 'created_date':str(image.created_date),
                 'comments':comments}
        images.append(imgvo)

    map['images'] = images
    return json.dumps(map)

# 这个改动不行
# @app.route('/')
# def user():
#     return render_template('user_login_new.html')

@app.route('/')
def index():
    images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    return render_template('index.html', images=images)


@app.route('/image/<int:image_id>/')
@login_required
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        return redirect('/')
    comments = Comment.query.filter_by(image_id=image_id).order_by(db.desc(Comment.id)).limit(20).all()
    return render_template('pageDetail.html', image=image, comments=comments)


@app.route('/profile/<int:user_id>/')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id=user_id).order_by(db.desc(Image.id)).paginate(page=1, per_page=3, error_out=False)
    return render_template('profile.html', user=user, images=paginate.items, has_next=paginate.has_next)


@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    paginate = Image.query.filter_by(user_id=user_id).order_by(db.desc(Image.id)).paginate(page=page, per_page=per_page, error_out=False)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comments)}
        images.append(imgvo)

    map['images'] = images
    return json.dumps(map)


@app.route('/regloginpage/')
def regloginpage():
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['reglogin']):
        msg = msg + m
    return render_template('login.html', msg=msg, next=request.values.get('next'))


def redirect_with_msg(target, msg, category):
    if msg != None:
        flash(msg, category=category)
    return redirect(target)


@app.route('/login/', methods={'post', 'get'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/', u'用户名或密码不能为空', 'reglogin')

    user = User.query.filter_by(username=username).first()
    if user == None:
        return redirect_with_msg('/regloginpage/', u'用户名不存在', 'reglogin')

    m = hashlib.md5()
    m.update(password + user.salt)
    if (m.hexdigest() != user.password):
        return redirect_with_msg('/regloginpage/', u'密码错误', 'reglogin')

    login_user(user)

    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)

    return redirect('/')


@app.route('/reg/', methods={'post', 'get'})
def reg():
    # request.args
    # request.form
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/', u'用户名或密码不能为空', 'reglogin')

    user = User.query.filter_by(username=username).first()
    if user != None:
        return redirect_with_msg('/regloginpage/', u'用户名已经存在', 'reglogin')

    # 更多判断

    salt = '.'.join(random.sample('01234567890abcdefghigABCDEFGHI', 10))
    m = hashlib.md5()
    m.update(password + salt)
    password = m.hexdigest()
    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()

    login_user(user)

    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)

    return redirect('/')


@app.route('/alter/',methods={'post', 'get'})
def alter():
    # request.args
    # request.form
    if request.method == 'post':
        username = request.values.get('username').strip()
        password = request.values.get('password').strip()

        # if username == '' or password == '':
        #     return redirect_with_msg('/alter/', u'用户名或密码不能为空', 'reglogin')
        #
        user = User.query.filter_by(username=username).first()
        print(user.username)
        # if user == None:
        #     return redirect_with_msg('/alter/', u'用户名不存在', 'reglogin')

        # 更多判断

        salt = '.'.join(random.sample('01234567890abcdefghigABCDEFGHI', 10))
        m = hashlib.md5()
        m.update(password + salt)
        password = m.hexdigest()
        user.password = password
        user.salt = salt
        db.session.commit()
        return redirect('/regloginpage/')

    else:
        return render_template('alter.html')


@app.route('/alter1/',methods={'post', 'get'})
def alter1():
    # request.args
    # request.form

    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    # if username == '' or password == '':
    #     return redirect_with_msg('/alter/', u'用户名或密码不能为空', 'reglogin')
    #
    user = User.query.filter_by(username=username).first()
    print(user.username)
    # if user == None:
    #     return redirect_with_msg('/alter/', u'用户名不存在', 'reglogin')

    # 更多判断

    salt = '.'.join(random.sample('01234567890abcdefghigABCDEFGHI', 10))
    m = hashlib.md5()
    m.update(password + salt)
    password = m.hexdigest()
    user.password = password
    user.salt = salt
    db.session.commit()
    return redirect('/')







@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')


@app.route('/image/<image_name>')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


@app.route('/addcomment/', methods={'post'})
@login_required
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content']
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({"code":0, "id":comment.id,
                       "content":comment.content,
                       "username":comment.user.username,
                       "user_id":comment.user_id})


def save_to_qiniu(file, file_name):
    return qiniu_upload_file(file, file_name)


def save_to_local(file, file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, file_name))
    return '/image/' + file_name


@app.route('/upload/', methods={"post"})
@login_required
def upload():
    file = request.files['file']
    # http://werkzeug.pocoo.org/docs/0.10/datastructures/
    # 需要对文件进行裁剪等操作
    file_ext = ''
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
        # url = qiniu_upload_file(file, file_name)
        url = save_to_local(file, file_name)
        if url != None:
            db.session.add(Image(url, current_user.id))
            db.session.commit()

    return redirect('/profile/%d' % current_user.id)


# 新的页面
# 喜欢页
@app.route('/user_like_list_new/<int:user_id>/')
@login_required
def user_like_list_new(user_id):
    likes = Like.query.filter_by(user_id=user_id).all()
    images = []
    for like in likes:
        image = Image.query.get(like.image_id)
        images.append(image)

    return render_template('user_like_list_new.html',images=images)


@app.route('/like_or_no_like/<int:image_id>/<int:current_user_id>')
@login_required
def like_or_no_like(image_id,current_user_id):
    likes = Like.query.filter_by(image_id=image_id,user_id=current_user_id).all()
    if len(likes) !=0:
        db.session.delete(likes[0])
        db.session.commit()
        return redirect('/')
    else:
        like = Like(image_id=image_id,user_id=current_user_id)
        db.session.add(like)
        db.session.commit()
        return redirect('/')





# 关注页
@app.route('/user_friend_list_new/<int:user_id>/')
@login_required
def user_friend_list_new(user_id):
    sql_toos = SQLConnectTools()
    followers = sql_toos.get_follows(110)
    users = []
    for follower in followers:
        user = User.query.get(follower)
        users.append(user)

    return render_template('user_friend_list_new.html', users=users)


# follow_friend
@app.route('/follow_friend/<int:current_user_id>/<int:follow_user_id>')
@login_required
def follow_friend(current_user_id,follow_user_id):
    current_user = User.query.get(current_user_id)
    follow_user = User.query.get(follow_user_id)
    if current_user.is_following(follow_user):
        return redirect('/')
    else:
        u = current_user.follow(follow_user)
        db.session.add(u)
        db.session.commit()
        return redirect('/')


# 设置页
@app.route('/settings/')
@login_required
def settings():
    # request.args
    # request.form
    if request.method == 'post':
        username = request.values.get('username').strip()
        password = request.values.get('password').strip()

        # if username == '' or password == '':
        #     return redirect_with_msg('/alter/', u'用户名或密码不能为空', 'reglogin')
        #
        user = User.query.filter_by(username=username).first()
        print(user.username)
        # if user == None:
        #     return redirect_with_msg('/alter/', u'用户名不存在', 'reglogin')

        # 更多判断

        salt = '.'.join(random.sample('01234567890abcdefghigABCDEFGHI', 10))
        m = hashlib.md5()
        m.update(password + salt)
        password = m.hexdigest()
        user.password = password
        user.salt = salt
        db.session.commit()
        return redirect('/regloginpage/')

    else:
        return render_template('user_settings.html')


# 搜索

@app.route('/search/',methods={'post', 'get'})
@login_required
def search():
    # request.args
    # request.form
    if request.method == 'post':
        username = request.values.get('username').strip()
        password = request.values.get('password').strip()

        # if username == '' or password == '':
        #     return redirect_with_msg('/alter/', u'用户名或密码不能为空', 'reglogin')
        #
        user = User.query.filter_by(username=username).first()
        print(user.username)
        # if user == None:
        #     return redirect_with_msg('/alter/', u'用户名不存在', 'reglogin')

        # 更多判断

        salt = '.'.join(random.sample('01234567890abcdefghigABCDEFGHI', 10))
        m = hashlib.md5()
        m.update(password + salt)
        password = m.hexdigest()
        user.password = password
        user.salt = salt
        db.session.commit()
        return 'yes'

    else:
        return render_template('search_input.html')


