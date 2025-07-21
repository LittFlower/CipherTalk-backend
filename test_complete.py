#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的API测试和数据库验证脚本
"""

import requests
import json
import time
import subprocess
import sys
import os

# API基础URL
BASE_URL = "http://localhost:5001/api"

def run_db_check():
    """运行数据库检查"""
    print("\n" + "="*60)
    print("🗄️  数据库状态检查")
    print("="*60)
    
    try:
        result = subprocess.run([sys.executable, "check_db.py"], 
                              capture_output=True, text=True, cwd=".")
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
    except Exception as e:
        print(f"运行数据库检查时出错: {e}")

def test_complete_workflow():
    """测试完整的工作流程"""
    print("🚀 开始完整的API测试和数据库验证")
    print("="*80)
    
    # 1. 检查初始数据库状态
    print("1️⃣ 检查初始数据库状态")
    run_db_check()
    
    # 2. 测试API
    print("\n2️⃣ 开始API测试")
    print("="*60)
    
    session = requests.Session()
    
    # 测试健康检查
    print("📡 测试健康检查...")
    try:
        response = session.get(f"{BASE_URL}/health")
        print(f"✅ 健康检查: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return
    
    # 测试用户注册
    print("\n👤 测试用户注册...")
    users_data = [
        {"username": "alice", "email": "alice@test.com", "password": "password123"},
        {"username": "bob", "email": "bob@test.com", "password": "password123"},
        {"username": "charlie", "email": "charlie@test.com", "password": "password123"}
    ]
    
    user_tokens = {}
    user_ids = {}
    
    for user_data in users_data:
        try:
            response = session.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code == 201:
                result = response.json()
                username = user_data["username"]
                user_tokens[username] = result.get('access_token')
                user_ids[username] = result.get('user', {}).get('id')
                print(f"✅ 用户 {username} 注册成功 (ID: {user_ids[username]})")
            else:
                print(f"❌ 用户 {user_data['username']} 注册失败: {response.json()}")
        except Exception as e:
            print(f"❌ 注册用户 {user_data['username']} 时出错: {e}")
    
    # 3. 检查注册后的数据库状态
    print("\n3️⃣ 检查用户注册后的数据库状态")
    run_db_check()
    
    # 4. 测试好友添加
    if len(user_tokens) >= 2:
        print("\n👥 测试添加好友...")
        
        # Alice 添加 Bob 为好友
        alice_session = requests.Session()
        alice_session.headers.update({'Authorization': f'Bearer {user_tokens["alice"]}'})
        
        try:
            response = alice_session.post(f"{BASE_URL}/friend/add", 
                                        json={"friend_username": "bob"})
            if response.status_code == 200:
                print("✅ Alice 成功添加 Bob 为好友")
            else:
                print(f"❌ 添加好友失败: {response.json()}")
        except Exception as e:
            print(f"❌ 添加好友时出错: {e}")
        
        # 5. 检查好友关系
        print("\n4️⃣ 检查添加好友后的数据库状态")
        run_db_check()
        
        # 6. 测试发送消息
        print("\n💬 测试发送消息...")
        
        messages = [
            "Hello Bob! How are you?",
            "This is a test message from Alice.",
            "Let's test our chat system!"
        ]
        
        for message in messages:
            try:
                response = alice_session.post(f"{BASE_URL}/message/send", 
                                            json={
                                                "receiver_id": user_ids["bob"],
                                                "content": message
                                            })
                if response.status_code == 200:
                    print(f"✅ 消息发送成功: {message[:30]}...")
                else:
                    print(f"❌ 消息发送失败: {response.json()}")
                time.sleep(0.5)  # 短暂延迟
            except Exception as e:
                print(f"❌ 发送消息时出错: {e}")
        
        # Bob 回复消息
        bob_session = requests.Session()
        bob_session.headers.update({'Authorization': f'Bearer {user_tokens["bob"]}'})
        
        try:
            response = bob_session.post(f"{BASE_URL}/message/send", 
                                      json={
                                          "receiver_id": user_ids["alice"],
                                          "content": "Hi Alice! I'm doing great, thanks for asking!"
                                      })
            if response.status_code == 200:
                print("✅ Bob 回复消息成功")
            else:
                print(f"❌ Bob 回复失败: {response.json()}")
        except Exception as e:
            print(f"❌ Bob 回复时出错: {e}")
        
        # 7. 检查消息发送后的数据库状态
        print("\n5️⃣ 检查发送消息后的数据库状态")
        run_db_check()
        
        # 8. 测试获取聊天记录
        print("\n📜 测试获取聊天记录...")
        
        try:
            response = alice_session.get(f"{BASE_URL}/message/history?friend_id={user_ids['bob']}")
            if response.status_code == 200:
                result = response.json()
                message_count = len(result.get('messages', []))
                print(f"✅ 获取聊天记录成功，共 {message_count} 条消息")
            else:
                print(f"❌ 获取聊天记录失败: {response.json()}")
        except Exception as e:
            print(f"❌ 获取聊天记录时出错: {e}")
        
        # 9. 测试获取聊天列表
        print("\n📋 测试获取聊天列表...")
        
        try:
            response = alice_session.get(f"{BASE_URL}/message/chats")
            if response.status_code == 200:
                result = response.json()
                chat_count = len(result.get('chats', []))
                print(f"✅ 获取聊天列表成功，共 {chat_count} 个聊天")
            else:
                print(f"❌ 获取聊天列表失败: {response.json()}")
        except Exception as e:
            print(f"❌ 获取聊天列表时出错: {e}")
    
    # 10. 最终数据库状态检查
    print("\n6️⃣ 最终数据库状态检查")
    run_db_check()
    
    print("\n" + "="*80)
    print("🎉 完整测试流程结束！")
    print("="*80)
    print("\n💡 提示:")
    print("1. 运行 'python check_db.py' 随时检查数据库状态")
    print("2. 运行 'python db_viewer.py' 使用交互式数据库查看器")
    print("3. 运行 'python shell.py' 进入Flask交互式环境")
    print("4. 数据库文件位置: instance/chat_app.db")

if __name__ == "__main__":
    test_complete_workflow()
