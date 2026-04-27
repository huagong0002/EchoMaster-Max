import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# 🚩 关键：允许所有子域名跨域访问，解决连接失败问题
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 模拟公共材料库存储
# 注意：Vercel 实例重启会清空，后续可接入正式数据库
ALL_MATERIALS = []

# 用户库
USERS = {
    "jerry": {"password": os.environ.get('ADMIN_PASSWORD', 'sdeducation'), "role": "admin", "name": "超级管理员"},
    "admin": {"password": "admin123", "role": "admin", "name": "管理员老师"}
}

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        u, p = data.get('username'), data.get('password')
        if u in USERS and USERS[u]["password"] == p:
            return jsonify({
                "status": "success",
                "user": {"username": u, "role": USERS[u]["role"], "displayName": USERS[u]["name"]}
            })
        return jsonify({"status": "fail", "message": "账号或密码错误"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/materials', methods=['GET', 'POST'])
def handle_materials():
    global ALL_MATERIALS
    if request.method == 'POST':
        new_mat = request.get_json()
        # 更新或追加：根据 ID 覆盖已有设置
        ALL_MATERIALS = [m for m in ALL_MATERIALS if m.get('id') != new_mat.get('id')]
        ALL_MATERIALS.append(new_mat)
        return jsonify({"status": "success"})
    
    return jsonify(ALL_MATERIALS)

def handler(event, context):
    return app(event, context)
