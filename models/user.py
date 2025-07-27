from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'doctor' or 'patient'
    private_key = db.Column(db.Text, nullable=False)
    public_key = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sent_files = db.relationship('File', foreign_keys='File.sender_id', backref='sender', lazy='dynamic')
    received_files = db.relationship('File', foreign_keys='File.recipient_id', backref='recipient', lazy='dynamic')
    messages = db.relationship('Message', backref='sender', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
