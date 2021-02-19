from flask import (
    render_template,
    redirect,
    flash,
    url_for,
    request,
    abort,
    send_from_directory,
    current_app,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
)
from sqlalchemy.sql import (
    func,
    desc
)
from app import db
from app.main import bp
from app.models import (
    User,
    Movie,
    Review,
    MovieRequest,
)
from app.forms import (
    LoginForm,
    RegistrationForm,
    ReviewForm,
    ProfileImageForm,
    ChangePasswordForm,
    RequestForm,
)
from app.query_utils import construct_page_links
from datetime import datetime
import imghdr
import os


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    top_graded = Movie.query.join(Review)\
        .with_entities(Movie.title, Movie.year, Movie.id, func.round(func.avg(Review.grade), 2)\
        .label('avg'))\
        .group_by(Movie.id).order_by(desc('avg')).limit(10).all()
    newbies = Movie.query.order_by(Movie.timestamp.desc()).limit(10).all()
    form = RequestForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        movreq = MovieRequest(user_id=current_user.id,
            name=form.name.data, year=form.year.data,
            other_info=form.other_info.data)
        db.session.add(movreq)
        db.session.commit()
        flash('Request sent!')
        return redirect(url_for('main.index'))
    return render_template('index.html', title='home',
        top_graded=top_graded, newbies=newbies, form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data)\
            or user.disabled:
            flash('invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    return render_template('login.html', title='login', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@bp.route('/profile/<id>/images', defaults={'img': ''}, methods=['GET', 'POST'])
@bp.route('/profile/<id>/images/<img>', methods=['GET', 'POST'])
@login_required
def image(id, img):
    user = User.query.get_or_404(id)
    profile_pic_form = ProfileImageForm()
    if profile_pic_form.validate_on_submit() and int(id) == current_user.id:
        image_file = profile_pic_form.file.data
        filename = image_file.filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or\
                file_ext != validate_image(image_file.stream):
                return render_template('400.html'), 400
            filename = id + '.' + datetime.now().strftime('%Y%m%d%H%M%S%f')
            user.image = filename
            db.session.add(user)
            db.session.commit()
            image_file.save(os.path.join(current_app.config['UPLOAD_PATH'], filename))
            return redirect(url_for('main.profile'))
        return '', 204
    path = current_app.config['UPLOAD_PATH']
    if img and os.path.isfile(os.path.join(path, img)):
        return send_from_directory(path, img)
    else:
        return send_from_directory(current_app.config['IMAGES_PATH'], 'cactus.jpg')

@bp.route('/profile', methods=['GET', 'POST'])
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
            return redirect(url_for('main.profile'))
        else:
            change_pw_form.oldpassword.errors.append('Incorrect old password')
    links = construct_page_links('main.profile', reviews)
    return render_template('profile.html', title='profile',
        current_page=reviews.page, total_pages=reviews.pages,
        next_page=links[0], prev_page=links[1] , first_page=links[2], last_page=links[3],
        change_pw_form=change_pw_form, profile_pic_form=profile_pic_form, reviews=reviews.items)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registered succesfully')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='register', form=form)

@bp.route('/browse')
def browse():
    movies = Movie.query.order_by(Movie.title.asc()).all()
    return render_template('browse.html', title='browse', movies=movies)

@bp.route('/movies/<id>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.movie_details', id=id))
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
        return abort(404)
    return reviews

@bp.route('/movies/<id>/reviews')
@login_required
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

    links = construct_page_links('main.reviews', reviews, **{ 'id': id, 'min_grade': min_grade,
        'max_grade': max_grade, 'min_date': min_date, 'max_date': max_date,
        'sort_by': sort_by, 'textcontains': textcontains })

    return render_template('movie_reviews.html', title='reviews',
        min_grade=min_grade, max_grade=max_grade, min_date=min_date, max_date=max_date,
        sort_by=sort_by, textcontains=textcontains, current_page=reviews.page, total_pages=reviews.pages,
        next_page=links[0] , prev_page=links[1] , first_page=links[2], last_page=links[3],
        movie=m, reviews=reviews.items)

@bp.route('/testing')
def testme_create_admin():
    if os.environ.get('FLASK_ENV') == 'production':
        return render_template('404.html'), 404
    name = 'testadmin'
    u = User.query\
        .filter_by(username=name)\
        .first()
    if u is None:
        u = User(username=name, admin=True)
        u.set_password('salainen')
        db.session.add(u)
        db.session.commit()
    return '', 200
