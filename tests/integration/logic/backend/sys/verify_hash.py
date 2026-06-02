"""既存のハッシュを検証"""
import bcrypt

password = "password".encode('utf-8')
existing_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWEHaSzi".encode('utf-8')

try:
    result = bcrypt.checkpw(password, existing_hash)
    print(f"Password 'password' matches existing hash: {result}")
except Exception as e:
    print(f"Error: {e}")
