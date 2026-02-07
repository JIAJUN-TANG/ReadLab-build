# Flask应用入口
from flask import Flask
from flask_cors import CORS
from config import config
from db import db
from routes import api_bp

# 创建应用工厂
def create_app(config_name='default'):
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化CORS，允许所有跨域请求
    CORS(app)
    
    # 初始化数据库
    db.init_app(app)
    
    # 将CORS也应用到API蓝图上，确保跨域请求能正常处理
    CORS(api_bp)
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    
    return app
    

# 运行应用
if __name__ == '__main__':
    app = create_app()
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
