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

    # Item details
    quantity = db.Column(db.Integer, default=1, nullable=False)

    # Item status
    status = db.Column(db.String(20), default='available', nullable=False)  # 'available', 'pending', 'exchanged', 'removed'
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Moderation fields
    moderation_status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'approved', 'rejected'
    moderation_notes = db.Column(db.Text, nullable=True)  # Admin notes for rejection or approval
    moderated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Admin who moderated
    moderated_at = db.Column(db.DateTime, nullable=True)  # When moderation occurred

    # Point system - calculated based on category
    points_required = db.Column(db.Integer, nullable=False)

    # Media storage
    media_filename = db.Column(db.String(100), nullable=True)  # Store filename only
    media_type = db.Column(db.String(10), nullable=True)  # 'image' or 'video'

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('items', lazy=True, cascade='all, delete-orphan'))
    moderator = db.relationship('User', foreign_keys=[moderated_by], backref=db.backref('moderated_items', lazy=True))

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
        self.quantity = kwargs.get('quantity', 1)
        self.points_required = self.calculate_points()
        self.media_filename = kwargs.get('media_filename')
        self.media_type = kwargs.get('media_type')
        # Set default moderation status to pending for new items
        self.moderation_status = kwargs.get('moderation_status', 'pending')

    def calculate_points(self):
        """Calculate points based on category and condition"""
        # Base points by category
        category_points = {
            'tops': 8,
            'bottoms': 10,
            'dresses': 15,
            'outerwear': 20,
            'shoes': 12,
            'accessories': 5,
            'activewear': 12,
            'formal': 18,
            'casual': 8,
            'vintage': 25,
            'other': 6
        }

        # Condition multipliers
        condition_multipliers = {
            'excellent': 1.0,
            'good': 0.8,
            'fair': 0.6,
            'poor': 0.4
        }

        base_points = category_points.get(self.category, 6)
        multiplier = condition_multipliers.get(self.condition, 0.8)

        return max(1, int(base_points * multiplier))

    def get_media_url(self):
        """Get the full URL path for the item media"""
        if self.media_filename:
            return f'/static/uploads/items/{self.media_filename}'
        return '/static/img/default-item.jpg'  # Default placeholder image

    def is_video(self):
        """Check if the media file is a video"""
        if self.media_filename:
            video_extensions = ['.mp4', '.mov', '.avi', '.webm']
            return any(self.media_filename.lower().endswith(ext) for ext in video_extensions)
        return False

    def is_image(self):
        """Check if the media file is an image"""
        if self.media_filename:
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            return any(self.media_filename.lower().endswith(ext) for ext in image_extensions)
        return False

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
            'quantity': self.quantity,
            'media_url': self.get_media_url(),
            'media_type': self.media_type,
            'is_video': self.is_video(),
            'is_image': self.is_image(),
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Item {self.title} by {self.user.username if self.user else "Unknown"}>'
