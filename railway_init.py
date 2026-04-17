# -*- coding: utf-8 -*-
"""
Railway 数据库初始化脚本
用于在 Railway 部署时初始化数据库
"""

from app import app, db
from models import Poll, PollOption, Vote, User

with app.app_context():
    try:
        print('=== Railway 数据库初始化 ===')
        
        # 创建所有表
        print('1. 创建数据库表...')
        db.create_all()
        print('   ✓ 数据库表创建成功')
        
        # 检查并创建管理员账户
        print('2. 检查管理员账户...')
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            import os
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin = User(
                username='admin',
                is_admin=True
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print('   ✓ 默认管理员账户已创建')
        else:
            print('   ✓ 管理员账户已存在')
        
        print('\n=== 数据库初始化完成 ===')
        print('您可以通过以下方式访问应用：')
        print('- 管理后台：/login')
        print('- 管理员账号：admin')
        print('- 管理员密码：环境变量中设置的 ADMIN_PASSWORD')
        
    except Exception as e:
        print(f'数据库初始化出错：{e}')
        print('请检查环境变量配置是否正确')
        import traceback
        traceback.print_exc()
