#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证循环导入问题已解决
"""

def test_imports():
    """测试所有模块导入"""
    print("🔍 开始测试模块导入...")
    
    try:
        # 测试基础模块导入
        print("  ✓ 导入 database 模块...")
        from database import db
        
        print("  ✓ 导入用户模型...")
        from models.user import User
        
        print("  ✓ 导入好友关系模型...")
        from models.friendship import Friendship
        
        print("  ✓ 导入消息模型...")
        from models.message import Message
        
        print("  ✓ 导入认证路由...")
        from routes.auth import auth_bp
        
        print("  ✓ 导入好友路由...")
        from routes.friend import friend_bp
        
        print("  ✓ 导入消息路由...")
        from routes.message import message_bp
        
        print("  ✓ 导入主应用...")
        from app import app, create_tables
        
        print("✅ 所有模块导入成功！循环导入问题已解决！")
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_database_creation():
    """测试数据库表创建"""
    print("\n🔍 开始测试数据库表创建...")
    
    try:
        from app import create_tables
        create_tables()
        print("✅ 数据库表创建成功！")
        return True
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n🔍 开始测试基本功能...")
    
    try:
        from app import app
        from models.user import User
        
        with app.app_context():
            # 测试用户模型基本功能
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            
            # 验证密码功能
            assert user.check_password("password123") == True
            assert user.check_password("wrongpassword") == False
            
            # 测试用户字典转换
            user_dict = user.to_dict()
            assert 'username' in user_dict
            assert 'email' in user_dict
            
        print("✅ 基本功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 聊天后端循环导入修复验证测试")
    print("=" * 60)
    
    tests = [
        ("模块导入测试", test_imports),
        ("数据库创建测试", test_database_creation),
        ("基本功能测试", test_basic_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        if test_func():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！循环导入问题已完全解决！")
        print("\n💡 提示:")
        print("   - 现在可以正常启动应用: python app.py")
        print("   - 可以运行API测试: python test_api.py")
        print("   - 项目结构已优化，避免了循环导入")
    else:
        print("❌ 部分测试失败，需要进一步检查")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
