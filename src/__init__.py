# -*- coding: utf-8 -*-
"""
Flask 在线投票系统源代码包
包含应用主文件、配置和数据库模型
"""

# 延迟导入，避免循环导入问题
app = None

__all__ = ['app']

# 当需要时再导入
if app is None:
    try:
        from .app import app
    except Exception as e:
        print(f"导入app模块时出错: {e}")