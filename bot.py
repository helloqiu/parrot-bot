# -*- coding: utf-8 -*-

from cqhttp import CQHttp
from utils import check_admin, SQLiteStorage
from gevent.pywsgi import WSGIServer
import random
import logging

bot = CQHttp(api_root='http://127.0.0.1:5700')
bot_config = {
    'rate': 0.05,
    'ban_duration': 60 * 5
}

session = SQLiteStorage()
session.config = bot_config


@bot.on_event('group_increase')
def handle_group_increase(context):
    logging.info('有新人!')
    bot.send(context, message='欢迎新人！\n请先关注群公告哦~')


@bot.on_message('group')
def handle_group_message(context):
    # check if the user is admin
    if_admin = check_admin(context['group_id'], context['user_id'], bot)
    if not context['anonymous']:
        last_message = session.get(context['group_id'])
        logging.debug(context['raw_message'])
        if last_message and last_message['message'] == context['raw_message'] and random.choice([True, False]):
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
            if random.randint(0, 9) < session.config['rate'] * 10:
                bot.send_group_msg(
                    group_id=context['group_id'],
                    message=context['message']
                )
        session.set(context['group_id'], {'message': context['raw_message']})


http_server = WSGIServer(('127.0.0.1', 8080), bot._server_app)
http_server.serve_forever()
