# 数据模型
from datetime import datetime, timezone, timedelta
from db import db

# 创建北京时间时区对象
beijing_tz = timezone(timedelta(hours=8))

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    phone_number = db.Column(db.String(20), primary_key=True, nullable=False, unique=True, index=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=True, unique=True)
    role = db.Column(db.String(20), nullable=False)
    group = db.Column(db.String(50), nullable=True, default='A')
    password = db.Column(db.String(255), nullable=True)
    consent_given = db.Column(db.Boolean, nullable=False, default=False)  # 新增字段，标记用户是否同意了知情同意书
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    education = db.Column(db.String(50), nullable=True)
    income = db.Column(db.Integer, nullable=True)
    occupation = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(beijing_tz))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(beijing_tz), onupdate=lambda: datetime.now(beijing_tz))

    def to_dict(self):
        """将模型转换为字典"""
        return {
            'phone_number': self.phone_number,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'group': self.group,
            'consent_given': self.consent_given,
            'age': self.age,
            'gender': self.gender,
            'education': self.education,
            'income': self.income,
            'occupation': self.occupation,
            'assigned_materials_count': len(self.assigned_materials),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Form(db.Model):
    """表单模型，用于存储知情同意书和问卷"""
    __tablename__ = 'forms'

    id = db.Column(db.String(36), primary_key=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # CONSENT, QUESTIONNAIRE
    content = db.Column(db.Text, nullable=False)  # 表单内容，HTML格式
    questions = db.Column(db.Text, nullable=True)  # 问卷问题，JSON格式存储
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(beijing_tz))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(beijing_tz), onupdate=lambda: datetime.now(beijing_tz))

    def to_dict(self):
        """将模型转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'content': self.content,
            'questions': self.questions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Material(db.Model):
    """材料模型"""
    __tablename__ = 'materials'

    id = db.Column(db.String(36), primary_key=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100), nullable=False, default='Unknown')
    type = db.Column(db.String(20), nullable=False)  # TEXT, VIDEO, HTML, AUDIO
    content = db.Column(db.Text, nullable=False)
    cover_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(beijing_tz))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(beijing_tz), onupdate=lambda: datetime.now(beijing_tz))

    def to_dict(self):
        """将模型转换为字典"""
        assigned_count = len(self.assignments)
        read_count = sum(1 for assignment in self.assignments if assignment.read_status)
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'type': self.type,
            'content': self.content,
            'coverUrl': self.cover_url,
            'assignedToUserIds': [assignment.user_id for assignment in self.assignments],
            'assignedCount': assigned_count,
            'readCount': read_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class MaterialAssignment(db.Model):
    """材料分配模型"""
    __tablename__ = 'material_assignments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    material_id = db.Column(db.String(36), db.ForeignKey('materials.id'), nullable=False)
    user_id = db.Column(db.String(20), db.ForeignKey('users.phone_number'), nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(beijing_tz))
    read_status = db.Column(db.Boolean, nullable=False, default=False)  # 标记材料是否已阅读

    # 关系
    material = db.relationship('Material', backref=db.backref('assignments', lazy=True))
    user = db.relationship('User', backref=db.backref('assigned_materials', lazy=True))

    __table_args__ = (db.UniqueConstraint('material_id', 'user_id', name='_material_user_uc'),)

class Log(db.Model):
    """操作日志模型"""
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.phone_number'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 操作类型：LOGIN, LOGOUT, OPEN_MATERIAL, CLOSE_MATERIAL, AI_QUERY, etc.
    material_id = db.Column(db.String(36), db.ForeignKey('materials.id'), nullable=True)  # 可选，与材料相关的操作
    details = db.Column(db.Text, nullable=True)  # 操作详情，如AI查询内容等
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(beijing_tz))

    # 关系
    user = db.relationship('User', backref=db.backref('logs', lazy=True))
    material = db.relationship('Material', backref=db.backref('logs', lazy=True))

    def to_dict(self):
        """将模型转换为字典"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'action': self.action,
            'materialId': self.material_id,
            'details': self.details,
            'createdAt': self.created_at.isoformat()
        }

class MaterialFormConfig(db.Model):
    """实验配置表：材料与表单的关联"""
    __tablename__ = 'material_form_configs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    material_id = db.Column(db.String(36), db.ForeignKey('materials.id'), nullable=False)
    form_id = db.Column(db.String(36), db.ForeignKey('forms.id'), nullable=False)
    trigger_timing = db.Column(db.String(20), default='post_read')  # 'pre_read', 'post_read'
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    material = db.relationship('Material', backref=db.backref('form_configs', lazy=True))
    form = db.relationship('Form', backref=db.backref('material_configs', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'materialId': self.material_id,
            'formId': self.form_id,
            'triggerTiming': self.trigger_timing,
            'isActive': self.is_active
        }

class UserResponse(db.Model):
    """用户答卷记录表"""
    __tablename__ = 'user_responses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.phone_number'), nullable=False)
    material_id = db.Column(db.String(36), db.ForeignKey('materials.id'), nullable=False)
    form_id = db.Column(db.String(36), db.ForeignKey('forms.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)  # JSON格式存储答案
    duration_seconds = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(beijing_tz))

    # 关系
    user = db.relationship('User', backref=db.backref('responses', lazy=True))
    material = db.relationship('Material', backref=db.backref('responses', lazy=True))
    form = db.relationship('Form', backref=db.backref('responses', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'materialId': self.material_id,
            'formId': self.form_id,
            'answers': self.answers,
            'durationSeconds': self.duration_seconds,
            'createdAt': self.created_at.isoformat()
        }
