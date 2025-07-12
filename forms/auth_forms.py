# -*- encoding: utf-8 -*-
"""
Authentication forms for ReWear platform
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from wtforms.widgets import TextArea
from models.user import User

class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email',
                       validators=[DataRequired(), Email()],
                       render_kw={"placeholder": "", "class": "form-control"})

    password = PasswordField('Password',
                            validators=[DataRequired()],
                            render_kw={"placeholder": "", "class": "form-control"})

    remember_me = BooleanField('Remember Me', render_kw={"class": "form-check-input"})

    def validate_email(self, email):
        """Custom validation for email during login"""
        # This will be used to check if user exists during login process
        pass

class RegisterForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username',
                          validators=[DataRequired(), Length(min=3, max=20)],
                          render_kw={"placeholder": "", "class": "form-control"})

    email = StringField('Email',
                       validators=[DataRequired(), Email()],
                       render_kw={"placeholder": "", "class": "form-control"})

    first_name = StringField('First Name',
                            validators=[DataRequired(), Length(min=2, max=50)],
                            render_kw={"placeholder": "", "class": "form-control"})

    last_name = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=50)],
                           render_kw={"placeholder": "", "class": "form-control"})

    phone_number = StringField('Phone Number',
                              validators=[Optional(), Length(max=20)],
                              render_kw={"placeholder": "Enter your phone number (optional)", "class": "form-control"})

    address = TextAreaField('Address',
                           validators=[Optional()],
                           render_kw={"placeholder": "Enter your address (optional)",
                                     "class": "form-control", "rows": 3})

    password = PasswordField('Password',
                            validators=[DataRequired(), Length(min=6)],
                            render_kw={"placeholder": "", "class": "form-control"})

    confirm_password = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password', message='Passwords must match')],
                                    render_kw={"placeholder": "Confirm your password", "class": "form-control"})

    def validate_username(self, username):
        """Check if username is already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email or login.')

class ProfileForm(FlaskForm):
    """Form for updating user profile"""
    first_name = StringField('First Name',
                            validators=[DataRequired(), Length(min=2, max=50)],
                            render_kw={"class": "form-control"})

    last_name = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=50)],
                           render_kw={"class": "form-control"})

    phone_number = StringField('Phone Number',
                              validators=[Optional(), Length(max=20)],
                              render_kw={"class": "form-control"})

    address = TextAreaField('Address',
                           validators=[Optional()],
                           render_kw={"class": "form-control", "rows": 3})

    bio = TextAreaField('Bio',
                       validators=[Optional(), Length(max=500)],
                       render_kw={"class": "form-control", "rows": 4,
                                 "placeholder": "Tell us about yourself..."})

class ChangePasswordForm(FlaskForm):
    """Form for changing password"""
    current_password = PasswordField('Current Password',
                                    validators=[DataRequired()],
                                    render_kw={"class": "form-control"})

    new_password = PasswordField('New Password',
                                validators=[DataRequired(), Length(min=6)],
                                render_kw={"class": "form-control"})

    confirm_new_password = PasswordField('Confirm New Password',
                                        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')],
                                        render_kw={"class": "form-control"})
