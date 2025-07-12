#!/usr/bin/env python3
"""
Test script to verify database connection before deployment
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test the database connection"""
    try:
        from sqlalchemy import create_engine, text
        
        # Get database URL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        print(f"🔌 Testing connection to: {db_url.split('@')[1] if '@' in db_url else 'database'}")
        
        # Create engine and test connection
        engine = create_engine(db_url)
        
        with engine.connect() as connection:
            # Test basic query
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"📊 PostgreSQL Version: {version}")
            
            # Test database permissions
            result = connection.execute(text("SELECT current_database(), current_user;"))
            db_info = result.fetchone()
            print(f"🗄️  Database: {db_info[0]}")
            print(f"👤 User: {db_info[1]}")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_flask_app():
    """Test Flask app initialization with database"""
    try:
        from app import app, db
        
        with app.app_context():
            # Test app configuration
            print(f"🏗️  Flask app initialized successfully")
            print(f"⚙️  Debug mode: {app.config.get('DEBUG')}")
            print(f"🔐 Secret key configured: {'✅' if app.config.get('SECRET_KEY') else '❌'}")
            
            # Test database tables creation
            db.create_all()
            print(f"📋 Database tables created successfully")
            
            # Test basic database operations
            from models.user import User
            test_user_count = User.query.count()
            print(f"👥 Current user count: {test_user_count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 ReWear Database Connection Test")
    print("=" * 40)
    
    # Test 1: Direct database connection
    print("\n1️⃣ Testing direct database connection...")
    db_success = test_database_connection()
    
    # Test 2: Flask app with database
    print("\n2️⃣ Testing Flask app initialization...")
    app_success = test_flask_app()
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"   Database Connection: {'✅ PASS' if db_success else '❌ FAIL'}")
    print(f"   Flask App: {'✅ PASS' if app_success else '❌ FAIL'}")
    
    if db_success and app_success:
        print("\n🎉 All tests passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
        sys.exit(1)
