#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的API功能测试脚本 - 使用现有用户
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:5002/api"

def test_with_existing_users():
    """使用现有用户测试所有功能"""
    print("🚀 开始完整API功能测试")
    print("=" * 60)
    
    # 1. 健康检查
    print("1️⃣ 测试健康检查")
    response = requests.get(f"{BASE_URL}/health")
    print(f"✅ 健康检查: {response.status_code} - {response.json()}")
    
    # 2. 用户登录
    print("\n2️⃣ 用户登录测试")
    
    # 登录 user1
    login_data = {"username": "user1", "password": "password123"}
    response1 = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response1.status_code == 200:
        user1_token = response1.json()['access_token']
        user1_id = response1.json()['user']['id']
        user1_headers = {'Authorization': f'Bearer {user1_token}'}
        print(f"✅ user1 登录成功 (ID: {user1_id})")
    else:
        print(f"❌ user1 登录失败: {response1.json()}")
        return
    
    # 登录 user2
    login_data2 = {"username": "user2", "password": "password123"}
    response2 = requests.post(f"{BASE_URL}/auth/login", json=login_data2)
    
    if response2.status_code == 200:
        user2_token = response2.json()['access_token']
        user2_id = response2.json()['user']['id']
        user2_headers = {'Authorization': f'Bearer {user2_token}'}
        print(f"✅ user2 登录成功 (ID: {user2_id})")
    else:
        print(f"❌ user2 登录失败: {response2.json()}")
        return
    
    # 3. 获取用户信息
    print("\n3️⃣ 获取用户信息测试")
    response = requests.get(f"{BASE_URL}/auth/profile", headers=user1_headers)
    if response.status_code == 200:
        print(f"✅ 获取用户信息成功: {response.json()['user']['username']}")
    else:
        print(f"❌ 获取用户信息失败: {response.json()}")
    
    # 4. 好友管理测试
    print("\n4️⃣ 好友管理测试")
    
    # 获取好友列表
    response = requests.get(f"{BASE_URL}/friend/list", headers=user1_headers)
    if response.status_code == 200:
        friends = response.json()['friends']
        print(f"✅ 获取好友列表成功，共 {len(friends)} 个好友")
        for friend in friends:
            print(f"   - {friend['username']} ({friend['email']})")
    else:
        print(f"❌ 获取好友列表失败: {response.json()}")
    
    # 搜索用户
    response = requests.get(f"{BASE_URL}/friend/search?keyword=user", headers=user1_headers)
    if response.status_code == 200:
        users = response.json()['users']
        print(f"✅ 搜索用户成功，找到 {len(users)} 个用户")
    else:
        print(f"❌ 搜索用户失败: {response.json()}")
    
    # 5. 消息功能测试
    print("\n5️⃣ 消息功能测试")
    
    # 发送新消息
    message_data = {
        "receiver_id": user2_id,
        "content": "这是一条新的测试消息！",
        "message_type": "text"
    }
    response = requests.post(f"{BASE_URL}/message/send", json=message_data, headers=user1_headers)
    if response.status_code == 200:
        print("✅ 发送消息成功")
    else:
        print(f"❌ 发送消息失败: {response.json()}")
    
    # user2 回复消息
    reply_data = {
        "receiver_id": user1_id,
        "content": "收到了，这是我的回复！",
        "message_type": "text"
    }
    response = requests.post(f"{BASE_URL}/message/send", json=reply_data, headers=user2_headers)
    if response.status_code == 200:
        print("✅ 回复消息成功")
    else:
        print(f"❌ 回复消息失败: {response.json()}")
    
    # 获取聊天列表 (这是之前失败的功能)
    print("\n6️⃣ 获取聊天列表测试 (重点测试)")
    response = requests.get(f"{BASE_URL}/message/chats", headers=user1_headers)
    if response.status_code == 200:
        chats = response.json()['chats']
        print(f"✅ 获取聊天列表成功，共 {len(chats)} 个聊天")
        for chat in chats:
            partner = chat['partner']['username']
            last_msg = chat['last_message']['content'][:30] + "..."
            unread = chat['unread_count']
            print(f"   - 与 {partner} 的聊天，最新消息: {last_msg}，未读: {unread}")
    else:
        print(f"❌ 获取聊天列表失败: {response.json()}")
    
    # 获取聊天历史
    print("\n7️⃣ 获取聊天历史测试")
    response = requests.get(f"{BASE_URL}/message/history?friend_id={user2_id}", headers=user1_headers)
    if response.status_code == 200:
        messages = response.json()['messages']
        print(f"✅ 获取聊天历史成功，共 {len(messages)} 条消息")
        for msg in messages[-3:]:  # 显示最后3条消息
            sender = "我" if msg['sender_id'] == user1_id else "对方"
            content = msg['content'][:30] + "..."
            print(f"   - {sender}: {content}")
    else:
        print(f"❌ 获取聊天历史失败: {response.json()}")
    
    # 获取最后一条消息
    print("\n8️⃣ 获取最后消息测试")
    response = requests.get(f"{BASE_URL}/message/last?friend_id={user2_id}", headers=user1_headers)
    if response.status_code == 200:
        last_msg = response.json()['last_message']
        print(f"✅ 获取最后消息成功: {last_msg['content'][:50]}...")
    else:
        print(f"❌ 获取最后消息失败: {response.json()}")
    
    print("\n" + "=" * 60)
    print("🎉 完整API功能测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_with_existing_users()
