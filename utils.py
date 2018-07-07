# -*- coding: utf-8 -*-


def check_admin(group_id, user_id, bot):
    result = bot.get_group_member_info(group_id=group_id, user_id=user_id)
    if result['role'] in ['owner', 'admin']:
        return True
    else:
        return False


class Message:
    def __init__(self):
        self.message = None
    
    def check(m):
        if m == self.message:
            return True
        else:
            self.message = m
            return False
