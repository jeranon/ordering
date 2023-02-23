import hashlib
import os

def generate_key(password, salt, iterations=100000, key_length=32):
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, key_length)
    return key
    
password = "your_password"  # Replace with your own password
salt = os.urandom(16)  # Generate a random salt
key = generate_key(password, salt)
with open("data/key.bin", "wb") as f:
    f.write(salt + key)
