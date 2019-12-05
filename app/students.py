''' Flask '''
from flask import render_template, request, redirect, url_for, session
''' WTForms '''
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, ValidationError
''' SQLAlchemy '''
from sqlalchemy import Column, Integer, String, DateTime, Float

''' Общие '''
import re
import dictionaries
import datetime

''' Внутренние '''
import db
import auth


'''
========================================================
Регистрация модуля
========================================================
'''

def register_module(app):
	app.add_url_rule('/groups', 'groups', show_groups, methods=['GET'])
	# new
	app.add_url_rule('/students/new', 'students/new', new_student, methods=['GET'])
	app.add_url_rule('/students/add', 'students/add', add_student, methods=['POST'])
	# exists
	app.add_url_rule('/students/edit/<sid>', 'students/edit', edit_student, methods=['GET'])
	app.add_url_rule('/students/update/<sid>', 'students/update', update_student, methods=['POST'])
	# all
	app.add_url_rule('/students/all', 'students/all', show_all_students, methods=['GET'])


'''
========================================================
Модель
========================================================
'''

''' Данные о студенте '''
class Student(db.Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)

    ''' Общие поля '''
    asurso_id = Column(Integer, unique=True, nullable=True) # ИД студента в АСУ РСО
    app_number = Column(String, nullable=True, default=None)
    registration_date = Column(DateTime, nullable=False, default=datetime.datetime(2019, 7, 20)) # Дата регистрации заявления
    user_id = Column(Integer, nullable=True) # Куратор
    group = Column(String, nullable=True, default=None)
    
    ''' Сведения о студенте общшие '''
    lastname = Column(String, nullable=False) # ФИО
    firstname = Column(String, nullable=False)
    middlename = Column(String, nullable=False)
    gender_id = Column(Integer, nullable=False, default=1) # Пол
    birth_date = Column(DateTime, nullable=False, default=datetime.datetime(2002, 1, 1))# Дата рождения
    
    ''' ПРОЖИВАНИЕ '''
    region_id = Column(Integer, nullable=False, default=63) # Регион
    town_type_id = Column(Integer, nullable=False, default=2) # Тип населенного пункта
    address = Column(String, nullable=False, default='Самарская обл., _ р-н., г._ , ул. _, д. _') # Адрес проживания
    
    ''' ДОКУМЕНТ ИЛ '''
    identity_document_type_id = Column(Integer, nullable=False, default=1)  # Тип документа ИЛ
    identity_document_series = Column(String, nullable=False, default='') # Серия документа ИЛ
    identity_document_number = Column(String, nullable=False, default='') # Номер документа ИЛ
    identity_document_date = Column(DateTime, nullable=False, default=datetime.datetime(2002, 1, 1)) # Дата выдачи документа ИЛ (2013-02-05)
    identity_document_organization = Column(String, nullable=False, default='') # Организация выдавшая документ ИЛ
    identity_document_dep_code = Column(String, nullable=False, default='') # Код подразделения
    identity_document_birth_place = Column(String, nullable=False, default='') # Место рождения
    identity_document_address = Column(String, nullable=False, default='')  # Адрес регистрации
    identity_document_nationality = Column(Integer, nullable=False, default=1) # Гражданство
    
    ''' ДОКУМЕНТ ОБ ОБРАЗОВАНИИ '''
    edoc_type = Column(String, nullable=False, default='SchoolCertificateDocument') # Тип документа об образовании
    edoc_number = Column(String, nullable=False, default='') # Номер документа об образовании
    edoc_date = Column(DateTime, nullable=False, default=datetime.datetime(2019, 1, 1)) # Дата документа об образовании (2017-06-20)
    edoc_organization = Column(String, nullable=False, default='') # Образовательная организация
    edoc_gpa = Column(Float, nullable=False, default=4.0)# Средний балл (1,0 — 5,0)



'''
========================================================
Формы
========================================================
'''

''' Форма студента '''
class StudentForm(FlaskForm):
	# Общие
	group = StringField('Номер группы')
	lastname = StringField('Фамилия', validators=[DataRequired()])
	firstname = StringField('Имя', validators=[DataRequired()])
	middlename = StringField('Отчество', validators=[DataRequired()])
	gender_id = SelectField('Пол', choices=[(dictionaries.PRIEM_GENDER[x],x) for x in dictionaries.PRIEM_GENDER], default=1, coerce=int)
	birth_date = DateField('Дата рождения',format='%Y-%m-%d', validators=[DataRequired()])
	# Проживание
	region_id = SelectField('Регион', choices=[(dictionaries.PRIEM_REGION[x],x) for x in dictionaries.PRIEM_REGION], default=63, coerce=int)
	town_type_id = SelectField('Вид населенного пункта', choices=[(dictionaries.PRIEM_TOWN_TYPE[x],x) for x in dictionaries.PRIEM_TOWN_TYPE], default=2, coerce=int)
	address = StringField('Адрес проживания', validators=[DataRequired()], default='Самарская обл., _ р-н., г._ , ул. _, д. _')
	# Документ УЛ
	identity_document_type_id = SelectField('Тип документа', choices=[(dictionaries.PRIEM_IDOC_TYPE[x],x) for x in dictionaries.PRIEM_IDOC_TYPE], default=1, coerce=int)
	identity_document_series = StringField('Серия')
	identity_document_number = StringField('Номер', validators=[DataRequired()])
	identity_document_date = DateField('Дата выдачи',format='%Y-%m-%d', validators=[DataRequired()])
	identity_document_organization = StringField('Кем выдан', validators=[DataRequired()])
	identity_document_dep_code = StringField('Номер подразделения')
	identity_document_birth_place = StringField('Место рождения', validators=[DataRequired()])
	identity_document_address = StringField('Адрес регистрации', validators=[DataRequired()])
	identity_document_nationality = SelectField('Гражданство', choices=[(dictionaries.PRIEM_IDOC_NATIONALITY_TYPE[x],x) for x in dictionaries.PRIEM_IDOC_NATIONALITY_TYPE], default=1, coerce=int)
	# Документ об образовании
	edoc_type = SelectField('Вид документа', choices=[(dictionaries.PRIEM_EDOC_TYPE[x],x) for x in dictionaries.PRIEM_EDOC_TYPE], default='SchoolCertificateDocument', coerce=str)
	edoc_number = StringField('Номер', validators=[DataRequired()])
	edoc_date = DateField('Дата выдачи',format='%Y-%m-%d', validators=[DataRequired()])
	edoc_organization = StringField('Кем выдан', validators=[DataRequired()])

	def edoc_gpa_check(form, field):
	    if not(re.search(r'^\d+\.\d+$', str(field.data))):
	        raise ValidationError('Должно быть вещественное число с . (например 4.09)!')

	edoc_gpa = FloatField('Средний балл', validators=[edoc_gpa_check], default=4.0)
	edoc_organizations_list = dictionaries.PRIEM_EDOC_ORGANIZATIONS


'''
========================================================
Контроллеры
========================================================
'''


''' Показывает группы студентов '''
def show_groups():
	#----------------------------------
	if not(auth.if_auth()):
		return redirect(url_for('login'))
	#----------------------------------
	user_id = auth.get_user_id()
	session = db.Session()
	
	users = session.query(
		Student.group, 
		Student.id, 
		Student.firstname, 
		Student.lastname, 
		Student.middlename,
		Student.birth_date
		).filter_by(user_id=user_id).order_by(Student.group).all() # 4
	
	groups = {}
	for user in users:
		group = user[0]
		sid = user[1]
		firstname = user[2]
		lastname = user[3]
		middlename = user[4]
		birth_date = user[5]	
		if not(group in groups):
			groups[group] = []
		(groups[group]).append({
			'id': sid,
			'firstname': firstname, 
			'lastname': lastname,
			'middlename': middlename,
			'birth_date': birth_date.strftime('%d-%m-%Y')})
	params = dict()
	params['username'] = auth.get_user_name()
	params['groups'] = groups
	return render_template('students/groups.html', params=params)


''' Создает нового студента и открывает редактор '''
def new_student():
	#----------------------------------
	if not(auth.if_auth()):
		return redirect(url_for('login'))
	#----------------------------------
	params = dict()
	params['form'] = StudentForm()
	params['username'] = auth.get_user_name()
	return render_template('students/edit_student.html', params=params)



''' Добавляет заполненного студента в БД '''
def add_student():
	#----------------------------------
	if not(auth.if_auth()):
		return redirect(url_for('login'))
	#----------------------------------
	student = Student()
	form = StudentForm(obj=student)
	if form.validate():
		session = db.Session()
		form.populate_obj(student)
		user_id = auth.get_user_id()
		student.user_id = user_id
		session.add(student)
		session.commit()
		return redirect(url_for('groups'))
	params = dict()
	params['form'] = form
	params['username'] = auth.get_user_name()
	return render_template('students/edit_student.html', params=params)



''' Создает форму редактирования нового студента '''
def edit_student(sid):
	#----------------------------------
	if not(auth.if_auth()):
		return redirect(url_for('login'))
	#----------------------------------
	student_id = sid
	session = db.Session()
	user = session.query(Student).filter_by(id=sid).first()
	if user:
		params = dict()
		params['form'] = StudentForm(obj=user)
		params['student_id'] = user.id
		params['username'] = auth.get_user_name()
		return render_template('students/edit_student.html', params=params)
	return redirect(url_for('groups'))


''' Сохраняет студента '''
def update_student(sid):
	#----------------------------------
	if not(auth.if_auth()):
		return redirect(url_for('login'))
	#----------------------------------
	form = StudentForm()
	if form.validate():
		student_id = sid
		session = db.Session()
		user = session.query(Student).filter_by(id=sid).first()
		if user:
			form.populate_obj(user)
			# Обновляем принадлежность к группе
			if user.group == '':
				user.user_id = None
			else:
				if not(auth.user_is_admin()):
					user.user_id = auth.get_user_id()
			# Сохраняем
			session.commit()
			return redirect(url_for('groups'))			
	params = dict()
	params['student_id'] = sid
	params['form'] = form
	params['username'] = auth.get_user_name()
	return render_template('students/edit_student.html', params=params)


def show_all_students():
	#----------------------------------
	if not(auth.if_auth()):
		return redirect(url_for('login'))
	#----------------------------------
	session = db.Session()
	users = session.query(
		Student.group, 
		Student.id, 
		Student.firstname, 
		Student.lastname, 
		Student.middlename,
		Student.birth_date
		).order_by(Student.lastname).all() # 4
	
	groups = {}
	alphabet = list('АБВГДЕЁЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ')
	for letter in alphabet:
		if not(letter in groups):
			groups[letter] = []

	for user in users:
		group = user[0]
		sid = user[1]
		firstname = user[2]
		lastname = user[3]
		middlename = user[4]
		birth_date = user[5]	

		letter = lastname[0:1]
		if group == None:
			group = ''
		
		(groups[letter]).append({
			'id': sid,
			'group': group,
			'firstname': firstname, 
			'lastname': lastname,
			'middlename': middlename,
			'birth_date': birth_date.strftime('%d-%m-%Y')})

	params = dict()
	params['groups'] = groups
	params['username'] = auth.get_user_name()
	return render_template('students/all.html', params=params)