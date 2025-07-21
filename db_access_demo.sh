#!/bin/bash
# 数据库访问方法演示脚本

echo "🗄️  聊天后端数据库访问方法演示"
echo "=================================="

echo ""
echo "📍 数据库文件位置:"
echo "   instance/chat_app.db"

echo ""
echo "🛠️  可用的访问方法:"
echo ""

echo "1️⃣ 快速检查 - check_db.py"
echo "   python check_db.py"
echo "   功能: 快速查看用户、好友、消息统计"
echo ""

echo "2️⃣ 交互式查看器 - db_viewer.py"  
echo "   python db_viewer.py"
echo "   功能: 菜单驱动的数据库浏览器"
echo ""

echo "3️⃣ Flask Shell - shell.py"
echo "   python shell.py"
echo "   功能: 使用ORM进行交互式查询"
echo ""

echo "4️⃣ 完整测试 - test_complete.py"
echo "   python test_complete.py"
echo "   功能: 端到端测试并验证数据库状态"
echo ""

echo "5️⃣ SQLite命令行工具"
echo "   sqlite3 instance/chat_app.db"
echo "   常用命令:"
echo "     .tables          - 查看所有表"
echo "     .schema users    - 查看表结构"
echo "     SELECT * FROM users; - 查询数据"
echo ""

echo "6️⃣ VS Code扩展"
echo "   安装 SQLite Viewer 扩展"
echo "   直接在编辑器中查看数据库"
echo ""

echo "📊 数据库表结构:"
echo "   users       - 用户信息"
echo "   friendships - 好友关系"  
echo "   messages    - 聊天消息"
echo ""

echo "🎯 验证操作步骤:"
echo "   1. 启动应用: python app.py"
echo "   2. 调用API进行操作"
echo "   3. 使用上述工具查看数据库变化"
echo ""

echo "💡 提示:"
echo "   - 每次API操作后都可以立即查看数据库变化"
echo "   - SQLite数据库文件可以直接复制备份"
echo "   - 删除数据库文件后重启应用会重新创建"
