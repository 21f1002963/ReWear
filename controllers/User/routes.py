# -*- encoding: utf-8 -*-
"""
User dashboard routes for ReWear platform
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from __init__ import db
from models.user import User
from models.item import Item
from models.exchange import Exchange
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
    completed_exchanges_count = Exchange.query.filter(
        db.or_(Exchange.requester_id == current_user.id, Exchange.owner_id == current_user.id),
        Exchange.status.in_(['completed', 'accepted'])
    ).count()

    user_stats = {
        'total_items_listed': Item.query.filter_by(user_id=current_user.id).count(),
        'total_swaps_completed': completed_exchanges_count,
        'total_points_earned': current_user.points_balance,
        'items_available': Item.query.filter_by(user_id=current_user.id, status='available').count(),
        'items_pending_review': Item.query.filter_by(user_id=current_user.id, moderation_status='pending').count(),
        'items_approved': Item.query.filter_by(user_id=current_user.id, moderation_status='approved').count(),
    }

    # Get recent items (last 6 items) for display - show all items to owner
    recent_items = Item.query.filter_by(user_id=current_user.id)\
                            .order_by(Item.created_at.desc())\
                            .limit(6).all()

    # Get pending exchange requests count (requests received by this user)
    pending_requests_count = Exchange.query.filter_by(
        owner_id=current_user.id,
        status='pending'
    ).count()

    return render_template('user/user_dashboard.html',
                         user_stats=user_stats,
                         recent_items=recent_items,
                         pending_requests_count=pending_requests_count)

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

    # Get completed exchanges (swaps) for the current user
    completed_exchanges = Exchange.query.filter(
        db.or_(Exchange.requester_id == current_user.id, Exchange.owner_id == current_user.id),
        Exchange.status.in_(['completed', 'accepted'])
    ).order_by(Exchange.completed_at.desc(), Exchange.updated_at.desc()).all()

    # Get pending exchanges
    pending_exchanges = Exchange.query.filter(
        db.or_(Exchange.requester_id == current_user.id, Exchange.owner_id == current_user.id),
        Exchange.status == 'pending'
    ).order_by(Exchange.created_at.desc()).all()

    # Calculate statistics
    total_swaps = len(completed_exchanges)
    total_points_earned = 0
    total_points_spent = 0

    for exchange in completed_exchanges:
        if exchange.exchange_type == 'points':
            if exchange.owner_id == current_user.id:
                # User received points
                total_points_earned += exchange.points_offered
            elif exchange.requester_id == current_user.id:
                # User spent points
                total_points_spent += exchange.points_offered

    swap_history_data = {
        'completed_swaps': completed_exchanges,
        'pending_swaps': pending_exchanges,
        'total_swaps': total_swaps,
        'total_points_earned': total_points_earned,
        'total_points_spent': total_points_spent
    }

    return render_template('user/user_swapHistory.html', swap_data=swap_history_data)

@user_bp.route('/browse')
@user_bp.route('/browse/<category>')
@login_required
def browse_items(category=None):
    """Browse all available items, optionally filtered by category"""
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Show 12 items per page
    search = request.args.get('search', '', type=str)

    # Base query for approved items only, excluding current user's items
    query = Item.query.filter(
        Item.moderation_status == 'approved',
        Item.status == 'available',
        Item.user_id != current_user.id
    )

    # Apply category filter if specified
    if category:
        query = query.filter(Item.category == category)

    # Apply search filter if specified
    if search:
        query = query.filter(
            Item.title.contains(search) |
            Item.description.contains(search) |
            Item.brand.contains(search)
        )

    # Get paginated results
    items = query.order_by(Item.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Check for pending exchange requests for each item
    pending_requests = {}
    for item in items.items:
        existing_request = Exchange.query.filter_by(
            requester_id=current_user.id,
            requested_item_id=item.id,
            status='pending'
        ).first()
        pending_requests[item.id] = existing_request is not None

    # Get category counts for sidebar
    category_counts = {}
    categories = ['tops', 'bottoms', 'dresses', 'outerwear', 'shoes', 'accessories',
                 'activewear', 'formal', 'casual', 'vintage', 'other']

    for cat in categories:
        count = Item.query.filter(
            Item.moderation_status == 'approved',
            Item.status == 'available',
            Item.user_id != current_user.id,
            Item.category == cat
        ).count()
        category_counts[cat] = count

    # Category display names mapping
    category_names = {
        'tops': 'Tops & Shirts',
        'bottoms': 'Bottoms',
        'dresses': 'Dresses',
        'outerwear': 'Outerwear',
        'shoes': 'Footwear',
        'accessories': 'Accessories',
        'activewear': 'Activewear',
        'formal': 'Formal Wear',
        'casual': 'Casual Wear',
        'vintage': 'Vintage',
        'other': 'Other'
    }

    return render_template('user/browse_items.html',
                         items=items,
                         current_category=category,
                         category_counts=category_counts,
                         category_names=category_names,
                         search=search,
                         pending_requests=pending_requests)

# ===============================
# EXCHANGE ROUTES
# ===============================

@user_bp.route('/request_exchange/<int:item_id>', methods=['POST'])
@login_required
def request_exchange(item_id):
    """Request an exchange for an item"""
    item = Item.query.get_or_404(item_id)

    # Prevent users from requesting their own items
    if item.user_id == current_user.id:
        return jsonify({'error': 'You cannot request exchange for your own item'}), 400

    # Check if item is available and approved
    if item.status != 'available' or item.moderation_status != 'approved':
        return jsonify({'error': 'This item is not available for exchange'}), 400

    # Check if exchange request already exists
    existing_request = Exchange.query.filter_by(
        requester_id=current_user.id,
        requested_item_id=item_id,
        status='pending'
    ).first()

    if existing_request:
        return jsonify({'error': 'You already have a pending request for this item'}), 400

    # Get form data
    exchange_type = request.json.get('exchange_type', 'points')
    offered_item_id = request.json.get('offered_item_id')
    points_offered = request.json.get('points_offered')
    message = request.json.get('message', '')

    # Validate exchange type
    if exchange_type == 'item':
        if not offered_item_id:
            return jsonify({'error': 'Please select an item to offer'}), 400

        offered_item = Item.query.get(offered_item_id)
        if not offered_item or offered_item.user_id != current_user.id:
            return jsonify({'error': 'Invalid offered item'}), 400

        if offered_item.status != 'available':
            return jsonify({'error': 'The offered item is not available'}), 400

    elif exchange_type == 'points':
        if not points_offered or points_offered <= 0:
            return jsonify({'error': 'Please specify valid points to offer'}), 400

        if current_user.points_balance < points_offered:
            return jsonify({'error': 'Insufficient points balance'}), 400
    else:
        return jsonify({'error': 'Invalid exchange type'}), 400

    # Create exchange request
    exchange = Exchange(
        requester_id=current_user.id,
        owner_id=item.user_id,
        requested_item_id=item_id,
        offered_item_id=offered_item_id if exchange_type == 'item' else None,
        exchange_type=exchange_type,
        points_offered=points_offered if exchange_type == 'points' else None,
        message=message,
        status='pending'
    )

    try:
        db.session.add(exchange)
        db.session.commit()
        return jsonify({'success': 'Exchange request sent successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to send exchange request'}), 500

@user_bp.route('/exchanges')
@login_required
def view_exchanges():
    """View all exchange requests (sent and received)"""
    # Get sent exchanges
    sent_exchanges = Exchange.query.filter_by(requester_id=current_user.id)\
                                  .order_by(Exchange.created_at.desc()).all()

    # Get received exchanges
    received_exchanges = Exchange.query.filter_by(owner_id=current_user.id)\
                                      .order_by(Exchange.created_at.desc()).all()

    return render_template('user/user_Requests.html',
                         sent_exchanges=sent_exchanges,
                         received_exchanges=received_exchanges)

@user_bp.route('/exchanges/respond/<int:exchange_id>', methods=['POST'])
@login_required
def respond_to_exchange(exchange_id):
    """Respond to an exchange request (accept/reject)"""
    exchange = Exchange.query.get_or_404(exchange_id)

    # Only the item owner can respond
    if exchange.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Only pending exchanges can be responded to
    if exchange.status != 'pending':
        return jsonify({'error': 'This exchange request is no longer pending'}), 400

    action = request.json.get('action')

    if action == 'accepted':
        exchange.status = 'accepted'

        # Handle the exchange logic
        if exchange.exchange_type == 'points':
            # Transfer points
            exchange.requester.points_balance -= exchange.points_offered
            current_user.points_balance += exchange.points_offered

        # Mark items as exchanged
        exchange.requested_item.status = 'exchanged'
        if exchange.offered_item:
            exchange.offered_item.status = 'exchanged'

        from datetime import datetime
        exchange.completed_at = datetime.utcnow()
        exchange.status = 'completed'

        flash('Exchange request accepted and completed!', 'success')

    elif action == 'rejected':
        exchange.status = 'rejected'
        flash('Exchange request rejected.', 'info')
    else:
        return jsonify({'error': 'Invalid action'}), 400

    try:
        db.session.commit()
        return jsonify({'success': f'Exchange request {action} successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to {action} exchange request'}), 500

@user_bp.route('/exchanges/cancel/<int:exchange_id>', methods=['POST'])
@login_required
def cancel_exchange(exchange_id):
    """Cancel a sent exchange request"""
    exchange = Exchange.query.get_or_404(exchange_id)

    # Only the requester can cancel
    if exchange.requester_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Only pending exchanges can be cancelled
    if exchange.status != 'pending':
        return jsonify({'error': 'This exchange request cannot be cancelled'}), 400

    exchange.status = 'cancelled'

    try:
        db.session.commit()
        flash('Exchange request cancelled.', 'info')
        return jsonify({'success': 'Exchange request cancelled successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel exchange request'}), 500

@user_bp.route('/api/user_items')
@login_required
def get_user_items():
    """API endpoint to get current user's available items for exchange offers"""
    items = Item.query.filter_by(
        user_id=current_user.id,
        status='available',
        moderation_status='approved'
    ).all()

    items_data = []
    for item in items:
        items_data.append({
            'id': item.id,
            'title': item.title,
            'category': item.category,
            'points_value': item.points_required,  # Using points_required field from Item model
            'media_filename': item.media_filename
        })

    return jsonify(items_data)
