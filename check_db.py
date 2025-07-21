#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的数据库检查脚本 - 不需要额外依赖
"""

import sqlite3
import os
from datetime import datetime

def check_database():
    """检查数据库内容"""
    db_path = "instance/chat_app.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        print("请先运行应用创建数据库：python app.py")
        return
    
    print("🗄️  数据库检查报告")
    print("=" * 50)
    
    with sqlite3.connect(db_path) as conn:
        # 检查用户
        print("\n👤 用户信息:")
        cursor = conn.execute("SELECT id, username, email, created_at FROM users ORDER BY id")
        users = cursor.fetchall()
        
        if users:
            for user_id, username, email, created_at in users:
                print(f"  ID: {user_id}, 用户名: {username}, 邮箱: {email}")
                print(f"      创建时间: {created_at}")
        else:
            print("  暂无用户")
        
        # 检查好友关系
        print("\n👥 好友关系:")
        cursor = conn.execute("""
            SELECT u1.username, u2.username, f.status, f.created_at
            FROM friendships f
            JOIN users u1 ON f.user_id = u1.id
            JOIN users u2 ON f.friend_id = u2.id
            ORDER BY f.created_at
        """)
        friendships = cursor.fetchall()
        
        if friendships:
            for user, friend, status, created_at in friendships:
                print(f"  {user} -> {friend} ({status}) - {created_at}")
        else:
            print("  暂无好友关系")
        
        # 检查消息
        print("\n💬 消息记录:")
        cursor = conn.execute("""
            SELECT u1.username, u2.username, m.content, m.is_read, m.created_at
            FROM messages m
            JOIN users u1 ON m.sender_id = u1.id
            JOIN users u2 ON m.receiver_id = u2.id
            ORDER BY m.created_at DESC
            LIMIT 10
        """)
        messages = cursor.fetchall()
        
        if messages:
            for sender, receiver, content, is_read, created_at in messages:
                read_status = "已读" if is_read else "未读"
                content_preview = content[:50] + "..." if len(content) > 50 else content
                print(f"  {sender} -> {receiver}: {content_preview} ({read_status})")
                print(f"      时间: {created_at}")
        else:
            print("  暂无消息")
        
        # 统计信息
        print("\n📊 统计信息:")
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        friendship_count = conn.execute("SELECT COUNT(*) FROM friendships WHERE status='accepted'").fetchone()[0]
        message_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        unread_count = conn.execute("SELECT COUNT(*) FROM messages WHERE is_read=0").fetchone()[0]
        
        print(f"  用户总数: {user_count}")
        print(f"  好友关系数: {friendship_count // 2}")  # 除以2因为是双向关系
        print(f"  消息总数: {message_count}")
        print(f"  未读消息数: {unread_count}")

if __name__ == "__main__":
    check_database()
