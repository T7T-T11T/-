# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于创建数据库和表结构
"""

import pymysql
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from config import Config


def create_database():
    """创建数据库（如果不存在）"""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )

        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"数据库 '{Config.MYSQL_DATABASE}' 创建成功或已存在")

        connection.commit()

    except pymysql.err.OperationalError as e:
        print(f"无法连接到 MySQL 服务器：{e}")
        print("请确保 MySQL 服务已启动，并且 config.py 中的配置正确")
        return False

    except Exception as e:
        print(f"创建数据库时出错：{e}")
        return False

    finally:
        if 'connection' in locals():
            connection.close()

    return True


def create_tables():
    """创建数据表"""
    from src.app import app, db

    with app.app_context():
        try:
            # 先删除旧的 users 表（如果存在），因为字段结构已经改变
            from src.models import User
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if inspector.has_table('users'):
                User.__table__.drop(db.engine)
                print("旧的 users 表已删除")
            
            # 创建所有表
            db.create_all()
            print("数据表创建成功")

            from sqlalchemy import text

            result = db.session.execute(text("SHOW CREATE TABLE polls"))
            print("\n=== polls 表结构 ===")
            for row in result:
                print(row[1])

            result = db.session.execute(text("SHOW CREATE TABLE poll_options"))
            print("\n=== poll_options 表结构 ===")
            for row in result:
                print(row[1])

            result = db.session.execute(text("SHOW CREATE TABLE votes"))
            print("\n=== votes 表结构 ===")
            for row in result:
                print(row[1])

            result = db.session.execute(text("SHOW CREATE TABLE users"))
            print("\n=== users 表结构 ===")
            for row in result:
                print(row[1])

        except Exception as e:
            print(f"创建数据表时出错：{e}")
            return False

    return True


def add_comments():
    """为数据库表和字段添加中文注释"""
    from src.app import app, db
    from sqlalchemy import text

    with app.app_context():
        try:
            # 为 polls 表添加注释
            db.session.execute(text("""
                ALTER TABLE polls
                MODIFY COLUMN id INT AUTO_INCREMENT COMMENT '投票ID',
                MODIFY COLUMN title VARCHAR(100) NOT NULL COMMENT '投票标题',
                MODIFY COLUMN description TEXT COMMENT '投票描述',
                MODIFY COLUMN is_multiple TINYINT(1) DEFAULT 0 COMMENT '是否多选',
                MODIFY COLUMN is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否已删除',
                MODIFY COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                MODIFY COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
            """))
            print("polls 表注释添加成功")

            # 为 poll_options 表添加注释
            db.session.execute(text("""
                ALTER TABLE poll_options
                MODIFY COLUMN id INT AUTO_INCREMENT COMMENT '选项ID',
                MODIFY COLUMN poll_id INT NOT NULL COMMENT '所属投票ID',
                MODIFY COLUMN option_text VARCHAR(200) NOT NULL COMMENT '选项内容',
                MODIFY COLUMN vote_count INT DEFAULT 0 COMMENT '得票数',
                MODIFY COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
            """))
            print("poll_options 表注释添加成功")

            # 为 votes 表添加注释
            db.session.execute(text("""
                ALTER TABLE votes
                MODIFY COLUMN id INT AUTO_INCREMENT COMMENT '投票记录ID',
                MODIFY COLUMN poll_id INT NOT NULL COMMENT '投票ID',
                MODIFY COLUMN ip_address VARCHAR(45) NOT NULL COMMENT '投票者IP地址',
                MODIFY COLUMN user_id VARCHAR(36) COMMENT '用户浏览器标识符',
                MODIFY COLUMN voted_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '投票时间'
            """))
            print("votes 表注释添加成功")

            # 为 users 表添加注释
            db.session.execute(text("""
                ALTER TABLE users
                MODIFY COLUMN id INT AUTO_INCREMENT COMMENT '用户ID',
                MODIFY COLUMN username VARCHAR(50) NOT NULL COMMENT '用户名',
                MODIFY COLUMN password_hash VARCHAR(100) NOT NULL COMMENT '密码哈希',
                MODIFY COLUMN is_admin TINYINT(1) DEFAULT 0 COMMENT '是否管理员',
                MODIFY COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
            """))
            print("users 表注释添加成功")

            db.session.commit()
            print("\n所有表和字段的中文注释添加成功")

        except Exception as e:
            print(f"添加注释时出错：{e}")
            db.session.rollback()
            return False

    return True


if __name__ == '__main__':
    print("=" * 50)
    print("Flask 投票系统数据库初始化")
    print("=" * 50)

    print("\n[步骤1] 创建数据库...")
    if not create_database():
        print("数据库创建失败，程序退出")
        exit(1)

    print("\n[步骤2] 创建数据表...")
    if not create_tables():
        print("数据表创建失败，程序退出")
        exit(1)

    print("\n[步骤3] 添加中文注释...")
    if not add_comments():
        print("添加注释失败，但数据库初始化已完成")

    print("\n" + "=" * 50)
    print("数据库初始化完成！")
    print("=" * 50)
