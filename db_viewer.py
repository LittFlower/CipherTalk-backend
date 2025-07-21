#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库查看工具
用于查看SQLite数据库中的数据，验证操作是否成功
"""

import sqlite3
import os
from datetime import datetime
from tabulate import tabulate

class DatabaseViewer:
    def __init__(self, db_path="instance/chat_app.db"):
        """初始化数据库查看器"""
        self.db_path = db_path
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            print("请先运行应用创建数据库：python app.py")
            exit(1)
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def show_tables(self):
        """显示所有表"""
        print("📋 数据库表列表:")
        print("=" * 50)
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = cursor.fetchall()
            
            for i, (table_name,) in enumerate(tables, 1):
                print(f"{i}. {table_name}")
        print()
    
    def show_users(self):
        """显示所有用户"""
        print("👤 用户列表:")
        print("=" * 80)
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, username, email, created_at, last_seen 
                FROM users 
                ORDER BY id
            """)
            users = cursor.fetchall()
            
            if users:
                headers = ["ID", "用户名", "邮箱", "创建时间", "最后在线"]
                formatted_users = []
                for user in users:
                    formatted_user = list(user)
                    # 格式化时间
                    if formatted_user[3]:
                        formatted_user[3] = formatted_user[3][:19]  # 截取到秒
                    if formatted_user[4]:
                        formatted_user[4] = formatted_user[4][:19]
                    formatted_users.append(formatted_user)
                
                print(tabulate(formatted_users, headers=headers, tablefmt="grid"))
            else:
                print("暂无用户数据")
        print()
    
    def show_friendships(self):
        """显示好友关系"""
        print("👥 好友关系:")
        print("=" * 100)
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT f.id, u1.username as user, u2.username as friend, 
                       f.status, f.created_at
                FROM friendships f
                JOIN users u1 ON f.user_id = u1.id
                JOIN users u2 ON f.friend_id = u2.id
                ORDER BY f.created_at DESC
            """)
            friendships = cursor.fetchall()
            
            if friendships:
                headers = ["ID", "用户", "好友", "状态", "创建时间"]
                formatted_friendships = []
                for friendship in friendships:
                    formatted_friendship = list(friendship)
                    if formatted_friendship[4]:
                        formatted_friendship[4] = formatted_friendship[4][:19]
                    formatted_friendships.append(formatted_friendship)
                
                print(tabulate(formatted_friendships, headers=headers, tablefmt="grid"))
            else:
                print("暂无好友关系数据")
        print()
    
    def show_messages(self, limit=20):
        """显示消息记录"""
        print(f"💬 最近 {limit} 条消息:")
        print("=" * 120)
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT m.id, u1.username as sender, u2.username as receiver, 
                       m.content, m.message_type, m.is_read, m.created_at
                FROM messages m
                JOIN users u1 ON m.sender_id = u1.id
                JOIN users u2 ON m.receiver_id = u2.id
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (limit,))
            messages = cursor.fetchall()
            
            if messages:
                headers = ["ID", "发送者", "接收者", "内容", "类型", "已读", "发送时间"]
                formatted_messages = []
                for message in messages:
                    formatted_message = list(message)
                    # 限制内容长度
                    if len(formatted_message[3]) > 30:
                        formatted_message[3] = formatted_message[3][:30] + "..."
                    # 格式化时间
                    if formatted_message[6]:
                        formatted_message[6] = formatted_message[6][:19]
                    # 格式化已读状态
                    formatted_message[5] = "是" if formatted_message[5] else "否"
                    formatted_messages.append(formatted_message)
                
                print(tabulate(formatted_messages, headers=headers, tablefmt="grid"))
            else:
                print("暂无消息数据")
        print()
    
    def show_user_stats(self):
        """显示用户统计信息"""
        print("📊 数据库统计:")
        print("=" * 50)
        
        with self.get_connection() as conn:
            # 用户总数
            user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            
            # 好友关系总数
            friendship_count = conn.execute(
                "SELECT COUNT(*) FROM friendships WHERE status='accepted'"
            ).fetchone()[0]
            
            # 消息总数
            message_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            
            # 未读消息数
            unread_count = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE is_read=0"
            ).fetchone()[0]
            
            stats = [
                ["用户总数", user_count],
                ["好友关系数", friendship_count // 2],  # 除以2因为是双向关系
                ["消息总数", message_count],
                ["未读消息数", unread_count]
            ]
            
            print(tabulate(stats, headers=["统计项", "数量"], tablefmt="grid"))
        print()
    
    def search_user(self, keyword):
        """搜索用户"""
        print(f"🔍 搜索用户: '{keyword}'")
        print("=" * 60)
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, username, email, created_at 
                FROM users 
                WHERE username LIKE ? OR email LIKE ?
                ORDER BY id
            """, (f"%{keyword}%", f"%{keyword}%"))
            users = cursor.fetchall()
            
            if users:
                headers = ["ID", "用户名", "邮箱", "创建时间"]
                formatted_users = []
                for user in users:
                    formatted_user = list(user)
                    if formatted_user[3]:
                        formatted_user[3] = formatted_user[3][:19]
                    formatted_users.append(formatted_user)
                
                print(tabulate(formatted_users, headers=headers, tablefmt="grid"))
            else:
                print(f"未找到包含 '{keyword}' 的用户")
        print()
    
    def execute_custom_query(self, query):
        """执行自定义SQL查询"""
        print(f"🔧 执行查询: {query}")
        print("=" * 80)
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query)
                results = cursor.fetchall()
                
                if results:
                    # 获取列名
                    column_names = [description[0] for description in cursor.description]
                    print(tabulate(results, headers=column_names, tablefmt="grid"))
                else:
                    print("查询结果为空")
        except Exception as e:
            print(f"❌ 查询执行失败: {e}")
        print()

def main():
    """主函数"""
    print("🗄️  聊天后端数据库查看工具")
    print("=" * 60)
    
    viewer = DatabaseViewer()
    
    while True:
        print("\n📋 可用操作:")
        print("1. 显示所有表")
        print("2. 查看用户列表")
        print("3. 查看好友关系")
        print("4. 查看消息记录")
        print("5. 显示统计信息")
        print("6. 搜索用户")
        print("7. 执行自定义查询")
        print("8. 退出")
        
        choice = input("\n请选择操作 (1-8): ").strip()
        
        if choice == "1":
            viewer.show_tables()
        elif choice == "2":
            viewer.show_users()
        elif choice == "3":
            viewer.show_friendships()
        elif choice == "4":
            limit = input("显示多少条消息? (默认20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            viewer.show_messages(limit)
        elif choice == "5":
            viewer.show_user_stats()
        elif choice == "6":
            keyword = input("请输入搜索关键词: ").strip()
            if keyword:
                viewer.search_user(keyword)
        elif choice == "7":
            query = input("请输入SQL查询语句: ").strip()
            if query:
                viewer.execute_custom_query(query)
        elif choice == "8":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()
