# -*- encoding: utf-8 -*-
"""
Admin dashboard routes for ReWear platform
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from __init__ import db
from models.user import User
from models.item import Item
from forms.auth_forms import ProfileForm
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify

# Create the admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard route"""
    # Get platform statistics (excluding admin users)
    total_users = User.query.filter_by(is_admin=False).count()
    active_users = User.query.filter_by(is_active=True, is_admin=False).count()
    new_users_today = User.query.filter(
        User.created_at >= db.func.date('now'), 
        User.is_admin == False
    ).count()

    admin_stats = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': total_users - active_users,
        'new_users_today': new_users_today,
        'total_items': Item.query.count(),
        'pending_items': Item.query.filter_by(status='pending').count(),
        'available_items': Item.query.filter_by(status='available').count(),
        'total_swaps': 0,  # Will be updated when Swap model is added
    }

    # Get recent users (excluding admin users)
    recent_users = User.query.filter_by(is_admin=False)\
                            .order_by(User.created_at.desc())\
                            .limit(5).all()

    return render_template('admin/admin_dashboard.html',
                         admin_stats=admin_stats,
                         recent_users=recent_users)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users route"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    # Filter out admin users from the query
    query = User.query.filter_by(is_admin=False)

    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.first_name.contains(search)) |
            (User.last_name.contains(search))
        )

    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template('admin/admin_manageUsers.html', users=users, search=search)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin.manage_users'))

    try:
        user.is_active = not user.is_active
        db.session.commit()

        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.username} has been {status}.', 'success')

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating user status.', 'error')
        print(f"User status update error: {e}")

    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<int:user_id>/make-admin', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    """Make user an admin"""
    user = User.query.get_or_404(user_id)

    try:
        user.is_admin = True
        db.session.commit()
        flash(f'User {user.username} has been made an admin.', 'success')

    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating user privileges.', 'error')
        print(f"Admin privilege update error: {e}")

    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile():
    """Admin edit profile route"""
    form = ProfileForm()

    if form.validate_on_submit():
        try:
            # Update admin profile
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.phone_number = form.phone_number.data
            current_user.address = form.address.data

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('admin.edit_profile'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile.', 'error')
            print(f"Admin profile update error: {e}")

    # Pre-populate form with current user data
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.phone_number.data = current_user.phone_number
    form.address.data = current_user.address

    return render_template('admin/admin_editprofile.html', form=form)

@admin_bp.route('/items')
@login_required
@admin_required
def view_items():
    """View all items route"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category_filter = request.args.get('category', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    moderation_filter = request.args.get('moderation', '', type=str)

    query = Item.query.join(User, Item.user_id == User.id)

    # Apply search filter
    if search:
        query = query.filter(
            (Item.title.contains(search)) |
            (Item.description.contains(search)) |
            (Item.category.contains(search)) |
            (Item.brand.contains(search)) |
            (User.username.contains(search))
        )

    # Apply category filter
    if category_filter:
        query = query.filter(Item.category == category_filter)

    # Apply status filter
    if status_filter:
        query = query.filter(Item.status == status_filter)
    
    # Apply moderation filter
    if moderation_filter:
        query = query.filter(Item.moderation_status == moderation_filter)

    items = query.order_by(Item.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    # Get unique categories for filter dropdown
    categories = db.session.query(Item.category.distinct()).all()
    categories = [cat[0] for cat in categories if cat[0]]

    # Get item statistics
    item_stats = {
        'total_items': Item.query.count(),
        'available_items': Item.query.filter_by(status='available').count(),
        'pending_items': Item.query.filter_by(status='pending').count(),
        'sold_items': Item.query.filter_by(status='sold').count(),
        'pending_moderation': Item.query.filter_by(moderation_status='pending').count(),
        'approved_items': Item.query.filter_by(moderation_status='approved').count(),
        'rejected_items': Item.query.filter_by(moderation_status='rejected').count(),
    }

    return render_template('admin/admin_viewItems.html', 
                         items=items, 
                         search=search,
                         category_filter=category_filter,
                         status_filter=status_filter,
                         moderation_filter=moderation_filter,
                         categories=categories,
                         item_stats=item_stats)

@admin_bp.route('/moderate_item/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def moderate_item(item_id):
    """Moderate an item (approve, reject, or remove)"""
    try:
        item = Item.query.get_or_404(item_id)
        action = request.json.get('action')
        notes = request.json.get('notes', '')
        
        if action not in ['approve', 'reject', 'remove']:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
        
        # Update item moderation status
        if action == 'approve':
            item.moderation_status = 'approved'
            item.is_active = True
            message = 'Item approved successfully'
        elif action == 'reject':
            item.moderation_status = 'rejected'
            item.is_active = False
            message = 'Item rejected successfully'
        elif action == 'remove':
            item.moderation_status = 'rejected'
            item.is_active = False
            item.status = 'removed'
            message = 'Item removed successfully'
        
        # Update moderation fields
        item.moderation_notes = notes
        item.moderated_by = current_user.id
        item.moderated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': message,
            'new_status': item.moderation_status
        })
        
    except Exception as e:
        current_app.logger.error(f"Error moderating item {item_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@admin_bp.route('/bulk_moderate', methods=['POST'])
@login_required
@admin_required
def bulk_moderate():
    """Bulk moderate multiple items"""
    try:
        item_ids = request.json.get('item_ids', [])
        action = request.json.get('action')
        notes = request.json.get('notes', '')
        
        if not item_ids or action not in ['approve', 'reject', 'remove']:
            return jsonify({'success': False, 'message': 'Invalid request'}), 400
        
        items = Item.query.filter(Item.id.in_(item_ids)).all()
        success_count = 0
        
        for item in items:
            if action == 'approve':
                item.moderation_status = 'approved'
                item.is_active = True
            elif action == 'reject':
                item.moderation_status = 'rejected'
                item.is_active = False
            elif action == 'remove':
                item.moderation_status = 'rejected'
                item.is_active = False
                item.status = 'removed'
            
            item.moderation_notes = notes
            item.moderated_by = current_user.id
            item.moderated_at = datetime.utcnow()
            success_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{success_count} items {action}d successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error bulk moderating items: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred'}), 500
