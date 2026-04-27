import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# 🚩 核心配置：允许所有来源访问，解决子域名登录报错
CORS(app, resources={r"/api/*": {"origins": "*"}})

# =========================================================
# 1. 模拟数据库存储
# =========================================================
# 这里的 ALL_MATERIALS 将存放所有老师上传并点击“保存”的设置
ALL_MATERIALS = []

# 用户名单
USERS = {
    "jerry": {
        "password": os.environ.get('ADMIN_PASSWORD', 'sdeducation'), 
        "role": "admin", 
        "name": "超级管理员"
    },
    "admin": {
        "password": "admin123", 
        "role": "admin", 
        "name": "管理员老师"
    },
    "test01": {
        "password": "123", 
        "role": "user", 
        "name": "测试学生"
    }
}

# =========================================================
# 2. 核心接口逻辑
# =========================================================

# 登录接口：返回完整的用户信息供前端展示
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "fail", "message": "请求格式错误"}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if username in USERS:
            user_info = USERS[username]
            if user_info["password"] == password:
                return jsonify({
                    "status": "success",
                    "user": {
                        "username": username,
                        "role": user_info["role"],
                        "displayName": user_info["name"]
                    }
                }), 200
        
        return jsonify({"status": "fail", "message": "用户名或密码错误"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 材料同步接口：支持拉取全量列表和保存新材料
@app.route('/api/materials', methods=['GET', 'POST'])
def handle_materials():
    global ALL_MATERIALS
    try:
        if request.method == 'POST':
            new_data = request.get_json()
            if not new_data or 'id' not in new_data:
                return jsonify({"status": "error", "message": "数据无效"}), 400
            
            # 更新逻辑：如果 ID 已存在则覆盖，不存在则追加
            ALL_MATERIALS = [m for m in ALL_MATERIALS if m.get('id') != new_data['id']]
            ALL_MATERIALS.append(new_data)
            return jsonify({"status": "success"}), 200
        
        # GET 请求：返回当前所有存储的材料列表
        return jsonify(ALL_MATERIALS), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 健康检查
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok", 
        "materials_count": len(ALL_MATERIALS),
        "user_count": len(USERS)
    })

# =========================================================
# 3. Vercel 适配
# =========================================================
def handler(event, context):
    return app(event, context)
