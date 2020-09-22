from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt

from flask_login import LoginManager

from flask_admin import Admin

from flask_mail import Mail
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'd8d24f46468cc1e73e5baa4e98d997c4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category = 'info'
mail = Mail(app)
admin=Admin(app)
from flaskblog import routes

