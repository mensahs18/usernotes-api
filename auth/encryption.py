from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv
import os

load_dotenv()
hex_key = os.getenv("ENCRYPT_KEY")
if not hex_key:
    raise RuntimeError("'ENCRYPT_KEY' environment variable is missing.")
ENC_KEY = bytes.fromhex(hex_key)

def encrypt(text: str) -> str:
    
    aesgcm = AESGCM(ENC_KEY)
    nonce = os.urandom(12)
    cipher = aesgcm.encrypt(nonce=nonce, data=text.encode(), associated_data=None)

    return (nonce + cipher).hex()

def decrypt(encrypted_hex: str) -> str:
    encrypted = bytes.fromhex(encrypted_hex)

    nonce = encrypted[:12]
    cipher = encrypted[12:]
    aesgcm = AESGCM(ENC_KEY)

    decrypted_bytes = aesgcm.decrypt(nonce=nonce, data=cipher, associated_data=None)
    return decrypted_bytes.decode()