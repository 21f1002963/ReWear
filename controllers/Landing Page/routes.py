# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Import blueprint from parent controllers package
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from controllers import blueprint
from flask import render_template, request, redirect, url_for
from flask_login import login_required
from jinja2 import TemplateNotFound
from models.item import Item


@blueprint.route('/')
def home():
    # Get featured items (latest approved items) for the homepage
    featured_items = Item.query.filter_by(
        moderation_status='approved',
        status='available'
    ).order_by(Item.created_at.desc()).limit(6).all()

    return render_template('home/index.html', segment='index', featured_items=featured_items)


@blueprint.route('/index')
def index():
    return redirect(url_for('home_blueprint.home'))


@blueprint.route('/<template>')
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
