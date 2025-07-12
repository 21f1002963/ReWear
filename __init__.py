# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module


db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = 'home_blueprint.home'  # Redirect to home page for now
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Please log in to access this page.'

    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        # For now, return None since we don't have User model yet
        # This will be updated when you add authentication
        return None
    
    # Handle unauthorized access
    @login_manager.unauthorized_handler
    def unauthorized():
        # For now, just redirect to home page instead of causing errors
        from flask import redirect, url_for, flash
        flash('Please log in to access this page.', 'info')
        return redirect(url_for('home_blueprint.home'))


def register_blueprints(app):
    # Import and register the home blueprint from Landing Page
    try:
        from controllers import blueprint
        if blueprint:
            app.register_blueprint(blueprint)
            print("Blueprint registered successfully")
        else:
            print("Blueprint is None - check controllers/__init__.py")
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
    static_folder = os.path.join(basedir, 'static_landing_site')

    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder,
                static_url_path='/static')  # Explicitly set the URL path for static files
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
