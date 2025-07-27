#!/usr/bin/env python3
"""
Database initialization script
Run this separately to initialize the database
"""

import os
import sys
import time
from database import db, init_app
from flask import Flask

def create_app():
    """Create Flask app for database initialization"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'postgresql://user:password@localhost/doctorpatient'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = init_app(app)
    return app, db

def wait_for_db(max_retries=30):
    """Wait for database to be ready"""
    app, database = create_app()
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                database.session.execute('SELECT 1')
                print("✓ Database connection successful!")
                return app, database
        except Exception as e:
            print(f"⏳ Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("❌ Failed to connect to database after all retries")
                sys.exit(1)

def initialize_database():
    """Initialize database tables and sample data"""
    app, database = wait_for_db()
    
    try:
        with app.app_context():
            # Import models
            from models.user import User
            from models.file import File
            from models.message import Message
            from models.chat_room import ChatRoom
            
            # Create tables
            print("Creating database tables...")
            database.create_all()
            print("✓ Database tables created successfully!")
            
            # Initialize sample data
            from utils.database import init_db
            init_db(database, User)
            print("✓ Sample data initialized successfully!")
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    initialize_database()
