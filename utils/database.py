def init_db(db, User):
    """Initialize database with sample data if needed"""
    from werkzeug.security import generate_password_hash
    from utils.encryption import RSAEncryption
    
    # Check if we already have users
    if User.query.first():
        return
    
    # Create sample lawyer and client accounts
    rsa_encryption = RSAEncryption()
    
    # Create lawyer account
    lawyer_private, lawyer_public = rsa_encryption.generate_key_pair()
    lawyer = User(
        name='Mr. John Smith',
        email='lawyer@example.com',
        password_hash=generate_password_hash('lawyer123'),
        role='lawyer',
        private_key=lawyer_private,
        public_key=lawyer_public
    )
    
    # Create client account
    client_private, client_public = rsa_encryption.generate_key_pair()
    client = User(
        name='Jane Doe',
        email='client@example.com',
        password_hash=generate_password_hash('client123'),
        role='client',
        private_key=client_private,
        public_key=client_public
    )
    
    db.session.add(lawyer)
    db.session.add(client)
    db.session.commit()
    
    print("Sample accounts created:")
    print("Lawyer: lawyer@example.com / lawyer123")
    print("Client: client@example.com / client123")
