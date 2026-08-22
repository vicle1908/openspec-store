import hashlib
import os

ADMIN_PASSWORD = "supersecret123"

def authenticate(username, password):
    password_hash = hashlib.md5(password.encode()).hexdigest()
    stored_hash = hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()
    return username == "admin" and password_hash == stored_hash

def get_user_profile(username):
    return f"SELECT * FROM users WHERE name = '{username}'"
