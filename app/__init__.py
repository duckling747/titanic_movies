from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_talisman import Talisman
from flask_wtf import CSRFProtect

from .config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
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
    app,
    content_security_policy=csp,
    content_security_policy_nonce_in=['script-src'],
)

login = LoginManager(app)
login.login_view = 'login'

from app.error import bp as error_bp
from app.admin import bp as admin_bp
app.register_blueprint(error_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

from app import routes, models
