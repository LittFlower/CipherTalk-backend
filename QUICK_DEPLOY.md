# 🚀 SQLite 部署快速指南

## 方式一：一键自动部署（推荐）

### 1. 准备服务器
```bash
# 确保服务器已安装基本工具
sudo apt update && sudo apt install -y git curl

# 将项目上传到服务器
scp -r . user@your-server:/tmp/chat-backend
```

### 2. 运行一键部署脚本
```bash
# 在服务器上执行
cd /tmp/chat-backend
sudo ./deploy.sh
```

部署脚本会自动：
- ✅ 安装所有系统依赖
- ✅ 创建专用用户和目录
- ✅ 配置 Python 虚拟环境
- ✅ 初始化 SQLite 数据库
- ✅ 配置 Gunicorn + Supervisor
- ✅ 配置 Nginx 反向代理
- ✅ 可选安装 SSL 证书
- ✅ 设置防火墙和安全配置
- ✅ 创建管理脚本和定时备份

### 3. 完成部署
部署完成后，访问你的服务器地址即可使用 API。

---

## 方式二：手动部署

如果需要自定义配置，请参考 `SQLITE_DEPLOYMENT.md` 详细指南。

---

## 管理命令

### 服务管理
```bash
# 查看服务状态
sudo supervisorctl status chat-backend

# 重启服务
sudo supervisorctl restart chat-backend

# 查看日志
sudo supervisorctl tail -f chat-backend
```

### 数据库管理
```bash
# 切换到应用用户
sudo su - chatapp
cd /home/chatapp/chat-backend

# 查看数据库状态
./health_check.sh

# 手动备份数据库
./backup.sh

# 查看数据库内容
source venv/bin/activate
python3 check_db.py
```

### 应用更新
```bash
# 应用更新（如果有新版本）
sudo su - chatapp
cd /home/chatapp/chat-backend
./update.sh
```

---

## 重要文件位置

- **应用目录**: `/home/chatapp/chat-backend/`
- **数据库文件**: `/home/chatapp/chat-backend/instance/chat_app_prod.db`
- **配置文件**: `/home/chatapp/chat-backend/.env`
- **日志文件**: `/home/chatapp/chat-backend/logs/`
- **备份目录**: `/home/chatapp/backups/`

---

## 安全建议

1. **修改默认密钥**
   ```bash
   sudo su - chatapp
   cd /home/chatapp/chat-backend
   nano .env
   # 修改 JWT_SECRET_KEY 和 SECRET_KEY
   ```

2. **启用 HTTPS**
   - 如果有域名，建议使用 SSL 证书
   - 部署脚本可以自动配置 Let's Encrypt

3. **定期备份**
   - 系统已自动设置每日凌晨2点备份
   - 手动备份：`./backup.sh`

4. **监控日志**
   ```bash
   # 查看错误日志
   tail -f /home/chatapp/chat-backend/logs/error.log
   
   # 查看访问日志
   tail -f /var/log/nginx/chat-backend-access.log
   ```

---

## 故障排除

### 服务无法启动
```bash
# 检查日志
sudo supervisorctl tail chat-backend

# 检查端口占用
sudo netstat -tlnp | grep :8000

# 手动测试启动
sudo su - chatapp
cd /home/chatapp/chat-backend
source venv/bin/activate
python3 app.py
```

### 数据库问题
```bash
# 检查数据库文件权限
ls -la /home/chatapp/chat-backend/instance/

# 重新初始化数据库
sudo su - chatapp
cd /home/chatapp/chat-backend
source venv/bin/activate
python3 -c "from app import create_tables; create_tables()"
```

### 网络访问问题
```bash
# 检查防火墙
sudo ufw status

# 检查 Nginx 配置
sudo nginx -t

# 测试本地访问
curl http://localhost:8000/api/health
```

---

## API 测试

部署完成后，可以使用以下命令测试 API：

```bash
# 健康检查
curl http://your-domain.com/api/health

# 用户注册
curl -X POST http://your-domain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"123456"}'

# 用户登录
curl -X POST http://your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'
```

使用返回的 token 进行其他 API 测试。
