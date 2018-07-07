# -*- coding: utf-8 -*-

from cqhttp import CQHttp
from utils import check_admin
from gevent.pywsgi import WSGIServer
import random

bot = CQHttp(api_root='http://127.0.0.1:5700')
bot_config = {
    'rate': 0.1
}
last_message = None


@bot.on_event('group_increase')
def handle_group_increase(context):
    bot.send(context, message='欢迎新人！\n请先关注群公告哦~', is_raw=True)


@bot.on_message('group')
def handle_group_message(context):
    global last_message
    # check if the user is admin
    if_admin = check_admin(context.group_id, context.user_id, bot)
    if not if_admin and not context.anonymous:
        if context.message == last_message and random.choice([True, False]):
            # 禁言！
            last_message = context.message
            bot.set_group_ban(context.group_id, context.user_id, 60 * 5)
            bot.send_group_msg(
                context.group_id,
                message='[CQ:at,qq={}]这是一只鹦鹉[CQ:emoji,id=128536]'.format(context.user_id)
            )
        else:
            # 变成复读机！
            if random.randint(0, 9) < bot_config['rate'] * 10:
                bot.send_group_msg(
                    context.group_id,
                    message=context.message
                )


http_server = WSGIServer(('127.0.0.1', 8080), bot._server_app)
http_server.serve_forever()
