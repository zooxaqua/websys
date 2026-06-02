"""パスワードハッシュ生成"""
import bcrypt

password = "password".encode('utf-8')
hash_value = bcrypt.hashpw(password, bcrypt.gensalt())
print(f"Password: password")
print(f"Hash: {hash_value.decode('utf-8')}")
print(f"\nVerify: {bcrypt.checkpw(password, hash_value)}")
