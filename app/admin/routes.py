from flask import (
    render_template,
    redirect,
    flash,
    url_for,
    request,
    abort,
)
from flask_login import (
    current_user,
    login_required,
)
from sqlalchemy.orm import joinedload
from app import db
from app.admin import bp
from app.models import (
    User,
    Movie,
    Actor,
    Review,
    Genre,
    Language,
)
from app.forms import (
    MovieForm,
    AdminRegistrationForm,
    ActorForm,
    GenreForm,
    SelectionForm,
    DeleteForm,
    DeleteSelectionForm,
    DisableSelectionForm,
    EnableSelectionForm,
    LanguageForm,
    EditForm,
    SelectSelectionForm,
)
from app.query_utils import construct_page_links

@bp.before_request
def before_request():
    if not current_user.admin:
        return render_template('403.html'), 403

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', default=1, type=int)
    reviews = Review.query\
        .with_entities(Movie.title, Movie.year, Review.id, Review.grade,
            Review.thoughts, Review.feelings, Review.timestamp, User.username)\
        .join(Movie)\
        .join(User).order_by(Movie.title.asc())\
        .paginate(page, 5, False)
    links = construct_page_links('admin.index', reviews)
    return render_template('admin.html', title='admin', current_page=reviews.page,
        total_pages=reviews.pages,
        next_page=links[0] , prev_page=links[1] , first_page=links[2], last_page=links[3],
        reviews=reviews.items, del_form=DeleteForm())

@bp.route('/reviews/<id>', methods=['POST'])
@login_required
def review_del(id):
    r = Review.query.get(id)
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for('admin.index'))


@bp.route('/users/toggle_enabled_status', methods=['POST'])
@login_required
def toggle_status_user():
    id = request.form.get('select')
    u = User.query.get_or_404(id)
    u.disabled = not u.disabled
    db.session.add(u)
    db.session.commit()
    return redirect(url_for('admin.user'))

@bp.route('/users', methods=['GET', 'POST'])
@login_required
def user():
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
        return redirect(url_for('admin.user'))
    return render_template('admin_user.html', title='admin.user',
        users=users, form=form, disable_form=disable_form,
        enable_form=enable_form)

@bp.route('/movies/<id>/actors', methods=['POST'])
@login_required
def movie_add_actor(id):
    actor = request.form['select']
    m = Movie.query.get_or_404(id)
    actor = Actor.query.get(actor)
    m.actors.append(actor)
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin.movie'))

@bp.route('/movies/<id>/genres', methods=['POST'])
@login_required
def movie_add_genre(id):
    genre = request.form['select']
    m = Movie.query.get_or_404(id)
    genre = Genre.query.get(genre)
    m.genres.append(genre)
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin.movie'))

@bp.route('/movies/<id>/languages', methods=['POST'])
@login_required
def movie_add_language(id):
    language = request.form['select']
    m = Movie.query.get_or_404(id)
    language = Language.query.get(language)
    m.languages.append(language)
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin.movie'))

@bp.route('/movies/<movie_id>/actors/<actor_id>', methods=['POST'])
@login_required
def movie_del_actor(movie_id, actor_id):
    m = Movie.query.get_or_404(movie_id)
    m.actors = [a for a in m.actors if a.id != int(actor_id)]
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin.movie'))

@bp.route('/movies/<movie_id>/genres/<genre_id>', methods=['POST'])
@login_required
def movie_del_genre(movie_id, genre_id):
    m = Movie.query.get_or_404(movie_id)
    m.genres = [g for g in m.genres if g.id != int(genre_id)]
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin.movie'))

@bp.route('/movies/<movie_id>/languages/<language_id>', methods=['POST'])
@login_required
def movie_del_language(movie_id, language_id):
    m = Movie.query.get_or_404(movie_id)
    m.languages = [l for l in m.languages if l.id != int(language_id)]
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('admin.movie'))

@bp.route('/movies', methods=['GET', 'POST'])
@login_required
def movie():
    page = request.args.get('page', default=1, type=int)
    movies = Movie.query\
        .options(joinedload('actors'), joinedload('genres'), joinedload('languages'))\
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
        return redirect(url_for('admin.movie'))
    links = construct_page_links('admin.movie', movies)
    return render_template('admin_movie.html', title='admin.movie',
        movies=movies.items, add_form=form, add_actor=add_actor, add_genre=add_genre,
        next_page=links[0] , prev_page=links[1] , first_page=links[2], last_page=links[3],
        add_language=add_language, current_page=movies.page, total_pages=movies.pages,
        del_form=DeleteForm(), del_movie_form=delete_movie_form, sel_director_form=select_director_form)

@bp.route('/movies/<id>/set_director', methods=['POST'])
@login_required
def movie_set_director(id):
    m = Movie.query.get_or_404(id)
    director = request.form['select']
    m.director_id = director
    db.session.commit()
    return redirect(url_for('admin.movie'))

@bp.route('/movies/<id>/editsynopsis', methods=['GET', 'POST'])
@login_required
def movie_synopsis(id):
    m = Movie.query.get_or_404(id)
    form = EditForm()
    if form.validate_on_submit():
        if form.editable.data:
            m.synopsis = form.editable.data
            db.session.commit()
        return redirect(url_for('admin.movie'))
    else:
        form.editable.data = m.synopsis if m.synopsis else ''
    return render_template('admin_edit.html', title='admin.edit',
        movie_title=m.title, movie_year=m.year, form=form, editable_name='synopsis')

@bp.route('/movies/<id>/set_trailer', methods=['GET', 'POST'])
@login_required
def movie_trailer(id):
    m = Movie.query.get_or_404(id)
    form = EditForm()
    if form.validate_on_submit():
        if form.editable.data:
            m.trailer_url = form.editable.data
            db.session.commit()
        return redirect(url_for('admin.movie'))
    else:
        form.editable.data = m.trailer_url if m.trailer_url else ''
    return render_template('admin_edit.html', title='admin.edit',
        movie_title=m.title, movie_year=m.year, form=form, editable_name='trailer\'s url')

@bp.route('/movies/delete', methods=['POST'])
@login_required
def del_movie():
    id = request.form.get('select')
    m = Movie.query.get_or_404(id)
    Review.query.filter_by(movie_id=m.id).delete()
    db.session.delete(m)
    db.session.commit()
    return redirect(url_for('admin.movie'))


@bp.route('/actors', methods=['GET', 'POST'])
@login_required
def actor():
    actors = Actor.query.order_by(Actor.name.asc()).all()
    form = ActorForm()
    if form.validate_on_submit():
        a = Actor(name=form.name.data)
        db.session.add(a)
        db.session.commit()
        flash('Actor added to db')
        return redirect(url_for('admin.actor'))
    return render_template('admin_movie_friend.html', title='admin.movie_friend',
        collection=actors, collection_name='actors', header='Actor', form=form)

@bp.route('/genres', methods=['GET', 'POST'])
@login_required
def genre():
    genres = Genre.query.order_by(Genre.name.asc()).all()
    form = GenreForm()
    if form.validate_on_submit():
        g = Genre(name=form.name.data)
        db.session.add(g)
        db.session.commit()
        flash('Genre added to db')
        return redirect(url_for('admin.genre'))
    return render_template('admin_movie_friend.html', title='admin.movie_friend',
        collection=genres, collection_name='genres', header='Genre', form=form)

@bp.route('/languages', methods=['GET', 'POST'])
@login_required
def language():
    languages = Language.query.order_by(Language.name.asc()).all()
    form = LanguageForm()
    if form.validate_on_submit():
        l = Language(name=form.name.data)
        db.session.add(l)
        db.session.commit()
        flash('Lang added to db')
        return redirect(url_for('admin.language'))
    return render_template('admin_movie_friend.html', title='admin.movie_friend',
        collection=languages, collection_name='languages', header='Language', form=form)

