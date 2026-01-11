# 配置文件
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Volcengine Media Generation Config
    API_KEY = os.environ.get('API_KEY')
    MEDIA_URL = os.environ.get('MEDIA_URL') or 'https://ark.cn-beijing.volces.com/api/v3/images/generations'
    MEDIA_MODEL = os.environ.get('MEDIA_MODEL') or 'doubao-seedream-4-0-250828'
    
    # SQLAlchemy连接池配置，优化Gunicorn多进程环境
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 1800  # 30分钟回收连接，避免MySQL的wait_timeout问题
    SQLALCHEMY_MAX_OVERFLOW = 20
    
    PORT = int(os.environ.get('PORT') or 5000)
    HOST = os.environ.get('HOST') or '127.0.0.1'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
