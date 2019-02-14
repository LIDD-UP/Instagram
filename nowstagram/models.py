# -*- encoding=UTF-8 -*-

from nowstagram import db, login_manager
from datetime import datetime
import random

class Comment(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(1024))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, default=0) # 0 正常 1 被删除
    user = db.relationship('User')

    def __init__(self, content, image_id, user_id):
        self.content = content
        self.image_id = image_id
        self.user_id = user_id

    def __repr__(self):
        return '<Comment %d %s>' % (self.id, self.content)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(512))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_date = db.Column(db.DateTime)
    comments = db.relationship('Comment')
    like = db.relationship('Like')

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.created_date = datetime.now()

    def __repr__(self):
        return '<Image %d %s>' % (self.id, self.url)


# 建立user的多对多关系
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model):
    # __tablename__ = 'user'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    # nickname = db.Column(db.String(80))
    # phone = db.Column(db.String(80))
    # email = db.Column(db.String(80))
    password = db.Column(db.String(32))
    salt = db.Column(db.String(32))
    verify_code = db.Column(db.String(32))
    # my_url = ''
    head_url = db.Column(db.String(256))
    images = db.relationship('Image', backref='user', lazy='dynamic')
    like = db.relationship('Like', backref='user', lazy='dynamic')
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')


    def __init__(self, username, password, salt=''):
        self.username = username
        self.password = password
        self.salt = salt
        self.head_url = 'http://images.nowcoder.com/head/' + str(random.randint(0,1000)) +  'm.png'

    def __repr__(self):
        return '[User %d %s]' % (self.id, self.username)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# 好友表（关注表）
# class Friend(db.Model):
#     __table_args__ = {'mysql_collate': 'utf8_general_ci'}
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     follow_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#
#     def __init__(self,follow_user_id, user_id):
#         self.follow_user_id = follow_user_id
#         self.user_id = user_id
#
#     def __repr__(self):
#         return '<Like %d %d>' % (self.id, self.follow_user_id)






# 喜欢表
class Like(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,image_id, user_id):
        self.image_id = image_id
        self.user_id = user_id

    def __repr__(self):
        return '<Like %d %d>' % (self.id, self.image_id)


class Reply(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(1024))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, default=0) # 0 正常 1 被删除
    user = db.relationship('User')

    def __init__(self, content, comment_id, user_id):
        self.content = content
        self.comment_id = comment_id
        self.user_id = user_id



