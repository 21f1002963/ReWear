# -*- encoding: utf-8 -*-
"""
User dashboard routes for ReWear platform
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from __init__ import db
from models.user import User

# Create the user blueprint
user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard route"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    # Get user statistics (placeholder for now)
    user_stats = {
        'total_items_listed': 0,  # Will be updated when Item model is added
        'total_swaps_completed': 0,  # Will be updated when Swap model is added
        'total_points_earned': current_user.points_balance,
        'items_available': 0,  # Will be updated when Item model is added
    }

    return render_template('user/user_dashboard.html', user_stats=user_stats)

@user_bp.route('/profile')
@login_required
def profile():
    """Redirect to auth profile route"""
    return redirect(url_for('auth.profile'))
