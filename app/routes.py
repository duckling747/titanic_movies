from flask import (
    render_template,
    redirect,
    flash,
    url_for,
)
from app import (
    app,
    db,
)

from app.models import (
    User,
    Movie,
)

from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
)

from app.forms import (
    LoginForm,
    RegistrationForm,
    MovieForm,
)

from datetime import datetime

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.j2', title='home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.j2', title='login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
            admin=False, joined=datetime.utcnow)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registered succesfully')
        return redirect(url_for('login'))
    return render_template('register.j2', title='register', form=form)

@app.route('/admin')
@login_required
def admin():
    if not current_user.admin:
        return redirect(url_for('index'))
    return render_template('admin.j2', title='admin')

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_user():
    if not current_user.admin:
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin_user.j2', title='admin_user',
        users=users)

@app.route('/admin/movies', methods=['GET', 'POST'])
@login_required
def admin_movie():
    if not current_user.admin:
        return redirect(url_for('index'))
    movies = Movie.query.all()
    form = MovieForm()
    if form.validate_on_submit():
        m = Movie(title=form.title.data, year=form.year.data)
        db.session.add(m)
        db.session.commit()
        flash('Movie added to db')
        return redirect(url_for('admin_movie'))
    return render_template('admin_movie.j2', title='admin_movie',
        movies=movies, form=form)
