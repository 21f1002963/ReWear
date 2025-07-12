# -*- encoding: utf-8 -*-
"""
Exchange model for ReWear platform
Handles item exchanges between users
"""

from datetime import datetime
from __init__ import db

class Exchange(db.Model):
    __tablename__ = 'exchanges'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Exchange participants
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Items involved in exchange
    requested_item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    offered_item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)  # Can be null for point-based exchanges
    
    # Exchange details
    exchange_type = db.Column(db.String(20), nullable=False, default='item')  # 'item' or 'points'
    points_offered = db.Column(db.Integer, nullable=True)  # For point-based exchanges
    message = db.Column(db.Text, nullable=True)  # Optional message from requester
    
    # Exchange status
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, accepted, rejected, completed, cancelled
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    requester = db.relationship('User', foreign_keys=[requester_id], backref='sent_exchanges')
    owner = db.relationship('User', foreign_keys=[owner_id], backref='received_exchanges')
    requested_item = db.relationship('Item', foreign_keys=[requested_item_id], backref='exchange_requests')
    offered_item = db.relationship('Item', foreign_keys=[offered_item_id], backref='exchange_offers')
    
    def __repr__(self):
        return f'<Exchange {self.id}: {self.requester.username} -> {self.owner.username} ({self.status})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'requester_id': self.requester_id,
            'owner_id': self.owner_id,
            'requested_item_id': self.requested_item_id,
            'offered_item_id': self.offered_item_id,
            'exchange_type': self.exchange_type,
            'points_offered': self.points_offered,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
