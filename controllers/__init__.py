# -*- encoding: utf-8 -*-
"""
Controllers package
"""

import sys
import os

# Add Landing Page directory to path to handle spaces in directory name
landing_page_path = os.path.join(os.path.dirname(__file__), 'Landing Page')
if landing_page_path not in sys.path:
    sys.path.insert(0, landing_page_path)

# Import the blueprint from Landing Page
try:
    from __init__ import blueprint
except ImportError:
    blueprint = None
