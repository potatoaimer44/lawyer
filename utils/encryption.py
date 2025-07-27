from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import os
import base64

class RSAEncryption:
    def __init__(self):
        self.backend = default_backend()
    
    def generate_key_pair(self):
        """Generate RSA key pair and return as PEM strings"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=self.backend
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem
    
    def load_private_key(self, private_key_pem):
        """Load private key from PEM string"""
        return serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=self.backend
        )
    
    def load_public_key(self, public_key_pem):
        """Load public key from PEM string"""
        return serialization.load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=self.backend
        )
    
    def encrypt_file(self, file_path, public_key_pem):
        """Encrypt a file using RSA public key"""
        public_key = self.load_public_key(public_key_pem)
        
        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # For large files, we need to encrypt in chunks
        # RSA can only encrypt data smaller than the key size
        max_chunk_size = 190  # For 2048-bit key, max is ~245 bytes, using 190 for safety
        
        encrypted_chunks = []
        for i in range(0, len(file_data), max_chunk_size):
            chunk = file_data[i:i + max_chunk_size]
            encrypted_chunk = public_key.encrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            encrypted_chunks.append(encrypted_chunk)
        
        # Save encrypted file
        encrypted_file_path = file_path + '.encrypted'
        with open(encrypted_file_path, 'wb') as f:
            # Write number of chunks first
            f.write(len(encrypted_chunks).to_bytes(4, byteorder='big'))
            # Write each chunk with its length
            for chunk in encrypted_chunks:
                f.write(len(chunk).to_bytes(4, byteorder='big'))
                f.write(chunk)
        
        return encrypted_file_path
    
    def decrypt_file(self, encrypted_file_path, private_key_pem):
        """Decrypt a file using RSA private key"""
        private_key = self.load_private_key(private_key_pem)
        
        # Read encrypted file
        with open(encrypted_file_path, 'rb') as f:
            # Read number of chunks
            num_chunks = int.from_bytes(f.read(4), byteorder='big')
            
            decrypted_chunks = []
            for _ in range(num_chunks):
                # Read chunk length
                chunk_length = int.from_bytes(f.read(4), byteorder='big')
                # Read encrypted chunk
                encrypted_chunk = f.read(chunk_length)
                
                # Decrypt chunk
                decrypted_chunk = private_key.decrypt(
                    encrypted_chunk,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                decrypted_chunks.append(decrypted_chunk)
        
        # Combine decrypted chunks
        decrypted_data = b''.join(decrypted_chunks)
        
        # Save decrypted file
        decrypted_file_path = encrypted_file_path.replace('.encrypted', '.decrypted')
        with open(decrypted_file_path, 'wb') as f:
            f.write(decrypted_data)
        
        return decrypted_file_path

def sign_message(message, private_key_pem):
    """Sign a message with private key"""
    rsa_encryption = RSAEncryption()
    private_key = rsa_encryption.load_private_key(private_key_pem)
    
    signature = private_key.sign(
        message.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(message, signature_b64, public_key_pem):
    """Verify a message signature with public key"""
    try:
        rsa_encryption = RSAEncryption()
        public_key = rsa_encryption.load_public_key(public_key_pem)
        signature = base64.b64decode(signature_b64.encode('utf-8'))
        
        public_key.verify(
            signature,
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
