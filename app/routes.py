from flask import (
    render_template,
    redirect,
    flash,
    url_for,
    request,
    abort,
    send_from_directory,
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
    Language,
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
    SelectionForm,
    DeleteForm,
    ReviewForm,
    DeleteSelectionForm,
    DisableSelectionForm,
    EnableSelectionForm,
    LanguageForm,
    ProfileImageForm,
    ChangePasswordForm,
    EditForm,
    SelectSelectionForm,
)
from sqlalchemy.sql import func, desc
from datetime import datetime
import imghdr
import os


@app.route('/')
@app.route('/index')
def index():
    top_graded = Movie.query.join(Review)\
        .with_entities(Movie.title, Movie.year, Movie.id, func.round(func.avg(Review.grade), 2)\
        .label('avg'))\
        .group_by(Movie.id).order_by(desc('avg')).limit(10).all()

    newbies = Movie.query.order_by(Movie.timestamp.desc()).limit(10).all()
    return render_template('index.html', title='home',
        top_graded=top_graded, newbies=newbies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data)\
            or user.disabled:
            flash('invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/profile/<id>/images', defaults={'img': ''})
@app.route('/profile/<id>/images/<img>', methods=['GET', 'POST'])
@login_required
def image(id, img):
    user = User.query.get_or_404(id)
    profile_pic_form = ProfileImageForm()
    if profile_pic_form.validate_on_submit() and int(id) == current_user.id:
        image_file = profile_pic_form.file.data
        filename = image_file.filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or\
                file_ext != validate_image(image_file.stream):
                return 'Invalid image file', 400
            filename = id + '.' + datetime.now().strftime('%Y%m%d%H%M%S%f')
            user.image = filename
            db.session.add(user)
            db.session.commit()
            image_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            return redirect(url_for('profile'))
        return '', 204
    path = app.config['UPLOAD_PATH']
    if img and os.path.isfile(os.path.join(path, img)):
        return send_from_directory(path, img)
    else:
        return send_from_directory(app.config['IMAGES_PATH'], 'cactus.jpg')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    page = request.args.get('page', default=1, type=int)
    reviews = Review.query\
        .with_entities(User.username, Review.grade, Review.feelings, Review.thoughts,
            Review.timestamp, Review.user_id, Review.movie_id, User.image, Movie.title, Movie.year)\
        .filter(Review.user_id == current_user.id)\
        .join(User)\
        .join(Movie)\
        .order_by(Review.timestamp.desc())\
        .paginate(page, 4, False)
    change_pw_form = ChangePasswordForm()
    profile_pic_form = ProfileImageForm()
    if change_pw_form.validate_on_submit():
        if current_user.check_password(change_pw_form.oldpassword.data):
            current_user.set_password(change_pw_form.password.data)
            db.session.add(current_user)
            db.session.commit()
            flash('Password changed!')
            return redirect(url_for('profile'))
        else:
            change_pw_form.oldpassword.errors.append('Incorrect old password')
    links = construct_page_links('profile', reviews)
    return render_template('profile.html', title='profile',
        current_page=reviews.page, total_pages=reviews.pages,
        next_page=links[0], prev_page=links[1] , first_page=links[2], last_page=links[3],
        change_pw_form=change_pw_form, profile_pic_form=profile_pic_form, reviews=reviews.items)

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
    return render_template('register.html', title='register', form=form)

@app.route('/browse')
def browse():
    movies = Movie.query.order_by(Movie.title.asc()).all()
    return render_template('browse.html', title='browse', movies=movies)

@app.route('/movies/<id>', methods=['GET', 'POST'])
@login_required
def movie_details(id):
    m = Movie.query.get_or_404(id)
    reviews = Review.query\
        .with_entities(User.username, Review.grade, Review.feelings, Review.thoughts,
            Review.timestamp, Review.user_id, User.image)\
        .filter(Review.movie_id == id)\
        .join(User)\
        .limit(4)\
        .all()
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
    return render_template('movie_details.html', title='movie_details',
        movie=m, reviews=reviews, form=form)

def to_date(datestr):
    return datetime.strptime(datestr, '%Y-%m-%d').date()

def construct_parameterized_query(id, textcontains, sort_by, max_grade, min_grade, max_date, min_date):
    reviews = Review.query\
        .with_entities(User.username, Review.grade, Review.feelings, Review.thoughts,
            Review.timestamp, Review.user_id, User.image)\
        .join(User)\
        .filter(Review.movie_id == id, Review.grade <= max_grade, Review.grade >= min_grade,
            func.date(Review.timestamp) <= max_date, func.date(Review.timestamp) >= min_date)
    if textcontains:
        ftextcontains = func.lower(textcontains)
        reviews = reviews.filter(func.lower(Review.feelings).contains(ftextcontains)
            | func.lower(Review.thoughts).contains(ftextcontains))
    if sort_by == 0:
        reviews = reviews.order_by(Review.grade.desc())
    elif sort_by == 1:
        reviews = reviews.order_by(Review.timestamp.desc())
    else:
        abort(404)
    return reviews

def construct_page_links(page_name, collection, **kwargs):
    next_page = url_for(page_name, page=collection.next_num, **kwargs)\
    if collection.has_next else None

    prev_page = url_for(page_name, page=collection.prev_num, **kwargs)\
    if collection.has_prev else None

    first_page = url_for(page_name, page=1, **kwargs)\
    if collection.pages > 1 and collection.page != 1 else None

    last_page = url_for(page_name, page=collection.pages, **kwargs)\
    if collection.pages > 1 and collection.page < collection.pages else None

    return (next_page, prev_page, first_page, last_page)

@app.route('/movies/<id>/reviews')
def reviews(id):
    m = Movie.query\
        .with_entities(Movie.title, Movie.year).filter(Movie.id == id).first_or_404()
    page = request.args.get('page', default=1, type=int)
    min_grade = request.args.get('min_grade', default=0, type=int)
    max_grade = request.args.get('max_grade', default=5, type=int)
    min_date = request.args.get('min_date', default=to_date('1800-01-01'), type=to_date)
    max_date = request.args.get('max_date', default=datetime.today().date(), type=to_date)
    sort_by = request.args.get('sort_by', default=0, type=int)
    textcontains = request.args.get('textcontains', default='', type=str)

    reviews = construct_parameterized_query(id, textcontains, sort_by, max_grade, min_grade, max_date, min_date)\
        .paginate(page, 4, False)

    links = construct_page_links('reviews', reviews, **{ 'id': id, 'min_grade': min_grade,
        'max_grade': max_grade, 'min_date': min_date, 'max_date': max_date,
        'sort_by': sort_by, 'textcontains': textcontains })

    return render_template('movie_reviews.html', title='reviews',
        min_grade=min_grade, max_grade=max_grade, min_date=min_date, max_date=max_date,
        sort_by=sort_by, textcontains=textcontains, current_page=reviews.page, total_pages=reviews.pages,
        next_page=links[0] , prev_page=links[1] , first_page=links[2], last_page=links[3],
        movie=m, reviews=reviews.items)

@app.route('/admin')
@login_required
def admin():
    if not current_user.admin:
        return redirect(url_for('index'))
    page = request.args.get('page', default=1, type=int)
    reviews = Review.query\
        .with_entities(Movie.title, Movie.year, Review.id, Review.grade,
            Review.thoughts, Review.feelings, Review.timestamp, User.username)\
        .join(Movie)\
        .join(User).order_by(Movie.title.asc())\
        .paginate(page, 5, False)
    links = construct_page_links('admin', reviews)
    return render_template('admin.html', title='admin', current_page=reviews.page,
        total_pages=reviews.pages,
        next_page=links[0] , prev_page=links[1] , first_page=links[2], last_page=links[3],
        reviews=reviews.items, del_form=DeleteForm())

@app.route('/admin/reviews/<id>', methods=['POST'])
@login_required
def admin_review_del(id):
    if not current_user.admin:
        return redirect(url_for('index'))
    r = Review.query.get(id)
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/admin/users/toggle_enabled_status', methods=['POST'])
@login_required
def admin_toggle_status_user():
    if not current_user.admin:
        return redirect(url_for('index'))
    id = request.form.get('select')
    u = User.query.get_or_404(id)
    u.disabled = not u.disabled
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('admin_user'))

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_user():
    if not current_user.admin:
        return redirect(url_for('index'))
    users = User.query.order_by(User.username.asc()).all()
    form = AdminRegistrationForm()
    disable_form = DisableSelectionForm(obj=User)
    enable_form = EnableSelectionForm(obj=User)
    disable_form.select.choices = \
        [(u.id, u.username) for u in users if u.id != current_user.id and not u.disabled]
    enable_form.select.choices = \
        [(u.id, u.username) for u in users if u.id != current_user.id and u.disabled]
    if form.validate_on_submit():
        user = User(username=form.username.data, admin=form.admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully')
        return redirect(url_for('admin_user'))
    return render_template('admin_user.html', title='admin_user',
        users=users, form=form, disable_form=disable_form,
        enable_form=enable_form)

@app.route('/admin/movies/<id>/actors', methods=['POST'])
@login_required
def admin_movie_add_actor(id):
    if not current_user.admin:
        return redirect(url_for('index'))
    actor = request.form['select']
    m = Movie.query.get_or_404(id)
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
    m = Movie.query.get_or_404(id)
    genre = Genre.query.get(genre)
    m.genres.append(genre)
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin_movie'))

@app.route('/admin/movies/<id>/languages', methods=['POST'])
@login_required
def admin_movie_add_language(id):
    if not current_user.admin:
        return redirect(url_for('index'))
    language = request.form['select']
    m = Movie.query.get_or_404(id)
    language = Language.query.get(language)
    m.languages.append(language)
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin_movie'))

@app.route('/admin/movies/<movie_id>/actors/<actor_id>', methods=['POST'])
@login_required
def admin_movie_del_actor(movie_id, actor_id):
    if not current_user.admin:
        return redirect(url_for('index'))
    m = Movie.query.get_or_404(movie_id)
    m.actors = [a for a in m.actors if a.id != int(actor_id)]
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin_movie'))

@app.route('/admin/movies/<movie_id>/genres/<genre_id>', methods=['POST'])
@login_required
def admin_movie_del_genre(movie_id, genre_id):
    if not current_user.admin:
        return redirect(url_for('index'))
    m = Movie.query.get_or_404(movie_id)
    m.genres = [g for g in m.genres if g.id != int(genre_id)]
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin_movie'))

@app.route('/admin/movies/<movie_id>/languages/<language_id>', methods=['POST'])
@login_required
def admin_movie_del_language(movie_id, language_id):
    if not current_user.admin:
        return redirect(url_for('index'))
    m = Movie.query.get_or_404(movie_id)
    m.languages = [l for l in m.languages if l.id != int(language_id)]
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin_movie'))

@app.route('/admin/movies', methods=['GET', 'POST'])
@login_required
def admin_movie():
    if not current_user.admin:
        return redirect(url_for('index'))
    page = request.args.get('page', default=1, type=int)
    movies = Movie.query\
        .with_entities(Movie.id, Movie.title, Movie.year, Movie.synopsis, Movie.timestamp,
            Movie.trailer_url, Actor.name.label('director'))\
        .outerjoin(Actor, Actor.id==Movie.director_id)\
        .order_by(Movie.title.asc())\
        .paginate(page, 4, False)
    form = MovieForm()
    add_actor = SelectionForm(obj=Actor)
    add_actor.select.choices = [(a.id, a.name) for a in Actor.query.order_by(Actor.name.asc())]
    add_genre = SelectionForm(obj=Genre)
    add_genre.select.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name.asc())]
    add_language = SelectionForm(obj=Language)
    add_language.select.choices = [(l.id, l.name) for l in Language.query.order_by(Language.name.asc())]
    delete_movie_form = DeleteSelectionForm(obj=Movie)
    delete_movie_form.select.choices = [(m.id, f'{m.title}, {m.year}') for m in movies.items]
    select_director_form = SelectSelectionForm(obj=Actor)
    select_director_form.select.choices = add_actor.select.choices
    if form.validate_on_submit():
        m = Movie(title=form.title.data, year=form.year.data, synopsis=form.synopsis.data)
        db.session.add(m)
        db.session.commit()
        flash('Movie added to db')
        return redirect(url_for('admin_movie'))
    links = construct_page_links('admin_movie', movies)
    return render_template('admin_movie.html', title='admin_movie',
        movies=movies.items, add_form=form, add_actor=add_actor, add_genre=add_genre,
        next_page=links[0] , prev_page=links[1] , first_page=links[2], last_page=links[3],
        add_language=add_language, current_page=movies.page, total_pages=movies.pages,
        del_form=DeleteForm(), del_movie_form=delete_movie_form, sel_director_form=select_director_form)

@app.route('/admin/movies/<id>/set_director', methods=['POST'])
@login_required
def admin_movie_set_director(id):
    if not current_user.admin:
        return redirect(url_for('index'))
    m = Movie.query.get_or_404(id)
    director = request.form['select']
    m.director_id = director
    db.session.commit()
    return redirect(url_for('admin_movie'))

@app.route('/admin/movies/<id>/editsynopsis', methods=['GET', 'POST'])
@login_required
def admin_movie_synopsis(id):
    if not current_user.admin:
        return redirect(url_for('index'))
    m = Movie.query.get_or_404(id)
    form = EditForm()
    if form.validate_on_submit():
        if form.editable.data:
            m.synopsis = form.editable.data
            db.session.commit()
        return redirect(url_for('admin_movie'))
    else:
        form.editable.data = m.synopsis if m.synopsis else ''
    return render_template('admin_edit.html', title='admin_edit',
        movie_title=m.title, movie_year=m.year, form=form, editable_name='synopsis')

@app.route('/admin/movies/<id>/set_trailer', methods=['GET', 'POST'])
@login_required
def admin_movie_trailer(id):
    if not current_user.admin:
        return redirect(url_for('index'))
    m = Movie.query.get_or_404(id)
    form = EditForm()
    if form.validate_on_submit():
        if form.editable.data:
            m.trailer_url = form.editable.data
            db.session.commit()
        return redirect(url_for('admin_movie'))
    else:
        form.editable.data = m.trailer_url if m.trailer_url else ''
    return render_template('admin_edit.html', title='admin_edit',
        movie_title=m.title, movie_year=m.year, form=form, editable_name='trailer\'s url')

@app.route('/admin/movies/delete', methods=['POST'])
@login_required
def admin_del_movie():
    if not current_user.admin:
        return redirect(url_for('index'))
    id = request.form.get('select')
    m = Movie.query.get_or_404(id)
    Review.query.filter_by(movie_id=m.id).delete()
    db.session.delete(m)
    db.session.commit()
    return redirect(url_for('admin_movie'))


@app.route('/admin/actors', methods=['GET', 'POST'])
@login_required
def admin_actor():
    if not current_user.admin:
        return redirect(url_for('index'))
    actors = Actor.query.order_by(Actor.name.asc()).all()
    form = ActorForm()
    if form.validate_on_submit():
        a = Actor(name=form.name.data)
        db.session.add(a)
        db.session.commit()
        flash('Actor added to db')
        return redirect(url_for('admin_actor'))
    return render_template('admin_movie_friend.html', title='admin_movie_friend',
        collection=actors, collection_name='actors', header='Actor', form=form)

@app.route('/admin/genres', methods=['GET', 'POST'])
@login_required
def admin_genre():
    if not current_user.admin:
        return redirect(url_for('index'))
    genres = Genre.query.order_by(Genre.name.asc()).all()
    form = GenreForm()
    if form.validate_on_submit():
        g = Genre(name=form.name.data)
        db.session.add(g)
        db.session.commit()
        flash('Genre added to db')
        return redirect(url_for('admin_genre'))
    return render_template('admin_movie_friend.html', title='admin_movie_friend',
        collection=genres, collection_name='genres', header='Genre', form=form)

@app.route('/admin/languages', methods=['GET', 'POST'])
@login_required
def admin_language():
    if not current_user.admin:
        return redirect(url_for('index'))
    languages = Language.query.order_by(Language.name.asc()).all()
    form = LanguageForm()
    if form.validate_on_submit():
        l = Language(name=form.name.data)
        db.session.add(l)
        db.session.commit()
        flash('Lang added to db')
        return redirect(url_for('admin_language'))
    return render_template('admin_movie_friend.html', title='admin_movie_friend',
        collection=languages, collection_name='languages', header='Language', form=form)


