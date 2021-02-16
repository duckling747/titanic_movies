from flask import render_template
from app import db, app
from app.error import bp

@bp.app_errorhandler(403)
def unauthorized(_error):
    return render_template('403.html'), 403

@bp.app_errorhandler(404)
def not_found(_error):
    return render_template('404.html'), 404

@bp.app_errorhandler(413)
def not_found(_error):
    return render_template('413.html'), 413

@bp.app_errorhandler(500)
def internal_error(_error):
    db.session.rollback()
    return render_template('500.html'), 500
