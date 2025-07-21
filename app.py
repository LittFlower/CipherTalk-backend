'''
Date: 2025-07-21 06:53:19
LastEditors: LittFlower xzy1476569428@163.com
LastEditTime: 2025-07-21 07:45:56
FilePath: /app2/app.py
'''
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from database import db

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
db.init_app(app)
jwt = JWTManager(app)

# 导入路由
from routes.auth import auth_bp
from routes.friend import friend_bp
from routes.message import message_bp

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(friend_bp, url_prefix='/api/friend')
app.register_blueprint(message_bp, url_prefix='/api/message')

@app.route('/api/health')
def health_check():
    return {'status': 'ok', 'message': '聊天后端服务正常运行'}

def create_tables():
    """创建数据库表"""
    with app.app_context():
        # 导入模型（确保表被创建）
        from models.user import User
        from models.friendship import Friendship  
        from models.message import Message
        
        db.create_all()
        print("✅ 数据库表创建成功！")

if __name__ == '__main__':
    # 只在直接运行时创建数据库表
    try:
        create_tables()
    except Exception as e:
        print(f"⚠️  数据库连接失败: {e}")
        print("请确保：")
        print("1. MySQL服务已启动")
        print("2. 数据库用户权限正确")
        print("3. .env文件中的数据库配置正确")
        print("4. 数据库已创建")
        exit(1)
    
    app.run(debug=True, host='0.0.0.0', port=5002)
