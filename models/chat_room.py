from database import db
from datetime import datetime

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_chats')
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_chats')
    messages = db.relationship('Message', backref='chat_room', lazy='dynamic')
    
    def __repr__(self):
        return f'<ChatRoom {self.id}>'
