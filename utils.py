# -*- coding: utf-8 -*-


def check_admin(group_id, user_id, bot):
    result = bot.get_group_member_info(group_id=group_id, user_id=user_id)
    if result['role'] in ['owner', 'admin']:
        return True
    else:
        return False
