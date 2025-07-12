# -*- encoding: utf-8 -*-
"""
User dashboard routes for ReWear platform
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from __init__ import db
from models.user import User
from models.item import Item
from forms.auth_forms import ProfileForm

# Create the user blueprint
user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard route"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    # Get user statistics with real data
    user_stats = {
        'total_items_listed': Item.query.filter_by(user_id=current_user.id).count(),
        'total_swaps_completed': 0,  # Will be updated when Swap model is added
        'total_points_earned': current_user.points_balance,
        'items_available': Item.query.filter_by(user_id=current_user.id, status='available').count(),
    }

    return render_template('user/user_dashboard.html', user_stats=user_stats)

@user_bp.route('/profile')
@login_required
def profile():
    """Redirect to auth profile route"""
    return redirect(url_for('auth.profile'))

@user_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """User edit profile route"""
    if current_user.is_admin:
        return redirect(url_for('admin.edit_profile'))

    form = ProfileForm()

    if form.validate_on_submit():
        try:
            # Update user profile
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.phone_number = form.phone_number.data
            current_user.address = form.address.data

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('user.edit_profile'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'error')
            print(f"User profile update error: {e}")

    # Pre-populate form with current user data
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.phone_number.data = current_user.phone_number
    form.address.data = current_user.address

    return render_template('user/user_editprofile.html', form=form)

@user_bp.route('/uploaded-items')
@login_required
def uploaded_items():
    """User uploaded items route"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    # Get user's uploaded items
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Show 12 items per page
    
    items = Item.query.filter_by(user_id=current_user.id).order_by(Item.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Get statistics for user's items
    item_stats = {
        'total_items': Item.query.filter_by(user_id=current_user.id).count(),
        'available_items': Item.query.filter_by(user_id=current_user.id, status='available').count(),
        'pending_items': Item.query.filter_by(user_id=current_user.id, status='pending').count(),
        'exchanged_items': Item.query.filter_by(user_id=current_user.id, status='exchanged').count(),
    }

    return render_template('user/user_uploadedItems.html', items=items, item_stats=item_stats)
