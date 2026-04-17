# -*- coding: utf-8 -*-
"""
Flask 在线投票系统主应用模块
提供投票的创建、查看、参与和管理功能
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from sqlalchemy import func
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import Config
from models import db, Poll, PollOption, Vote, User

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # 在生产环境中可能没有.env文件，忽略加载错误
    pass

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# 数据库初始化函数
def init_database():
    """初始化数据库，创建表结构和默认管理员账户"""
    with app.app_context():
        try:
            # 尝试连接数据库并创建表
            print('正在初始化数据库...')
            db.create_all()
            print('数据库表创建成功')
            
            # 创建默认管理员账户
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                # 从环境变量读取管理员密码，默认值仅用于开发环境
                admin_password = os.environ.get('ADMIN_PASSWORD', 'asdfghjkl555')
                admin = User(
                    username='admin',
                    is_admin=True
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                print('默认管理员账户已创建')
                print('提示：在生产环境中，请通过 ADMIN_PASSWORD 环境变量设置强密码')
            else:
                print('管理员账户已存在')
        except Exception as e:
            print(f'数据库初始化出错：{e}')
            print('请确保数据库连接配置正确，并且数据库服务已启动')

# 在应用启动时执行数据库初始化
init_database()


def login_required(f):
    """登录装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员权限装饰器"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'error')
            return redirect(url_for('login'))
        try:
            user = User.query.get(session['user_id'])
            if not user or not user.is_admin:
                flash('需要管理员权限', 'error')
                return redirect(url_for('index'))
        except Exception:
            flash('请先登录', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """首页路由：展示投票列表"""
    page = request.args.get('page', 1, type=int)
    per_page = Config.POLLS_PER_PAGE

    polls_query = db.session.query(
        Poll,
        func.coalesce(func.sum(PollOption.vote_count), 0).label('total_votes')
    ).outerjoin(PollOption, Poll.id == PollOption.poll_id)\
     .filter(Poll.is_deleted == False)\
     .group_by(Poll.id)\
     .order_by(Poll.created_at.desc())

    pagination = polls_query.paginate(page=page, per_page=per_page, error_out=False)
    polls = [{'poll': p[0], 'total_votes': p[1]} for p in pagination.items]

    return render_template('index.html', polls=polls, pagination=pagination)


@app.route('/poll/create', methods=['GET', 'POST'])
def create_poll():
    """创建投票路由"""
    # 检查是否为管理员
    if 'user_id' not in session:
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    try:
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('需要管理员权限', 'error')
            return redirect(url_for('index'))
    except Exception:
        flash('请先登录', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        is_multiple = request.form.get('is_multiple') == 'on'
        options = request.form.getlist('options')

        if not title:
            flash('投票标题不能为空', 'error')
            return redirect(url_for('create_poll'))

        if len(title) > Config.MAX_TITLE_LENGTH:
            flash(f'投票标题不能超过{Config.MAX_TITLE_LENGTH}个字符', 'error')
            return redirect(url_for('create_poll'))

        if len(description) > Config.MAX_DESCRIPTION_LENGTH:
            flash(f'投票描述不能超过{Config.MAX_DESCRIPTION_LENGTH}个字符', 'error')
            return redirect(url_for('create_poll'))

        valid_options = [opt.strip() for opt in options if opt.strip()]

        if len(valid_options) < Config.MIN_OPTIONS:
            flash(f'投票至少需要{Config.MIN_OPTIONS}个选项', 'error')
            return redirect(url_for('create_poll'))

        if len(valid_options) > Config.MAX_OPTIONS:
            flash(f'投票最多只能有{Config.MAX_OPTIONS}个选项', 'error')
            return redirect(url_for('create_poll'))

        for opt_text in valid_options:
            if len(opt_text) > Config.MAX_OPTION_TEXT_LENGTH:
                flash(f'选项内容不能超过{Config.MAX_OPTION_TEXT_LENGTH}个字符', 'error')
                return redirect(url_for('create_poll'))

        try:
            new_poll = Poll(
                title=title,
                description=description,
                is_multiple=is_multiple
            )
            db.session.add(new_poll)
            db.session.flush()

            for opt_text in valid_options:
                option = PollOption(
                    poll_id=new_poll.id,
                    option_text=opt_text
                )
                db.session.add(option)

            db.session.commit()
            flash('投票创建成功', 'success')
            return redirect(url_for('poll_detail', poll_id=new_poll.id))

        except Exception as e:
            db.session.rollback()
            flash(f'创建投票失败：{str(e)}', 'error')
            return redirect(url_for('create_poll'))

    return render_template('create_poll.html')


@app.route('/poll/<int:poll_id>')
def poll_detail(poll_id):
    """投票详情路由"""
    try:
        poll = Poll.query.filter_by(id=poll_id, is_deleted=False).first()

        if not poll:
            flash('投票不存在或已被删除', 'error')
            return redirect(url_for('index'))

        options = poll.options.all()
        total_votes = poll.get_total_votes()

        options_data = []
        for option in options:
            options_data.append({
                'option': option,
                'percentage': option.get_percentage(total_votes)
            })

        client_ip = request.remote_addr
        print(f'Poll detail - 用户IP地址: {client_ip}')
        
        # 查询投票记录（基于IP）
        vote_record = None
        try:
            vote_record = Vote.query.filter_by(poll_id=poll_id, ip_address=client_ip).first()
        except Exception as e:
            print(f'查询投票记录出错: {e}')
            vote_record = None
        
        has_voted = vote_record is not None
        print(f'Poll detail - 投票记录查询结果: {vote_record}')
        print(f'Poll detail - has_voted: {has_voted}')
        
        # 查询所有投票记录，用于调试
        try:
            all_votes = Vote.query.filter_by(poll_id=poll_id).all()
            print(f'Poll detail - 该投票的所有投票记录: {len(all_votes)} 条')
            for vote in all_votes:
                print(f'  - IP: {vote.ip_address}, 时间: {vote.voted_at}')
        except Exception as e:
            print(f'查询所有投票记录出错: {e}')

        return render_template('poll_detail.html',
                             poll=poll,
                             options_data=options_data,
                             total_votes=total_votes,
                             has_voted=has_voted)
    except Exception as e:
        print(f'Poll detail 路由出错: {e}')
        import traceback
        traceback.print_exc()
        # 返回错误页面或重定向到首页
        flash('页面加载出错，请稍后重试', 'error')
        return redirect(url_for('index'))


@app.route('/poll/<int:poll_id>/vote', methods=['POST'])
def vote(poll_id):
    """投票路由：处理用户投票请求"""
    poll = Poll.query.filter_by(id=poll_id, is_deleted=False).first()

    if not poll:
        return jsonify({'success': False, 'message': '投票不存在或已被删除'}), 404

    client_ip = request.remote_addr
    user_id = request.form.get('user_id')
    print(f'Vote - 用户IP地址: {client_ip}')
    print(f'Vote - 用户标识符: {user_id}')

    # 检查是否已经投过票（基于IP）
    existing_vote = None
    try:
        existing_vote = Vote.query.filter_by(poll_id=poll_id, ip_address=client_ip).first()
    except Exception as e:
        print(f'查询投票记录出错: {e}')
        existing_vote = None
    
    # 如果有user_id，检查localStorage中的投票记录
    if user_id:
        # 这里可以使用Redis或其他缓存系统来存储user_id和投票记录
        # 由于没有缓存系统，我们暂时只基于IP地址检查
        print(f'收到用户标识符: {user_id}，但暂时只基于IP地址检查')
    
    if existing_vote:
        print(f'用户已经投过票，投票记录ID: {existing_vote.id}')
        return jsonify({'success': False, 'message': '您已经投过票了'}), 403

    selected_options = request.form.getlist('options')

    if not selected_options:
        return jsonify({'success': False, 'message': '请至少选择一个选项'}), 400

    if not poll.is_multiple and len(selected_options) > 1:
        return jsonify({'success': False, 'message': '该投票为单选投票，只能选择一个选项'}), 400

    valid_option_ids = [opt.id for opt in poll.options.all()]
    for opt_id in selected_options:
        if int(opt_id) not in valid_option_ids:
            return jsonify({'success': False, 'message': '选择的选项无效'}), 400

    try:
        # 创建投票记录（基于IP）
        vote_record = Vote(
            poll_id=poll_id,
            ip_address=client_ip
        )
        db.session.add(vote_record)
        print(f'创建投票记录: poll_id={poll_id}, ip={client_ip}')

        for opt_id in selected_options:
            option = PollOption.query.get(int(opt_id))
            if option:
                option.vote_count += 1
                print(f'更新选项票数: option_id={opt_id}, new_count={option.vote_count}')

        db.session.commit()
        print('投票记录保存成功')

        # 再次检查是否保存成功
        saved_vote = Vote.query.filter_by(poll_id=poll_id, ip_address=client_ip).first()
        if saved_vote:
            print(f'投票记录已保存，ID: {saved_vote.id}')
        else:
            print('投票记录保存失败')

        return jsonify({
            'success': True,
            'message': '投票成功',
            'total_votes': poll.get_total_votes()
        })

    except Exception as e:
        db.session.rollback()
        print(f'投票失败: {str(e)}')
        return jsonify({'success': False, 'message': f'投票失败：{str(e)}'}), 500


@app.route('/poll/<int:poll_id>/delete', methods=['POST'])
def delete_poll(poll_id):
    """删除投票路由（软删除）"""
    # 检查是否为管理员
    if 'user_id' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': '请先登录'}), 401
        else:
            flash('请先登录', 'error')
            return redirect(url_for('login'))
    try:
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': '需要管理员权限'}), 403
            else:
                flash('需要管理员权限', 'error')
                return redirect(url_for('index'))
    except Exception:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': '请先登录'}), 401
        else:
            flash('请先登录', 'error')
            return redirect(url_for('login'))
    
    poll = Poll.query.filter_by(id=poll_id, is_deleted=False).first()

    # 检查是否为 AJAX 请求
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Content-Type') == 'application/json'

    if not poll:
        if is_ajax:
            return jsonify({'success': False, 'message': '投票不存在或已被删除'}), 404
        else:
            flash('投票不存在或已被删除', 'error')
            return redirect(url_for('index'))

    try:
        poll.is_deleted = True
        poll.updated_at = datetime.utcnow()
        db.session.commit()

        if is_ajax:
            return jsonify({'success': True, 'message': '投票删除成功'})
        else:
            flash('投票删除成功', 'success')
            return redirect(url_for('index'))

    except Exception as e:
        db.session.rollback()
        if is_ajax:
            return jsonify({'success': False, 'message': f'删除失败：{str(e)}'}), 500
        else:
            flash(f'删除失败：{str(e)}', 'error')
            return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({'success': False, 'message': '页面不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    db.session.rollback()
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录路由"""
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash('用户名或密码错误', 'error')
            return redirect(url_for('login'))

        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        flash('登录成功', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """登出路由"""
    session.clear()
    flash('已成功登出', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
