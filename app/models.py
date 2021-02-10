from app import (
    db,
    login,
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)
from flask_login import UserMixin

from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean, default=False)
    joined = db.Column(db.DateTime, default=datetime.utcnow)
    disabled = db.Column(db.Boolean, default=False)
    reviews = db.relationship('Review', backref='user', lazy=True, uselist=True)

    def __repr__(self):
        return f'User {self.username}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


CAST = db.Table('cast',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True),
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id'), primary_key=True)
)


MOVIEGENRE = db.Table('moviegenre',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)


MOVIELANGUAGE = db.Table('movielanguage',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True),
    db.Column('language_id', db.Integer, db.ForeignKey('language.id'), primary_key=True)
)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True)
    year = db.Column(db.Integer, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    synopsis = db.Column(db.String(256), unique=True)
    reviews = db.relationship('Review', backref='movie', lazy=True, uselist=True)
    actors = db.relationship('Actor', secondary=CAST, lazy='subquery',
        backref=db.backref('movies', lazy=True), uselist=True)
    genres = db.relationship('Genre', secondary=MOVIEGENRE, lazy='subquery',
        backref=db.backref('movies', lazy=True), uselist=True)
    languages = db.relationship('Language', secondary=MOVIELANGUAGE, lazy='subquery',
        backref=db.backref('languages', lazy=True), uselist=True)

    def __repr__(self):
        return f'Movie {self.title}, {self.year}'


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, index=True)
    thoughts = db.Column(db.Text)
    feelings = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False, index=True)

    def __repr__(self):
        return f'Review {self.grade}'


class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, index=True)


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
