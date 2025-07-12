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
import os
import uuid
from werkzeug.utils import secure_filename
from forms.item_forms import AddItemForm, EditItemForm

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

    # Get recent items (last 6 items) for display
    recent_items = Item.query.filter_by(user_id=current_user.id)\
                            .order_by(Item.created_at.desc())\
                            .limit(6).all()

    return render_template('user/user_dashboard.html', 
                         user_stats=user_stats, 
                         recent_items=recent_items)

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

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi', 'webm'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_media_file(file):
    """Save uploaded media file and return filename and type"""
    if file and allowed_file(file.filename):
        # Create unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Determine media type
        video_extensions = ['.mp4', '.mov', '.avi', '.webm']
        media_type = 'video' if any(unique_filename.lower().endswith(ext) for ext in video_extensions) else 'image'
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'uploads', 'items')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        return unique_filename, media_type
    return None, None

@user_bp.route('/add-item', methods=['GET', 'POST'])
@login_required
def add_item():
    """Add new item route"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    form = AddItemForm()

    if form.validate_on_submit():
        try:
            # Save media file
            media_filename = None
            media_type = None
            if form.media_file.data:
                media_filename, media_type = save_media_file(form.media_file.data)
            
            # Create new item
            new_item = Item(
                title=form.title.data,
                description=form.description.data,
                category=form.category.data,
                size=form.size.data,
                condition=form.condition.data,
                user_id=current_user.id,
                color=form.color.data,
                brand=form.brand.data,
                quantity=form.quantity.data,
                media_filename=media_filename,
                media_type=media_type
            )

            db.session.add(new_item)
            db.session.commit()
            flash('Item added successfully!', 'success')
            return redirect(url_for('user.uploaded_items'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding your item. Please try again.', 'error')
            print(f"Add item error: {e}")

    return render_template('user/add_item.html', form=form)

@user_bp.route('/edit-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    """Edit item route"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    form = EditItemForm()

    if form.validate_on_submit():
        try:
            # Save new media file if uploaded
            if form.media_file.data:
                # Delete old file if exists
                if item.media_filename:
                    old_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'uploads', 'items', item.media_filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                # Save new file
                item.media_filename, item.media_type = save_media_file(form.media_file.data)
            
            # Update item
            item.title = form.title.data
            item.description = form.description.data
            item.category = form.category.data
            item.size = form.size.data
            item.condition = form.condition.data
            item.color = form.color.data
            item.brand = form.brand.data
            item.quantity = form.quantity.data
            # Recalculate points when category or condition changes
            item.points_required = item.calculate_points()

            db.session.commit()
            flash('Item updated successfully!', 'success')
            return redirect(url_for('user.uploaded_items'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your item. Please try again.', 'error')
            print(f"Edit item error: {e}")

    # Pre-populate form with current item data
    if request.method == 'GET':
        form.title.data = item.title
        form.description.data = item.description
        form.category.data = item.category
        form.size.data = item.size
        form.condition.data = item.condition
        form.color.data = item.color
        form.brand.data = item.brand
        form.quantity.data = item.quantity

    return render_template('user/edit_item.html', form=form, item=item)

@user_bp.route('/delete-item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    """Delete item route"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    
    try:
        # Delete media file if exists
        if item.media_filename:
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'uploads', 'items', item.media_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete item from database
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting your item. Please try again.', 'error')
        print(f"Delete item error: {e}")

    return redirect(url_for('user.uploaded_items'))

@user_bp.route('/swap-history')
@login_required
def swap_history():
    """User swap history route"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    # For now, we'll show a placeholder since Swap model doesn't exist yet
    # When Swap model is created, this will show actual swap history
    swap_history_data = {
        'completed_swaps': [],  # Will be populated when Swap model exists
        'pending_swaps': [],    # Will be populated when Swap model exists
        'total_swaps': 0,
        'total_points_earned': current_user.points_balance,
        'total_points_spent': 0  # Will be calculated when Swap model exists
    }
    
    return render_template('user/user_swapHistory.html', swap_data=swap_history_data)
