# API路由
from flask import Blueprint, request, jsonify
from models import User, Material, MaterialAssignment, Log, Form
from db import db
import json
import bcrypt

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/users', methods=['GET'])
def get_users():
    """获取所有用户"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@api_bp.route('/users/<string:phone_number>', methods=['GET'])
def get_user(phone_number):
    """获取单个用户"""
    user = User.query.get(phone_number)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())

@api_bp.route('/users', methods=['POST'])
def create_user():
    """创建用户"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 检查必填字段
    required_fields = ['phone_number', 'name', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # 检查用户是否已存在
    existing_user = User.query.get(data['phone_number'])
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    # 创建新用户，对密码进行加密
    password = data.get('password')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if password else None
    
    new_user = User(
        phone_number=data['phone_number'],
        name=data['name'],
        email=data.get('email'),
        role=data['role'],
        group=data.get('group'),
        avatar_url=data.get('avatar_url'),
        password=hashed_password
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<string:phone_number>', methods=['PUT'])
def update_user(phone_number):
    """更新用户"""
    user = User.query.get(phone_number)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 更新用户信息
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        user.role = data['role']
    if 'group' in data:
        user.group = data['group']
    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']
    if 'password' in data:
        # 对密码进行加密
        password = data['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password = hashed_password

    try:
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<string:phone_number>', methods=['DELETE'])
def delete_user(phone_number):
    """删除用户"""
    user = User.query.get(phone_number)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 检查必填字段
    if 'phone_number' not in data:
        return jsonify({'error': 'Missing required field: phone_number'}), 400

    # 查找用户
    user = User.query.get(data['phone_number'])
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    # 密码验证逻辑
    if 'password' not in data:
        return jsonify({'error': 'Missing required field: password'}), 400
    
    # 密码验证逻辑
    password_valid = False
    
    try:
        # 尝试使用bcrypt验证密码
        password_valid = bcrypt.checkpw(data.get('password').encode('utf-8'), user.password.encode('utf-8'))
    except ValueError:
        # 如果bcrypt验证失败，尝试直接比较明文密码
        password_valid = (user.password == data.get('password'))
        
        # 如果明文密码匹配，自动将其转换为bcrypt哈希并更新数据库
        if password_valid:
            hashed_password = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
    
    if not password_valid:
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({
        'success': True,
        'user': user.to_dict()
    })

# Material Routes
@api_bp.route('/materials', methods=['GET'])
def get_materials():
    """获取所有材料"""
    materials = Material.query.all()
    return jsonify([material.to_dict() for material in materials])

@api_bp.route('/materials/<string:id>', methods=['GET'])
def get_material(id):
    """获取单个材料"""
    material = Material.query.get(id)
    if not material:
        return jsonify({'error': 'Material not found'}), 404
    return jsonify(material.to_dict())

@api_bp.route('/materials', methods=['POST'])
def create_material():
    """创建材料"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 检查必填字段
    required_fields = ['id', 'title', 'type', 'content']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # 检查材料是否已存在
    existing_material = Material.query.get(data['id'])
    if existing_material:
        return jsonify({'error': 'Material already exists'}), 400

    # 创建新材料
    new_material = Material(
        id=data['id'],
        title=data['title'],
        author=data.get('author', 'Unknown'),
        type=data['type'],
        content=data['content'],
        cover_url=data.get('coverUrl')
    )

    try:
        db.session.add(new_material)
        db.session.commit()
        return jsonify(new_material.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/materials/<string:id>', methods=['PUT'])
def update_material(id):
    """更新材料"""
    material = Material.query.get(id)
    if not material:
        return jsonify({'error': 'Material not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 更新材料信息
    if 'title' in data:
        material.title = data['title']
    if 'author' in data:
        material.author = data['author']
    if 'type' in data:
        material.type = data['type']
    if 'content' in data:
        material.content = data['content']
    if 'coverUrl' in data:
        material.cover_url = data['coverUrl']

    try:
        db.session.commit()
        return jsonify(material.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/materials/<string:id>', methods=['DELETE'])
def delete_material(id):
    """删除材料"""
    material = Material.query.get(id)
    if not material:
        return jsonify({'error': 'Material not found'}), 404

    try:
        # 删除相关分配
        MaterialAssignment.query.filter_by(material_id=id).delete()
        db.session.delete(material)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/materials/<string:id>/assign', methods=['POST'])
def assign_material(id):
    """分配材料给用户"""
    data = request.get_json()
    if not data or 'userIds' not in data:
        return jsonify({'error': 'Missing userIds field'}), 400

    material = Material.query.get(id)
    if not material:
        return jsonify({'error': 'Material not found'}), 404

    try:
        for user_id in data['userIds']:
            # 检查用户是否存在
            user = User.query.get(user_id)
            if not user:
                continue
            
            # 检查是否已分配
            existing_assignment = MaterialAssignment.query.filter_by(
                material_id=id, user_id=user_id
            ).first()
            if not existing_assignment:
                assignment = MaterialAssignment(material_id=id, user_id=user_id)
                db.session.add(assignment)
        
        db.session.commit()
        return jsonify(material.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/materials/<string:id>/unassign/<string:userId>', methods=['DELETE'])
def unassign_material(id, userId):
    """取消分配材料"""
    try:
        assignment = MaterialAssignment.query.filter_by(
            material_id=id, user_id=userId
        ).first()
        if assignment:
            db.session.delete(assignment)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'error': 'Assignment not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/materials/<string:id>/mark-read/<string:userId>', methods=['PUT'])
def mark_material_read(id, userId):
    """标记材料为已阅读"""
    try:
        assignment = MaterialAssignment.query.filter_by(
            material_id=id, user_id=userId
        ).first()
        if assignment:
            assignment.read_status = True
            db.session.commit()
            return jsonify({'success': True, 'readStatus': assignment.read_status})
        return jsonify({'error': 'Assignment not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/materials/<string:id>/mark-unread/<string:userId>', methods=['PUT'])
def mark_material_unread(id, userId):
    """标记材料为未阅读"""
    try:
        assignment = MaterialAssignment.query.filter_by(
            material_id=id, user_id=userId
        ).first()
        if assignment:
            assignment.read_status = False
            db.session.commit()
            return jsonify({'success': True, 'readStatus': assignment.read_status})
        return jsonify({'error': 'Assignment not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<string:userId>/materials', methods=['GET'])
def get_user_materials(userId):
    """获取用户分配的材料"""
    user = User.query.get(userId)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # 返回包含阅读状态的材料列表
    materials = []
    for assignment in user.assigned_materials:
        material_dict = assignment.material.to_dict()
        material_dict['readStatus'] = assignment.read_status
        materials.append(material_dict)
    return jsonify(materials)

# Log Routes
@api_bp.route('/logs', methods=['POST'])
def create_log():
    """创建操作日志"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 检查必填字段
    required_fields = ['userId', 'action']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # 创建新日志
    new_log = Log(
        user_id=data['userId'],
        action=data['action'],
        material_id=data.get('materialId'),
        details=data.get('details')
    )

    try:
        db.session.add(new_log)
        db.session.commit()
        return jsonify(new_log.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/logs', methods=['GET'])
def get_logs():
    """获取所有日志"""
    logs = Log.query.order_by(Log.created_at.desc()).all()
    return jsonify([log.to_dict() for log in logs])

@api_bp.route('/logs/user/<string:userId>', methods=['GET'])
def get_user_logs(userId):
    """获取特定用户的日志"""
    logs = Log.query.filter_by(user_id=userId).order_by(Log.created_at.desc()).all()
    return jsonify([log.to_dict() for log in logs])

@api_bp.route('/logs/material/<string:materialId>', methods=['GET'])
def get_material_logs(materialId):
    """获取特定材料的日志"""
    logs = Log.query.filter_by(material_id=materialId).order_by(Log.created_at.desc()).all()
    return jsonify([log.to_dict() for log in logs])

# Form Routes
@api_bp.route('/forms', methods=['GET'])
def get_forms():
    """获取所有表单"""
    forms = Form.query.all()
    return jsonify([form.to_dict() for form in forms])

@api_bp.route('/forms/<string:id>', methods=['GET'])
def get_form(id):
    """获取单个表单"""
    form = Form.query.get(id)
    if not form:
        return jsonify({'error': 'Form not found'}), 404
    return jsonify(form.to_dict())

@api_bp.route('/forms', methods=['POST'])
def create_form():
    """创建表单"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 检查必填字段
    required_fields = ['id', 'title', 'type', 'content']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # 检查表单是否已存在
    existing_form = Form.query.get(data['id'])
    if existing_form:
        return jsonify({'error': 'Form already exists'}), 400

    # 创建新表单
    new_form = Form(
        id=data['id'],
        title=data['title'],
        type=data['type'],
        content=data['content'],
        questions=json.dumps(data.get('questions')) if data.get('questions') else None
    )

    try:
        db.session.add(new_form)
        db.session.commit()
        return jsonify(new_form.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/forms/<string:id>', methods=['PUT'])
def update_form(id):
    """更新表单"""
    form = Form.query.get(id)
    if not form:
        return jsonify({'error': 'Form not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 更新表单信息
    if 'title' in data:
        form.title = data['title']
    if 'type' in data:
        form.type = data['type']
    if 'content' in data:
        form.content = data['content']
    if 'questions' in data:
        form.questions = json.dumps(data['questions']) if data['questions'] else None

    try:
        db.session.commit()
        return jsonify(form.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/forms/<string:id>', methods=['DELETE'])
def delete_form(id):
    """删除表单"""
    form = Form.query.get(id)
    if not form:
        return jsonify({'error': 'Form not found'}), 404

    try:
        db.session.delete(form)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/users/<string:phone_number>/consent', methods=['PUT'])
def update_consent(phone_number):
    """更新用户的知情同意状态"""
    user = User.query.get(phone_number)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # 更新知情同意状态
    if 'consent_given' in data:
        user.consent_given = data['consent_given']

    try:
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
