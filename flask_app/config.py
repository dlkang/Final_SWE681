import os


class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'postgresql://fabianmr@localhost/projectdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Used to avoid XSS, httponly makes cookies inaccesible through JS API
    SESSION_COOKIE_HTTPONLY = True
    # Only send cookie over HTTPS
    SESSION_COOKIE_SECURE = True
    # Time of the Remember Me cookie
    REMEMBER_COOKIE_DURATION = 86400
