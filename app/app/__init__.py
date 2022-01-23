from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///passmgr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
# login_manager.session_protection = 'strong'
from app.db_models import User, SavedPassword, SecretPart
db.create_all()

from app import routes