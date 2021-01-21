import os


BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'salainen'
    PORT = os.environ.get('PORT')
    HOST = os.environ.get('DB_URL')
    USER = os.environ.get('DB_USER')
    PASSWORD = os.environ.get('DB_PASSWORD')
    DATABASE = os.environ.get('DB_NAME')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:5432/{DATABASE}'

    if os.environ.get('TESTING'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    SQLALCHEMY_TRACK_MODIFICATIONS = False


