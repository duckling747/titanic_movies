from flask import (
    render_template,
    redirect,
    flash,
    url_for,
    request,
)
from app import (
    app,
    db,
)
from app.models import (
    User,
    Movie,
    Actor,
    Review,
    Genre,
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
    AdminRegistrationForm,
    ActorForm,
    GenreForm,
    AddToMovieForm,
    DelFromMovieForm,
    ReviewForm,
)

from sqlalchemy.sql import func, desc


@app.route('/')
@app.route('/index')
def index():
    top_graded = Movie.query.join(Review)\
        .with_entities(Movie.title, Movie.year, Movie.id, func.round(func.avg(Review.grade), 2)\
        .label('avg'))\
        .group_by(Movie.id).order_by(desc('avg')).limit(10).all()

    newbies = Movie.query.order_by(Movie.timestamp.desc()).limit(10).all()
    return render_template('index.j2', title='home',
        top_graded=top_graded, newbies=newbies)

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
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registered succesfully')
        return redirect(url_for('login'))
    return render_template('register.j2', title='register', form=form)

@app.route('/browse')
def browse():
    movies = Movie.query.order_by(Movie.title.asc()).all()
    return render_template('browse.j2', title='browse', movies=movies)

@app.route('/movies/<id>', methods=['GET', 'POST'])
@login_required
def movie_details(id):
    m = Movie.query.outerjoin(Review).outerjoin(User).filter(Movie.id == id).first_or_404()
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            grade=form.grade.data, thoughts=form.thoughts.data,
            feelings=form.feelings.data, user_id=current_user.id,
            movie_id=id)
        db.session.add(review)
        db.session.commit()
        flash('Review sent succesfully')
        return redirect(url_for('movie_details', id=id))
    return render_template('movie_details.j2', title='movie_details', movie=m,
        form=form)

@app.route('/admin')
@login_required
def admin():
    if not current_user.admin:
        return redirect(url_for('index'))
    reviews = Review.query.order_by(Review.timestamp.desc()).limit(10).all()
    return render_template('admin.j2', title='admin', reviews=reviews)

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_user():
    if not current_user.admin:
        return redirect(url_for('index'))
    users = User.query.all()
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, admin=form.admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully')
        return redirect(url_for('admin_user'))
    return render_template('admin_user.j2', title='admin_user',
        users=users, form=form)

@app.route('/admin/movies/<id>/actors', methods=['POST'])
@login_required
def admin_movie_add_actor(id):
    if not current_user.admin:
        return redirect(url_for('index'))
    actor = request.form['select']
    m = Movie.query.get(id)
    actor = Actor.query.get(actor)
    m.actors.append(actor)
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin_movie'))

@app.route('/admin/movies/<id>/genres', methods=['POST'])
@login_required
def admin_movie_add_genre(id):
    if not current_user.admin:
        return redirect(url_for('index'))
    genre = request.form['select']
    m = Movie.query.get(id)
    genre = Genre.query.get(genre)
    m.genres.append(genre)
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin_movie'))

@app.route('/admin/movies/<movie_id>/actors/<actor_id>', methods=['POST'])
@login_required
def admin_movie_del_actor(movie_id, actor_id):
    if not current_user.admin:
        return redirect(url_for('index'))
    m = Movie.query.get(movie_id)
    m.actors = [a for a in m.actors if a.id != int(actor_id)]
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin_movie'))

@app.route('/admin/movies/<movie_id>/genres/<genre_id>', methods=['POST'])
@login_required
def admin_movie_del_genre(movie_id, genre_id):
    if not current_user.admin:
        return redirect(url_for('index'))
    m = Movie.query.get(movie_id)
    m.genres = [g for g in m.genres if g.id != int(genre_id)]
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin_movie'))

@app.route('/admin/movies', methods=['GET', 'POST'])
@login_required
def admin_movie():
    if not current_user.admin:
        return redirect(url_for('index'))
    movies = Movie.query.all()
    form = MovieForm()
    add_actor = AddToMovieForm(obj=Actor)
    add_actor.select.choices = [(a.id, a.name) for a in Actor.query.order_by('name')]
    add_genre = AddToMovieForm(obj=Genre)
    add_genre.select.choices = [(g.id, g.name) for g in Genre.query.order_by('name')]
    
    if form.validate_on_submit():
        m = Movie(title=form.title.data, year=form.year.data)
        db.session.add(m)
        db.session.commit()
        flash('Movie added to db')
        return redirect(url_for('admin_movie'))
    return render_template('admin_movie.j2', title='admin_movie',
        movies=movies, form=form, add_actor=add_actor, add_genre=add_genre,
        del_form = DelFromMovieForm())


@app.route('/admin/actors', methods=['GET', 'POST'])
@login_required
def admin_actor():
    if not current_user.admin:
        return redirect(url_for('index'))
    actors = Actor.query.all()
    form = ActorForm()
    if form.validate_on_submit():
        a = Actor(name=form.name.data)
        db.session.add(a)
        db.session.commit()
        flash('Actor added to db')
        return redirect(url_for('admin_actor'))
    return render_template('admin_actor.j2', title='admin_actor',
        actors=actors, form=form)

@app.route('/admin/genres', methods=['GET', 'POST'])
@login_required
def admin_genre():
    if not current_user.admin:
        return redirect(url_for('index'))
    genres = Genre.query.all()
    form = GenreForm()
    if form.validate_on_submit():
        g = Genre(name=form.name.data)
        db.session.add(g)
        db.session.commit()
        flash('Genre added to db')
        return redirect(url_for('admin_genre'))
    return render_template('admin_genre.j2', title='admin_genre',
        genres=genres, form=form)

