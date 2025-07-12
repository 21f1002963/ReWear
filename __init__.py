# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from importlib import import_module


db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Please log in to access this page.'

    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))

    # Handle unauthorized access
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import redirect, url_for, flash
        flash('Please log in to access this page.', 'info')
        return redirect(url_for('auth.login'))


def register_blueprints(app):
    # Import and register all blueprints
    try:
        # Register home/landing page blueprint
        from controllers import blueprint
        if blueprint:
            app.register_blueprint(blueprint)
            print("Home blueprint registered successfully")

        # Register auth blueprint
        from controllers.Auth import auth_bp
        app.register_blueprint(auth_bp)
        print("Auth blueprint registered successfully")

        # Register user blueprint
        from controllers.User import user_bp
        app.register_blueprint(user_bp)
        print("User blueprint registered successfully")

        # Register admin blueprint
        from controllers.Admin import admin_bp
        app.register_blueprint(admin_bp)
        print("Admin blueprint registered successfully")

    except ImportError as e:
        print(f"Error importing blueprint: {e}")
    except Exception as e:
        print(f"Error registering blueprint: {e}")


def configure_database(app):

    @app.before_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

            print('> Fallback to SQLite ')
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def create_app(config):
    # Set explicit paths for templates and static files
    basedir = os.path.abspath(os.path.dirname(__file__))
    template_folder = os.path.join(basedir, 'templates')
    static_folder = os.path.join(basedir, 'static')

    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder,
                static_url_path='/static')  # Explicitly set the URL path for static files
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
