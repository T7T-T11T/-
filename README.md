# 在线投票系统

基于 Flask + MySQL 的简单在线投票系统，支持管理员创建投票，普通用户参与投票。

## 功能特点

- ✅ 管理员可以创建投票（支持单选/多选）
- ✅ 普通用户无需登录即可参与投票
- ✅ 基于 IP 地址的防重复投票机制
- ✅ 实时显示投票结果和比例
- ✅ 支持投票的软删除功能
- ✅ 响应式前端界面
- ✅ 安全的密码哈希存储

## 技术栈

- **后端**：Flask, SQLAlchemy, MySQL
- **前端**：HTML, CSS, JavaScript
- **安全**：bcrypt 密码哈希, 会话安全配置

## 安装配置

### 1. 环境准备

- Python 3.7+
- MySQL 5.7+

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

1. 复制 `.env.example` 文件为 `.env`
2. 修改 `.env` 文件中的配置：

```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=voting_system

# 管理员密码（生产环境必须设置）
ADMIN_PASSWORD=your-strong-admin-password
```

### 4. 初始化数据库

```bash
python init_db.py
```

### 5. 启动应用

```bash
python app.py
```

### 6. 访问应用

- **本地地址**：http://localhost:5000
- **管理员登录**：http://localhost:5000/login
  - 用户名：admin
  - 密码：环境变量中设置的 ADMIN_PASSWORD

## 部署说明

### 生产环境部署

1. 设置强密码：通过 `ADMIN_PASSWORD` 环境变量设置强密码
2. 配置 SECRET_KEY：设置唯一的 SECRET_KEY
3. 关闭 DEBUG 模式：在 config.py 中设置 `DEBUG = False`
4. 使用 WSGI 服务器：推荐使用 Gunicorn

### 示例部署命令

```bash
# 使用 Gunicorn 启动
ADMIN_PASSWORD=your-strong-password gunicorn app:app -w 4 -b 0.0.0.0:5000
```

### Railway 部署步骤

1. **创建 Railway 账号**：访问 [Railway](https://railway.app) 并注册账号
2. **创建新项目**：点击 "New Project" → "Deploy from GitHub repo"
3. **连接 GitHub 仓库**：选择你的投票系统仓库
4. **配置环境变量**：
   - 点击 "Variables" → "Add Variable"
   - 添加以下环境变量：
     - `ADMIN_PASSWORD`：设置管理员密码
     - `SECRET_KEY`：设置唯一的密钥
     - `MYSQL_HOST`：使用 Railway 提供的 MySQL 主机
     - `MYSQL_PORT`：使用 Railway 提供的 MySQL 端口
     - `MYSQL_USER`：使用 Railway 提供的 MySQL 用户名
     - `MYSQL_PASSWORD`：使用 Railway 提供的 MySQL 密码
     - `MYSQL_DATABASE`：使用 Railway 提供的 MySQL 数据库名
5. **添加 MySQL 数据库**：
   - 点击 "Add Service" → "MySQL"
   - Railway 会自动创建数据库并提供连接信息
6. **部署应用**：
   - 点击 "Deploy" 按钮
   - Railway 会自动构建和部署应用
7. **访问应用**：
   - 部署完成后，Railway 会提供一个公共 URL
   - 使用该 URL 访问你的投票系统

### 部署注意事项

- **数据库初始化**：首次部署后，需要运行 `python init_db.py` 初始化数据库
  - 可以在 Railway 的 "Deployments" → "Run Command" 中执行
- **环境变量安全**：确保所有敏感信息都通过环境变量设置，不要硬编码在代码中
- **定期备份**：定期备份数据库，以防数据丢失
- **监控应用**：使用 Railway 的监控功能，及时发现并解决问题

## 安全注意事项

- 不要将 `.env` 文件提交到版本控制
- 在生产环境中设置强密码
- 定期更新依赖包
- 配置适当的防火墙规则
