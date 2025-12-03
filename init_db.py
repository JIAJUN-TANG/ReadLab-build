#!/usr/bin/env python3

"""
数据库初始化Script
"""

import os
from datetime import datetime, timezone, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# 创建Flask应用
app = Flask(__name__)

load_dotenv(encoding='utf-8')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化SQLAlchemy数据库扩展
db = SQLAlchemy(app)

# 创建北京时间时区对象
beijing_tz = timezone(timedelta(hours=8))

# Define models
class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    phone_number = db.Column(db.String(20), primary_key=True, nullable=False, unique=True, index=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=True, unique=True)
    role = db.Column(db.String(20), nullable=False)
    group = db.Column(db.String(50), nullable=True, default='A')
    password = db.Column(db.String(255), nullable=True)
    consent_given = db.Column(db.Boolean, nullable=False, default=False)
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
        assigned_count = len(self.assignments) if hasattr(self, 'assignments') else 0
        read_count = sum(1 for assignment in self.assignments if assignment.read_status) if hasattr(self, 'assignments') else 0
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'type': self.type,
            'content': self.content,
            'coverUrl': self.cover_url,
            'assignedToUserIds': [assignment.user_id for assignment in self.assignments] if hasattr(self, 'assignments') else [],
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
    read_status = db.Column(db.Boolean, nullable=False, default=False)
    
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

# Create database and tables
with app.app_context():
    from urllib.parse import urlparse
    import pymysql
    
    db_url = os.environ.get('DATABASE_URL')
    parsed_url = urlparse(db_url)
    
    db_user = parsed_url.username
    db_password = parsed_url.password
    db_host = parsed_url.hostname
    db_port = parsed_url.port or 3306
    db_name = parsed_url.path.lstrip('/')
    
    # Create database if it doesn't exist
    print(f"Creating database {db_name} if it doesn't exist...")
    conn = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.close()
    conn.close()
    print(f"Database {db_name} created or already exists!")
    
    # 清除所有表
    print("Dropping all existing tables...")
    db.drop_all()
    print("All tables dropped successfully!")
    
    # 创建表
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")
    
    # Initialize default users
    if not User.query.first():
        print("Initializing default users...")
        default_users = [
            {
                'phone_number': '13800138001',
                'name': 'Alice Researcher',
                'email': 'alice@example.com',
                'role': 'PARTICIPANT',
                'group': 'A',
                'consent_given': False,
                'gender': 'Female',
                'income': 5000,
                'education': 'Bachelor',
                'password': 'password1'
            },
            {
                'phone_number': '13800138002',
                'name': 'Bob Subject',
                'email': 'bob@example.com',
                'role': 'PARTICIPANT',
                'group': 'B',
                'consent_given': False,
                'gender': 'Male',
                'income': 6000,
                'education': 'Master',
                'password': 'password2'
            },
            {
                'phone_number': '16680808521',
                'name': '唐嘉骏',
                'email': 'jiajuntang1101@smail.nju.edu.cn',
                'role': 'ADMIN',
                'group': 'A',
                'consent_given': True,
                'gender': 'Male',
                'income': 7000,
                'education': 'PhD',
                'password': 'NJLDS1101tjj!'
            }
        ]
        
        for user_data in default_users:
            user = User(**user_data)
            db.session.add(user)
        db.session.commit()
        print("Default users added successfully!")
