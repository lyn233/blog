__author__ = 'daiguanlin'
# -*- coding:utf-8 -*-
from flask import render_template, session, redirect, url_for, flash, abort, request
from flask_login import login_required,login_user,logout_user,current_user

from .import main
from .import forms
from weblog.app import db
from weblog.app import models,login_manager
from weblog.app.models import User,Post
from flask_login import LoginManager

@main.route('/')
def index():
     #posts = Post.query.all()

    page = request.args.get('page', 1, type=int)
    #page = request.arges.get('page',1,type=int)
    pagination = Post.query.paginate(page, per_page=4, error_out=True)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.Login_Email.data).first()
        if user is not None and user.verify_password(form.Login_Password.data):
            login_user(user, form.remember_me.data)
            flash("登陆成功")
            return redirect(url_for('.index'))
    return render_template('login.html',form=form, error=error)


@main.route('/user/<username>/pwdmodi', methods=["GET", "POST"])
@login_required
def pwdmodi(username):
    form = forms.ModifyPasswordForm()
    user = User.query.filter_by(name=username).first()
    if form.validate_on_submit():
        if user is not None and user.verify_password(form.old_password.data):
            user.password = form.new_password_2.data
            db.session.add(user)
            db.session.commit()
            flash("密码修改成功")
            return redirect(url_for(".index"))
        #else:
        #    flash("密码错误")
    return render_template("pwdmodi.html", form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have been log out')
    return redirect(url_for(".index"))

@main.route('/user/<username>', methods=["GET", "POST"])
@login_required
def user(username):
    user = User.query.filter_by(name=username).first()
    form = forms.PostForm()
    if user is None:
        abort(404)
    elif form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash("发表成功")
        return redirect(url_for(".index"))
        #return render_template('user.html', user=user,form=form)
    return render_template('user.html', user=user, form=form)

@main.route("/user/<username>/article", methods=["GET", "POST"])
@login_required
def article(username):
    form = forms.DelArtForm()
    sub_form = forms.SubForm()
    user = User.query.filter_by(name=username).first()
    #user_id = current_user.name
    if user is None:
        abort(404)
    if form.validate_on_submit():
        pass
    #posts = Post.query.filter_by(author=user).all() #后台逻辑
    posts = Post.query.all()
    return render_template("article.html", user=user, posts=posts, form=form, sub_form=sub_form)


@main.route('/register', methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.username.data, email=form.user_email.data, password_hash=form.user_password_2.data)
        models.create_user(name=form.username.data, email=form.user_email.data, password_hash=form.user_password_2.data)
        token = user.generate_confirmation_token()
        return redirect(url_for('.login'))
    return render_template("register.html", form=form)

@main.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author:
        abort(403)
    form = forms.PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash("编辑成功")
        return redirect("")
        #return redirect(url_for('post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
