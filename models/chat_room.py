from database import db
from datetime import datetime

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    lawyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lawyer = db.relationship('User', foreign_keys=[lawyer_id], backref='lawyer_chats')
    client = db.relationship('User', foreign_keys=[client_id], backref='client_chats')
    messages = db.relationship('Message', backref='chat_room', lazy='dynamic')
    
    def __repr__(self):
        return f'<ChatRoom {self.id}>'
