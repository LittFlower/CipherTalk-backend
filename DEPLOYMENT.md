# 部署指南

## 生产环境部署

### 1. 服务器环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python3和相关工具
sudo apt install python3 python3-pip python3-venv nginx mysql-server -y

# 安装MySQL开发包
sudo apt install libmysqlclient-dev -y
```

### 2. MySQL数据库配置

```bash
# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置MySQL
sudo mysql_secure_installation

# 创建数据库和用户
sudo mysql -u root -p
```

在MySQL中执行：
```sql
CREATE DATABASE chat_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'chatuser'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON chat_app.* TO 'chatuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. 应用部署

```bash
# 创建应用目录
sudo mkdir -p /var/www/chat_backend
sudo chown $USER:$USER /var/www/chat_backend

# 克隆或上传代码
cd /var/www/chat_backend
# 上传你的代码文件

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn

# 配置环境变量
cp .env.example .env
nano .env
```

### 4. 环境变量配置

编辑 `.env` 文件：
```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=chatuser
DB_PASSWORD=strong_password_here
DB_NAME=chat_app
JWT_SECRET_KEY=very-long-and-secure-jwt-secret-key-for-production
SECRET_KEY=another-very-secure-secret-key
DEBUG=false
```

### 5. 创建Systemd服务

```bash
sudo nano /etc/systemd/system/chat-backend.service
```

服务文件内容：
```ini
[Unit]
Description=Chat Backend API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/chat_backend
Environment=PATH=/var/www/chat_backend/venv/bin
ExecStart=/var/www/chat_backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start chat-backend
sudo systemctl enable chat-backend
sudo systemctl status chat-backend
```

### 6. Nginx反向代理配置

```bash
sudo nano /etc/nginx/sites-available/chat-backend
```

Nginx配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件处理（如果有的话）
    location /static {
        alias /var/www/chat_backend/static;
        expires 30d;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/chat-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL证书配置（使用Let's Encrypt）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 8. 防火墙配置

```bash
# 启用UFW防火墙
sudo ufw enable

# 允许SSH、HTTP和HTTPS
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# 检查状态
sudo ufw status
```

### 9. 监控和日志

查看应用日志：
```bash
# 应用日志
sudo journalctl -u chat-backend -f

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 10. 性能优化

#### Gunicorn优化
```bash
# 编辑服务文件中的ExecStart行
ExecStart=/var/www/chat_backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --bind 127.0.0.1:5000 \
    app:app
```

#### MySQL优化
编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`：
```ini
[mysqld]
innodb_buffer_pool_size = 128M
innodb_log_file_size = 32M
max_connections = 100
query_cache_size = 16M
```

### 11. 备份策略

创建数据库备份脚本：
```bash
#!/bin/bash
# backup_db.sh
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u chatuser -p chat_app > /var/backups/chat_app_$DATE.sql
find /var/backups -name "chat_app_*.sql" -mtime +7 -delete
```

设置定时备份：
```bash
sudo crontab -e
# 每天凌晨2点备份
0 2 * * * /path/to/backup_db.sh
```

## Docker部署（可选）

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "app:app"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DB_HOST=db
      - DB_USER=chatuser
      - DB_PASSWORD=password
      - DB_NAME=chat_app
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: chat_app
      MYSQL_USER: chatuser
      MYSQL_PASSWORD: password
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

## 维护和监控

1. **日志监控**: 定期检查应用和系统日志
2. **性能监控**: 使用工具如htop、iostat监控系统资源
3. **安全更新**: 定期更新系统和依赖包
4. **数据库维护**: 定期优化数据库表，清理旧数据
5. **备份验证**: 定期测试备份恢复流程
