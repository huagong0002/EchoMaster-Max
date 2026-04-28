import os
from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)

# 🚩 核心：根本解决子域名访问问题
# origins=["*"] 允许任何子域名(listening, test等)访问主域名的这个接口
CORS(app, resources={r"/api/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# --- 模拟数据库存储（放在内存中，适合快速开发） ---
# 提醒：Vercel 实例重启会重置此数据，如需永久保存未来需对接数据库
GLOBAL_STORE = {
    "materials": [],
    "users": {
        "jerry": {"password": os.environ.get('ADMIN_PASSWORD', 'sdeducation'), "role": "admin", "name": "超级管理员"},
        "admin": {"password": "admin123", "role": "admin", "name": "管理员老师"},
        "test01": {"password": "123", "role": "user", "name": "测试学生"}
    }
}

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

# 2. 材料库同步接口（核心：负责保存和下发所有人的设置）
@app.route('/api/materials', methods=['GET', 'POST'])
def handle_materials():
    global GLOBAL_STORE
    try:
        if request.method == 'POST':
            new_item = request.get_json()
            if not new_item or 'id' not in new_item:
                return jsonify({"status": "error", "message": "材料数据不完整"}), 400
            
            # 更新或追加逻辑：如果 ID 相同则覆盖旧的
            GLOBAL_STORE["materials"] = [m for m in GLOBAL_STORE["materials"] if m.get('id') != new_item['id']]
            GLOBAL_STORE["materials"].append(new_item)
            return jsonify({"status": "success"})
        
        # GET 请求：返回所有人分享的材料列表
        return jsonify(GLOBAL_STORE["materials"])
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. 注册接口（可选，满足您截图中的注册需求）
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

# 4. 健康检查（用于排查 Vercel 运行状态）
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "materials_count": len(GLOBAL_STORE["materials"])})

# Vercel 需要的启动句柄
def handler(event, context):
    return app(event, context)
