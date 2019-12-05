from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect
import datetime


''' Внутренние библиотеки '''
import configuration
import db
''' Модули с роутами '''
import auth
import students

''' Приложение '''
app = Flask(__name__)


''' Безопасность '''
app.config['SECRET_KEY'] = configuration.FLASK_SECRET_KEY
csrf = CSRFProtect(app)


''' Инициализация '''
db.init()


''' Регистрация модуля авторизации '''
auth.register_module(app)


''' Регистрируем модуль Студенты '''
students.register_module(app)


'''
======================================== 
Основные маршруты
======================================== 
'''

@app.route('/', methods=['POST', 'GET'])
def index():
	#----------------------------------
	if not(auth.if_auth()):
		return redirect(url_for('login'))
	#----------------------------------
	params = dict()
	params['username'] = auth.get_user_name()
	return render_template('index.html', params=params)
		





if __name__=='__main__':
	app.run(debug=True)