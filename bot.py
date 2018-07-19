# -*- coding: utf-8 -*-

from cqhttp import CQHttp
from utils import check_admin, SQLiteStorage, lucky_enough, compile_command
from gevent.pywsgi import WSGIServer
import random
import logging

bot = CQHttp(api_root='http://127.0.0.1:5700')
bot_config = {
    'rate': 0.05,
    'ban_duration': 60 * 5,
    'ban_rate': 0.5
}
help_message = '[CQ:at,qq={}]\n' \
               '/help 获取帮助\n' \
               '/setbanrate 设置鹦鹉查处力度（0-1）\n' \
               '/setrepeatrate 设置鹦鹉力度（0-1）\n' \
               '/showconfig 显示当前设置'

session = SQLiteStorage()
session.config = bot_config


@bot.on_event('group_increase')
def handle_group_increase(context):
    logging.info('有新人!')
    bot.send(context, message='欢迎新人！\n请先关注群公告哦~')


@bot.on_message('group')
def handle_group_message(context):
    # check if this is a command
    command = compile_command(context['raw_message'])
    if command:
        return handle_command(context, *command)
    else:
        return handle_plain_text(context)


def handle_plain_text(context):
    # check if the user is admin
    if_admin = check_admin(context['group_id'], context['user_id'], bot)
    if not context['anonymous']:
        last_message = session.get(context['group_id'])
        logging.debug(context['raw_message'])
        if last_message and last_message['message'] == context['raw_message'] and lucky_enough(
                int(last_message['ban_rate'] * 100)):
            if not if_admin:
                # 禁言！
                logging.debug('禁言！')
                bot.set_group_ban(
                    group_id=context['group_id'],
                    user_id=context['user_id'],
                    duration=session.config['ban_duration']
                )
                bot.send_group_msg(
                    group_id=context['group_id'],
                    message='[CQ:at,qq={}]\n这是一只鹦鹉[CQ:emoji,id=128536]'.format(context['user_id'])
                )
            else:
                # 低头！
                logging.debug('低头！')
                bot.send_group_msg(
                    group_id=context['group_id'],
                    message='[CQ:at,qq={}]\n亲亲可爱鹦鹉\n[CQ:emoji,id=128536]'.format(context['user_id'])
                )
        else:
            # 变成复读机！
            if lucky_enough(int(last_message['rate'] * 100)):
                bot.send_group_msg(
                    group_id=context['group_id'],
                    message=context['message']
                )
        if not last_message:
            session.set(context['group_id'], {'message': context['raw_message'], **bot_config})
        else:
            last_message['message'] = context['raw_message']
            session.set(context['group_id'], last_message)


def handle_command(context, command, arg):
    if_admin = check_admin(context['group_id'], context['user_id'], bot)
    if not if_admin:
        bot.send_group_msg(
            group_id=context['group_id'],
            message='[CQ:at,qq={}]\n只有亲亲管理员是我大哥'.format(context['user_id'])
        )
    else:
        _command = command.strip().lower()
        if _command == 'help':
            bot.send_group_msg(
                group_id=context['group_id'],
                message=help_message.format(context['user_id'])
            )
        elif _command == 'setbanrate':
            return handle_setbanrate(context, _command, arg)
        elif _command == 'setrepeatrate':
            return handle_setrepeatrate(context, _command, arg)
        elif _command == 'showconfig':
            group_session = session.get(context['group_id'])
            bot.send_group_msg(
                group_id=context['group_id'],
                message='[CQ:at,qq={}]\n鹦鹉查处力度：{}\n鹦鹉力度：{}'.format(context['user_id'],
                                                                   round(group_session['ban_rate'], 2),
                                                                   round(group_session['rate'], 2))
            )


def handle_setbanrate(context, command, arg):
    try:
        arg = float(arg)
    except ValueError:
        bot.send_group_msg(
            group_id=context['group_id'],
            message='[CQ:at,qq={}]\n指令错误'.format(context['user_id'])
        )
    if int(arg * 100) not in range(0, 101):
        bot.send_group_msg(
            group_id=context['group_id'],
            message='[CQ:at,qq={}]\n必须是0-1的数字哦'.format(context['user_id'])
        )
    else:
        group_session = session.get(context['group_id'])
        if 'ban_rate' in group_session:
            group_session['ban_rate'] = arg
        else:
            group_session['ban_rate'] = bot_config['ban_rate']
        session.set(context['group_id'], group_session)


def handle_setrepeatrate(context, command, arg):
    try:
        arg = float(arg)
    except ValueError:
        bot.send_group_msg(
            group_id=context['group_id'],
            message='[CQ:at,qq={}]\n指令错误'.format(context['user_id'])
        )
    if int(arg * 100) not in range(0, 101):
        bot.send_group_msg(
            group_id=context['group_id'],
            message='[CQ:at,qq={}]\n必须是0-1的数字哦'.format(context['user_id'])
        )
    else:
        group_session = session.get(context['group_id'])
        if 'rate' in group_session:
            group_session['rate'] = arg
        else:
            group_session['rate'] = bot_config['rate']
        session.set(context['group_id'], group_session)


http_server = WSGIServer(('127.0.0.1', 8080), bot._server_app)
http_server.serve_forever()
