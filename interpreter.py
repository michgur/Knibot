import re
from typing import List, Tuple

import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Contact, Bot

from database import *


class _token_labels:
    NAME = 0
    SHARE = 1
    SEND = 6
    LIST = 7
    NEW = 8
    WRITE = 9
    ERASE = 10
    CANCEL = 11
    ALL = 12
    EXCEPT = 13
    INSTEAD = 14
    COMMA = 15
    FINISH = 16
    BOUGHT = 17
    TURN_INTO = 18
    ADMIN = 19
    HELP = 20
    USERS = 21
    LISTS = 22

    operators = {
        'שלח': SEND,
        'רשימה': LIST,
        'חדשה': NEW,
        'רשום': WRITE,
        'תרשום': WRITE,
        'מחק': ERASE,
        'תמחק': ERASE,
        'בטל': CANCEL,
        'הכול': ALL,
        'כולם': ALL,
        'חוץ': EXCEPT,
        'במקום': INSTEAD,
        ',': COMMA,
        'זהו': FINISH,
        'קניתי': BOUGHT,
        'שתף': SHARE,
        'תשתף': SHARE,
        'הפוך': TURN_INTO,
        'תהפוך': TURN_INTO,
        'למנהל': ADMIN,
        'למנהלת': ADMIN,
        'למנהלים': ADMIN,
        'למנהלות': ADMIN,
        'עזרה': HELP,
        'משתתפים': USERS,
        'רשימות': LISTS,
    }
    name_re = re.compile(r'[^,]+')


bot = None


# split a string message to labeled tokens
def _tokenize(msg):
    tokens = re.split(r'\s+|(,)', msg)
    name = ''
    for t in tokens:
        if not t:
            continue
        if t in _token_labels.operators:
            op = _token_labels.operators[t]
            if name != '':
                yield _token_labels.NAME, name
                name = ''
            if op != _token_labels.COMMA:
                yield op, t
        else:
            name_match = _token_labels.name_re.match(t)
            if name_match is not None:
                if name != '':
                    name += ' '
                name += name_match.group()
            else:
                raise ValueError('unknown token %s' % t)
    if name != '':
        yield _token_labels.NAME, name


def _add_tokenized_items(user, tokens, add_fn=knibot_db.add_items, rmv_fn=knibot_db.remove_items):
    cmds, items = zip(*tokens)
    if rmv_fn is not None and _token_labels.INSTEAD in cmds:
        instead_index = cmds.index(_token_labels.INSTEAD)
        rmv_fn(user, items[instead_index + 1:])
        items = items[:instead_index]
    existing = knibot_db.get_existing_items(user, items)
    non_existing = [i for i in items if i not in existing]
    add_fn(user, non_existing)
    return prompts_he.existing_item_err % prompts_he.list_to_string(existing) if len(existing) > 0 else ''


def _remove_tokenized_items(user, tokens, rmv_fn=knibot_db.remove_items,
                            rmv_all_fn=knibot_db.remove_all_items,
                            rmv_all_but_fn=knibot_db.remove_all_items_but):
    global bot
    cmds, items = zip(*tokens)
    if cmds[0] == _token_labels.ALL:
        if len(cmds) > 2 and cmds[1] == _token_labels.EXCEPT:
            if items[2].startswith(prompts_he.mem):
                items = list(items)
                items[2] = items[2][1:]
            all_items = knibot_db.get_list_items(user)
            rmv_items = [i[0] for i in all_items if i not in items[2:]]
            _notify_users(bot, user, rmv_items)
            rmv_all_but_fn(user, items[2:])
        else:
            _notify_users(bot, user)
            rmv_all_fn(user)
    else:
        existing = knibot_db.get_existing_items(user, items)
        non_existing = [i for i in items if i not in existing]
        _notify_users(bot, user, existing)
        rmv_fn(user, existing)
        if len(non_existing) == 1:
            return prompts_he.non_existing_item_err % non_existing[0]
        elif len(non_existing) > 1:
            return prompts_he.non_existing_items_err % prompts_he.list_to_string(non_existing)
    return ''


def _admin_check(user):
    if not knibot_db.is_admin(user):
        raise PermissionError(prompts_he.not_admin_err)


def _notify_users(bot: telegram.Bot, buyer: int, items: list = None):
    with knibot_db.connect() as conn:
        c = conn.cursor()
        working_list = knibot_db.get_working_list(buyer, c)
        c.execute('SELECT user_id FROM listsForUsers WHERE list_id=%i' % working_list)
        users = list(*zip(*c.fetchall()))
        for u in users:
            missing_items = []
            if items is not None:
                c.execute('SELECT name FROM items WHERE list_id=%i AND request_by=%i' % (working_list, u))
                u_items = list(*zip(*c.fetchall()))
                if len(u_items) == 0:
                    continue
                missing_items = [i for i in u_items if i not in items]
                if len(missing_items) == len(u_items):
                    continue
            text = prompts_he.mention(bot.get_chat(buyer)) + ' ' + \
                   prompts_he.everything_but(missing_items, prompts_he.bought_everything)
            bot.send_message(chat_id=u, parse_mode='HTML', text=text)


class _inline_buttons:
    SEND = InlineKeyboardButton(text=prompts_he.send_btn, switch_inline_query_current_chat='שלח')
    LIST = InlineKeyboardButton(text=prompts_he.list_btn, switch_inline_query_current_chat='רשימה ')
    LISTS = InlineKeyboardButton(text=prompts_he.lists_btn, switch_inline_query_current_chat='רשימות')
    NEW_LIST = InlineKeyboardButton(text=prompts_he.new_list_btn, switch_inline_query_current_chat='רשימה חדשה ')
    WRITE = InlineKeyboardButton(text=prompts_he.write_btn, switch_inline_query_current_chat='תרשום ')
    REMOVE = InlineKeyboardButton(text=prompts_he.remove_btn, switch_inline_query_current_chat='תמחק ')
    REMOVE_ALL = InlineKeyboardButton(text=prompts_he.remove_all_btn, switch_inline_query_current_chat='תמחק הכול')
    BUY = InlineKeyboardButton(text=prompts_he.bought_btn, switch_inline_query_current_chat='קניתי ')
    BUY_BUT = InlineKeyboardButton(text=prompts_he.bought_but_btn, switch_inline_query_current_chat='קניתי הכול חוץ מ')


def run_command(bott, user, message):
    global bot
    bot = bott
    try:
        tokens = list(_tokenize(message))
        if tokens[0][1].startswith('@'):
            tokens = tokens[1:]
        cmd = tokens[0][0]

        if cmd == _token_labels.NAME:
            state = knibot_db.get_working_state(user)
            if state == knibot_db.STATE_WRITING:
                return _add_tokenized_items(user, tokens)
            elif state == knibot_db.STATE_ERASING:
                return _remove_tokenized_items(user, tokens)
            else:
                return prompts_he.default_working_state_err

        if cmd == _token_labels.SEND:
            users = len(tokens) > 1 and tokens[1][0] == _token_labels.USERS
            items_raw = knibot_db.get_list_users(user) if users else knibot_db.get_list_items(user)
            items_text = '\n'.join('• <code>' + r[0] + '</code> (' + prompts_he.mention(bot.get_chat(r[2])) + ')'
                                   for r in items_raw)
            text = prompts_he.send_msg + items_text if items_text != '' else prompts_he.empty_list_err
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text='shalom', switch_inline_query_current_chat='shalomm')]])
            bot.send_message(chat_id=user, text=text, reply_markup=keyboard)
            return ''

        if cmd == _token_labels.LIST:
            if tokens[1][0] == _token_labels.NEW:
                knibot_db.create_list(user, tokens[2][1])
                knibot_db.set_working_list(user, tokens[2][1])
                return prompts_he.new_list_msg % tokens[2][1]
            else:
                knibot_db.set_working_list(user, tokens[1][1])
                return prompts_he.list_msg % tokens[1][1]

        if cmd == _token_labels.NEW:
            knibot_db.create_list(user, tokens[1][1])
            return prompts_he.new_msg % tokens[1][1]

        if cmd == _token_labels.WRITE:
            if len(tokens) == 1:
                knibot_db.set_working_state(user, knibot_db.STATE_WRITING)
                return prompts_he.write_msg
            else:
                return prompts_he.finish_write_msg + ' ' + \
                       _add_tokenized_items(user, tokens[1:])

        if cmd == _token_labels.ERASE:
            if len(tokens) == 1:
                knibot_db.set_working_state(user, knibot_db.STATE_ERASING)
                return prompts_he.remove_msg
            else:
                return prompts_he.finish_remove_msg + ' ' + \
                       _remove_tokenized_items(user, tokens[1:])

        if cmd == _token_labels.FINISH:
            state = knibot_db.get_working_state(user)
            knibot_db.set_working_state(user, knibot_db.STATE_DEFAULT)
            return prompts_he.finish_write_msg if state == knibot_db.STATE_WRITING \
                else prompts_he.finish_remove_msg if state == knibot_db.STATE_ERASING \
                else prompts_he.finish_share_msg

        if cmd == _token_labels.BOUGHT:
            if len(tokens) == 1:
                tokens.append((_token_labels.ALL, ''))
            return prompts_he.bought_msg + ' ' + \
                   _remove_tokenized_items(user, tokens[1:])

        if cmd == _token_labels.SHARE:
            knibot_db.set_working_state(user, knibot_db.STATE_SHARING)
            return prompts_he.share_msg

        if cmd == _token_labels.TURN_INTO and tokens[1][0] == _token_labels.ADMIN:
            _admin_check(user)
            _add_tokenized_items(user, tokens[2:], knibot_db.set_as_admins)
            return prompts_he.set_admins_msg

        if cmd == _token_labels.LISTS:
            lists_raw = knibot_db.get_lists_for_user(user)
            lists_string = '\n'.join('• <code>%s</code>' % l[0] for l in lists_raw)
            return prompts_he.no_lists_err if not lists_string else lists_string

        if cmd == _token_labels.HELP:
            # check tokens[1] for specific command help
            return prompts_he.greet_msg

    except Exception as e:
        print(e)
        return str(e)
    return prompts_he.unrecognized_msg_err


def add_contact(bot: Bot, user: int, contact: Contact):
    if knibot_db.get_working_state(user) == knibot_db.STATE_SHARING:
        knibot_db.add_users_to_list(user, contact.user_id)
    else:
        bot.send_message(chat_id=user, text=prompts_he.unrecognized_msg_err)


if __name__ == '__main__':
    print(*zip(*[('a',), ('b',), ('c',)]))
