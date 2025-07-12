# -*- encoding: utf-8 -*-
"""
Controllers package  
"""

# Try importing blueprint directly
blueprint = None

try:
    # Import Flask to create blueprint here if needed
    from flask import Blueprint
    
    # Create the blueprint here since importing from Landing Page is problematic
    blueprint = Blueprint(
        'home_blueprint',
        __name__,
        url_prefix=''
    )
    
    print("Blueprint created successfully")
    
    # Now import routes to register them with the blueprint
    import sys
    import os
    landing_page_path = os.path.join(os.path.dirname(__file__), 'Landing Page')
    sys.path.insert(0, landing_page_path)
    
    # Import routes module
    import routes
    print("Routes imported successfully")
    
except Exception as e:
    print(f"Error creating blueprint: {e}")
    blueprint = None
