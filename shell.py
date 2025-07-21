#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Shell 交互式数据库查询
"""

from app import app
from database import db
from models.user import User
from models.friendship import Friendship
from models.message import Message

def init_shell():
    """初始化Flask Shell环境"""
    with app.app_context():
        print("🚀 Flask Shell 已启动")
        print("可用的对象: app, db, User, Friendship, Message")
        print("\n常用查询示例:")
        print("  查看所有用户: User.query.all()")
        print("  按ID查找用户: User.query.get(1)")
        print("  按用户名查找: User.query.filter_by(username='testuser').first()")
        print("  查看好友关系: Friendship.query.all()")
        print("  查看消息: Message.query.all()")
        print("  用户总数: User.query.count()")
        print("\n输入 'help()' 查看更多帮助")
        
        # 返回有用的对象供交互使用
        return {
            'app': app,
            'db': db,
            'User': User,
            'Friendship': Friendship,
            'Message': Message
        }

if __name__ == "__main__":
    # 启动交互式shell
    import code
    shell_context = init_shell()
    code.interact(local=shell_context)
