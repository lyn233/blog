# -*- coding:utf-8 -*-
from weblog.app import db
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
import bleach
from markdown import markdown

class Permission():
    WRITE_ARTICLES = 0x01
    ADMINISTER = 0x02


class Role(db.Model):
    __tablename__ = 'Role'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    #users = db.relationship('Role', backref='role', lazy='dynamic')
    role_id = db.Column(db.Integer, db.ForeignKey('User.id'))


class User(UserMixin, db.Model):
    __tablename__ = 'User'

    def __init__(self, name, email, password_hash):
        self.name = name
        self.email = email
        self.password_hash = password_hash

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    address = db.Column(db.String(128), index=True)
    #age = db.Column(db.Integer)
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    users = db.relationship('Role', backref='role', lazy='dynamic')

    #加盐加密生成与验证
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #生成验证令牌
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    #提交数据库
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self


def create_user(name, email, password_hash):
    user = User(name, email, password_hash)
    user.password = password_hash
    user.save()
    return user


class Tag(db.Model):
    __tablename__ = 'Tag'
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(50))

class Template(db.Model):
    __tablename__ = 'Template'
    id = db.Column(db.Integer, primary_key=True)
    tem_body = db.Column(db.Text)

class Post(db.Model):
    __tablename__ = 'Post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text)
    summary = db.Column(db.Text)
    post_time = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    body_html = db.Column(db.Text)
    summary_html = db.Column(db.Text)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul','h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

    @staticmethod
    def on_changed_summary(target,value,oldvalue,initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul','h1', 'h2', 'h3', 'p']
        target.summary_html= bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Post.summary,'set',Post.on_changed_summary)