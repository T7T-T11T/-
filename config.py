# -*- coding: utf-8 -*-
"""
Flask 应用配置文件
包含数据库连接、Flask 密钥等配置信息
"""

import os


class Config:
    """Flask 应用配置类"""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'voting_system')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000

    POLLS_PER_PAGE = 10

    MIN_OPTIONS = 2
    MAX_OPTIONS = 10

    MAX_TITLE_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    MAX_OPTION_TEXT_LENGTH = 200

    # 会话配置
    SESSION_TYPE = 'filesystem'  # 会话存储类型
    SESSION_PERMANENT = False  # 会话是否持久化
    SESSION_USE_SIGNER = True  # 会话使用签名
    SESSION_COOKIE_SECURE = False  # HTTPS 时设置为 True
    SESSION_COOKIE_HTTPONLY = True  # 防止 JavaScript 访问会话 cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # 防止 CSRF 攻击

    # 密码哈希
    PASSWORD_HASH_SCHEME = 'bcrypt'  # 密码哈希算法
