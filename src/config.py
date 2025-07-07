import os
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SUPABASE_DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

    JWT_TOKEN_LOCATION = ['cookies']
    JWT_ACCESS_COOKIE_NAME = "access_token_cookie"
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_HTTPONLY = False
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_ACCESS_COOKIE_PATH = "/"
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ORIGINS = "*"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(weeks=1)