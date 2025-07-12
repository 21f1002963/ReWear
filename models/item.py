# -*- encoding: utf-8 -*-
"""
Item model for ReWear platform
"""

from datetime import datetime
import sys
import os

# Add the parent directory to sys.path to import from __init__
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from __init__ import db

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'shirt', 'pants', 'dress', 'shoes'
    size = db.Column(db.String(20), nullable=False)  # e.g., 'S', 'M', 'L', 'XL', '32', '34'
    condition = db.Column(db.String(20), nullable=False)  # e.g., 'excellent', 'good', 'fair'
    color = db.Column(db.String(30), nullable=True)
    brand = db.Column(db.String(50), nullable=True)
    
    # Item status
    status = db.Column(db.String(20), default='available', nullable=False)  # 'available', 'pending', 'exchanged', 'removed'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Point system
    points_required = db.Column(db.Integer, default=10, nullable=False)
    
    # Image storage
    image_filename = db.Column(db.String(100), nullable=True)  # Store filename only
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('items', lazy=True, cascade='all, delete-orphan'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, title, description, category, size, condition, user_id, **kwargs):
        self.title = title
        self.description = description
        self.category = category
        self.size = size
        self.condition = condition
        self.user_id = user_id
        self.color = kwargs.get('color')
        self.brand = kwargs.get('brand')
        self.points_required = kwargs.get('points_required', 10)
        self.image_filename = kwargs.get('image_filename')

    def get_image_url(self):
        """Get the full URL path for the item image"""
        if self.image_filename:
            return f'/static/uploads/items/{self.image_filename}'
        return '/static/img/default-item.jpg'  # Default placeholder image

    def to_dict(self):
        """Convert item object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'size': self.size,
            'condition': self.condition,
            'color': self.color,
            'brand': self.brand,
            'status': self.status,
            'is_active': self.is_active,
            'points_required': self.points_required,
            'image_url': self.get_image_url(),
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Item {self.title} by {self.user.username if self.user else "Unknown"}>'
