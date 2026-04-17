# -*- coding: utf-8 -*-
"""
数据库模型模块
定义投票系统的数据模型，包括投票主题、选项和投票记录
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt

from config import Config

db = SQLAlchemy()


class Poll(db.Model):
    """投票主题模型"""
    __tablename__ = 'polls'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='投票ID')
    title = db.Column(db.String(100), nullable=False, comment='投票标题')
    description = db.Column(db.Text, comment='投票描述')
    is_multiple = db.Column(db.Boolean, default=False, comment='是否多选')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否已删除')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    options = db.relationship('PollOption', backref='poll', lazy='dynamic', cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='poll', lazy='dynamic', cascade='all, delete-orphan')

    def get_total_votes(self):
        """获取投票的总票数"""
        return sum(option.vote_count for option in self.options)

    def to_dict(self):
        """将投票对象转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'is_multiple': self.is_multiple,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_votes': self.get_total_votes(),
            'options': [option.to_dict() for option in self.options]
        }


class PollOption(db.Model):
    """投票选项模型"""
    __tablename__ = 'poll_options'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='选项ID')
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'), nullable=False, comment='所属投票ID')
    option_text = db.Column(db.String(200), nullable=False, comment='选项内容')
    vote_count = db.Column(db.Integer, default=0, comment='得票数')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    def to_dict(self):
        """将选项对象转换为字典格式"""
        return {
            'id': self.id,
            'poll_id': self.poll_id,
            'option_text': self.option_text,
            'vote_count': self.vote_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_percentage(self, total_votes):
        """计算当前选项的得票百分比"""
        if total_votes == 0:
            return 0.0
        return round((self.vote_count / total_votes) * 100, 2)


class Vote(db.Model):
    """投票记录模型"""
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='投票记录ID')
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'), nullable=False, comment='投票ID')
    ip_address = db.Column(db.String(45), nullable=False, comment='投票者IP地址')
    user_id = db.Column(db.String(36), nullable=True, comment='用户浏览器标识符')
    voted_at = db.Column(db.DateTime, default=datetime.utcnow, comment='投票时间')
    
    # 添加唯一约束，确保每个用户只能对每个投票投一次票
    __table_args__ = (
        db.UniqueConstraint('poll_id', 'ip_address', name='_poll_ip_uc'),
        db.UniqueConstraint('poll_id', 'user_id', name='_poll_user_uc'),
    )

    def to_dict(self):
        """将投票记录对象转换为字典格式"""
        return {
            'id': self.id,
            'poll_id': self.poll_id,
            'ip_address': self.ip_address,
            'user_id': self.user_id,
            'voted_at': self.voted_at.isoformat() if self.voted_at else None
        }


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(100), nullable=False, comment='密码哈希')
    is_admin = db.Column(db.Boolean, default=False, comment='是否管理员')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    def to_dict(self):
        """将用户对象转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def set_password(self, password):
        """设置密码（自动哈希）"""
        # bcrypt 限制密码长度为 72 字节
        password = password[:72]
        # 生成盐并哈希密码
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """检查密码是否正确"""
        # bcrypt 限制密码长度为 72 字节
        password = password[:72]
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
