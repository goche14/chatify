import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chatify.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
