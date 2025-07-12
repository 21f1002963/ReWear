# -*- encoding: utf-8 -*-
"""
Authentication routes for ReWear platform
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from __init__ import db
from models.user import User
from forms.auth_forms import LoginForm, RegisterForm, ProfileForm, ChangePasswordForm

# Create the auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        # Redirect based on user role
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('accounts/login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            user.update_last_login()

            flash(f'Welcome back, {user.first_name}!', 'success')

            # Handle next parameter for redirecting after login
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                if user.is_admin:
                    next_page = url_for('admin.dashboard')
                else:
                    next_page = url_for('user.dashboard')

            return redirect(next_page)
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('accounts/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Check if username or email already exists
            existing_user = User.query.filter(
                (User.username == form.username.data) |
                (User.email == form.email.data.lower())
            ).first()

            if existing_user:
                if existing_user.username == form.username.data:
                    flash('Username already taken. Please choose a different one.', 'error')
                else:
                    flash('Email already registered. Please use a different email.', 'error')
                return render_template('accounts/register.html', form=form)

            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone_number=form.phone_number.data,
                address=form.address.data
            )

            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Welcome to ReWear!', 'success')
            login_user(user)

            return redirect(url_for('user.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            print(f"Registration error: {e}")

    return render_template('accounts/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home_blueprint.home'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management route"""
    form = ProfileForm()

    if form.validate_on_submit():
        try:
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.phone_number = form.phone_number.data
            current_user.address = form.address.data
            current_user.bio = form.bio.data

            db.session.commit()
            flash('Profile updated successfully!', 'success')

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'error')
            print(f"Profile update error: {e}")

    # Pre-populate form with current user data
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone_number.data = current_user.phone_number
        form.address.data = current_user.address
        form.bio.data = current_user.bio

    return render_template('accounts/profile.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route"""
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            try:
                current_user.set_password(form.new_password.data)
                db.session.commit()
                flash('Password changed successfully!', 'success')
                return redirect(url_for('auth.profile'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while changing your password.', 'error')
                print(f"Password change error: {e}")
        else:
            flash('Current password is incorrect.', 'error')

    return render_template('accounts/change_password.html', form=form)
