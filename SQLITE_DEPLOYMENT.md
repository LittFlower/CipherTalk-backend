# SQLite 部署指南

## 🚀 使用 SQLite 在服务器上部署聊天后端

### 📋 SQLite 的优势

- ✅ **零配置**：无需安装和配置数据库服务器
- ✅ **轻量级**：数据库就是一个文件
- ✅ **高性能**：对于中小型应用性能优秀
- ✅ **可靠性**：支持事务，数据安全
- ✅ **便携性**：数据库文件可以直接复制备份

### 🛠️ 服务器环境准备

#### 1. 系统要求
```bash
# Ubuntu/Debian 系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和必要工具
sudo apt install python3 python3-pip python3-venv nginx supervisor git -y

# CentOS/RHEL 系统
sudo yum update -y
sudo yum install python3 python3-pip nginx supervisor git -y
```

#### 2. 创建部署用户
```bash
# 创建专用部署用户
sudo adduser chatapp
sudo usermod -aG sudo chatapp

# 切换到部署用户
sudo su - chatapp
```

### 📁 项目部署

#### 1. 创建项目目录
```bash
# 创建项目目录
mkdir -p /home/chatapp/chat-backend
cd /home/chatapp/chat-backend

# 上传或克隆项目文件
# 方法1: 使用 git (如果有仓库)
# git clone your-repo-url .

# 方法2: 手动上传文件
# 将本地项目文件上传到服务器
```

#### 2. 创建 Python 虚拟环境
```bash
cd /home/chatapp/chat-backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装生产环境所需的 WSGI 服务器
pip install gunicorn
```

#### 3. 配置环境变量
```bash
# 创建生产环境配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

生产环境 `.env` 配置：
```bash
# 数据库配置 - 使用 SQLite
DB_TYPE=sqlite
DB_NAME=chat_app_prod

# 安全配置
JWT_SECRET_KEY=your-very-long-and-secure-jwt-secret-key-for-production-use
SECRET_KEY=another-very-secure-secret-key-for-flask

# 生产模式
DEBUG=false

# 可选：如果需要CORS支持
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 4. 创建数据库和测试
```bash
# 激活虚拟环境
source venv/bin/activate

# 创建数据库表
python3 -c "from app import app, create_tables; create_tables(); print('数据库初始化完成')"

# 测试应用是否能正常启动
python3 -c "from app import app; print('应用导入成功')"
```

### 🔧 生产环境配置

#### 1. 创建 Gunicorn 配置文件
```bash
# 创建 gunicorn 配置
nano /home/chatapp/chat-backend/gunicorn.conf.py
```

`gunicorn.conf.py` 内容：
```python
# Gunicorn 配置文件
import multiprocessing

# 服务器套接字
bind = "127.0.0.1:8000"
backlog = 2048

# 工作进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# 重启
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 日志
accesslog = "/home/chatapp/chat-backend/logs/access.log"
errorlog = "/home/chatapp/chat-backend/logs/error.log"
loglevel = "info"

# 进程命名
proc_name = "chat-backend"

# 用户权限
user = "chatapp"
group = "chatapp"

# 临时目录
tmp_upload_dir = None
```

#### 2. 创建日志目录
```bash
mkdir -p /home/chatapp/chat-backend/logs
```

#### 3. 创建启动脚本
```bash
nano /home/chatapp/chat-backend/start.sh
```

`start.sh` 内容：
```bash
#!/bin/bash
cd /home/chatapp/chat-backend
source venv/bin/activate
exec gunicorn -c gunicorn.conf.py app:app
```

```bash
# 添加执行权限
chmod +x /home/chatapp/chat-backend/start.sh
```

### 🔄 系统服务配置

#### 1. 创建 Supervisor 配置
```bash
sudo nano /etc/supervisor/conf.d/chat-backend.conf
```

配置内容：
```ini
[program:chat-backend]
command=/home/chatapp/chat-backend/start.sh
directory=/home/chatapp/chat-backend
user=chatapp
group=chatapp
autostart=true
autorestart=true
startsecs=5
startretries=3
redirect_stderr=true
stdout_logfile=/home/chatapp/chat-backend/logs/supervisor.log
stdout_logfile_maxbytes=20MB
stdout_logfile_backups=5
environment=PATH="/home/chatapp/chat-backend/venv/bin"
```

#### 2. 启动和管理服务
```bash
# 重新加载 supervisor 配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start chat-backend

# 查看状态
sudo supervisorctl status chat-backend

# 重启服务
sudo supervisorctl restart chat-backend

# 查看日志
sudo supervisorctl tail -f chat-backend
```

### 🌐 Nginx 反向代理配置

#### 1. 创建 Nginx 站点配置
```bash
sudo nano /etc/nginx/sites-available/chat-backend
```

配置内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    # 日志
    access_log /var/log/nginx/chat-backend-access.log;
    error_log /var/log/nginx/chat-backend-error.log;

    # 客户端上传大小限制
    client_max_body_size 10M;

    # API 代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 健康检查
    location /api/health {
        proxy_pass http://127.0.0.1:8000/api/health;
        access_log off;
    }

    # 静态文件（如果有）
    location /static {
        alias /home/chatapp/chat-backend/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 2. 启用站点
```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/chat-backend /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 🔒 SSL 证书配置 (HTTPS)

#### 使用 Let's Encrypt (推荐)
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 🔥 防火墙配置

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 📊 数据库管理

#### 1. 数据库备份脚本
```bash
nano /home/chatapp/chat-backend/backup.sh
```

```bash
#!/bin/bash
# SQLite 数据库备份脚本

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/chatapp/backups"
DB_FILE="/home/chatapp/chat-backend/instance/chat_app_prod.db"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_DIR/chat_app_$DATE.db"
    echo "备份完成: $BACKUP_DIR/chat_app_$DATE.db"
    
    # 删除7天前的备份
    find $BACKUP_DIR -name "chat_app_*.db" -mtime +7 -delete
else
    echo "数据库文件不存在: $DB_FILE"
fi
```

```bash
chmod +x /home/chatapp/chat-backend/backup.sh

# 设置定时备份
crontab -e
# 添加：每天凌晨2点备份
# 0 2 * * * /home/chatapp/chat-backend/backup.sh
```

#### 2. 数据库查看工具
```bash
# 在服务器上查看数据库
cd /home/chatapp/chat-backend
source venv/bin/activate
python3 check_db.py

# 或使用 SQLite 命令行
sqlite3 instance/chat_app_prod.db
```

### 📈 监控和日志

#### 1. 日志查看
```bash
# 应用日志
tail -f /home/chatapp/chat-backend/logs/error.log
tail -f /home/chatapp/chat-backend/logs/access.log

# Supervisor 日志
sudo supervisorctl tail -f chat-backend

# Nginx 日志
sudo tail -f /var/log/nginx/chat-backend-access.log
sudo tail -f /var/log/nginx/chat-backend-error.log
```

#### 2. 性能监控脚本
```bash
nano /home/chatapp/chat-backend/monitor.sh
```

```bash
#!/bin/bash
# 简单的监控脚本

echo "=== 聊天后端服务状态 ==="
echo "时间: $(date)"
echo ""

echo "服务状态:"
sudo supervisorctl status chat-backend

echo ""
echo "内存使用:"
ps aux | grep gunicorn | grep -v grep

echo ""
echo "数据库大小:"
ls -lh /home/chatapp/chat-backend/instance/*.db 2>/dev/null || echo "数据库文件不存在"

echo ""
echo "磁盘使用:"
df -h /home/chatapp

echo ""
echo "最近错误 (最后10行):"
tail -10 /home/chatapp/chat-backend/logs/error.log 2>/dev/null || echo "无错误日志"
```

### 🔄 更新和维护

#### 1. 应用更新脚本
```bash
nano /home/chatapp/chat-backend/update.sh
```

```bash
#!/bin/bash
# 应用更新脚本

echo "开始更新聊天后端应用..."

# 备份数据库
./backup.sh

# 停止服务
sudo supervisorctl stop chat-backend

# 激活虚拟环境
source venv/bin/activate

# 更新代码 (如果使用 git)
# git pull origin main

# 更新依赖
pip install -r requirements.txt

# 重启服务
sudo supervisorctl start chat-backend

echo "更新完成！"
echo "检查服务状态:"
sudo supervisorctl status chat-backend
```

#### 2. 健康检查
```bash
# 创建健康检查脚本
nano /home/chatapp/chat-backend/health_check.sh
```

```bash
#!/bin/bash
# 健康检查脚本

HEALTH_URL="http://localhost:8000/api/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ "$RESPONSE" = "200" ]; then
    echo "✅ 服务正常运行"
    exit 0
else
    echo "❌ 服务异常，HTTP状态码: $RESPONSE"
    # 可以添加重启逻辑
    # sudo supervisorctl restart chat-backend
    exit 1
fi
```

### 🚀 部署检查清单

部署完成后，检查以下项目：

```bash
# 1. 服务状态
sudo supervisorctl status chat-backend

# 2. 端口监听
sudo netstat -tlnp | grep :8000

# 3. Nginx 状态
sudo systemctl status nginx

# 4. 健康检查
curl http://your-domain.com/api/health

# 5. 数据库检查
cd /home/chatapp/chat-backend && python3 check_db.py

# 6. 日志检查
tail -f logs/error.log

# 7. SSL 证书 (如果配置了)
curl -I https://your-domain.com/api/health
```

### 💡 性能优化建议

1. **SQLite 优化**
   ```python
   # 在 config.py 中添加 SQLite 优化
   SQLALCHEMY_ENGINE_OPTIONS = {
       'pool_pre_ping': True,
       'pool_recycle': 300,
       'connect_args': {
           'check_same_thread': False,
           'timeout': 20
       }
   }
   ```

2. **Gunicorn 优化**
   - 根据服务器 CPU 核心数调整 workers 数量
   - 监控内存使用，适当调整 max_requests

3. **Nginx 优化**
   - 启用 gzip 压缩
   - 配置适当的缓存策略

4. **定期维护**
   - 定期备份数据库
   - 监控日志文件大小
   - 定期更新系统和依赖包

这样部署的 SQLite 版本适合大多数中小型聊天应用，简单可靠且易于维护！
