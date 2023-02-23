from cryptography.fernet import Fernet

with open("data/key.bin", "rb") as f:
    key_data = f.read()
    salt = key_data[:16]
    key = key_data[16:]

with open("data/credentials.json", "rb") as f:
    plaintext = f.read()

cipher = Fernet(key)
ciphertext = cipher.encrypt(plaintext)

with open("data/credentials.encrypted", "wb") as f:
    f.write(salt + ciphertext)
