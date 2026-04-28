import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# 🚩 核心修正 1：增强 CORS 配置
# 仅仅 origins="*" 有时是不够的，必须允许特定的 Header 才能通过子域名的身份验证
CORS(app, resources={r"/api/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS", "DELETE"],
    "allow_headers": ["Content-Type", "Authorization", "Accept"],
    "supports_credentials": True
}})

# --- 模拟数据库存储 ---
GLOBAL_STORE = {
    "materials": [],
    "users": {
        "jerry": {"password": os.environ.get('ADMIN_PASSWORD', 'sdeducation'), "role": "admin", "name": "超级管理员"},
        "admin": {"password": "admin123", "role": "admin", "name": "管理员老师"},
        "test01": {"password": "123", "role": "user", "name": "测试学生"}
    }
}

# 🚩 核心修正 2：增加专用的同步接口以适配您的 App.tsx (第106行)
# 您的前端代码请求的是 /api/materials/sync，原本的代码里没有这个路径
@app.route('/api/materials/sync', methods=['POST'])
def sync_materials():
    global GLOBAL_STORE
    try:
        data = request.get_json()
        if data and "materials" in data:
            # 全量更新模式：用前端传来的列表覆盖后端
            GLOBAL_STORE["materials"] = data["materials"]
            return jsonify({"status": "success", "count": len(GLOBAL_STORE["materials"])})
        return jsonify({"status": "error", "message": "无效的数据格式"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 1. 登录接口
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "无数据输入"}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')

        user_db = GLOBAL_STORE["users"]
        if username in user_db and user_db[username]["password"] == password:
            return jsonify({
                "status": "success",
                "user": {
                    "username": username,
                    "role": user_db[username]["role"],
                    "displayName": user_db[username]["name"]
                }
            })
        
        return jsonify({"status": "fail", "message": "账号或密码错误"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 2. 基础材料库接口
@app.route('/api/materials', methods=['GET', 'POST', 'DELETE'])
@app.route('/api/materials/<id>', methods=['DELETE'])
def handle_materials(id=None):
    global GLOBAL_STORE
    try:
        if request.method == 'POST':
            new_item = request.get_json()
            if not new_item or 'id' not in new_item:
                return jsonify({"status": "error", "message": "材料数据不完整"}), 400
            GLOBAL_STORE["materials"] = [m for m in GLOBAL_STORE["materials"] if m.get('id') != new_item['id']]
            GLOBAL_STORE["materials"].append(new_item)
            return jsonify({"status": "success"})
        
        if request.method == 'DELETE':
            target_id = id or request.args.get('id')
            if target_id:
                GLOBAL_STORE["materials"] = [m for m in GLOBAL_STORE["materials"] if m.get('id') != target_id]
                return jsonify({"status": "success"})
        
        return jsonify(GLOBAL_STORE["materials"])
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. 注册接口
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        u = data.get('username', '').strip()
        p = data.get('password', '')
        if u and p:
            GLOBAL_STORE["users"][u] = {"password": p, "role": "user", "name": u}
            return jsonify({"status": "success", "user": {"username": u, "role": "user", "displayName": u}})
        return jsonify({"status": "fail", "message": "信息不全"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 4. 健康检查
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "materials_count": len(GLOBAL_STORE["materials"])})

# Vercel 启动句柄
def handler(event, context):
    return app(event, context)
