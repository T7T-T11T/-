# -*- coding: utf-8 -*-
"""
Flask 在线投票系统主应用模块
提供投票的创建、查看、参与和管理功能
"""

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import func
from config import Config
from models import db, Poll, PollOption, Vote

# 创建 Flask 应用实例
app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)


@app.route('/')
def index():
    """
    首页路由：展示投票列表
    获取所有未删除的投票，按创建时间倒序排列
    Returns:
        render_template: 渲染首页模板
    """
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = Config.POLLS_PER_PAGE

    # 查询所有未删除的投票，并计算每个投票的总票数
    # 使用子查询获取投票总数
    polls_query = db.session.query(
        Poll,
        func.coalesce(func.sum(PollOption.vote_count), 0).label('total_votes')
    ).outerjoin(PollOption, Poll.id == PollOption.poll_id)\
     .filter(Poll.is_deleted == False)\
     .group_by(Poll.id)\
     .order_by(Poll.created_at.desc())

    # 执行分页
    pagination = polls_query.paginate(page=page, per_page=per_page, error_out=False)
    polls = [{'poll': p[0], 'total_votes': p[1]} for p in pagination.items]

    return render_template('index.html', polls=polls, pagination=pagination)


@app.route('/poll/create', methods=['GET', 'POST'])
def create_poll():
    """
    创建投票路由
    GET: 显示创建投票表单
    POST: 处理创建投票请求
    Returns:
        GET: 渲染创建投票模板
        POST: 重定向到投票详情页或返回错误
    """
    if request.method == 'POST':
        # 获取表单数据
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        is_multiple = request.form.get('is_multiple') == 'on'
        options = request.form.getlist('options')

        # 验证投票标题
        if not title:
            flash('投票标题不能为空', 'error')
            return redirect(url_for('create_poll'))

        if len(title) > Config.MAX_TITLE_LENGTH:
            flash(f'投票标题不能超过{Config.MAX_TITLE_LENGTH}个字符', 'error')
            return redirect(url_for('create_poll'))

        # 验证投票描述
        if len(description) > Config.MAX_DESCRIPTION_LENGTH:
            flash(f'投票描述不能超过{Config.MAX_DESCRIPTION_LENGTH}个字符', 'error')
            return redirect(url_for('create_poll'))

        # 验证投票选项
        valid_options = [opt.strip() for opt in options if opt.strip()]

        if len(valid_options) < Config.MIN_OPTIONS:
            flash(f'投票至少需要{Config.MIN_OPTIONS}个选项', 'error')
            return redirect(url_for('create_poll'))

        if len(valid_options) > Config.MAX_OPTIONS:
            flash(f'投票最多只能有{Config.MAX_OPTIONS}个选项', 'error')
            return redirect(url_for('create_poll'))

        # 检查选项长度
        for opt_text in valid_options:
            if len(opt_text) > Config.MAX_OPTION_TEXT_LENGTH:
                flash(f'选项内容不能超过{Config.MAX_OPTION_TEXT_LENGTH}个字符', 'error')
                return redirect(url_for('create_poll'))

        try:
            # 创建投票
            new_poll = Poll(
                title=title,
                description=description,
                is_multiple=is_multiple
            )
            db.session.add(new_poll)
            db.session.flush()

            # 创建投票选项
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
    """
    投票详情路由
    获取指定投票的详细信息，包括选项和投票结果
    Args:
        poll_id (int): 投票ID
    Returns:
        render_template: 渲染投票详情模板
    """
    poll = Poll.query.filter_by(id=poll_id, is_deleted=False).first()

    if not poll:
        flash('投票不存在或已被删除', 'error')
        return redirect(url_for('index'))

    # 获取投票的所有选项
    options = poll.options.all()
    total_votes = poll.get_total_votes()

    # 计算每个选项的百分比
    options_data = []
    for option in options:
        options_data.append({
            'option': option,
            'percentage': option.get_percentage(total_votes)
        })

    # 检查当前IP是否已投票
    client_ip = request.remote_addr
    has_voted = Vote.query.filter_by(poll_id=poll_id, ip_address=client_ip).first() is not None

    return render_template('poll_detail.html',
                         poll=poll,
                         options_data=options_data,
                         total_votes=total_votes,
                         has_voted=has_voted)


@app.route('/poll/<int:poll_id>/vote', methods=['POST'])
def vote(poll_id):
    """
    投票路由：处理用户投票请求
    Args:
        poll_id (int): 投票ID
    Returns:
        JSON: 返回投票结果或错误信息
    """
    # 检查投票是否存在
    poll = Poll.query.filter_by(id=poll_id, is_deleted=False).first()

    if not poll:
        return jsonify({'success': False, 'message': '投票不存在或已被删除'}), 404

    # 获取投票者IP
    client_ip = request.remote_addr

    # 检查是否已投票（防止重复投票）
    existing_vote = Vote.query.filter_by(poll_id=poll_id, ip_address=client_ip).first()
    if existing_vote:
        return jsonify({'success': False, 'message': '您已经投过票了'}), 403

    # 获取选择的选项
    selected_options = request.form.getlist('options')

    if not selected_options:
        return jsonify({'success': False, 'message': '请至少选择一个选项'}), 400

    # 验证选项数量
    if not poll.is_multiple and len(selected_options) > 1:
        return jsonify({'success': False, 'message': '该投票为单选投票，只能选择一个选项'}), 400

    # 验证选项是否属于该投票
    valid_option_ids = [opt.id for opt in poll.options.all()]
    for opt_id in selected_options:
        if int(opt_id) not in valid_option_ids:
            return jsonify({'success': False, 'message': '选择的选项无效'}), 400

    try:
        # 记录投票
        vote_record = Vote(
            poll_id=poll_id,
            ip_address=client_ip
        )
        db.session.add(vote_record)

        # 更新选项票数
        for opt_id in selected_options:
            option = PollOption.query.get(int(opt_id))
            if option:
                option.vote_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '投票成功',
            'total_votes': poll.get_total_votes()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'投票失败：{str(e)}'}), 500


@app.route('/poll/<int:poll_id>/delete', methods=['POST'])
def delete_poll(poll_id):
    """
    删除投票路由（软删除）
    Args:
        poll_id (int): 投票ID
    Returns:
        JSON: 返回删除结果
    """
    poll = Poll.query.filter_by(id=poll_id, is_deleted=False).first()

    if not poll:
        return jsonify({'success': False, 'message': '投票不存在或已被删除'}), 404

    try:
        # 软删除：将 is_deleted 设置为 True
        poll.is_deleted = True
        poll.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'success': True, 'message': '投票删除成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败：{str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """
    404 错误处理
    Args:
        error: 错误对象
    Returns:
        JSON: 返回404错误信息
    """
    return jsonify({'success': False, 'message': '页面不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    """
    500 错误处理
    Args:
        error: 错误对象
    Returns:
        JSON: 返回500错误信息
    """
    db.session.rollback()
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500


if __name__ == '__main__':
    with app.app_context():
        # 创建所有表
        db.create_all()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
