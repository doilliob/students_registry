''' Flask '''
from flask import render_template, request, session, redirect, url_for
''' SQLAlchemy '''
from sqlalchemy import Column, Integer, String, DateTime, Float
''' werkzeug '''
from werkzeug.security import generate_password_hash, check_password_hash
''' WTForms '''
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

''' Общие '''
import random
import string
import datetime
''' Внутренние '''
import configuration
import db

''' 
========================================
Инициализация 
========================================
'''
APP_SECRET = None

def register_module(app):
	global APP_SECRET
	APP_SECRET = configuration.FLASK_SECRET_KEY
	app.add_url_rule('/logout', 'logout', route_logout, methods=['GET'])
	app.add_url_rule('/login', 'login', route_login, methods=['POST', 'GET'])
	app.add_url_rule('/config/delete_sample_user/<code>', 'config/delete_sample_user', delete_sample_user, methods=['GET'])
	app.add_url_rule('/config/create_sample_user/<code>', 'config/create_sample_user', create_sample_user, methods=['GET'])


''' 
========================================
Роли в системе 
========================================
'''
ROLE_ADMINISTRATOR = 'ADMINISTRATOR'
ROLE_USER = 'USER'
ROLE_ALL = [
		ROLE_ADMINISTRATOR, 
		ROLE_USER
]

def crypt_user_role(role):
	global APP_SECRET
	return generate_password_hash(role)

def role_is_admin(role):
	return (role == ROLE_ADMINISTRATOR)

def role_is_user(role):
	return (role == ROLE_USER)

def role_is_role(role):
	return (role in ROLE_ALL)

def user_is_admin():
	if ('role' in session):
		return check_password_hash(session['role'], ROLE_ADMINISTRATOR)
	return False


def user_is_user():
	if ('role' in session):
		return check_password_hash(session['role'], ROLE_USER)
	return False

'''
========================================
Функции управления авторизацией
========================================
'''
def if_auth() -> 'True':
	global APP_SECRET
	if 'auth_code' in session:
		if check_password_hash(session['auth_code'], APP_SECRET):
			return True
	del_auth()
	return False


def auth(user):
	global APP_SECRET
	session['auth_code'] = generate_password_hash(APP_SECRET)
	session['user_id'] = user.id
	session['fullname'] = user.fullname
	session['role'] = crypt_user_role(user.role)


def del_auth():
	session.pop('auth_code', None)
	session.pop('fullname', None)
	session.pop('role', None)
	session.pop('auth_code', None)


def get_user_id():
	return session['user_id']

def get_user_name():
	return session['fullname']


'''
======================================== 
Модели
========================================
'''
''' Класс пользователя системы '''
class User(db.Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    fullname = Column(String)
    password = Column(String)
    salt = Column(String)
    role = Column(String)
    
    def __init__(self, login, fullname, password, role):
        self.login = login
        self.fullname = fullname
        self.salt = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz@!#$%^&') for x in range(8))
        self.password = generate_password_hash(password + self.salt)
        if not(role_is_role(role)):
        	raise Exception('Ошибка! Указана несуществующая роль!')
        self.role = role

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.login, self.fullname, self.password)

    def is_password_ok(self, password):
    	return check_password_hash(self.password, password + self.salt)
# --//-- class User(db.Base)


'''
======================================== 
Формы
========================================
'''
''' Форма авторизации '''
class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])


'''
======================================== 
Маршруты
========================================
'''

''' Создание стандартного пользователя '''
def create_sample_user(code):
	global APP_SECRET
	if (code == APP_SECRET):
		session = db.Session()
		if (len(session.query(User).filter_by(login="admin").all()) == 0):
			user = User('admin', 'Администратор системы', 'admin', ROLE_ADMINISTRATOR)
			session.add(user)
			session.commit()
	return redirect(url_for('login'))


''' Удаление стандартного пользователя '''
def delete_sample_user(code):
	global APP_SECRET
	if (code == APP_SECRET):
		session = db.Session()
		users = session.query(User).filter_by(login="admin").all()
		if (len(users) > 0):
			for user in users:
				session.delete(user)
			session.commit()
	return redirect(url_for('login'))


''' Login/Logout '''
def route_logout():
	del_auth()
	return redirect(url_for('login'), code=302)


def route_login():
	loginForm = LoginForm()
	# POST
	if (request.method == 'POST'):
		if loginForm.validate_on_submit():
			''' Получаем логин и пароль из формы '''
			login = loginForm.login.data
			password = loginForm.password.data
			''' Находим в БД логин '''
			user = db.Session().query(User).filter_by(login=login).first()
			if user:
				if user.is_password_ok(password):
					auth(user)
					return redirect(url_for('index'), code=302)
				else:
					return render_template('login.html', form=loginForm, login_message='Пользователя с таким логином и паролем не существует!')
			else:
					return render_template('login.html', form=loginForm, login_message='Пользователя с таким логином и паролем не существует!')
	# GET AND OTHER
	return render_template('login.html', form=loginForm, login_message='Вы не авторизированы! Введите логин и пароль!')
