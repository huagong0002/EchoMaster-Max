# 必须显式列出您的子域名，或者使用 "*" 允许所有（测试阶段推荐 "*"）
CORS(app, resources={r"/api/*": {
    "origins": [
        "https://test.sd-education.online",
        "https://www.sd-education.online"
    ],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})
