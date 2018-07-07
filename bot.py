# -*- coding: utf-8 -*-

from cqhttp import CQHttp
from utils import check_admin, Message
from gevent.pywsgi import WSGIServer
import random
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
bot = CQHttp(api_root='http://127.0.0.1:5700')
bot_config = {
    'rate': 0.1
}

last_message = Message()


@bot.on_event('group_increase')
def handle_group_increase(context):
    logging.info('有新人!')
    bot.send(context, message='欢迎新人！\n请先关注群公告哦~', is_raw=True)


@bot.on_message('group')
def handle_group_message(context):
    # check if the user is admin
    if_admin = check_admin(context['group_id'], context['user_id'], bot)
    if not if_admin and not context['anonymous']:
        logging.info(context['raw_message'])
        logging.info(last_message.message)
        if last_message.check(context['raw_message']) and random.choice([True, False]):
            # 禁言！
            logging.info('禁言！')
            bot.set_group_ban(group_id=context['group_id'], user_id=context['user_id'], duration=60 * 5)
            bot.send_group_msg(
                group_id=context['group_id'],
                message='[CQ:at,qq={}]这是一只鹦鹉[CQ:emoji,id=128536]'.format(context['user_id'])
            )
        else:
            # 变成复读机！
            if random.randint(0, 9) < bot_config['rate'] * 10:
                bot.send_group_msg(
                    group_id=context['group_id'],
                    message=context['message']
                )


http_server = WSGIServer(('127.0.0.1', 8080), bot._server_app)
http_server.serve_forever()
