# 在线投票系统规格文档

## 1. 项目概述

**项目名称**: Flask 在线投票系统
**项目类型**: Web 应用（前后端分离）
**核心功能**: 提供在线投票、查看投票结果等功能
**目标用户**: 需要进行投票活动的组织或个人

## 2. 技术栈

- **后端框架**: Flask (Python)
- **数据库**: MySQL
- **前端**: HTML + CSS + JavaScript (Jinja2 模板)
- **ORM**: SQLAlchemy
- **配置管理**: config.py

## 3. 功能需求

### 3.1 投票管理

- **创建投票**: 用户可以创建新的投票主题
  - 投票标题（必填，最大100字符）
  - 投票描述（可选，最大500字符）
  - 投票选项（至少2个选项，最多10个选项）
  - 单选/多选设置

- **查看投票列表**: 展示所有投票主题
  - 显示投票标题、创建时间、投票人数

- **查看投票详情**: 查看单个投票的详细信息和结果
  - 显示投票标题、描述、选项
  - 显示每个选项的票数和百分比
  - 以可视化方式展示投票结果（进度条）

- **删除投票**: 删除指定的投票（软删除）

### 3.2 投票参与

- **进行投票**: 用户选择选项并提交投票
  - 单选投票：只能选择一个选项
  - 多选投票：可以选择多个选项
  - 防止重复投票（基于 IP 地址）

- **查看结果**: 不需要登录即可查看投票结果

## 4. 数据库设计

### 4.1 表结构

#### polls 表（投票主题表）
- `id`: 主键，自增
- `title`: 投票标题，VARCHAR(100)，NOT NULL
- `description`: 投票描述，TEXT
- `is_multiple`: 是否多选，BOOLEAN，DEFAULT FALSE
- `is_deleted`: 是否删除（软删除），BOOLEAN，DEFAULT FALSE
- `created_at`: 创建时间，DATETIME
- `updated_at`: 更新时间，DATETIME

#### poll_options 表（投票选项表）
- `id`: 主键，自增
- `poll_id`: 所属投票ID，外键关联 polls 表
- `option_text`: 选项内容，VARCHAR(200)，NOT NULL
- `vote_count`: 投票数量，INT，DEFAULT 0
- `created_at`: 创建时间，DATETIME

#### votes 表（投票记录表）
- `id`: 主键，自增
- `poll_id`: 投票ID，外键关联 polls 表
- `ip_address`: 投票者IP地址，VARCHAR(45)
- `voted_at`: 投票时间，DATETIME

## 5. API 接口设计

### 5.1 投票相关接口

| 接口路径 | 方法 | 说明 | 请求参数 |
|---------|------|------|---------|
| `/` | GET | 首页，展示投票列表 | - |
| `/poll/create` | GET/POST | 创建投票 | title, description, is_multiple, options[] |
| `/poll/<id>` | GET | 查看投票详情和结果 | - |
| `/poll/<id>/vote` | POST | 提交投票 | option_ids[] |
| `/poll/<id>/delete` | POST | 删除投票 | - |

## 6. 前端页面

### 6.1 页面列表

1. **首页** (`index.html`)
   - 展示所有投票列表
   - 显示投票标题、创建时间、投票人数
   - 提供创建投票入口

2. **创建投票页** (`create_poll.html`)
   - 投票标题输入框
   - 投票描述输入框
   - 单选/多选切换
   - 动态添加/删除选项
   - 提交按钮

3. **投票详情页** (`poll_detail.html`)
   - 投票标题和描述
   - 投票选项列表（单选/多选）
   - 提交投票按钮
   - 投票结果展示（进度条+百分比+票数）

## 7. 项目结构

```
c:\Users\ctt37\Desktop\新建文件夹/
├── app.py                 # 应用入口
├── config.py             # 配置文件
├── models.py             # 数据库模型
├── init_db.py            # 数据库初始化脚本
├── templates/            # HTML 模板目录
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页模板
│   ├── create_poll.html  # 创建投票模板
│   └── poll_detail.html  # 投票详情模板
├── static/               # 静态资源目录
│   ├── css/
│   │   └── style.css     # 样式文件
│   └── js/
│       └── main.js       # JavaScript 文件
├── requirements.txt      # Python 依赖
├── .gitignore           # Git 忽略文件
└── history.md            # 版本历史记录
```

## 8. 配置项

### 8.1 配置文件内容

配置项包括：
- **SECRET_KEY**: Flask 密钥
- **MYSQL_HOST**: MySQL 主机地址
- **MYSQL_PORT**: MySQL 端口
- **MYSQL_USER**: MySQL 用户名
- **MYSQL_PASSWORD**: MySQL 密码
- **MYSQL_DATABASE**: MySQL 数据库名

## 9. 安全考虑

- 使用参数化查询防止 SQL 注入
- 对用户输入进行验证和过滤
- 基于 IP 地址防止重复投票
- 软删除机制保护数据

## 10. 验收标准

1. ✅ 可以成功创建投票主题
2. ✅ 可以查看所有投票列表
3. ✅ 可以查看单个投票详情
4. ✅ 可以进行投票（单选/多选）
5. ✅ 可以查看投票结果（百分比、票数）
6. ✅ 防止重复投票
7. ✅ 可以删除投票
8. ✅ 数据库表有完整的中文注释
9. ✅ 代码添加完整的 JSdoc 注释
10. ✅ 配置文件每行都有中文注释

## 11. 约束条件

- 每个投票至少2个选项，最多10个选项
- 投票标题最大100字符
- 投票描述最大500字符
- 每人每票只能投一次（基于IP限制）
