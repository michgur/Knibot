import re

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
    }
    name_re = re.compile(r'[^,]+')


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


# merge a list of hebrew strings
def _list_string_hebrew(items):
    return ', '.join(items[:-1]) + ' ' + prompts.vav + items[-1] if len(items) > 1 else items[0]


def _add_tokenized_items(user, tokens, add_fn=knibot_db.add_items, rmv_fn=knibot_db.remove_items):
    cmds, items = zip(*tokens)
    if rmv_fn is not None and _token_labels.INSTEAD in cmds:
        instead_index = cmds.index(_token_labels.INSTEAD)
        rmv_fn(user, items[instead_index + 1:])
        items = items[:instead_index]
    existing = knibot_db.get_existing_items(user, items)
    non_existing = [i for i in items if i not in existing]
    add_fn(user, non_existing)
    return prompts.existing_item_err % _list_string_hebrew(existing) if len(existing) > 0 else ''


def _remove_tokenized_items(user, tokens, rmv_fn=knibot_db.remove_items,
                            rmv_all_fn=knibot_db.remove_all_items,
                            rmv_all_but_fn=knibot_db.remove_all_items_but):
    cmds, items = zip(*tokens)
    if cmds[0] == _token_labels.ALL:
        if len(cmds) > 2 and cmds[1] == _token_labels.EXCEPT:
            if items[2].startswith(prompts.mem):
                items = list(items)
                items[2] = items[2][1:]
            rmv_all_but_fn(user, items[2:])
        else:
            rmv_all_fn(user)
    else:
        existing = knibot_db.get_existing_items(user, items)
        non_existing = [i for i in items if i not in existing]
        rmv_fn(user, existing)
        if len(non_existing) == 1:
            return prompts.non_existing_item_err % non_existing[0]
        elif len(non_existing) > 1:
            return prompts.non_existing_items_err % _list_string_hebrew(non_existing)
    return ''


def _admin_check(user):
    if not knibot_db.is_admin(user):
        raise PermissionError(prompts.not_admin_err)


def run_command(user, message):
    try:
        tokens = list(_tokenize(message))
        cmd = tokens[0][0]

        if cmd == _token_labels.NAME:
            state = knibot_db.get_working_state(user)
            if state == knibot_db.STATE_WRITING:
                return _add_tokenized_items(user, tokens)
            elif state == knibot_db.STATE_ERASING:
                return _remove_tokenized_items(user, tokens)
            else:
                return prompts.default_working_state_err

        if cmd == _token_labels.SEND:
            users = len(tokens) > 1 and tokens[1][0] == _token_labels.USERS
            items_raw = knibot_db.get_list_users(user) if users else knibot_db.get_list_items(user)
            items_text = '\n'.join(str(i + 1) + ': ' + r[0] + ' (' + str(r[2]) + ')'
                                   for i, r in enumerate(items_raw))
            return prompts.send_msg + items_text if items_text != '' else prompts.empty_list_err

        if cmd == _token_labels.LIST:
            if tokens[1][0] == _token_labels.NEW:
                knibot_db.create_list(user, tokens[2][1])
                knibot_db.set_working_list(user, tokens[2][1])
                return prompts.new_list_msg % tokens[2][1]
            else:
                knibot_db.set_working_list(user, tokens[1][1])
                return prompts.list_msg % tokens[1][1]

        if cmd == _token_labels.NEW:
            knibot_db.create_list(user, tokens[1][1])
            return prompts.new_msg % tokens[1][1]

        if cmd == _token_labels.WRITE:
            if len(tokens) == 1:
                knibot_db.set_working_state(user, knibot_db.STATE_WRITING)
                return prompts.write_msg
            else:
                return prompts.finish_write_msg + ' ' + \
                       _add_tokenized_items(user, tokens[1:])

        if cmd == _token_labels.ERASE:
            if len(tokens) == 1:
                knibot_db.set_working_state(user, knibot_db.STATE_ERASING)
                return prompts.remove_msg
            else:
                return prompts.finish_remove_msg + ' ' + \
                       _remove_tokenized_items(user, tokens[1:])

        if cmd == _token_labels.FINISH:
            state = knibot_db.get_working_state(user)
            knibot_db.set_working_state(user, knibot_db.STATE_DEFAULT)
            return prompts.finish_write_msg if state == knibot_db.STATE_WRITING \
                else prompts.finish_remove_msg

        if cmd == _token_labels.BOUGHT:
            if len(tokens) == 1:
                tokens.append((_token_labels.ALL, ''))
            return prompts.bought_msg + ' ' + \
                   _remove_tokenized_items(user, tokens[1:])

        if cmd == _token_labels.SHARE:
            _add_tokenized_items(user, tokens[1:],
                                 knibot_db.add_users_to_list, knibot_db.remove_users_from_list)
            return prompts.share_msg

        if cmd == _token_labels.TURN_INTO and tokens[1][0] == _token_labels.ADMIN:
            _admin_check(user)
            _add_tokenized_items(user, tokens[2:], knibot_db.set_as_admins)
            return prompts.set_admins_msg

        if cmd == _token_labels.HELP:
            # check tokens[1] for specific command help
            return prompts.greet_msg

    except Exception as e:
        return str(e)
    return prompts.unrecognized_msg_err


if __name__ == '__main__':
    print(run_command(972502057283, 'תמחק חציל, אביר'))
