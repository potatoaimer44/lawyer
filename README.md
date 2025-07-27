# SecureHealth - Doctor-Patient File Sharing Platform

A professional, secure web application for encrypted file sharing and communication between doctors and patients. Built with Flask, PostgreSQL, and RSA encryption.

## Features

- **RSA Encryption**: All files are encrypted using asymmetric encryption
- **Digital Signatures**: Messages are digitally signed for authenticity verification
- **Real-time Chat**: Secure 1-on-1 communication between doctors and patients
- **File Sharing**: Upload and download encrypted files
- **Role-based Access**: Separate doctor and patient accounts
- **Professional UI**: Clean, responsive design suitable for healthcare environments

## Security Features

- RSA 2048-bit encryption for file security
- Digital message signing and verification
- Secure user authentication
- Role-based access control
- Encrypted file storage
- Message integrity verification

## Technology Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Real-time**: Socket.IO
- **Encryption**: Python Cryptography library
- **Deployment**: Docker & Docker Compose

## Quick Start with Docker

1. **Clone the repository**
   \`\`\`bash
   git clone <repository-url>
   cd doctor-patient-app
   \`\`\`

2. **Start the application**
   \`\`\`bash
   docker-compose up --build
   \`\`\`

3. **Access the application**
   - Open your browser and go to: http://localhost:5000
   - The database will be automatically initialized with sample accounts

## Demo Accounts

The application comes with pre-configured demo accounts:

- **Doctor Account**
  - Email: doctor@example.com
  - Password: doctor123

- **Patient Account**
  - Email: patient@example.com
  - Password: patient123

## Manual Installation

If you prefer to run without Docker:

1. **Install PostgreSQL**
   \`\`\`bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   \`\`\`

2. **Create database**
   \`\`\`bash
   sudo -u postgres createdb doctorpatient
   sudo -u postgres createuser user
   sudo -u postgres psql -c "ALTER USER user PASSWORD 'password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE doctorpatient TO user;"
   \`\`\`

3. **Install Python dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. **Set environment variables**
   \`\`\`bash
   export DATABASE_URL="postgresql://user:password@localhost/doctorpatient"
   export SECRET_KEY="your-secret-key-here"
   \`\`\`

5. **Run the application**
   \`\`\`bash
   python app.py
   \`\`\`

## Project Structure

\`\`\`
doctor-patient-app/
├── app.py                 # Main Flask application
├── models/                # Database models
│   ├── __init__.py
│   ├── user.py           # User model
│   ├── file.py           # File model
│   ├── message.py        # Message model
│   └── chat_room.py      # Chat room model
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── encryption.py     # RSA encryption utilities
│   └── database.py       # Database initialization
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard
│   ├── upload.html       # File upload page
│   └── chat.html         # Chat interface
├── static/               # Static files
│   └── css/
│       └── style.css     # Custom styles
├── uploads/              # Encrypted file storage
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
└── README.md           # This file
\`\`\`

## How It Works

### File Encryption Process

1. **Upload**: User selects a file and recipient
2. **Key Retrieval**: System retrieves recipient's public key
3. **Encryption**: File is encrypted using RSA with recipient's public key
4. **Storage**: Encrypted file is stored on server
5. **Download**: Only the recipient can decrypt using their private key

### Message Security

1. **Signing**: Each message is signed with sender's private key
2. **Transmission**: Message and signature are sent to recipient
3. **Verification**: Recipient can verify message authenticity using sender's public key
4. **Integrity**: Any tampering with the message will fail verification

### User Authentication

- Secure password hashing using Werkzeug
- Session-based authentication
- Role-based access control (doctor/patient)
- RSA key pair generation during registration

## API Endpoints

### Authentication
- `GET /` - Landing page
- `GET /login` - Login form
- `POST /login` - Process login
- `GET /register` - Registration form
- `POST /register` - Process registration
- `GET /logout` - Logout user

### Main Features
- `GET /dashboard` - User dashboard
- `GET /upload` - File upload form
- `POST /upload` - Process file upload
- `GET /download/<file_id>` - Download and decrypt file
- `GET /chat/<room_id>` - Chat interface
- `POST /create_chat` - Create new chat room
- `POST /verify_message` - Verify message signature

### WebSocket Events
- `join` - Join chat room
- `leave` - Leave chat room
- `message` - Send/receive messages

## Security Considerations

### Production Deployment

1. **Environment Variables**
   \`\`\`bash
   # Set strong secret key
   export SECRET_KEY="your-very-long-random-secret-key"
   
   # Use secure database credentials
   export DATABASE_URL="postgresql://secure_user:strong_password@db:5432/doctorpatient"
   \`\`\`

2. **HTTPS Configuration**
   - Use SSL/TLS certificates in production
   - Configure reverse proxy (nginx/Apache)
   - Enable HSTS headers

3. **Database Security**
   - Use strong database passwords
   - Enable database encryption at rest
   - Regular security updates

4. **File Storage**
   - Implement file size limits
   - Scan uploaded files for malware
   - Use secure file permissions

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   \`\`\`bash
   # Check if PostgreSQL is running
   docker-compose ps
   
   # View logs
   docker-compose logs db
   \`\`\`

2. **File Upload Issues**
   \`\`\`bash
   # Check uploads directory permissions
   ls -la uploads/
   
   # Create directory if missing
   mkdir -p uploads
   chmod 755 uploads
   \`\`\`

3. **Encryption Errors**
   - Ensure cryptography library is properly installed
   - Check RSA key format in database
   - Verify file size limits

### Development Mode

To run in development mode with debug enabled:

\`\`\`bash
export FLASK_ENV=development
python app.py
\`\`\`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the security considerations

## Disclaimer

This application is designed for educational and demonstration purposes. For production healthcare environments, ensure compliance with relevant regulations (HIPAA, GDPR, etc.) and conduct thorough security audits.
# lawyer
# lawyer
