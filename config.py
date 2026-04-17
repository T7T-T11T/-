# -*- coding: utf-8 -*-
"""
Flask 应用配置文件
包含数据库连接、Flask 密钥等配置信息
"""


class Config:
    """Flask 应用配置类"""

    # Flask 密钥，用于会话管理和 CSRF 保护
    SECRET_KEY = 'your-secret-key-change-in-production'

    # MySQL 数据库配置
    MYSQL_HOST = 'localhost'          # MySQL 服务器主机地址
    MYSQL_PORT = 3306                 # MySQL 服务器端口
    MYSQL_USER = 'root'               # MySQL 用户名
    MYSQL_PASSWORD = 'your-password'  # MySQL 密码
    MYSQL_DATABASE = 'voting_system'  # MySQL 数据库名称

    # SQLAlchemy 数据库 URI 格式
    # 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'

    # 是否追踪对象修改（建议关闭以提升性能）
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 应用配置
    DEBUG = True                      # 调试模式开关（生产环境应设为 False）
    HOST = '0.0.0.0'                  # 服务器监听地址
    PORT = 5000                       # 服务器监听端口

    # 每页显示的投票数量（分页用）
    POLLS_PER_PAGE = 10

    # 投票选项限制
    MIN_OPTIONS = 2                  # 每个投票最少选项数
    MAX_OPTIONS = 10                 # 每个投票最多选项数

    # 投票标题和描述长度限制
    MAX_TITLE_LENGTH = 100           # 投票标题最大字符数
    MAX_DESCRIPTION_LENGTH = 500     # 投票描述最大字符数
    MAX_OPTION_TEXT_LENGTH = 200    # 选项文本最大字符数
