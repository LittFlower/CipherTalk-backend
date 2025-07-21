# 数据库访问指南

## 📋 概述

本项目使用 SQLite 数据库存储数据，数据库文件位于 `instance/chat_app.db`。以下是几种访问和查看数据库的方法：

## 🛠️ 方法1：使用项目提供的工具

### 1. 简单检查脚本
```bash
python check_db.py
```
快速查看数据库中的用户、好友关系、消息等信息。

### 2. 交互式数据库查看器
```bash
python db_viewer.py
```
提供菜单式界面，可以：
- 查看所有表
- 浏览用户列表
- 查看好友关系
- 查看消息记录
- 显示统计信息
- 搜索用户
- 执行自定义SQL查询

### 3. Flask Shell 交互环境
```bash
python shell.py
```
进入Python交互式环境，可以直接使用ORM查询：
```python
# 查看所有用户
User.query.all()

# 查找特定用户
User.query.filter_by(username='alice').first()

# 查看用户数量
User.query.count()

# 查看所有消息
Message.query.all()
```

## 🔧 方法2：使用命令行工具

### 1. 使用 sqlite3 命令行工具
```bash
# 进入数据库
sqlite3 instance/chat_app.db

# 查看所有表
.tables

# 查看表结构
.schema users

# 查询数据
SELECT * FROM users;
SELECT * FROM messages LIMIT 10;
SELECT * FROM friendships;

# 退出
.exit
```

### 2. 常用SQL查询示例
```sql
-- 查看所有用户
SELECT id, username, email, created_at FROM users;

-- 查看好友关系（去重）
SELECT DISTINCT 
    u1.username as user, 
    u2.username as friend, 
    f.created_at 
FROM friendships f
JOIN users u1 ON f.user_id = u1.id
JOIN users u2 ON f.friend_id = u2.id
WHERE f.status = 'accepted'
AND f.user_id < f.friend_id;  -- 避免重复显示

-- 查看最近的消息
SELECT 
    u1.username as sender,
    u2.username as receiver,
    m.content,
    m.created_at
FROM messages m
JOIN users u1 ON m.sender_id = u1.id
JOIN users u2 ON m.receiver_id = u2.id
ORDER BY m.created_at DESC
LIMIT 10;

-- 统计信息
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM messages) as total_messages,
    (SELECT COUNT(*) FROM friendships WHERE status='accepted') / 2 as total_friendships;
```

## 🔍 方法3：使用图形化工具

### 1. DB Browser for SQLite
下载地址：https://sqlitebrowser.org/
- 跨平台的SQLite数据库浏览器
- 可视化查看表结构和数据
- 支持SQL查询和数据编辑

### 2. VS Code 扩展
安装 SQLite Viewer 扩展，可以在VS Code中直接查看数据库。

## 📊 完整测试流程

运行完整的测试和验证流程：
```bash
# 1. 启动应用（在另一个终端）
python app.py

# 2. 运行完整测试（在新终端）
python test_complete.py
```

这个脚本会：
1. 检查初始数据库状态
2. 注册多个测试用户
3. 添加好友关系
4. 发送消息
5. 每步之后检查数据库状态

## 🚀 实时验证操作

### 验证用户注册
1. 调用注册API
2. 运行 `python check_db.py` 查看新用户
3. 确认用户信息正确存储

### 验证好友添加
1. 调用添加好友API
2. 检查数据库中的 friendships 表
3. 确认双向好友关系已创建

### 验证消息发送
1. 调用发送消息API
2. 查看 messages 表
3. 确认消息内容、发送者、接收者信息

## 🎯 调试技巧

### 1. 查看API请求日志
应用运行时会在控制台显示所有API请求。

### 2. 数据库备份
```bash
# 备份数据库
cp instance/chat_app.db instance/chat_app_backup.db

# 恢复数据库
cp instance/chat_app_backup.db instance/chat_app.db
```

### 3. 重置数据库
```bash
# 删除数据库文件，重新创建
rm instance/chat_app.db
python app.py  # 重新创建表
```

## 📝 常见问题

### Q: 数据库文件在哪里？
A: `instance/chat_app.db`

### Q: 如何查看实时的数据变化？
A: 每次API操作后运行 `python check_db.py`

### Q: 如何备份测试数据？
A: 复制 `instance/chat_app.db` 文件

### Q: 如何清空数据库重新测试？
A: 删除 `instance/chat_app.db` 文件，重启应用

## 🔗 相关文件

- `check_db.py` - 简单数据库检查
- `db_viewer.py` - 交互式数据库查看器  
- `shell.py` - Flask交互式环境
- `test_complete.py` - 完整测试流程
- `test_api.py` - API测试脚本
