from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_talisman import Talisman
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import Config


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
csp = {
    'object-src': ['\'none\''],
    'default-src': [
        '\'self\'',
        'data:'
    ],
    'font-src': ['\'self\''],
    'script-src': [
        '\'unsafe-inline\'',
        'https:',
        '\'self\'',
    ],
    'base-uri': ['\'none\''],
    'child-src': [
        'https://youtube.com',
        'https://www.youtube.com',
    ],
}
talisman = Talisman(
    content_security_policy=csp,
    content_security_policy_nonce_in=['script-src'],
)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["2 per second"],
)
login = LoginManager()
login.login_view = 'login'

def init_app(conf_class=Config):
    app = Flask(__name__)
    app.config.from_object(conf_class)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    talisman.init_app(app)
    limiter.init_app(app)
    
    from app.error import bp as error_bp
    from app.admin import bp as admin_bp
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(error_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

from app import models
