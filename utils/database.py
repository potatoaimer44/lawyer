def init_db(db, User):
    """Initialize database with sample data if needed"""
    from werkzeug.security import generate_password_hash
    from utils.encryption import RSAEncryption
    
    # Check if we already have users
    if User.query.first():
        return
    
    # Create sample doctor and patient accounts
    rsa_encryption = RSAEncryption()
    
    # Create doctor account
    doctor_private, doctor_public = rsa_encryption.generate_key_pair()
    doctor = User(
        name='Dr. John Smith',
        email='doctor@example.com',
        password_hash=generate_password_hash('doctor123'),
        role='doctor',
        private_key=doctor_private,
        public_key=doctor_public
    )
    
    # Create patient account
    patient_private, patient_public = rsa_encryption.generate_key_pair()
    patient = User(
        name='Jane Doe',
        email='patient@example.com',
        password_hash=generate_password_hash('patient123'),
        role='patient',
        private_key=patient_private,
        public_key=patient_public
    )
    
    db.session.add(doctor)
    db.session.add(patient)
    db.session.commit()
    
    print("Sample accounts created:")
    print("Doctor: doctor@example.com / doctor123")
    print("Patient: patient@example.com / patient123")
