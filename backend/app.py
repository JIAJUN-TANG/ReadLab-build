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
    
    # 导入bcrypt用于密码哈希
    import bcrypt
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        
        # 初始化默认用户数据
        from models import User, Material, Form
        if not User.query.first():
            default_users = [
                {
                    'phone_number': '13800138001',
                    'name': 'Alice Researcher',
                    'email': 'alice@example.com',
                    'role': 'PARTICIPANT',
                    'group': 'A',
                    'password': 'password1',
                    'consent_given': False
                },
                {
                    'phone_number': '13800138002',
                    'name': 'Bob Subject',
                    'email': 'bob@example.com',
                    'role': 'PARTICIPANT',
                    'group': 'B',
                    'password': 'password2',
                    'consent_given': False
                },
                {
                    'phone_number': '16680808521',
                    'name': '唐嘉骏',
                    'email': 'jiajuntang1101@smail.nju.edu.cn',
                    'role': 'ADMIN',
                    'group': 'ADMIN',
                    'password': 'NJLDS1101tjj',
                    'consent_given': True
                }
            ]
            
            for user_data in default_users:
                # 对密码进行哈希处理
                password = user_data.pop('password')
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                user = User(**user_data, password=hashed_password)
                db.session.add(user)
            db.session.commit()
        
        # 初始化默认表单数据
        if not Form.query.first():
            default_forms = [
                {
                    'id': 'form1',
                    'title': '知情同意书',
                    'type': 'CONSENT',
                    'content': '<h2>知情同意书</h2><p>尊敬的参与者：</p><p>您好！我们正在进行一项关于阅读行为的研究，诚邀您参加。</p><p>本研究旨在了解不同阅读策略对理解效果的影响。参与本研究完全是自愿的，您可以随时退出，不会对您产生任何不利影响。</p><p>参与本研究的风险极小，主要是花费您的时间和精力。您的参与将有助于我们更好地理解阅读行为，为改进阅读教学提供依据。</p><p>您的个人信息将被严格保密，仅用于研究目的。研究结果将以匿名方式发表，不会泄露您的个人身份。</p><p>如果您有任何问题，请随时联系我们的研究团队。</p><p>感谢您的参与！</p><p>研究团队</p>'
                },
                {
                    'id': 'form2',
                    'title': '阅读体验问卷',
                    'type': 'QUESTIONNAIRE',
                    'content': '<h2>阅读体验问卷</h2><p>请根据您的阅读体验，回答以下问题：</p><ol><li>您对阅读材料的难度评价：<br/>□ 非常简单 □ 简单 □ 适中 □ 困难 □ 非常困难</li><li>您对阅读材料的兴趣程度：<br/>□ 非常感兴趣 □ 感兴趣 □ 一般 □ 不感兴趣 □ 非常不感兴趣</li><li>您认为阅读材料的内容是否清晰：<br/>□ 非常清晰 □ 清晰 □ 一般 □ 不清晰 □ 非常不清晰</li><li>您对阅读体验的整体评价：<br/>□ 非常满意 □ 满意 □ 一般 □ 不满意 □ 非常不满意</li></ol>'
                }
            ]
            
            for form_data in default_forms:
                form = Form(**form_data)
                db.session.add(form)
            db.session.commit()
        
        # 初始化默认材料数据
        if not Material.query.first():
            default_materials = [
                {
                    'id': 'mat1',
                    'title': '阅读实验材料示例',
                    'author': '研究团队',
                    'type': 'TEXT',
                    'content': '这是一篇用于阅读实验的示例文本材料。\n\n阅读实验是研究人类阅读过程和认知机制的重要方法。通过分析阅读时间、眼动轨迹和理解测试等数据，研究者可以深入了解阅读过程中的信息加工方式。\n\n本实验旨在探索不同阅读策略对理解效果的影响。请仔细阅读以下内容，并在阅读完成后回答相关问题。\n\n实验说明：\n1. 请在安静的环境中进行阅读\n2. 阅读过程中尽量保持专注\n3. 不要回读已阅读的内容\n4. 按照自己的正常速度阅读\n\n感谢您的参与！',
                    'cover_url': 'https://picsum.photos/id/100/300/450'
                }
            ]
            
            for material_data in default_materials:
                material = Material(**material_data)
                db.session.add(material)
            db.session.commit()
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    
    return app

# 运行应用
if __name__ == '__main__':
    app = create_app()
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
