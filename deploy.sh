#!/bin/bash
# 一键部署脚本 - 适用于 Ubuntu/Debian 系统

set -e  # 遇到错误立即退出

echo "🚀 开始部署聊天后端 (SQLite版本)"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="chat-backend"
USER_NAME="chatapp"
PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
DOMAIN=""

# 函数：打印彩色消息
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：检查是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用 root 权限运行此脚本："
        echo "sudo $0"
        exit 1
    fi
}

# 函数：获取用户输入
get_user_input() {
    echo ""
    print_status "请提供部署配置信息："
    
    read -p "请输入域名 (如: chat.example.com): " DOMAIN
    if [ -z "$DOMAIN" ]; then
        print_warning "未输入域名，将使用服务器IP访问"
    fi
    
    read -p "是否安装SSL证书? (y/n): " INSTALL_SSL
}

# 函数：安装系统依赖
install_system_deps() {
    print_status "更新系统包..."
    apt update && apt upgrade -y
    
    print_status "安装系统依赖..."
    apt install -y python3 python3-pip python3-venv nginx supervisor git curl sqlite3
}

# 函数：创建用户
create_user() {
    print_status "创建部署用户..."
    if ! id "$USER_NAME" &>/dev/null; then
        adduser --disabled-password --gecos "" $USER_NAME
        usermod -aG sudo $USER_NAME
        print_status "用户 $USER_NAME 创建成功"
    else
        print_status "用户 $USER_NAME 已存在"
    fi
}

# 函数：部署应用代码
deploy_app() {
    print_status "部署应用代码..."
    
    # 创建项目目录
    mkdir -p $PROJECT_DIR
    
    # 复制当前目录的所有文件到部署目录
    cp -r . $PROJECT_DIR/
    
    # 设置目录权限
    chown -R $USER_NAME:$USER_NAME $PROJECT_DIR
    
    # 切换到项目用户
    sudo -u $USER_NAME bash << EOF
cd $PROJECT_DIR

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建日志目录
mkdir -p logs

# 创建实例目录
mkdir -p instance

# 复制生产环境配置
if [ ! -f .env ]; then
    cp .env.production .env
    echo "⚠️  请编辑 .env 文件设置生产环境配置"
fi

# 初始化数据库
python3 -c "from app import create_tables; create_tables(); print('数据库初始化完成')"

EOF
}

# 函数：配置 Gunicorn
setup_gunicorn() {
    print_status "配置 Gunicorn..."
    
    cat > $PROJECT_DIR/gunicorn.conf.py << 'EOF'
import multiprocessing

bind = "127.0.0.1:8000"
backlog = 2048
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
accesslog = "/home/chatapp/chat-backend/logs/access.log"
errorlog = "/home/chatapp/chat-backend/logs/error.log"
loglevel = "info"
proc_name = "chat-backend"
user = "chatapp"
group = "chatapp"
EOF

    # 创建启动脚本
    cat > $PROJECT_DIR/start.sh << 'EOF'
#!/bin/bash
cd /home/chatapp/chat-backend
source venv/bin/activate
exec gunicorn -c gunicorn.conf.py app:app
EOF

    chmod +x $PROJECT_DIR/start.sh
    chown $USER_NAME:$USER_NAME $PROJECT_DIR/start.sh
}

# 函数：配置 Supervisor
setup_supervisor() {
    print_status "配置 Supervisor..."
    
    cat > /etc/supervisor/conf.d/chat-backend.conf << 'EOF'
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
EOF

    # 重新加载配置并启动服务
    supervisorctl reread
    supervisorctl update
    supervisorctl start chat-backend
    
    print_status "等待服务启动..."
    sleep 3
    supervisorctl status chat-backend
}

# 函数：配置 Nginx
setup_nginx() {
    print_status "配置 Nginx..."
    
    local server_name="localhost"
    if [ ! -z "$DOMAIN" ]; then
        server_name="$DOMAIN"
    fi
    
    cat > /etc/nginx/sites-available/chat-backend << EOF
server {
    listen 80;
    server_name $server_name;

    access_log /var/log/nginx/chat-backend-access.log;
    error_log /var/log/nginx/chat-backend-error.log;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /api/health {
        proxy_pass http://127.0.0.1:8000/api/health;
        access_log off;
    }
}
EOF

    # 启用站点
    ln -sf /etc/nginx/sites-available/chat-backend /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    nginx -t
    
    # 重启 Nginx
    systemctl restart nginx
    systemctl enable nginx
}

# 函数：安装 SSL 证书
install_ssl() {
    if [ "$INSTALL_SSL" = "y" ] && [ ! -z "$DOMAIN" ]; then
        print_status "安装 SSL 证书..."
        
        # 安装 Certbot
        apt install -y certbot python3-certbot-nginx
        
        # 获取证书
        certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN
        
        # 设置自动续期
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
        
        print_status "SSL 证书安装完成"
    fi
}

# 函数：配置防火墙
setup_firewall() {
    print_status "配置防火墙..."
    
    # 安装并配置 UFW
    apt install -y ufw
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80
    ufw allow 443
    ufw --force enable
    
    print_status "防火墙配置完成"
}

# 函数：创建管理脚本
create_management_scripts() {
    print_status "创建管理脚本..."
    
    # 备份脚本
    cat > $PROJECT_DIR/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/chatapp/backups"
DB_FILE="/home/chatapp/chat-backend/instance/chat_app_prod.db"

mkdir -p $BACKUP_DIR

if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_DIR/chat_app_$DATE.db"
    echo "备份完成: $BACKUP_DIR/chat_app_$DATE.db"
    find $BACKUP_DIR -name "chat_app_*.db" -mtime +7 -delete
else
    echo "数据库文件不存在: $DB_FILE"
fi
EOF

    # 健康检查脚本
    cat > $PROJECT_DIR/health_check.sh << 'EOF'
#!/bin/bash
HEALTH_URL="http://localhost:8000/api/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ "$RESPONSE" = "200" ]; then
    echo "✅ 服务正常运行"
    exit 0
else
    echo "❌ 服务异常，HTTP状态码: $RESPONSE"
    exit 1
fi
EOF

    # 更新脚本
    cat > $PROJECT_DIR/update.sh << 'EOF'
#!/bin/bash
echo "开始更新聊天后端应用..."

# 备份数据库
./backup.sh

# 停止服务
sudo supervisorctl stop chat-backend

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 重启服务
sudo supervisorctl start chat-backend

echo "更新完成！"
echo "检查服务状态:"
sudo supervisorctl status chat-backend
EOF

    # 设置执行权限
    chmod +x $PROJECT_DIR/backup.sh
    chmod +x $PROJECT_DIR/health_check.sh
    chmod +x $PROJECT_DIR/update.sh
    
    chown $USER_NAME:$USER_NAME $PROJECT_DIR/backup.sh
    chown $USER_NAME:$USER_NAME $PROJECT_DIR/health_check.sh
    chown $USER_NAME:$USER_NAME $PROJECT_DIR/update.sh
    
    # 设置定时备份
    sudo -u $USER_NAME bash -c '(crontab -l 2>/dev/null; echo "0 2 * * * /home/chatapp/chat-backend/backup.sh") | crontab -'
}

# 函数：运行最终测试
run_tests() {
    print_status "运行部署测试..."
    
    # 检查服务状态
    print_status "检查服务状态:"
    supervisorctl status chat-backend
    
    # 检查端口
    print_status "检查端口监听:"
    netstat -tlnp | grep :8000 || print_warning "端口 8000 未监听"
    
    # 健康检查
    print_status "健康检查:"
    sleep 2
    if curl -s http://localhost:8000/api/health > /dev/null; then
        print_status "✅ 健康检查通过"
    else
        print_error "❌ 健康检查失败"
    fi
    
    # 检查数据库
    print_status "检查数据库:"
    sudo -u $USER_NAME bash -c "cd $PROJECT_DIR && source venv/bin/activate && python3 check_db.py"
}

# 函数：显示部署信息
show_deployment_info() {
    echo ""
    echo "🎉 部署完成！"
    echo "=================================="
    echo ""
    echo "📋 部署信息:"
    echo "  - 应用目录: $PROJECT_DIR"
    echo "  - 用户: $USER_NAME"
    echo "  - 数据库: SQLite (instance/chat_app_prod.db)"
    
    if [ ! -z "$DOMAIN" ]; then
        if [ "$INSTALL_SSL" = "y" ]; then
            echo "  - 访问地址: https://$DOMAIN"
        else
            echo "  - 访问地址: http://$DOMAIN"
        fi
    else
        echo "  - 访问地址: http://$(curl -s ifconfig.me 2>/dev/null || echo "服务器IP")"
    fi
    
    echo ""
    echo "🛠️  管理命令:"
    echo "  - 查看服务状态: sudo supervisorctl status chat-backend"
    echo "  - 重启服务: sudo supervisorctl restart chat-backend"
    echo "  - 查看日志: sudo supervisorctl tail -f chat-backend"
    echo "  - 健康检查: $PROJECT_DIR/health_check.sh"
    echo "  - 备份数据库: $PROJECT_DIR/backup.sh"
    echo ""
    echo "📁 重要文件:"
    echo "  - 配置文件: $PROJECT_DIR/.env"
    echo "  - 数据库: $PROJECT_DIR/instance/chat_app_prod.db"
    echo "  - 日志目录: $PROJECT_DIR/logs/"
    echo ""
    echo "⚠️  安全提醒:"
    echo "  - 请修改 .env 文件中的密钥"
    echo "  - 定期备份数据库文件"
    echo "  - 监控应用日志"
    
    if [ "$INSTALL_SSL" != "y" ] && [ ! -z "$DOMAIN" ]; then
        print_warning "建议为域名配置SSL证书以提高安全性"
    fi
}

# 主函数
main() {
    check_root
    get_user_input
    
    install_system_deps
    create_user
    deploy_app
    setup_gunicorn
    setup_supervisor
    setup_nginx
    install_ssl
    setup_firewall
    create_management_scripts
    run_tests
    show_deployment_info
    
    print_status "🎊 恭喜！聊天后端部署成功！"
}

# 脚本入口
main "$@"
