import os


BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'salainen'
    PORT = os.environ.get('PORT')
    HOST = os.environ.get('DB_URL')
    USER = os.environ.get('DB_USER')
    PASSWORD = os.environ.get('DB_PASSWORD')
    DATABASE = os.environ.get('DB_NAME')

    MAX_CONTENT_LENGTH = 1024*1024 # 1 MB
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
    IMAGES_PATH = os.path.join(BASEDIR, 'static/images')
    UPLOAD_PATH = os.path.join(BASEDIR, 'static/uploads')

    SESSION_COOKIE_SAMESITE = 'Strict'

    DATABASE_URL = os.environ.get('DATABASE_URL')

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif os.environ.get('TESTING'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    else:
        SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:5432/{DATABASE}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False


