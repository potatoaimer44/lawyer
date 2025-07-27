from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid
from utils.encryption import RSAEncryption, sign_message, verify_signature
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/doctorpatient')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
from database import db, init_app
db = init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Import models after db initialization
from models.user import User
from models.file import File
from models.message import Message
from models.chat_room import ChatRoom

def create_tables():
    """Create database tables with retry logic"""
    import time
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            with app.app_context():
                db.create_all()
                # Initialize with sample data
                from utils.database import init_db
                init_db(db, User)
                print("Database initialized successfully!")
                return
        except Exception as e:
            retry_count += 1
            print(f"Database connection attempt {retry_count}/{max_retries} failed: {e}")
            if retry_count < max_retries:
                print("Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print("Failed to connect to database after all retries")
                raise

# Authentication routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_name'] = user.name
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Generate RSA key pair for the user
        rsa_encryption = RSAEncryption()
        private_key, public_key = rsa_encryption.generate_key_pair()
        
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            private_key=private_key,
            public_key=public_key
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Dashboard and main functionality
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get files shared with this user or uploaded by this user
    files = File.query.filter(
        (File.sender_id == user.id) | (File.recipient_id == user.id)
    ).order_by(File.created_at.desc()).all()
    
    # Get chat rooms for this user
    chat_rooms = ChatRoom.query.filter(
        (ChatRoom.doctor_id == user.id) | (ChatRoom.patient_id == user.id)
    ).all()
    
    # Get potential chat partners
    if user.role == 'doctor':
        potential_partners = User.query.filter_by(role='patient').all()
    else:
        potential_partners = User.query.filter_by(role='doctor').all()
    
    return render_template('dashboard.html', user=user, files=files, chat_rooms=chat_rooms, potential_partners=potential_partners)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        recipient_id = request.form['recipient_id']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
            
            # Save the original file temporarily
            file.save(file_path)
            
            # Encrypt the file
            recipient = User.query.get(recipient_id)
            sender = User.query.get(session['user_id'])
            
            rsa_encryption = RSAEncryption()
            encrypted_file_path = rsa_encryption.encrypt_file(file_path, recipient.public_key)
            
            # Remove original file
            os.remove(file_path)
            
            # Create file record
            file_record = File(
                id=file_id,
                filename=filename,
                file_path=encrypted_file_path,
                sender_id=session['user_id'],
                recipient_id=recipient_id,
                file_size=os.path.getsize(encrypted_file_path)
            )
            
            db.session.add(file_record)
            db.session.commit()
            
            flash('File uploaded and encrypted successfully!', 'success')
            return redirect(url_for('dashboard'))
    
    # Get potential recipients (doctors can send to patients and vice versa)
    current_user = User.query.get(session['user_id'])
    if current_user.role == 'doctor':
        recipients = User.query.filter_by(role='patient').all()
    else:
        recipients = User.query.filter_by(role='doctor').all()
    
    return render_template('upload.html', recipients=recipients)

@app.route('/download/<file_id>')
def download_file(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    file_record = File.query.get_or_404(file_id)
    
    # Check if user is authorized to download this file
    if file_record.sender_id != session['user_id'] and file_record.recipient_id != session['user_id']:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    # Decrypt the file
    user = User.query.get(session['user_id'])
    rsa_encryption = RSAEncryption()
    
    try:
        decrypted_file_path = rsa_encryption.decrypt_file(file_record.file_path, user.private_key)
        return send_file(decrypted_file_path, as_attachment=True, download_name=file_record.filename)
    except Exception as e:
        flash('Error decrypting file', 'error')
        return redirect(url_for('dashboard'))

@app.route('/chat/<int:room_id>')
def chat(room_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    chat_room = ChatRoom.query.get_or_404(room_id)
    
    # Check if user is part of this chat room
    if chat_room.doctor_id != session['user_id'] and chat_room.patient_id != session['user_id']:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    messages = Message.query.filter_by(chat_room_id=room_id).order_by(Message.created_at.asc()).all()
    
    return render_template('chat.html', chat_room=chat_room, messages=messages)

@app.route('/create_chat', methods=['POST'])
def create_chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    other_user_id = request.form['other_user_id']
    current_user = User.query.get(session['user_id'])
    other_user = User.query.get(other_user_id)
    
    # Check if chat room already exists
    existing_room = ChatRoom.query.filter(
        ((ChatRoom.doctor_id == session['user_id']) & (ChatRoom.patient_id == other_user_id)) |
        ((ChatRoom.doctor_id == other_user_id) & (ChatRoom.patient_id == session['user_id']))
    ).first()
    
    if existing_room:
        return redirect(url_for('chat', room_id=existing_room.id))
    
    # Create new chat room
    if current_user.role == 'doctor':
        chat_room = ChatRoom(doctor_id=session['user_id'], patient_id=other_user_id)
    else:
        chat_room = ChatRoom(doctor_id=other_user_id, patient_id=session['user_id'])
    
    db.session.add(chat_room)
    db.session.commit()
    
    return redirect(url_for('chat', room_id=chat_room.id))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Socket.IO events for real-time chat
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('status', {'msg': f"{session['user_name']} has entered the chat."}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f"{session['user_name']} has left the chat."}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    message_content = data['message']
    
    # Get sender's private key for signing
    sender = User.query.get(session['user_id'])
    
    # Sign the message
    signature = sign_message(message_content, sender.private_key)
    
    # Save message to database
    message = Message(
        chat_room_id=room,
        sender_id=session['user_id'],
        content=message_content,
        signature=signature
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Emit message to room
    emit('message', {
        'message': message_content,
        'sender': session['user_name'],
        'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'signature': signature,
        'sender_id': session['user_id']
    }, room=room)

@app.route('/verify_message', methods=['POST'])
def verify_message():
    data = request.get_json()
    message_content = data['message']
    signature = data['signature']
    sender_id = data['sender_id']
    
    sender = User.query.get(sender_id)
    is_valid = verify_signature(message_content, signature, sender.public_key)
    
    return jsonify({'valid': is_valid})

if __name__ == '__main__':
    print("Starting SecureHealth application...")
    
    # Initialize database on startup
    try:
        create_tables()
        print("✓ Database initialization completed successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("The application will continue to run, but database operations may fail.")
    
    print("🚀 Starting Flask-SocketIO server...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
