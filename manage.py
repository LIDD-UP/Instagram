# -*- encoding=UTF-8 -*-

from nowstagram import app, db
from flask_script import Manager
from sqlalchemy import or_,and_
from nowstagram.models import User, Image, Comment,Like
from tools.sql_connect_tools import SQLConnectTools
import random, unittest, tests
import sys
reload(sys)
sys.setdefaultencoding('gbk')


manager = Manager(app)

def get_image_url():
    return 'http://images.nowcoder.com/head/' + str(random.randint(0,1000)) +  'm.png'


def get_image():
    return '/image/276a1feef5f111e8988fb46d83f68db1.jpg'

@manager.command
def run_test():
    #init_database()
    db.drop_all()
    db.create_all()
    tests = unittest.TestLoader().discover('./')
    unittest.TextTestRunner().run(tests)


@manager.command
def run_test2():
    db.drop_all()
    db.create_all()
    for i in range(0, 100):
        db.session.add(User('User' + str(i + 1), 'a' + str(i + 1)))
        # if i>2:
        #     db.session.add(Friend('User'+str(i),'User'+str(i-1)))
        for j in range(0, 10):
            db.session.add(Image(get_image_url(), i + 1))
            for k in range(0, 3):
                db.session.add(Comment('This is a comment' + str(k), 1 + 10 * i + j, i + 1))
                db.session.add(Like(1 + 10 * i + j, i + 1))

    db.session.commit()

    for i in range(50, 100, 2):
        user = User.query.get(i)
        user.username = '[New1]' + user.username

    User.query.filter_by(id=51).update({'username': '[New2]'})
    db.session.commit()

    for i in range(50, 100, 2):
        comment = Comment.query.get(i + 1)
        db.session.delete(comment)

    db.session.commit()

    print 1, User.query.all()
    print 2, User.query.get(3)
    print 3, User.query.filter_by(id=5).first()
    print 4, User.query.order_by(User.id.desc()).offset(1).limit(2).all()
    print 5, User.query.filter(User.username.endswith('0')).limit(3).all()
    print 6, User.query.filter(or_(User.id == 88, User.id == 99)).all()
    print 7, User.query.filter(and_(User.id > 88, User.id < 93)).all()
    print 8, User.query.filter(and_(User.id > 88, User.id < 93)).first_or_404()
    print 9, User.query.order_by(User.id.desc()).paginate(page=1, per_page=10).items
    user = User.query.get(1)
    print 10, user.images

    image = Image.query.get(1)
    print 11, image, image.user





@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0, 100):
        db.session.add(User('User' + str(i+1), 'a'+str(i+1)))
        for j in range(0, 10):
            db.session.add(Image(get_image_url(), i+1))
            for k in range(0, 3):
                db.session.add(Comment('This is a comment' + str(k), 1+10*i+j, i+1))

    db.session.commit()

    for i in range(50, 100, 2):
        user = User.query.get(i)
        user.username = '[New1]' + user.username

    User.query.filter_by(id=51).update({'username':'[New2]'})
    db.session.commit()

    for i in range(50, 100, 2):
        comment = Comment.query.get(i+1)
        db.session.delete(comment)




    db.session.commit()

    print 1, User.query.all()
    print 2, User.query.get(3)
    print 3, User.query.filter_by(id=5).first()
    print 4, User.query.order_by(User.id.desc()).offset(1).limit(2).all()
    print 5, User.query.filter(User.username.endswith('0')).limit(3).all()
    print 6, User.query.filter(or_(User.id == 88, User.id == 99)).all()
    print 7, User.query.filter(and_(User.id > 88, User.id < 93)).all()
    print 8, User.query.filter(and_(User.id > 88, User.id < 93)).first_or_404()
    print 9, User.query.order_by(User.id.desc()).paginate(page=1, per_page=10).items
    user = User.query.get(1)
    print 10, user.images



    image = Image.query.get(1)
    print 11, image, image.user

def test_follow():
    u1 = User('bluesli8','123456')
    u2 = User('bluesli00','123456 ')
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()
    assert u1.unfollow(u2) == None
    u = u1.follow(u2)
    db.session.add(u)
    db.session.commit()
    assert u1.follow(u2) == None
    assert u1.is_following(u2)
    assert u1.followed.count() == 1
    assert u1.followed.first().username == 'bluesli'
    assert u2.followers.count() == 1
    assert u2.followers.first().username == 'bluesli2'
    u = u1.unfollow(u2)
    assert u != None
    db.session.add(u)
    db.session.commit()
    assert u1.is_following(u2) == False
    assert u1.followed.count() == 0
    assert u2.followers.count() == 0

if __name__ == '__main__':
    test_follow()
    # manager.run()