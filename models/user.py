# -*- encoding: utf-8 -*-
"""
User model for ReWear platform
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sys
import os

# Add the parent directory to sys.path to import from __init__
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    # Profile information
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    bio = db.Column(db.Text, nullable=True)

    # Point system for clothing exchange
    points_balance = db.Column(db.Integer, default=100, nullable=False)  # Starting points

    # User status and roles
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def __init__(self, username, email, password, first_name, last_name, **kwargs):
        self.username = username
        self.email = email.lower()
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = kwargs.get('phone_number')
        self.address = kwargs.get('address')
        self.bio = kwargs.get('bio')

    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches the stored hash"""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}"

    def add_points(self, points):
        """Add points to user's balance"""
        self.points_balance += points
        db.session.commit()

    def deduct_points(self, points):
        """Deduct points from user's balance if sufficient"""
        if self.points_balance >= points:
            self.points_balance -= points
            db.session.commit()
            return True
        return False

    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'address': self.address,
            'bio': self.bio,
            'points_balance': self.points_balance,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
