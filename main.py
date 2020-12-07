from flask import Blueprint, render_template, flash, redirect, url_for, request
from datetime import timedelta, datetime
from hashlib import md5
from . import db, mail
import string
import random
from .models import User
from flask_login import login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from flask_mail import Mail, Message
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length

main = Blueprint('main', __name__)

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    submit = SubmitField('Получить пароль')

class PasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    id = HiddenField()
    submit1 = SubmitField('Войти')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.login)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form1 = PasswordForm()
    if form1.submit1.data and form1.validate():
        password = md5(form1.password.data.encode('utf-8')).hexdigest()
        id = form1.id.data
        user = User.query.filter_by(id=int(id)).first()
        #проверка пароля и таймштампа
        if user.md5_password == password:
            if datetime.timestamp(datetime.today()) <= float(user.TTL):
                login_user(user)
                return redirect(url_for('main.profile'))
            flash('Истекло время действия пароля')
        else:
            flash('Неверный пароль')
        return redirect(url_for('main.login'))
    if form.submit.data and form.validate():
        user = User.query.filter_by(login=form.login.data).first()
        if user is None:
            flash('Неверный логин')
            return redirect(url_for('main.login'))
        pwd = ''
        for i in range(10):
            pwd += random.choice(string.ascii_letters + string.digits + string.punctuation)
        TTL = datetime.today() + timedelta(minutes=5)
        user.md5_password = md5(pwd.encode('utf-8')).hexdigest()
        user.TTL = datetime.timestamp(TTL)
        db.session.commit()

        msg = Message("Пароль", recipients=[user.email])
        msg.body = "Используйте этот пароль для входа: " + pwd

        try:
            mail.send(msg)
        except:
            flash("Что-то пошло не так. Напишите администратору.")

        return render_template('login.html', title = 'Логин', form=PasswordForm(id = user.id), id=user.id)

    return render_template('login.html', title = 'Логин', form=form, id=0)




@main.route('/')
def index():
    return render_template('index.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
