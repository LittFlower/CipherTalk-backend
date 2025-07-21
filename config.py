import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # 数据库配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'chat_app')
    DB_TYPE = os.getenv('DB_TYPE', 'mysql')  # mysql 或 sqlite
    
    # SQLAlchemy配置
    if DB_TYPE.lower() == 'sqlite':
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}.db"
    else:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-this-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = False  # 不自动过期，可根据需要调整
    
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', JWT_SECRET_KEY)
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
