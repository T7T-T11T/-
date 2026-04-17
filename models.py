# -*- coding: utf-8 -*-
"""
数据库模型模块
定义投票系统的数据模型，包括投票主题、选项和投票记录
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# 创建 SQLAlchemy 数据库实例
db = SQLAlchemy()


class Poll(db.Model):
    """
    投票主题模型
    存储投票的基本信息，包括标题、描述、投票类型等
    """
    __tablename__ = 'polls'

    # 主键，自增ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='投票ID')
    # 投票标题，最大100字符
    title = db.Column(db.String(100), nullable=False, comment='投票标题')
    # 投票描述，可选，最大500字符
    description = db.Column(db.Text, comment='投票描述')
    # 是否为多选投票，默认为单选
    is_multiple = db.Column(db.Boolean, default=False, comment='是否多选')
    # 软删除标记，防止数据误删
    is_deleted = db.Column(db.Boolean, default=False, comment='是否已删除')
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    # 更新时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 定义与 PollOption 的一对多关系
    options = db.relationship('PollOption', backref='poll', lazy='dynamic', cascade='all, delete-orphan')
    # 定义与 Vote 的一对多关系
    votes = db.relationship('Vote', backref='poll', lazy='dynamic', cascade='all, delete-orphan')

    def get_total_votes(self):
        """
        获取投票的总票数
        Returns:
            int: 所有选项的票数总和
        """
        return sum(option.vote_count for option in self.options)

    def to_dict(self):
        """
        将投票对象转换为字典格式，用于 API 响应
        Returns:
            dict: 包含投票所有信息的字典
        """
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
    """
    投票选项模型
    存储投票的各个选项及其得票数
    """
    __tablename__ = 'poll_options'

    # 主键，自增ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='选项ID')
    # 关联投票ID，外键关联 polls 表
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'), nullable=False, comment='所属投票ID')
    # 选项内容，最大200字符
    option_text = db.Column(db.String(200), nullable=False, comment='选项内容')
    # 投票计数，默认为0
    vote_count = db.Column(db.Integer, default=0, comment='得票数')
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    def to_dict(self):
        """
        将选项对象转换为字典格式，用于 API 响应
        Returns:
            dict: 包含选项所有信息的字典
        """
        return {
            'id': self.id,
            'poll_id': self.poll_id,
            'option_text': self.option_text,
            'vote_count': self.vote_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_percentage(self, total_votes):
        """
        计算当前选项的得票百分比
        Args:
            total_votes (int): 投票总票数
        Returns:
            float: 得票百分比，保留2位小数
        """
        if total_votes == 0:
            return 0.0
        return round((self.vote_count / total_votes) * 100, 2)


class Vote(db.Model):
    """
    投票记录模型
    存储每次投票的记录，用于防止重复投票
    """
    __tablename__ = 'votes'

    # 主键，自增ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='投票记录ID')
    # 关联投票ID，外键关联 polls 表
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'), nullable=False, comment='投票ID')
    # 投票者IP地址，用于防止重复投票
    ip_address = db.Column(db.String(45), nullable=False, comment='投票者IP地址')
    # 投票时间
    voted_at = db.Column(db.DateTime, default=datetime.utcnow, comment='投票时间')

    def to_dict(self):
        """
        将投票记录对象转换为字典格式
        Returns:
            dict: 包含投票记录信息的字典
        """
        return {
            'id': self.id,
            'poll_id': self.poll_id,
            'ip_address': self.ip_address,
            'voted_at': self.voted_at.isoformat() if self.voted_at else None
        }
