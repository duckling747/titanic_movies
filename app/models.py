from app import (
    db,
    login,
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean)
    joined = db.Column(db.DateTime)
    reviews = db.relationship('Review', backref='user', lazy=True, uselist=True)

    def __repr__(self):
        return f'User {self.username}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True)
    year = db.Column(db.Integer, index=True)
    reviews = db.relationship('Review', backref='movie', lazy=True, uselist=True)

    def __repr__(self):
        return f'Movie {self.title}, {self.year}'


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, index=True)
    thoughts = db.Column(db.Text)
    feelings = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    def __repr__(self):
        return f'Review {self.grade}'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
