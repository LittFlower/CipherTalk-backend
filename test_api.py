#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天后端API测试脚本
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:5002/api"

class ChatAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def set_auth_header(self):
        """设置认证头"""
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
    
    def test_health(self):
        """测试健康检查"""
        print("=== 测试健康检查 ===")
        response = self.session.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
        
    def test_register(self, username="testuser", email="test@example.com", password="password123"):
        """测试用户注册"""
        print("=== 测试用户注册 ===")
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        response = self.session.post(f"{BASE_URL}/auth/register", json=data)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {result}")
        
        if response.status_code == 201:
            self.access_token = result.get('access_token')
            self.user_id = result.get('user', {}).get('id')
            self.set_auth_header()
            print("注册成功，已设置认证令牌")
        print()
        
    def test_login(self, username="testuser", password="password123"):
        """测试用户登录"""
        print("=== 测试用户登录 ===")
        data = {
            "username": username,
            "password": password
        }
        response = self.session.post(f"{BASE_URL}/auth/login", json=data)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {result}")
        
        if response.status_code == 200:
            self.access_token = result.get('access_token')
            self.user_id = result.get('user', {}).get('id')
            self.set_auth_header()
            print("登录成功，已设置认证令牌")
        print()
        
    def test_get_profile(self):
        """测试获取用户信息"""
        print("=== 测试获取用户信息 ===")
        response = self.session.get(f"{BASE_URL}/auth/profile")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
        
    def test_add_friend(self, friend_username="friend1"):
        """测试添加好友"""
        print("=== 测试添加好友 ===")
        data = {"friend_username": friend_username}
        response = self.session.post(f"{BASE_URL}/friend/add", json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
        
    def test_get_friends(self):
        """测试获取好友列表"""
        print("=== 测试获取好友列表 ===")
        response = self.session.get(f"{BASE_URL}/friend/list")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
        
    def test_search_users(self, keyword="test"):
        """测试搜索用户"""
        print("=== 测试搜索用户 ===")
        response = self.session.get(f"{BASE_URL}/friend/search?keyword={keyword}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
        
    def test_send_message(self, receiver_id, content="Hello, this is a test message!"):
        """测试发送消息"""
        print("=== 测试发送消息 ===")
        data = {
            "receiver_id": receiver_id,
            "content": content,
            "message_type": "text"
        }
        response = self.session.post(f"{BASE_URL}/message/send", json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
        
    def test_get_chats(self):
        """测试获取聊天列表"""
        print("=== 测试获取聊天列表 ===")
        response = self.session.get(f"{BASE_URL}/message/chats")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
        
    def test_get_message_history(self, friend_id):
        """测试获取聊天历史"""
        print("=== 测试获取聊天历史 ===")
        response = self.session.get(f"{BASE_URL}/message/history?friend_id={friend_id}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
        
    def test_get_last_message(self, friend_id):
        """测试获取最后消息"""
        print("=== 测试获取最后消息 ===")
        response = self.session.get(f"{BASE_URL}/message/last?friend_id={friend_id}")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()

def main():
    """主测试函数"""
    tester = ChatAPITester()
    
    print("开始测试聊天后端API...")
    print("=" * 50)
    
    # 基础测试
    tester.test_health()
    
    # 认证测试
    tester.test_register("user1", "user1@test.com", "password123")
    tester.test_get_profile()
    
    # 创建第二个用户用于测试
    tester2 = ChatAPITester()
    tester2.test_register("user2", "user2@test.com", "password123")
    
    # 好友管理测试
    tester.test_add_friend("user2")
    tester.test_get_friends()
    tester.test_search_users("user")
    
    # 消息测试
    if tester2.user_id:
        tester.test_send_message(tester2.user_id, "Hello from user1!")
        time.sleep(1)  # 等待一秒
        tester2.test_send_message(tester.user_id, "Hello from user2!")
        
        tester.test_get_chats()
        tester.test_get_message_history(tester2.user_id)
        tester.test_get_last_message(tester2.user_id)
    
    print("测试完成！")

if __name__ == "__main__":
    main()
