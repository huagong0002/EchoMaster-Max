import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# 允许跨域：这是解决“网络连接失败”的关键，确保子域名能访问主域名接口
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 模拟全局存储
GLOBAL_DATA = {
    "materials": [], 
    "users": {
        "jerry": {"password": os.environ.get('ADMIN_PASSWORD', 'sdeducation'), "role": "admin", "name": "超级管理员"},
        "admin": {"password": "admin123", "role": "admin", "name": "管理员老师"}
    }
}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    u, p = data.get('username'), data.get('password')
    user_db = GLOBAL_DATA["users"]
    if u in user_db and user_db[u]["password"] == p:
        return jsonify({
            "status": "success",
            "user": {"username": u, "role": user_db[u]["role"], "displayName": user_db[u]["name"]}
        })
    return jsonify({"status": "fail", "message": "账号或密码错误"}), 401

@app.route('/api/materials', methods=['GET', 'POST'])
def handle_materials():
    if request.method == 'POST':
        new_mat = request.get_json()
        # 更新逻辑：根据ID覆盖
        GLOBAL_DATA["materials"] = [m for m in GLOBAL_DATA["materials"] if m.get('id') != new_mat.get('id')]
        GLOBAL_DATA["materials"].append(new_mat)
        return jsonify({"status": "success"})
    return jsonify(GLOBAL_DATA["materials"])

def handler(event, context):
    return app(event, context)
