# 聊天后端 API

基于 Python Flask + MySQL 的聊天应用后端API，支持用户注册登录、好友管理、消息发送等核心功能。

## 功能特性

- ✅ 用户注册/登录/修改密码
- ✅ JWT token 身份验证
- ✅ 好友添加/删除/列表查看
- ✅ 消息发送/接收
- ✅ 聊天历史记录
- ✅ 聊天列表（最近联系人）
- ✅ 消息已读状态管理
- ✅ 用户搜索功能

## 技术栈

- **后端框架**: Flask 2.3.3
- **数据库**: MySQL 8.0+
- **ORM**: SQLAlchemy
- **身份验证**: JWT (Flask-JWT-Extended)
- **密码加密**: bcrypt
- **数据序列化**: marshmallow

## 项目结构

```
chat_backend/
├── app.py                 # 应用主文件
├── requirements.txt       # 依赖包列表
├── .env.example          # 环境变量示例
├── DATABASE.md           # 数据库设计文档
├── models/               # 数据模型
│   ├── user.py          # 用户模型
│   ├── friendship.py    # 好友关系模型
│   └── message.py       # 消息模型
└── routes/               # API路由
    ├── auth.py          # 认证相关API
    ├── friend.py        # 好友管理API
    └── message.py       # 消息管理API
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd /path/to/project

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，选择数据库类型和设置连接信息
```

### 2. 数据库配置

#### 选项1: 使用 SQLite（推荐用于开发测试）
```bash
# 在 .env 文件中设置
DB_TYPE=sqlite
DB_NAME=chat_app
```

#### 选项2: 使用 MySQL（推荐用于生产环境）
```bash
# 创建数据库（在MySQL中执行）
CREATE DATABASE chat_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 在 .env 文件中设置
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=chat_app
```

详细的数据库表结构请查看 [DATABASE.md](DATABASE.md)

### 3. 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5001` 启动

### 4. 测试

```bash
# 测试循环导入修复
python test_imports.py

# 测试API功能（需要先启动应用）
python test_api.py
```

## API 文档

### 认证 API

#### 1. 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}
```

#### 2. 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "testuser",
    "password": "password123"
}
```

#### 3. 修改密码
```http
POST /api/auth/change_password
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "old_password": "oldpassword",
    "new_password": "newpassword"
}
```

#### 4. 获取用户信息
```http
GET /api/auth/profile
Authorization: Bearer <access_token>
```

### 好友管理 API

#### 1. 添加好友
```http
POST /api/friend/add
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "friend_username": "friendname"
}
```

#### 2. 获取好友列表
```http
GET /api/friend/list
Authorization: Bearer <access_token>
```

#### 3. 删除好友
```http
POST /api/friend/remove
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "friend_id": 2
}
```

#### 4. 搜索用户
```http
GET /api/friend/search?keyword=user
Authorization: Bearer <access_token>
```

### 消息管理 API

#### 1. 发送消息
```http
POST /api/message/send
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "receiver_id": 2,
    "content": "Hello, this is a message!",
    "message_type": "text"
}
```

#### 2. 获取聊天历史
```http
GET /api/message/history?friend_id=2&page=1&per_page=20
Authorization: Bearer <access_token>
```

#### 3. 获取聊天列表
```http
GET /api/message/chats
Authorization: Bearer <access_token>
```

#### 4. 获取最后一条消息
```http
GET /api/message/last?friend_id=2
Authorization: Bearer <access_token>
```

#### 5. 标记消息已读
```http
POST /api/message/mark_read
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "sender_id": 2
}
```

### 系统 API

#### 健康检查
```http
GET /api/health
```

## 响应格式

### 成功响应
```json
{
    "message": "操作成功",
    "data": {...}
}
```

### 错误响应
```json
{
    "error": "错误信息"
}
```

## 环境变量

创建 `.env` 文件并配置以下变量：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=chat_app

# JWT密钥
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

## 开发说明

### 数据库迁移

应用启动时会自动创建数据库表。如果需要手动创建，可以参考 `DATABASE.md` 中的SQL脚本。

### 身份验证

API使用JWT token进行身份验证。在请求头中添加：
```
Authorization: Bearer <access_token>
```

### 错误处理

所有API都包含完善的错误处理，返回适当的HTTP状态码和错误信息。

## 部署建议

1. **生产环境配置**
   - 使用环境变量管理敏感信息
   - 设置复杂的JWT密钥
   - 配置HTTPS
   - 使用专业的WSGI服务器（如Gunicorn）

2. **数据库优化**
   - 为查询频繁的字段添加索引
   - 定期备份数据库
   - 监控数据库性能

3. **安全考虑**
   - 实施API速率限制
   - 输入验证和SQL注入防护
   - 定期更新依赖包

## 许可证

本项目仅用于学习和教育目的。
