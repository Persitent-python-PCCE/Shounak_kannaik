
import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "sk_UnObMG0tNhe3ugvDow0Wx6PVJ1jlFpkm")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "sk_8OF38wKlaD1VvhOqJYvZ8FO2ccd7bBwL")
    JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS") or 24)
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False
    CACHE_TYPE = os.environ.get("CACHE_TYPE") or "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT") or 300)


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    CACHE_TYPE = "SimpleCache"


class ProductionConfig(Config):
    DEBUG = False
