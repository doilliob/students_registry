from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import configuration


''' Переменные '''
Base = declarative_base()
Engine = None
Session = None


''' Инициализация БД '''


def init():
	global Session
	global Engine
	conn_str = '%s://%s:%s@%s/%s' % (configuration.DB_ENGINE, configuration.DB_LOGIN, configuration.DB_PASSWORD, configuration.DB_HOST, configuration.DB_BASE)
	Engine = create_engine(conn_str, echo=True)
	Session = sessionmaker(bind=Engine)
    # Создание таблицы в БД
	Base.metadata.create_all(Engine)

